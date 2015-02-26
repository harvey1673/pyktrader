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
        self.expiries = expiries
        self.volgrids = dict([(expiry, None) for expiry in expiries])
        self.accrual = 'CFE'
        opt_dict = self.get_option_map(underliers, expiries, strikes)
        self.option_insts = dict([(inst, None) for inst in opt_dict.values()])
        self.option_map = pd.DataFrame(0, index = self.underliers + opt_dict.values(), \
                                       columns = ['underlier', 'cont_mth', 'otype', 'strike', 'multiple', \
                                                  'pv', 'delta', 'gamma', 'vega', 'theta', 
												  'ppv', 'pdelta', 'pgamma', 'pvega', 'ptheta', 'pos', 'outbuy', 'outsell'])
		self.group_risk = None
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
		self.folder = ''
        self.logger = None
        self.reset()
        self.positions  = dict([(inst, 0) for inst in self.instIDs])
        self.submitted_pos = []
		self.is_initialized = False
		self.proxy_flag = {'delta': False, 'gamma': True, 'vega': True, 'theta': True} 

    def reset(self):
        if self.agent != None:
            self.folder = self.agent.folder + self.name + '_'
            self.logger = self.agent.logger
            for inst in self.instIDs:
				self.option_map.loc[under, 'multiple'] = self.agent.instruments[under].multiple
				self.option_map.loc[under, 'cont_mth'] = self.agent.instruments[under].cont_mth
        #self.load_state()
	
	def day_start(self):
		pass

    def initialize(self):
        self.load_state()
		dtoday = date2xl(self.agent.scur_day) + max(self.agent.tick_id - 600000, 0)/2400000.0
		spot = self.agent.instruments[self.underliers[0]].price
        for idx, expiry in enumerate(self.expiries):
            dexp = datetime2xl(expiry)
			if self.accrual in ['SSE', 'SZE']:
				fwd = spot * np.exp(self.irate * max(dexp - dtoday,0)/365.0)
            else:
				fwd = self.agent.instruments[self.underliers[idx]].price
            if self.volgrids[expiry] == None:
                self.volgrids[expiry] = pyktlib.Delta5VolNode(dtoday, dexp, fwd, 0.24, 0.0, 0.0, 0.0, 0.0, self.accrual)                
            self.volgrids[expiry].setFwd(fwd)
            self.volgrids[expiry].setToday(dtoday)
            self.volgrids[expiry].setExp(dexp)
            self.volgrids[expiry].initialize()
            cont_mth = expiry.year * 100 + expiry.month
            indices = self.option_map.index((self.option_map.cont_mth == cont_mth) and (self.option_map.otype != 0))
            for inst in indices:
				if self.is_initialized == False:
					strike = self.option_map.loc[inst].strike
					otype  = self.option_map.loc[inst].otype
					self.option_insts[inst] = pyktlib.BlackPricer(dtoday, dexp, fwd, self.volgrids[expiry], strike, self.irate, otype)
                self.update_greeks(inst)
		self.update_pos_greeks()
		self.update_group_risk()
		self.is_initialized = True
        return

    def update_greeks(self, inst):
		multiple = self.option_map.loc[inst, 'multiple']
        pv = self.option_insts[inst].price()
        delta = self.option_insts[inst].delta()
        gamma = self.option_insts[inst].gamma()
        vega  = self.option_insts[inst].vega()
        theta = self.option_insts[inst].theta()
        opt_info = {'pv': pv * multiple, 'delta': delta * multiple, 'gamma': gamma * multiple, 'vega': vega * multiple, 'theta': theta * multiple}
        self.option_map.loc[inst] = pd.Series(opt_info)
        return 
	
	def update_pos_greeks(self):
		keys = ['pv', 'delta', 'gamma', 'vega', 'theta']
		for key in keys:
			pos_key = 'p' + key
			self.option_map[pos_key] = self.option_map[pos_key] * self.option_map['pos']
		return 
    
	def risk_reval(self, is_recalib):
		dtoday = date2xl(self.agent.scur_day) + max(self.agent.tick_id - 600000, 0)/2400000.0
		if is_recalib:
			spot = self.agent.instruments[self.underliers[0]].price
			for idx, expiry in enumerate(self.expiries):
				dexp = datetime2xl(expiry)
				if self.accrual in ['SSE', 'SZE']:
					fwd = spot * np.exp(self.irate * max(dexp - dtoday,0)/365.0)
				else:
					fwd = self.agent.instruments[self.underliers[idx]].price
				self.volgrids[expiry].setFwd(fwd)
				self.volgrids[expiry].setToday(dtoday)			
				self.volgrids[expiry].initialize()				
		for inst in self.option_insts:
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
			
	def trade_status_callback(self, trade_ref, status):
		pass
	
	def position_hedger(self):
		pass
        
class EquityOptStrat(OptionStrategy):
    def __init__(self, name, underliers, expiries, strikes, agent = None):
        OptionStrategy.__init__(self, name, underliers, expiries, strikes, agent)
        self.accrual = 'SSE'
		self.proxy_flag = {'delta': True, 'gamma': True, 'vega': True, 'theta': True} 
        
    def get_option_map(self, underliers, expiries, strikes):
        cont_mths = [expiry.year*100 + expiry.month for expiry in expiries]
        all_map = {}
        for under in underliers:
            map = mysqlaccess.get_stockopt_map(under, cont_mths, strikes)
            all_map.update(map)
        return all_map
    
class IndexOptStrat(OptionStrategy):
    def __init__(self, name, underliers, expiries, strikes, agent = None):
        OptionStrategy.__init__(self, name, underliers, expiries, strikes, agent)
		self.accrual = 'CFE'
		self.proxy_flag = {'delta': True, 'gamma': True, 'vega': True, 'theta': True} 
		
	def position_hedger(self):
		pass
