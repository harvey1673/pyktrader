#-*- coding:utf-8 -*-
import pandas as pd
from base import *
import data_handler
import order as order
from ctp.futures import ApiStruct
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
    
    def set_tradeid(self, tradeid, pos):
        direction = 1 if pos > 0 else -1
        if direction == self.direction:
            self.entry_tradeid = tradeid
        else:
            self.exit_tradeid = tradeid
        return 

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
    def __init__(self, name, underliers, agent = None, data_func = {}, trade_unit = [] ):
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
            self.folder = self.folder + self.name + '\\'
        
    def initialize(self):
        if self.agent == None:
            self.folder = ''
        else:
            self.folder = self.agent.folder + self.name + '\\'
            self.logger = self.agent.logger
        if len(self.data_func)>0:
            for (freq, fobj) in self.data_func:
                self.agent.register_data_func(freq,fobj)
        self.update_trade_unit()
    
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
                        tradepos.set_tradeid(entry_tradeid, tradepos.direction)
                        
                    if row[11] == '':
                        exit_tradeid = None
                    else:
                        exit_tradeid = int(row[11])        
                        tradepos.set_tradeid(exit_tradeid, -tradepos.direction)
                    
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
   
class TurtleTrader(Strategy):
    def __init__(self, name, underliers,  capital, agent = None):
        Strategy.__init__(name, underliers, agent)
        self.data_func = [ 
                ('d', BaseObject(name = 'ATR_20', sfunc=fcustom(data_handler.ATR, n=20), rfunc=fcustom(data_handler.atr, n=20))), \
                ('d', BaseObject(name = 'DONCH_L10', sfunc=fcustom(data_handler.DONCH_L, n=10), rfunc=fcustom(data_handler.donch_l, n=10))),\
                ('d', BaseObject(name = 'DONCH_H10', sfunc=fcustom(data_handler.DONCH_H, n=10), rfunc=fcustom(data_handler.donch_h, n=10))),\
                ('d', BaseObject(name = 'DONCH_L20', sfunc=fcustom(data_handler.DONCH_L, n=20), rfunc=fcustom(data_handler.donch_l, n=20))),\
                ('d', BaseObject(name = 'DONCH_H20', sfunc=fcustom(data_handler.DONCH_H, n=20), rfunc=fcustom(data_handler.donch_h, n=10))),\
                ('d', BaseObject(name = 'DONCH_L55', sfunc=fcustom(data_handler.DONCH_L, n=55), rfunc=fcustom(data_handler.donch_l, n=10))),\
                ('d', BaseObject(name = 'DONCH_H55', sfunc=fcustom(data_handler.DONCH_H, n=55), rfunc=fcustom(data_handler.donch_h, n=55)))]    
        self.capital = capital 
        self.pos_ratio = 0.01
        self.stop_loss = 2.0
    
    def run_tick(self, ctick):
        inst = ctick.instID
        under = [inst]
        df = self.agent.day_data[inst]
        cur_atr = df.ix[-1,'ATR_20']
        hh = [df.ix[-1,'DONCH_H20'],df.ix[-1,'DONCH_H10']]
        ll  = [df.ix[-1,'DONCH_L20'],df.ix[-1,'DONCH_H10']]
        idx = 0
        for i, under in enumerate(self.underliers):
            if inst == under[0]:
                idx = i
                break
        sub_trades = self.submitted_pos[idx]
        for etrade in sub_trades:
            if etrade.status == order.ETradeStatus.Done:
                traded_price = etrade.filled_price[0]
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
                self.positions[idx] = [ tradepos for tradepos in self.positions[idx] if not tradepos.is_closed()]
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
                    
        self.submitted_pos[idx] = [etrade for etrade in self.submitted_pos[idx] if etrade.status!=order.ETradeStatus.StratConfirm]
        cur_price = (ctick.askPrice1 + ctick.bidPrice1)/2.0
        if len(self.submitted_pos[idx]) == 0:
            #开仓 
            if len(self.positions[inst]) == 0: 
                buysell = 0
                if (cur_price > hh[0]):
                    buysell = 1
                elif (cur_price < ll[0]):
                    buysell = -1                 
                if buysell !=0:
                    valid_time = self.agent.tick_id + 600
                    etrade = order.ETrade( [inst], [self.trade_unit[idx][0]*buysell], \
                                           [ApiStruct.OPT_LimitPrice], cur_price, [5],  \
                                           valid_time, self.name, self.agent.name)
                    tradepos = TradePos([inst], self.trade_unit[idx], buysell, \
                                        cur_price, cur_price - cur_atr*self.stop_loss*buysell)
                    tradepos.set_tradeid(etrade.id, buysell)
                    self.submitted_pos[idx].append(etrade)
                    self.positions[inst].append(tradepos)
                    self.agent.submit_trade(etrade)
                    return 1
            #加仓或清仓
            else:
                buysell = self.positions[idx][0].direction
                #清仓1
                units = len(self.positions[idx])
                for tradepos in self.positions[idx]:
                    if (cur_price < ll[1] and buysell == 1) or (cur_price > hh[1] and buysell == -1) \
                        or ((cur_price - tradepos.exit_target)*buysell < 0):
                        valid_time = self.agent.tick_id + 600
                        etrade = order.ETrade( [inst], [-self.trade_unit[idx][0]*buysell], \
                                               [ApiStruct.OPT_LimitPrice], cur_price, [5], \
                                               valid_time, self.name, self.agent.name)
                        tradepos.set_tradeid(etrade.id, -buysell)
                        self.submitted_pos[idx].append(etrade)
                        self.agent.submit_trade(etrade)
                    elif  units < 4 and (cur_price - self.positions[idx][-1].entry_price)*buysell >= cur_atr/2.0:
                        valid_time = self.agent.tick_id + 600
                        etrade = order.ETrade( [inst], [self.trade_unit[idx][0]*buysell], \
                                               [ApiStruct.OPT_LimitPrice], cur_price, [5],  \
                                               valid_time, self.name, self.agent.name)
                        tradepos = TradePos([inst], self.trade_unit[idx], buysell, \
                                            cur_price, cur_price - cur_atr*self.stop_loss*buysell)
                        tradepos.set_tradeid(etrade.id, buysell)
                        self.submitted_pos[idx].append(etrade)
                        self.positions[inst].append(tradepos)
                        self.agent.submit_trade(etrade)                  
                    return 1
        
    def update_trade_unit(self):
        for under, pos in zip(self.underliers,self.positions):
            if len(pos) == 0: 
                inst = under[0]
                pinst  = self.agent.instruments[inst]
                df  = self.agent.day_data[inst]                
                self.trade_unit = [int(self.capital*self.pos_ratio/(pinst.multiple*df.ix[-1,'ATR_20']))]
