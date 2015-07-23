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
                   'exit_price', 'exit_time', 'exit_target', 'exit_tradeid', 'profit', 'is_closed', 'price_unit']
class TrailLossType:
    Ratio, Level = range(2)
                                  
class TradePos(object):
    def __init__(self, insts, vols, pos, entry_target, exit_target, price_unit = 1):
        self.insts = insts
        self.volumes = vols
        self.price_unit = price_unit
        self.pos = pos
        self.direction = 1 if pos > 0 else -1
        self.entry_target = entry_target
        self.entry_price = 0
        self.entry_time = ''
        self.entry_tradeid = 0
        self.exit_target = exit_target
        self.exit_price = 0
        self.exit_time = ''
        self.exit_tradeid = 0
        self.is_closed = False
        self.profit = 0.0
        self.trail_loss = 0
        self.close_comment = ''
    
    def trail_check(self, curr_price, margin):
        if (self.direction * (self.exit_target - curr_price) >= margin):
            return True
        return False
    
    def trail_update(self, curr_price):
        if (curr_price - self.exit_target) * self.direction > 0:
            self.exit_target = curr_price
            return True
        return False        
    
    def check_stop(self, curr_price, margin):
        if (curr_price - self.entry_price) * sign(margin) * self.direction >= abs(margin):
            return True
        else:
            return False
        
    def open(self, price, start_time):
        self.entry_price = price
        self.entry_time = start_time
        self.is_closed = False
        
    def cancel_open(self):
        self.is_closed = True
        
    def close(self, price, end_time):
        self.exit_time = end_time
        self.exit_price = price
        self.profit = (self.exit_price - self.entry_price) * self.direction * self.price_unit
        self.is_closed = True
    
    def cancel_close(self):
        self.exit_tradeid = 0

def tradepos2dict(tradepos):
    trade = {}
    trade['insts'] = ' '.join(tradepos.insts)
    trade['vols'] = ' '.join([str(v) for v in tradepos.volumes])
    trade['pos'] = tradepos.pos
    trade['direction'] = tradepos.direction
    trade['entry_target'] = tradepos.entry_target
    trade['exit_target'] = tradepos.exit_target
    trade['entry_tradeid'] = tradepos.entry_tradeid
    trade['exit_tradeid'] = tradepos.exit_tradeid
    trade['entry_price'] = tradepos.entry_price
    trade['exit_price'] = tradepos.exit_price
    if tradepos.entry_time != '':
        trade['entry_time'] = tradepos.entry_time.strftime('%Y%m%d %H:%M:%S %f')
    else:
        trade['entry_time'] = ''
    if tradepos.exit_time != '':
        trade['exit_time'] = tradepos.exit_time.strftime('%Y%m%d %H:%M:%S %f')
    else:
        trade['exit_time'] = ''
    trade['profit'] = tradepos.profit
    trade['price_unit'] = tradepos.price_unit
    trade['is_closed'] = 1 if tradepos.is_closed else 0
    return trade
  
class Strategy(object):
    def __init__(self, name, underliers, volumes, trade_unit = [], agent = None, email_notify = None):
        self.name = name
        self.underliers = underliers
        num_assets = len(underliers)
        self.volumes = volumes
        self.instIDs = list(set().union(*underliers))
        if len(trade_unit) > 0: 
            self.trade_unit = trade_unit
        else:
            self.trade_unit = [1] * num_assets
        self.positions  = [[] for _ in self.underliers]
        self.submitted_pos = [[] for _ in self.underliers]
        self.data_func = []
        self.agent = agent
        self.folder = ''
        self.logger = None
        self.reset()
        self.email_notify = email_notify
        self.trade_valid_time = 600
        self.num_tick = 0
        self.num_entries = [0] * num_assets
        self.num_exits   = [0] * num_assets
        self.daily_close_buffer = 5
        self.close_tday = [False] * num_assets
        self.last_min_id = [2055] * num_assets
        self.trail_loss = [0] * num_assets
        self.curr_prices = [0.0] * num_assets
        self.order_type = OPT_LIMIT_ORDER
        self.locked = False
        
    def reset(self):
        if self.agent != None:
            self.folder = self.agent.folder + self.name + '_'
            self.logger = self.agent.logger
            if len(self.data_func)>0:
                for (freq, fobj) in self.data_func:
                    for inst in self.instIDs:
                        self.agent.register_data_func(inst, freq, fobj)
        return
    
    def initialize(self):
        self.load_state()
        return
    
    def get_index(self, under):
        idx = -1
        for i, insts in enumerate(self.underliers):
            if set(under) == set(insts):
                idx = i
                break
        return idx
    
    def update_positions(self, idx):
        sub_trades = self.submitted_pos[idx]
        save_status = False
        for etrade in sub_trades:
            if etrade.status == order.ETradeStatus.Done:
                traded_price = etrade.final_price()
                for tradepos in self.positions[idx]:
                    if tradepos.entry_tradeid == etrade.id:
                        tradepos.open( traded_price, datetime.datetime.now())
                        self.logger.info('strat %s successfully opened a position on %s after tradeid=%s is done, trade status is changed to confirmed' % 
                                         (self.name, tradepos.insts[0], etrade.id))
                        etrade.status = order.ETradeStatus.StratConfirm
                        self.num_entries[idx] += 1
                        save_status = True
                        break
                    elif tradepos.exit_tradeid == etrade.id:
                        tradepos.close( traded_price, datetime.datetime.now())
                        self.save_closed_pos(tradepos)
                        self.logger.info('strat %s successfully closed a position on %s after tradeid=%s is done, the closed trade position is saved' % 
                                         (self.name, tradepos.insts[0], etrade.id))
                        etrade.status = order.ETradeStatus.StratConfirm
                        self.num_exits[idx] += 1
                        save_status = True
                        break
                if etrade.status != order.ETradeStatus.StratConfirm:
                    etrade.status = order.ETradeStatus.StratConfirm
                    save_status = True                    
                    self.logger.warning('the trade %s is done but not found in the strat=%s tradepos table' % (etrade.id, self.name))
            elif etrade.status == order.ETradeStatus.Cancelled:
                for tradepos in self.positions[idx]:
                    if tradepos.entry_tradeid == etrade.id:
                        tradepos.cancel_open()
                        self.logger.info('strat %s cancelled an open position on %s after tradeid=%s is cancelled. Both the trade and the position will be removed.' % 
                                         (self.name, tradepos.insts[0], etrade.id))
                        etrade.status = order.ETradeStatus.StratConfirm
                        save_status = True
                        break
                    elif tradepos.exit_tradeid == etrade.id:
                        tradepos.cancel_close()
                        self.logger.info('strat %s cancelled closing a position on %s after tradeid=%s is cancelled. The position is still open with pos=%s.' % 
                                         (self.name, tradepos.insts[0], etrade.id, tradepos.pos))
                        etrade.status = order.ETradeStatus.StratConfirm
                        save_status = True
                        break
                if etrade.status != order.ETradeStatus.StratConfirm: 
                    print "WARNING:the trade %s is cancelled but not found in the strat=%s tradepos table, removing the trade" % (etrade.id, self.name)
                    self.logger.warning('the trade %s is cancelled but not found in the strat=%s tradepos table' % (etrade.id, self.name))
                    etrade.status = order.ETradeStatus.StratConfirm
                    save_status = True
        self.positions[idx] = [ tradepos for tradepos in self.positions[idx] if not tradepos.is_closed]            
        self.submitted_pos[idx] = [etrade for etrade in self.submitted_pos[idx] if etrade.status!=order.ETradeStatus.StratConfirm]        
        for pos in self.positions[idx]:
            if pos.trail_loss > 0:
                updated = pos.trail_update(self.curr_prices[idx])
                if pos.trail_check(self.curr_price[idx], pos.entry_price * pos.trail_loss):
                    msg = 'Strat = %s to close position after hitting trail loss for underlier = %s, direction=%s, volume=%s, current tick_id = %s, current price = %s, exit_target = %s, trail_loss buffer = %s' \
                                    % (self.name, self.underliers[idx], pos.direction, self.trade_unit[idx], self.agent.tick_id, self.curr_prices[idx], pos.exit_target, pos.entry_price * pos.trail_loss)
                    self.close_tradepos(idx, pos, self.curr_prices[idx])
                    self.status_notifier(msg)                    
                    updated = True
                save_status = save_status or updated
        return save_status
        
    def resume(self):
        pass
    
    def add_submitted_pos(self, etrade):
        for idx, under in enumerate(self.underliers):
            if set(under) == set(etrade.instIDs):
                self.submitted_pos[idx].append(etrade)
                return True
        return False
    
    def day_finalize(self):    
        self.update_trade_unit()
        for idx, under in enumerate(self.underliers):
            self.update_positions(idx)
        self.logger.info('strat %s is finalizing the day - update trade unit, save state' % self.name)
        self.num_entries = [0] * len(self.underliers)
        self.num_exits = [0] * len(self.underliers)
        self.save_state()
        self.initialize()
        return
    
    def calc_curr_price(self, idx):        
        prices = [ self.agent.instruments[inst].mid_price for inst in self.underliers[idx] ]
        conv_f = [ self.agent.instruments[inst].multiple for inst in self.underliers[idx] ]    
        self.curr_prices[idx] = sum([p*v*cf for p, v, cf in zip(prices, self.volumes[idx], conv_f)])/conv_f[-1]
        return
        
    def run_tick(self, ctick):
        inst = ctick.instID
        idx = self.get_index([inst]) 
        if idx < 0:
            self.logger.warning('the inst=%s is not in this strategy = %s' % (inst, self.name))
            return
        self.calc_curr_price(idx)
        if self.update_positions(idx):
            self.save_state()
        self.run_tick(idx, ctick)
        return
    
    def run_min(self, inst, freq):
        pass
    
    def on_tick(self, idx, ctick):
        pass
    
    def on_bar(self, idx):
        pass
    
    def speedup(self, etrade):
        self.logger.info('need to speed up the trade = %s' % etrade.id)
        pass
    
    def open_tradepos(self, idx, direction, price):
        valid_time = self.agent.tick_id + self.trade_valid_time
        insts = self.underliers[idx]
        nAsset = len(insts)
        trade_vol = [ v * self.trade_unit[idx] * direction for v in self.volumes[idx] ]
        order_type = [self.order_type] * nAsset
        if (self.order_type == OPT_LIMIT_ORDER) and (nAsset > 1):
            order_type[-1] = OPT_MARKET_ORDER
        conv_f = [ self.agent.instruments[inst].multiple for inst in insts ]    
        etrade = order.ETrade( insts, trade_vol, order_type, price * direction, [self.num_tick] * nAsset,  \
                                valid_time, self.name, self.agent.name, conv_f[-1]*self.trade_unit[idx], conv_f)
        tradepos = TradePos(insts, self.volumes[idx], direction * self.trade_unit[idx], \
                                price, price, conv_f[-1]*self.trade_unit[idx])
        tradepos.entry_tradeid = etrade.id
        self.submitted_pos[idx].append(etrade)
        self.positions[idx].append(tradepos)
        self.agent.submit_trade(etrade)
        return 
    
    def close_tradepos(self, idx, tradepos, price):
        valid_time = self.agent.tick_id + self.trade_valid_time
        insts = tradepos.insts
        nAsset = len(insts)
        if insts != self.underliers[idx]:
            self.logger.warning('some inconsistency on underlier index and the refered tradepos for insts = %s' % (insts))
            return
        trade_vol = [ -v*tradepos.pos for v in tradepos.volumes]
        order_type = [self.order_type] * nAsset
        if (self.order_type == OPT_LIMIT_ORDER) and (nAsset > 1):
            order_type[-1] = OPT_MARKET_ORDER
        conv_f = [ self.agent.instruments[inst].multiple for inst in insts ]
        etrade = order.ETrade( insts, trade_vol, order_type, -price*tradepos.direction, [self.num_tick] * nAsset, \
                                valid_time, self.name, self.agent.name, conv_f[-1]*abs(tradepos.pos), conv_f)
        tradepos.exit_tradeid = etrade.id
        self.submitted_pos[idx].append(etrade)
        self.agent.submit_trade(etrade)
        return
        
    def update_trade_unit(self):
        pass
    
    def status_notifier(self, msg):
        self.logger.info(msg)
        if len(self.email_notify) > 0: 
            send_mail(EMAIL_HOTMAIL, self.email_notify, '%s trade signal' % (self.name), msg)
        return
    
    def save_local_variables(self, file_writer):
        pass
    
    def load_local_variables(self, row):
        pass
        
    def save_state(self):
        filename = self.folder + 'strat_status.csv'
        self.logger.info('save state for strat = %s' % (self.name))
        with open(filename,'wb') as log_file:
            file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for tplist in self.positions:
                for tradepos in tplist:
                    tradedict = tradepos2dict(tradepos)
                    row = ['tradepos'] + [tradedict[itm] for itm in tradepos_header]
                    file_writer.writerow(row)
            self.save_local_variables(file_writer)
        return
    
    def load_state(self):
        logfile = self.folder + 'strat_status.csv'
        positions  = [[] for under in self.underliers]
        if not os.path.isfile(logfile):
            self.positions  = positions
            return 
        self.logger.info('load state for strat = %s' % (self.name))
        with open(logfile, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == 'tradepos':
                    insts = row[1].split(' ')
                    vols = [ int(n) for n in row[2].split(' ')]
                    pos = int(row[3])
                    #direction = int(row[3])
                    entry_target = float(row[7])
                    exit_target = float(row[11])
                    price_unit = float(row[15])
                    tradepos = TradePos(insts, vols, pos, entry_target, exit_target, price_unit)
                    if row[6] == '':
                        entry_time = ''
                        entry_price = 0
                    else:
                        entry_time = datetime.datetime.strptime(row[6], '%Y%m%d %H:%M:%S %f')
                        entry_price = float(row[5])
                        tradepos.open(entry_price,entry_time)

                    tradepos.entry_tradeid = int(row[8])           
                    tradepos.exit_tradeid = int(row[12])    
                    
                    if row[10] == '':
                        exit_time = ''
                        exit_price = 0
                    else:                    
                        exit_time = datetime.datetime.strptime(row[10], '%Y%m%d %H:%M:%S %f')
                        exit_price = float(row[9])
                        tradepos.close(exit_price, exit_time)
                    
                    is_added = False
                    for under, tplist in zip(self.underliers, positions):
                        if set(under) == set(insts):
                            tplist.append(tradepos)
                            is_added = True
                            break
                    if is_added == False:
                        #self.underliers.append(insts)
                        #positions.append([tradepos])
                        self.logger.warning('underlying = %s is missing in strategy=%s. It is added now' % (insts, self.name))
                else:
                    self.load_local_variables(row)
        self.positions = positions
        return    
        
    def save_closed_pos(self, tradepos):
        logfile = self.folder + 'hist_tradepos.csv'
        with open(logfile,'a') as log_file:
            file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            tradedict = tradepos2dict(tradepos)
            file_writer.writerow([tradedict[itm] for itm in tradepos_header])
        return
    
    def check_price_limit(self, inst, curr_price, num_tick):
        inst_obj = self.agent.instruments[inst]
        tick_base = inst_obj.tick_base
        if (curr_price >= inst_obj.up_limit - num_tick * tick_base) or (curr_price <= inst_obj.down_limit + num_tick * tick_base):
            return True
        else:
            return False
    