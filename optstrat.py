#-*- coding:utf-8 -*-
'''
optstrat.py
Created on Feb 03, 2015
@author: Harvey
'''
BDAYS_PER_YEAR = 245.0
RISK_FREE_RATE = 0.04

import os
import csv
import pyktlib
import mysqlaccess
import numpy as np
import pandas as pd
from misc import *

def fut2opt(fut_inst, expiry, otype, strike):
    product = inst2product(fut_inst)
    if product == 'IF':
        optkey = fut_inst.replace('IF','IO')
    else:
        optkey = product
    if product == 'Stock':
        optkey = optkey + otype + expiry.strftime('%y%m')
    else:
        optkey + '-' + upper(type) + '-'
    opt_inst = optkey + str(int(strike))
    return opt_inst

def get_opt_margin(fut_price, strike, type):
    return 0.0

def time2exp(opt_expiry, curr_time):
    curr_date = curr_time.date()
    exp_date = opt_expiry.date()
    if curr_time > opt_expiry:
        return 0.0
    elif exp_date < curr_date:
        return workdays.networkdays(curr_date, exp_date, misc.CHN_Holidays)/BDAYS_PER_YEAR
    else:
        delta = opt_expiry - curr_time 
        return (delta.hour*3600+delta.min*60+delta.second)/3600.0/5.5/BDAYS_PER_YEAR


class OptionStrategy(object):
    def __init__(self, name, underliers, expiries, strikes, agent = None):
        self.name = name
        self.underliers = underliers
        self.main_cont = 0
        self.expiries = expiries
        self.DFs = [1.0] * len(expiries)
        self.volgrids = dict([(expiry, None) for expiry in expiries])
        self.accrual = 'CFFEX'
        self.strikes = strikes
        self.opt_dict = self.get_option_map(underliers, expiries, strikes)
        self.option_insts = dict([(inst, None) for inst in self.opt_dict.values()])
        self.option_map = pd.DataFrame(0, index = self.underliers + self.opt_dict.values(), 
                                columns = ['underlier', 'cont_mth', 'otype', 'strike', 'multiple', 'df',
                                           'pv', 'delta', 'gamma', 'vega', 'theta',  
                                           'ppv', 'pdelta', 'pgamma', 'pvega', 'ptheta', 
                                           'pos', 'outlong', 'outshort', 'margin_long', 'margin_short'])
        self.group_risk = None
        for inst in underliers:
            self.option_map.loc[inst, 'underlier'] = inst
            self.option_map.loc[inst, 'df'] = 1.0
        for key in self.opt_dict:
            inst = self.opt_dict[key]
            opt_info = {'underlier': key[0], 'cont_mth': key[1], 'otype': key[2], 'strike': key[3], 'df':1.0}
            self.option_map.loc[inst, opt_info.keys()] = pd.Series(opt_info) 
        self.instIDs = self.underliers + self.option_insts.keys()
        self.irate = RISK_FREE_RATE
        self.agent = agent
        self.folder = ''
        self.logger = None
        self.reset()
        self.submitted_pos = dict([(inst, []) for inst in self.instIDs])
        self.is_initialized = False
        self.proxy_flag = {'delta': False, 'gamma': True, 'vega': True, 'theta': True} 
        self.hedge_config = {'order_type': OPT_MARKET_ORDER, 'num_tick':1}
        self.spot_model = False
        self.pricer = pyktlib.BlackPricer
        self.last_updated = dict([(expiry, {'dtoday':0, 'fwd':0.0}) for expiry in expiries]) 

    def reset(self):
        if self.agent != None:
            self.folder = self.agent.folder + self.name + '_'
            self.logger = self.agent.logger
            for inst in self.instIDs:
                self.option_map.loc[inst, 'multiple'] = self.agent.instruments[inst].multiple
                self.option_map.loc[inst, 'cont_mth'] = self.agent.instruments[inst].cont_mth
        #self.load_state()
    
    def day_start(self):
        pass
    
    def get_fwd(self, idx):
        return self.agent.instruments[self.underliers[idx]].price
    
    def get_DF(self, dtoday, dexp):
        return np.exp(-self.irate * max(dexp - dtoday,0)/365.0)
        
    def initialize(self):
        self.load_state()
        dtoday = date2xl(self.agent.scur_day) + max(self.agent.tick_id - 600000, 0)/2400000.0
        for idx, expiry in enumerate(self.expiries):
            dexp = datetime2xl(expiry)
            self.DFs[idx] = self.get_DF(dtoday, dexp)
            fwd = self.get_fwd(idx) 
            self.last_updated[expiry]['fwd'] = fwd
            self.last_updated[expiry]['dtoday'] = dtoday
            if self.spot_model:
                self.option_map.loc[self.underliers[0], 'delta'] = 1.0
                self.option_map.loc[self.underliers[0], 'df'] = 1.0
            else:
                self.option_map.loc[self.underliers[idx], 'delta'] = self.DFs[idx]
                self.option_map.loc[self.underliers[idx], 'df'] = self.DFs[idx]
            if self.volgrids[expiry] == None:
                self.volgrids[expiry] = pyktlib.Delta5VolNode(dtoday, dexp, fwd, 0.24, 0.0, 0.0, 0.0, 0.0, self.accrual)                
            self.volgrids[expiry].setFwd(fwd)
            self.volgrids[expiry].setToday(dtoday)
            self.volgrids[expiry].setExp(dexp)
            self.volgrids[expiry].initialize()
            cont_mth = expiry.year * 100 + expiry.month
            indices = self.option_map[(self.option_map.cont_mth == cont_mth) & (self.option_map.otype != 0)].index
            for inst in indices:
                strike = self.option_map.loc[inst].strike
                otype  = self.option_map.loc[inst].otype
                if not self.spot_model:
                    self.option_map.loc[inst, 'df'] = self.DFs[idx]
                self.option_insts[inst] = self.pricer(dtoday, dexp, fwd, self.volgrids[expiry], strike, self.irate, otype)
                self.update_greeks(inst)
        self.update_pos_greeks()
        self.update_group_risk()
        self.update_margin()
        self.is_initialized = True
        return
    
    def set_volgrids(self, expiry, vol_params):
        if self.volgrids[expiry] != None:
            self.volgrids[expiry].setFwd(vol_params['fwd'])
            self.volgrids[expiry].setAtm(vol_params['atm'])
            self.volgrids[expiry].setD90Vol(vol_params['v90'])
            self.volgrids[expiry].setD75Vol(vol_params['v75'])
            self.volgrids[expiry].setD25Vol(vol_params['v25'])
            self.volgrids[expiry].setD10Vol(vol_params['v10'])
            self.volgrids[expiry].initialize()
        return 
    
    def update_margin(self):
        for inst in self.instIDs:
            if inst in self.underliers:
                self.option_map.loc[inst, 'margin_long'] = self.agent.instruments[inst].calc_margin_amount(ORDER_BUY)
                self.option_map.loc[inst, 'margin_short'] = self.agent.instruments[inst].calc_margin_amount(ORDER_SELL)
            else:
                under = self.agent.instruments[inst].underlying
                under_price = self.agent.instruments[under].price
                self.option_map.loc[inst, 'margin_long'] = self.agent.instruments[inst].calc_margin_amount(ORDER_BUY, under_price)
                self.option_map.loc[inst, 'margin_short'] = self.agent.instruments[inst].calc_margin_amount(ORDER_SELL, under_price)
                 
    def update_greeks(self, inst): 
        '''update option instrument greeks'''
        multiple = self.option_map.loc[inst, 'multiple']
        pv = self.option_insts[inst].price() * multiple
        delta = self.option_insts[inst].delta() * multiple
        gamma = self.option_insts[inst].gamma() * multiple
        vega  = self.option_insts[inst].vega() * multiple/100.0
        theta = self.option_insts[inst].theta() * multiple
        df = self.option_map.loc[inst, 'df']
        opt_info = {'pv': pv, 'delta': delta/df, 'gamma': gamma/df/df, 'vega': vega, 'theta': theta}
        self.option_map.loc[inst, opt_info.keys()] = pd.Series(opt_info)
        return 
    
    def update_pos_greeks(self):
        '''update position greeks according to current positions'''
        keys = ['pv', 'delta', 'gamma', 'vega', 'theta']
        for key in keys:
            pos_key = 'p' + key
            self.option_map[pos_key] = self.option_map[key] * self.option_map['pos']
        return 
        
    def risk_reval(self, expiry, is_recalib=True):
        '''recalibrate vol surface per fwd move, get greeks update for instrument greeks'''
        dtoday = date2xl(self.agent.scur_day) + max(self.agent.tick_id - 600000, 0)/2400000.0
        cont_mth = expiry.year * 100 + expiry.month
        indices = self.option_map[(self.option_map.cont_mth == cont_mth) & (self.option_map.otype != 0)].index
        dexp = datetime2xl(expiry)
        fwd = self.get_fwd(idx)
        if is_recalib:
            self.last_updated[expiry]['fwd'] = fwd
            self.last_updated[expiry]['dtoday'] = dtoday
            self.volgrids[expiry].setFwd(fwd)
            self.volgrids[expiry].setToday(dtoday)            
            self.volgrids[expiry].initialize()                
        for inst in indices:
            self.option_insts[inst].setFwd(fwd)
            self.option_insts[inst].setFwd(dtoday)
            self.update_greeks(inst)
        return 
    
    def update_group_risk(self):
        group_keys = ['cont_mth', 'ppv', 'pdelta', 'pgamma','pvega','ptheta']
        self.group_risk = self.option_map[group_keys].groupby('cont_mth').sum()
        return
    
    def add_submitted_pos(self, etrade):
        is_added = False
        for trade in self.submitted_pos:
            if trade.id == etrade.id:
                is_added = False
                return
        self.submitted_pos.append(etrade)
        return True
    
    def update_positions(self):
#         save_status = False
#         for etrade in self.submitted_pos:
#             if etrade.status == order.ETradeStatus.Done:
#                 for inst, fvol, fp in zip(etrade.instIDs, etrade.filled_vol, etrade.filled_price):
#                     
#                 if etrade.status != order.ETradeStatus.StratConfirm:
#                     etrade.status = order.ETradeStatus.StratConfirm
#                     save_status = True                    
#                     self.logger.warning('the trade %s is done but not found in the strat=%s tradepos table' % (etrade.id, self.name))
#             elif etrade.status == order.ETradeStatus.Cancelled:
#                 if etrade.status != order.ETradeStatus.StratConfirm: 
#                     print "WARNING:the trade %s is cancelled but not found in the strat=%s tradepos table, removing the trade" % (etrade.id, self.name)
#                     self.logger.warning('the trade %s is cancelled but not found in the strat=%s tradepos table' % (etrade.id, self.name))
#                     etrade.status = order.ETradeStatus.StratConfirm
#                     save_status = True
#         self.positions[idx] = [ tradepos for tradepos in self.positions[idx] if not tradepos.is_closed]            
#         self.submitted_pos[idx] = [etrade for etrade in self.submitted_pos[idx] if etrade.status!=order.ETradeStatus.StratConfirm]
#         return save_status        
        pass

    def day_finalize(self):    
        self.save_state()
        self.logger.info('strat %s is finalizing the day - update trade unit, save state' % self.name)
        self.is_initialized = False
        pass
        
    def get_option_map(self, underliers, expiries, strikes):
        opt_map = {}
        for under, expiry, ks in zip(underliers, expiries, strikes):
            for otype in ['C', 'P']:
                for strike in ks:
                    cont_mth = int(under[-4:]) + 200000
                    key = (str(under), cont_mth, otype, strike)
                    instID = under
                    if instID[:2] == "IF":
                        instID = instID.replace('IF', 'IO')
                    instID = instID + '-' + otype + '-' + str(strike)
                    opt_map[key] = instID
        return opt_map
    
    def run_tick(self, ctick):
        pass

    def run_min(self, ctick):
        pass
    
    def save_state(self):
        filename = self.folder + 'strat_status.csv'
        self.logger.info('save state for strat = %s' % (self.name))
        with open(filename,'wb') as log_file:
            file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for expiry in self.expiries:
                if self.volgrids[expiry] != None:
                    volnode = self.volgrids[expiry]
                    row = [ 'VolNode', 
                            expiry.strftime('%Y%m%d %H:%M:%S'), 
                            volnode.fwd_(), 
                            volnode.atmVol_(), 
                            volnode.d90Vol_(),
                            volnode.d75Vol_(),
                            volnode.d25Vol_(),
                            volnode.d10Vol_() ]
                    file_writer.writerow(row)
            for inst in self.option_map.index:
                row = ['Pos', str(inst), self.option_map.loc[inst, 'pos']]
                file_writer.writerow(row)
        return
    
    def load_state(self):
        logfile = self.folder + 'strat_status.csv'
        if not os.path.isfile(logfile):
            return 
        self.logger.info('load state for strat = %s' % (self.name))
        with open(logfile, 'rb') as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if row[0] == 'VolNode':
                    expiry = datetime.datetime.strptime(row[1], '%Y%m%d %H:%M:%S')
                    fwd = float(row[2])
                    atm = float(row[3])
                    v90 = float(row[4])
                    v75 = float(row[5])
                    v25 = float(row[6])
                    v10 = float(row[7])
                    dtoday = datetime2xl(datetime.datetime.now())
                    dexp   = datetime2xl(expiry)
                    self.volgrids[expiry] = pyktlib.Delta5VolNode(dtoday, dexp, fwd, atm, v90, v75, v25, v10, self.accrual)
                elif row[0]== 'Pos':
                    instID = str(row[1])
                    self.option_map.loc[instID, 'pos'] = int(row[2]) 
        return
    
    def delta_hedger(self):
        tot_deltas = self.group_risk.pdelta.sum()
        cum_vol = 0
        if (self.spot_model == False) and (self.proxy_flag['delta']== False):
            for idx, inst in enumerate(self.underliers):
                if idx == self.main_cont: 
                    continue
                multiple = self.option_map[inst, 'multiple']
                cont_mth = self.option_map[inst, 'cont_mth']
                pdelta = self.group_risk[cont_mth, 'delta'] 
                volume = int( - pdeltas/multiple + 0.5)
                cum_vol += volume
                if volume!=0:
                    curr_price = self.agent.instruments[inst].price
                    buysell = 1 if volume > 0 else -1
                    valid_time = self.agent.tick_id + 600
                    etrade = order.ETrade( [inst], [volume], [self.hedge_config['order_type']], curr_price*buysell, [self.hedge_config['num_tick']], \
                                               valid_time, self.name, self.agent.name)
                    self.submitted_pos[inst].append(etrade)
                    self.agent.submit_trade(etrade)
        inst = self.underliers[self.main_cont]
        multiple = self.option_map[inst, 'multiple']
        tot_deltas += cum_vol
        volume = int( tot_deltas/multiple + 0.5)
        if volume!=0:
            curr_price = self.agent.instruments[inst].price
            buysell = 1 if volume > 0 else -1
            etrade = order.ETrade( [inst], [volume], [self.hedge_config['order_type']], curr_price*buysell, [self.hedge_config['num_tick']], \
                                valid_time, self.name, self.agent.name)
            self.submitted_pos[inst].append(etrade)
            self.agent.submit_trade(etrade)
        return
        
class EquityOptStrat(OptionStrategy):
    def __init__(self, name, underliers, expiries, strikes, agent = None):
        OptionStrategy.__init__(self, name, underliers, expiries, strikes, agent)
        self.accrual = 'SSE'
        self.proxy_flag = {'delta': True, 'gamma': True, 'vega': True, 'theta': True}
        self.spot_model = True
        self.rate_diff = 0.06 
        self.dividends = [(datetime.date(2015,4,20), 0.0), (datetime.date(2015,11,20), 0.10)]
        
    def get_option_map(self, underliers, expiries, strikes):
        cont_mths = [expiry.year*100 + expiry.month for expiry in expiries]
        all_map = {}
        for under in underliers:
            map = mysqlaccess.get_stockopt_map(under, cont_mths, strikes)
            all_map.update(map)
        return all_map
    
    def get_fwd(self, idx):
        spot = self.agent.instruments[self.underliers[0]].price
        return spot*self.DFs[idx]
    
class IndexFutOptStrat(OptionStrategy):
    def __init__(self, name, underliers, expiries, strikes, agent = None):
        OptionStrategy.__init__(self, name, underliers, expiries, strikes, agent)
        self.accrual = 'CFFEX'
        self.proxy_flag = {'delta': True, 'gamma': True, 'vega': True, 'theta': True} 
        self.spot_model = False
        self.rate_diff = 0.0 

class CommodOptStrat(OptionStrategy):
    def __init__(self, name, underliers, expiries, strikes, agent = None):
        OptionStrategy.__init__(self, name, underliers, expiries, strikes, agent)
        self.accrual = 'COM'
        self.proxy_flag = {'delta': False, 'gamma': False, 'vega': True, 'theta': True} 
        self.spot_model = False
        self.pricer = pyktlib.AmericanFutPricer  
        
class OptArbStrat(CommodOptStrat):
    def __init__(self, name, underliers, expiries, strikes, agent = None):
        CommodOptStrat.__init__(self, name, underliers, expiries, strikes, agent)
        self.callspd = dict([(exp, dict([(s, {'upbnd':0.0, 'lowbnd':0.0, 'pos':0.0}) for s in ss])) for exp, ss in zip(expiries, strikes)])
        self.putspd = dict([(exp, dict([(s, {'upbnd':0.0, 'lowbnd':0.0, 'pos':0.0}) for s in ss])) for exp, ss in zip(expiries, strikes)])
        self.bfly = dict([(exp, dict([(s, {'upbnd':0.0, 'lowbnd':0.0, 'pos':0.0}) for s in ss])) for exp, ss in zip(expiries, strikes)])
        
              
    def run_tick(self, ctick):         
        inst = ctick.instID
        pass
