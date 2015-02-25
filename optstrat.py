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
        self.expiries = expiries
        #self.fwds  = [1] * len(cont_mths)
        #self.volparams = dict([(mth, [0.2, 0.0, 0.0, 0.0, 0.0]) for mth in cont_mths])
        self.volgrids = dict([(expiry, None) for expiry in expiries])
        self.accrual = 'CFE'
        opt_dict = self.get_option_map(underliers, expiries, strikes)
        self.option_insts = dict([(inst, None) for inst in opt_dict.values()])
        self.option_map = pd.DataFrame(0, index = self.underliers + opt_dict.values(), \
                                       columns = ['underlier', 'cont_mth', 'otype', 'strike', 'multiple', \
                                                  'pv', 'delta', 'gamma', 'vega', 'theta', 'pos'])
        for inst in underliers:
            inst_info = {'underlier': inst, 'delta': 1 }
            self.option_map.loc[inst, 'underlier'] = pd.Series(inst_info)
        for key in opt_dict:
            inst = opt_dict[key]
            opt_info = {'underlier': key[0], 'cont_mth': key[1], 'otype': key[2], 'strike': key[3]}
            self.option_map.loc[inst] = pd.Series(opt_info) 
        self.instIDs = self.underliers + self.option_insts.keys()
        self.irate = RISK_FREE_RATE
        self.agent = agent
        self.logger = None
        if self.agent != None:
            self.logger = self.agent.logger 
        self.positions  = dict([(inst, 0) for inst in self.instIDs])
        self.submitted_pos = []
        if agent == None:
            self.folder = ''
        else:
            self.folder = self.folder + self.name + '_'

    def reset(self):
        if self.agent == None:
            self.folder = ''
        else:
            self.folder = self.agent.folder + self.name + '_'
            self.logger = self.agent.logger
            for inst in self.instIDs:
                self.option_map.loc[inst, 'multiple'] = self.agent.instruments[inst].multiple
        self.load_state()

    def initialize(self):
        self.load_state()
        for under, expiry in zip(self.underliers, self.expiries):
            dtoday = date2xl(self.agent.scur_day) + max(self.agent.tick_id - 600000, 0)/2400000.0
            dexp = datetime2xl(expiry)
            fwd = self.agent.instruments[under].price
            if self.volgrids[expiry] == None:
                self.volgrids[expiry] = pyktlib.Delta5VolNode(dtoday, dexp, fwd, 0.24, 0.0, 0.0, 0.0, 0.0, self.accrual)                
            self.volgrids[expiry].setFwd(fwd)
            self.volgrids[expiry].setToday(dtoday)
            self.volgrids[expiry].setExp(dexp)
            self.volgrids[expiry].initialize()
            cont_mth = expiry.year * 100 + expiry.month
            self.option_map.loc[under, 'multiple'] = self.agent.instruments[under].multiple
            indices = self.option_map.index((self.option_map.underlier == under) & (self.option_map.cont_mth == cont_mth))
            for inst in indices:
                strike = self.option_map.loc[inst].strike
                otype  = self.option_map.loc[inst].otype
                self.option_insts[inst] = pyktlib.BlackPricer(dtoday, dexp, fwd, self.volgrids[expiry], strike, self.irate, otype)
                self.option_map.loc[inst, 'multiple'] = self.agent.instruments[inst].multiple
                self.update_greeks(inst)
        return

    def update_greeks(selfself, inst):
        pv = self.option_insts[inst].price()
        delta = self.option_insts[inst].delta()
        gamma = self.option_insts[inst].gamma()
        vega  = self.option_insts[inst].vega()
        theta = self.option_insts[inst].theta()
        opt_info = {'pv': pv, 'delta': delta, 'gamma': gamma, 'vega': vega, 'theta': theta}
        self.option_map.loc[inst] = pd.Series(opt_info)
        return 
    
    def add_submitted_pos(self, etrade):
        is_added = False
        for trade in self.submitted_pos:
            if trade.id == etrade.id:
                is_added = False
                return
        self.submitted_pos.append(etrade)
        return True

    def day_finalize(self):    
        self.save_state()
        self.logger.info('strat %s is finalizing the day - update trade unit, save state' % self.name)
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
            for idx, expiry in enumerate(self.expiries):
                dtoday = datetime2xl(datetime.datetime.now())
                dexp   = datetime2xl(expiry)
                fwd = 100.0
                atm = 0.24
                if self.agent != None:
                    if len(self.expiries) == len(self.underliers):
                        fwd = self.agent.instruments[self.underliers[idx]].price
                    else:
                        spot = self.agent.instruments[self.underliers[0]].price
                        fwd = spot * exp(self.irate * (dexp - dtoday)/365.0)
                self.logger.info('strat=%s status file is not found, use default fwd=%s, vol=%s' % (self.name, fwd, atm))
                self.volgrids[expiry] = pyktlib.Delta5VolNode(dtoday, dexp, fwd, atm, 0.0, 0.0, 0.0, 0.0, self.accrual)
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
        
class EquityOptStrat(OptionStrategy):
    def __init__(self, name, underliers, expiries, strikes, agent = None):
        OptionStrategy.__init__(self, name, underliers, expiries, strikes, agent)
        self.accrual = 'SSE'
        
    def get_option_map(self, underliers, expiries, strikes):
        cont_mths = [expiry.year*100 + expiry.month for expiry in expiries]
        all_map = {}
        for under in underliers:
            map = mysqlaccess.get_stockopt_map(under, cont_mths, strikes)
            all_map.update(map)
        return all_map
    
    def initialize(self):
        self.load_state()
        spot = self.agent.instruments[self.underliers[0]].price
        
        for expiry in zip(self.volgrids):
            dtoday = date2xl(self.agent.scur_day) + max(self.agent.tick_id - 600000, 0)/2400000.0
            dexp = datetime2xl(expiry)
            fwd = spot * np.exp(max(dexp-dtoday, 0)*self.irate/365.0)
            if self.volgrids[expiry] == None:
                self.volgrids[expiry] = pyktlib.Delta5VolNode(dtoday, dexp, fwd, 0.3, 0.0, 0.0, 0.0, 0.0, self.accrual)
            self.volgrids[expiry].setFwd(fwd)
            self.volgrids[expiry].setToday(dtoday)
            self.volgrids[expiry].setExp(dexp)
            self.volgrids[expiry].initialize()
        pass