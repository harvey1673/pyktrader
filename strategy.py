#-*- coding:utf-8 -*-
import pandas as pd
from base import *
from misc import *
import data_handler
import order as order
import math
import logging
import datetime
import csv
import os

sign = lambda x: math.copysign(1, x)
tradepos_header = ['insts', 'vols', 'pos', 'direction', 'entry_price', 'entry_time', 'entry_target', 'entry_tradeid',
                   'exit_price', 'exit_time', 'exit_target', 'exit_tradeid', 'profit', 'is_closed']
                                  
class TradePos(object):
    def __init__(self, insts, vols, pos, entry_target, exit_target):
        self.insts = insts
        self.volumes = vols
        self.pos = pos
        self.direction = 1 if pos > 0 else -1
        self.entry_target = entry_target
        self.entry_price = None
        self.entry_time = None
        self.entry_tradeid = None
        self.exit_target = exit_target
        self.exit_price = None
        self.exit_time = None
        self.exit_tradeid = None
        self.is_closed = False
        self.profit = 0.0

    def open(self, price, start_time):
        self.entry_price = price
        self.entry_time = start_time
        self.is_closed = False
        
    def cancel_open(self):
        self.is_closed = True
        
    def close(self, price, end_time):
        self.exit_time = end_time
        self.exit_price = price
        self.profit = (self.exit_price - self.entry_price) * self.pos
        self.is_closed = True
    
    def cancel_close(self):
        self.exit_tradeid = None

def tradepos2dict(tradepos):
    trade = {}
    trade['insts'] = ' '.join(tradepos.insts)
    trade['vols'] = ' '.join([str(v) for v in tradepos.volumes])
    trade['pos'] = tradepos.pos
    trade['direction'] = tradepos.direction
    trade['entry_target'] = tradepos.entry_target
    trade['exit_target'] = tradepos.exit_target
    if tradepos.entry_tradeid == None:
        trade['entry_tradeid'] = 0
    else:
        trade['entry_tradeid'] = tradepos.entry_tradeid

    if tradepos.exit_tradeid == None:
        trade['exit_tradeid'] = 0
    else:
        trade['exit_tradeid'] = tradepos.exit_tradeid
        
    if tradepos.entry_time == None:
        trade['entry_time'] = ''
        trade['entry_price'] = 0.0
    else:
        trade['entry_time'] = tradepos.entry_time.strftime('%Y%m%d %H:%M:%S %f')
        trade['entry_price'] = tradepos.entry_price
    
    if tradepos.exit_time == None:
        trade['exit_time'] = ''
        trade['exit_price'] = 0.0
    else:
        trade['exit_time'] = tradepos.exit_time.strftime('%Y%m%d %H:%M:%S %f')
        trade['exit_price'] = tradepos.exit_price

    trade['profit'] = tradepos.profit
    trade['is_closed'] = 1 if tradepos.is_closed else 0
    return trade
  
class Strategy(object):
    def __init__(self, name, underliers, agent = None, data_func = [], trade_unit = [] ):
        self.name = name
        self.underliers = underliers
        self.agent = agent
        self.logger = None
        if self.agent != None:
            self.logger = self.agent.logger 
        if len(trade_unit) > 0: 
            self.trade_unit = trade_unit
        else:
            self.trade_unit = [ [1]*len(under) for under in underliers ]
        self.positions  = [[] for under in underliers]
        self.submitted_pos = [ [] for under in underliers ]
        self.data_func = data_func
        if agent == None:
            self.folder = ''
        else:
            self.folder = self.folder + self.name + '_'
        
    def initialize(self):
        if self.agent == None:
            self.folder = ''
        else:
            self.folder = self.agent.folder + self.name + '_'
            self.logger = self.agent.logger
        if len(self.data_func)>0:
            for (freq, fobj) in self.data_func:
                self.agent.register_data_func(freq,fobj)
        self.update_trade_unit()
    
	def get_index(self, under):
		idx = -1
		for i, insts in enumerate(self.underliers):
            if set(under) == set(insts):
                idx = i
                break
		return idx
	
	def update_positions(self, idx):
        sub_trades = self.submitted_pos[idx]
        for etrade in sub_trades:
            if etrade.status == order.ETradeStatus.Done:
                traded_price = etrade.final_price()
                for tradepos in reversed(self.positions[idx]):
                    if tradepos.entry_tradeid == etrade.id:
                        tradepos.open( traded_price, datetime.datetime.now())
                        etrade.status = order.ETradeStatus.StratConfirm
                        break
                    elif tradepos.exit_tradeid == etrade.id:
                        tradepos.close( traded_price, datetime.datetime.now())
                        self.save_closed_pos(tradepos)
                        etrade.status = order.ETradeStatus.StratConfirm
                        break
                if etrade.status != order.ETradeStatus.StratConfirm:
                    self.logger.warning('the trade %s is done but not found in the strat=%s tradepos table' % (etrade, self.name))
            elif etrade.status == order.ETradeStatus.Cancelled:
                for tradepos in reversed(self.positions[idx]):
                    if tradepos.entry_tradeid == etrade.id:
                        tradepos.cancel_open()
                        etrade.status = order.ETradeStatus.StratConfirm
                        break
                    elif tradepos.exit_tradeid == etrade.id:
                        tradepos.cancel_close()
                        etrade.status = order.ETradeStatus.StratConfirm
                        break
                if etrade.status != order.ETradeStatus.StratConfirm:
                    self.logger.warning('the trade %s is done but not found in the strat=%s tradepos table' % (etrade, self.name))
        self.positions[idx] = [ tradepos for tradepos in self.positions[idx] if not tradepos.is_closed]            
        self.submitted_pos[idx] = [etrade for etrade in self.submitted_pos[idx] if etrade.status!=order.ETradeStatus.StratConfirm]
		return 
		
    def state_refresh(self):
        self.load_state()
        
    def resume(self):
        pass
    
    def add_submitted_pos(self, etrade):
        is_added = False
        for under, sub_pos in zip(self.underliers, self.submitted_pos):
            if set(under) == set(etrade.instIDs):
                sub_pos.append(etrade)
                is_added = True
                break
        return is_added
    
    def day_finalize(self):    
        self.update_trade_unit()
        self.save_state()
        pass
        
    def run_tick(self, ctick):
        pass
    
    def run_min(self, inst):
        pass
    
    def liquidate(self):
        pass
    
    def update_trade_unit(self):
        pass
    
    def save_state(self):
        filename = self.folder + 'strat_status.csv'
        with open(filename,'wb') as log_file:
            file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(tradepos_header)
            for tplist in self.positions:
                for tradepos in tplist:
                    tradedict = tradepos2dict(tradepos)
                    file_writer.writerow([tradedict[itm] for itm in tradepos_header])
        return
    
    def load_state(self):
        logfile = self.folder + 'strat_status.csv'
        positions  = [[] for under in self.underliers]
        if not os.path.isfile(logfile):
            self.positions  = positions
            return 
        with open(logfile, 'rb') as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if idx > 0:
                    insts = row[0].split(' ')
                    vols = [ int(n) for n in row[1].split(' ')]
                    pos = int(row[2])
                    #direction = int(row[3])
                    entry_target = float(row[6])
                    exit_target = float(row[10])
                    tradepos = TradePos(insts, vols, pos, entry_target, exit_target)
                    if row[5] == '':
                        entry_time = None
                        entry_price = None
                        entry_tradeid = None
                    else:
                        entry_time = datetime.datetime.strptime(row[5], '%Y%m%d %H:%M:%S %f')
                        entry_price = float(row[4])
                        tradepos.open(entry_price,entry_time)
                        
                    if row[7] == '':
                        entry_tradeid = None
                    else:
                        entry_tradeid = int(row[7])
                        tradepos.entry_tradeid = entry_tradeid
                        
                    if row[11] == '':
                        exit_tradeid = None
                    else:
                        exit_tradeid = int(row[11])        
                        tradepos.exit_tradeid = exit_tradeid
                    
                    if row[9] == '':
                        exit_time = None
                        exit_price = None
                    else:                    
                        exit_time = datetime.datetime.strptime(row[9], '%Y%m%d %H:%M:%S %f')
                        exit_price = float(row[8])
                        tradepos.close(exit_price, exit_time)
                    
                    is_added = False
                    for under, tplist in zip(self.underliers, self.positions):
                        if set(under) == set(insts):
                            tplist.append(tradepos)
                            is_added = True
                            break
                    if is_added == False:
                        self.underliers.append(insts)
                        self.positions.append([tradepos])
                        self.logger.warning('underlying = %s is missing in strategy=%s. It is added now' % (insts, self.name))
        return    
        
    def save_closed_pos(self, tradepos):
        logfile = self.folder + 'hist_tradepos.csv'
        with open(logfile,'a') as log_file:
            file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            tradedict = tradepos2dict(tradepos)
            file_writer.writerow([tradedict[itm] for itm in tradepos_header])
        return
	
	#def load_closed_pos(self):
	#	logfile = self.folder + 'hist_tradepos.csv'
	
