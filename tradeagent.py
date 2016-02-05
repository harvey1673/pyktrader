#-*- coding:utf-8 -*-
import workdays
import time
import copy
import datetime
import logging
import bisect
import mysqlaccess
import order as order
import math
import os
import csv
import instrument
import pandas as pd
from base import *
from misc import *
import data_handler
import backtest
import pyktlib
import numpy as np
from eventType import *
from eventEngine import *

MAX_REALTIME_DIFF = 100
min_data_list = ['datetime', 'min_id', 'open', 'high','low', 'close', 'volume', 'openInterest'] 
day_data_list = ['date', 'open', 'high','low', 'close', 'volume', 'openInterest']

def get_tick_id(dt):
    return ((dt.hour+6)%24)*100000+dt.minute*1000+dt.second*10+dt.microsecond/100000

def get_tick_num(dt):
    return ((dt.hour+6)%24)*36000+dt.minute*600+dt.second*10+dt.microsecond/100000

def get_min_id(dt):
    return ((dt.hour+6)%24)*100+dt.minute

def trading_hours(product, exch):
    hrs = [(1500, 1615), (1630, 1730), (1930, 2100)]
    if exch in ['SSE', 'SZE']:
        hrs = [(1530, 1730), (1900, 2100)]
    elif exch == 'CFFEX':
        hrs = [(1515, 1730), (1900, 2115)]
    else:
        if product in night_session_markets:
            night_idx = night_session_markets[product]
            hrs = [night_trading_hrs[night_idx]] + hrs  
    return hrs 
                    
class Agent(object):
 
    def __init__(self, name, trader, cuser, instruments, strategies = [], tday=datetime.date.today(), config_file = None):
        '''
            trader为交易对象
            tday为当前日,为0则为当日
        '''
        self.tick_id = 0
        self.timer_count = 0
        folder = 
        if 'folder' in config:
            folder = config['folder']
        daily_data_days = 60
        if 'daily_data_days' in config:
            daily_data_days = config['daily_data_days']   
        min_data_days = 5
        if 'min_data_days' in config:
            min_data_days = config['min_data_days']        
        live_trading = False
        if 'live_trading' in config:
            live_trading = config['live_trading']  
        self.logger = logging.getLogger('.'.join([name, 'agent']))
        self.name = name
        self.folder = config.get('folder', self.name + os.path.sep)
        self.initialized = False
		self.eod_flag = False
        self.scur_day = tday
        #保存分钟数据标志
        self.save_flag = False  #默认不保存
        self.live_trading = live_trading
        self.tick_db_table = config.get('tick_db_table', 'fut_tick')
        self.min_db_table  = config.get('min_db_table', 'fut_min')
        self.daily_db_table = config.get('daily_db_table', 'fut_daily')
        # market data
        self.daily_data_days = config.get('daily_data_days', 30)
        self.min_data_days = config.get('min_data_days', 5)
        self.instruments = {}
        self.tick_data  = {}
        self.day_data  = {}
        self.min_data  = {}
        self.cur_min = {}
        self.cur_day = {}  
        self.positions= {} 
        self.day_data_func = {}
        self.min_data_func = {}
        self.inst2strat = {}            
        self.add_instruments(instruments, self.scur_day)
        self.strategies = {}
        self.strat_list = []
        for strat in strategies:
            self.add_strategy(strat)
        ###交易
        self.ref2order = {}    #orderref==>order
        self.ref2trade = {}
        #self.queued_orders = []     #因为保证金原因等待发出的指令(合约、策略族、基准价、基准时间(到秒))

        self.eventEngine = EventEngine(1)
        self.eventEngine.register(EVENT_LOG, self.log_handler)
        self.eventEngine.register(EVENT_TICK, self.rtn_tick)
        self.eventEngine.register(EVENT_DAYSWITCH, self.day_switch)
        self.cancel_protect_period = 200
        self.market_order_tick_multiple = 5

        self.init_init()    #init中的init,用于子类的处理

    def set_capital_limit(self, margin_cap):
        self.margin_cap = margin_cap

    def log_handler(self, event):
        lvl = event.dict['level']
        self.logger.log(lvl, event.dict['log'])

    def td_disconnected(self, event):
        pass

    def time_scheduler(self, event):
        if self.timer_count % 1800:
            if self.tick_id >= 2100000-10:
                min_id = get_min_id(datetime.datetime.now())
                if (min_id >= 2116) and (self.eod_flag == False):
                    self.qry_commands.append(self.run_eod)

    def add_instruments(self, names, tday):
        add_names = [ name for name in names if name not in self.instruments]
        for name in add_names:
            if name.isdigit():
                if len(name) == 8:
                    self.instruments[name] = instrument.StockOptionInst(name)
                else:
                    self.instruments[name] = instrument.Stock(name)
            else:
                if len(name) > 10:
                    self.instruments[name] = instrument.FutOptionInst(name)
                else:
                    self.instruments[name] = instrument.Future(name)
            self.instruments[name].update_param(tday)                    
            self.tick_data[name] = []
            self.day_data[name]  = pd.DataFrame(columns=['open', 'high','low','close','volume','openInterest'])
            self.min_data[name]  = {1: pd.DataFrame(columns=['open', 'high','low','close','volume','openInterest','min_id'])}
            self.cur_min[name]   = dict([(item, 0) for item in min_data_list])
            self.cur_day[name]   = dict([(item, 0) for item in day_data_list])  
            self.positions[name] = order.Position(self.instruments[name])
            self.day_data_func[name] = []
            self.min_data_func[name] = {}    
            self.qry_pos[name]   = {'tday': [0, 0], 'yday': [0, 0]}
            self.cur_min[name]['datetime'] = datetime.datetime.fromordinal(self.scur_day.toordinal())
            self.cur_day[name]['date'] = tday
            if name not in self.inst2strat:
                self.inst2strat[name] = {}
        
    def add_strategy(self, strat):
        self.add_instruments(strat.instIDs, self.scur_day)
        for instID in strat.instIDs:
            self.inst2strat[instID][strat.name] = []
        self.strategies[strat.name] = strat
        self.strat_list.append(strat.name)
        strat.agent = self
        strat.reset()
                 
    def initialize(self, event):
        '''
            初始化，如保证金率，账户资金等
        '''
        self.isSettlementInfoConfirmed = True
        if not self.initialized:
            for inst in self.instruments:
                self.instruments[inst].update_param(self.scur_day)
   
    def register_data_func(self, inst, freq, fobj):
        if inst not in self.day_data_func:
            self.day_data_func[inst] = []
            self.min_data_func[inst] = {}
        if 'd' in freq:
            for func in self.day_data_func[inst]:
                if fobj.name == func.name:
                    return False
            self.day_data_func[inst].append(fobj)
            return True
        else:
            mins = int(freq[:-1])
            if mins not in self.min_data_func[inst]:
                self.min_data_func[inst][mins] = []
            for func in self.min_data_func[inst][mins]:
                if fobj.name == func.name:
                    return False            
            if fobj != None:
                self.min_data_func[inst][mins].append(fobj)
            return True
        
    def prepare_data_env(self, mid_day = True): 
        if self.daily_data_days > 0 or mid_day:
            self.logger.debug('Updating historical daily data for %s' % self.scur_day.strftime('%Y-%m-%d'))
            daily_start = workdays.workday(self.scur_day, -self.daily_data_days, CHN_Holidays)
            daily_end = self.scur_day
            for inst in self.instruments:  
                if (self.instruments[inst].ptype == instrument.ProductType.Option):
                    continue
                self.day_data[inst] = mysqlaccess.load_daily_data_to_df('fut_daily', inst, daily_start, daily_end)
                df = self.day_data[inst]
                if len(df) > 0:
                    self.instruments[inst].price = df['close'][-1]
                    self.instruments[inst].last_update = 0
                    self.instruments[inst].prev_close = df['close'][-1]
                    for fobj in self.day_data_func[inst]:
                        ts = fobj.sfunc(df)
                        df[ts.name]= pd.Series(ts, index=df.index)

        if self.min_data_days > 0 or mid_day:
            self.logger.debug('Updating historical min data for %s' % self.scur_day.strftime('%Y-%m-%d'))
            d_start = workdays.workday(self.scur_day, -self.min_data_days, CHN_Holidays)
            d_end = self.scur_day
            for inst in self.instruments: 
                if (self.instruments[inst].ptype == instrument.ProductType.Option):
                    continue
                min_start = int(self.instruments[inst].start_tick_id/1000)
                min_end = int(self.instruments[inst].last_tick_id/1000)+1
                #print "loading inst = %s" % inst
                mindata = mysqlaccess.load_min_data_to_df('fut_min', inst, d_start, d_end, minid_start=min_start, minid_end=min_end)        
                mindata = backtest.cleanup_mindata(mindata, self.instruments[inst].product)
                self.min_data[inst][1] = mindata
                if len(mindata)>0:
                    min_date = mindata.index[-1].date()
                    if (len(self.day_data[inst].index)==0) or (min_date > self.day_data[inst].index[-1]):
                        ddf = data_handler.conv_ohlc_freq(mindata, 'd')
                        self.cur_day[inst]['open'] = float(ddf.open[-1])
                        self.cur_day[inst]['close'] = float(ddf.close[-1])
                        self.cur_day[inst]['high'] = float(ddf.high[-1])
                        self.cur_day[inst]['low'] = float(ddf.low[-1])
                        self.cur_day[inst]['volume'] = int(ddf.volume[-1])
                        self.cur_day[inst]['openInterest'] = int(ddf.openInterest[-1])
                        self.cur_min[inst]['datetime'] = pd.datetime(*mindata.index[-1].timetuple()[0:-3])
                        self.cur_min[inst]['open'] = float(mindata.ix[-1,'open'])
                        self.cur_min[inst]['close'] = float(mindata.ix[-1,'close'])
                        self.cur_min[inst]['high'] = float(mindata.ix[-1,'high'])
                        self.cur_min[inst]['low'] = float(mindata.ix[-1,'low'])
                        self.cur_min[inst]['volume'] = self.cur_day[inst]['volume']
                        self.cur_min[inst]['openInterest'] = self.cur_day[inst]['openInterest']
                        self.cur_min[inst]['min_id'] = int(mindata.ix[-1,'min_id'])
                        self.instruments[inst].price = float(mindata.ix[-1,'close'])
                        self.instruments[inst].last_update = 0
                        self.logger.debug('inst=%s tick data loaded for date=%s' % (inst, min_date))
                    for m in self.min_data_func[inst]:
                        if m != 1:
                            self.min_data[inst][m] = data_handler.conv_ohlc_freq(self.min_data[inst][1], str(m)+'min')
                        df = self.min_data[inst][m]
                        for fobj in self.min_data_func[inst][m]:
                            ts = fobj.sfunc(df)
                            df[ts.name]= pd.Series(ts, index=df.index)
        return

    def resume(self):
        if self.initialized:
            return 
        self.logger.debug('Prepare market data for %s' % self.scur_day.strftime('%y%m%d'))
        self.prepare_data_env(mid_day = True)
        self.get_eod_positions()            
        self.logger.debug('Prepare trade environment for %s' % self.scur_day.strftime('%y%m%d'))
        file_prefix = self.folder
        self.ref2order = order.load_order_list(self.scur_day, file_prefix, self.positions)
        keys = self.ref2order.keys()
        if len(keys) > 1:
            keys.sort()
        for key in keys:
            iorder =  self.ref2order[key]
            if len(iorder.conditionals)>0:
                self.ref2order[key].conditionals = dict([(self.ref2order[o_id], iorder.conditionals[o_id]) 
                                                         for o_id in iorder.conditionals])
        self.ref2trade = order.load_trade_list(self.scur_day, file_prefix)
        for trade_id in self.ref2trade:
            etrade = self.ref2trade[trade_id]
            orderdict = etrade.order_dict
            for inst in orderdict:
                etrade.order_dict[inst] = [ self.ref2order[order_ref] for order_ref in orderdict[inst] ]
            etrade.update()
        
        for strat_name in self.strat_list:
            strat = self.strategies[strat_name]
            strat.initialize()
            strat_trades = [etrade for etrade in self.ref2trade.values() if (etrade.strategy == strat.name) \
                            and (etrade.status != order.ETradeStatus.StratConfirm)]
            for trade in strat_trades:
                strat.add_live_trades(trade)
            
        for inst in self.positions:
            self.positions[inst].re_calc()        
        self.calc_margin()
        self.initialized = True
        self.eventEngine.start()

    def check_price_limit(self, inst, num_tick):
        inst_obj = self.instruments[inst]
        tick_base = inst_obj.tick_base
        if (inst_obj.ask_price1 >= inst_obj.up_limit - num_tick * tick_base) or (inst_obj.bid_price1 <= inst_obj.down_limit + num_tick * tick_base):
            return True
        else:
            return False

    def calc_margin(self):
        locked_margin = 0
        used_margin = 0
        yday_pnl = 0
        tday_pnl = 0
        for instID in self.instruments:
            inst = self.instruments[instID]
            pos = self.positions[instID]
            under_price = 0.0
            if (inst.ptype == instrument.ProductType.Option):
                under_price = self.instruments[inst.underlying].price
            #print inst.name, inst.marginrate, inst.calc_margin_amount(ORDER_BUY), inst.calc_margin_amount(ORDER_SELL)
            locked_margin += pos.locked_pos.long * inst.calc_margin_amount(ORDER_BUY, under_price)
            locked_margin += pos.locked_pos.short * inst.calc_margin_amount(ORDER_SELL, under_price) 
            used_margin += pos.curr_pos.long * inst.calc_margin_amount(ORDER_BUY, under_price)
            used_margin += pos.curr_pos.short * inst.calc_margin_amount(ORDER_SELL, under_price)
            yday_pnl += (pos.pos_yday.long - pos.pos_yday.short) * (inst.price - inst.prev_close) * inst.multiple
            tday_pnl += pos.tday_pos.long * (inst.price-pos.tday_avp.long) * inst.multiple
            tday_pnl -= pos.tday_pos.short * (inst.price-pos.tday_avp.short) * inst.multiple
            #print "inst=%s, yday_long=%s, yday_short=%s, tday_long=%s, tday_short=%s" % (instID, pos.pos_yday.long, pos.pos_yday.short, pos.tday_pos.long, pos.tday_pos.short)
        self.locked_margin = locked_margin
        self.used_margin = used_margin
        self.pnl_total = yday_pnl + tday_pnl
        self.curr_capital = self.prev_capital + self.pnl_total
        self.available = self.curr_capital - self.locked_margin
        self.logger.debug('calc_margin: curr_capital=%s, prev_capital=%s, pnl_tday=%s, pnl_yday=%s, locked_margin=%s, used_margin=%s, available=%s' \
                        % (self.curr_capital, self.prev_capital, tday_pnl, yday_pnl, locked_margin, used_margin, self.available))
 
    def save_state(self):
        '''
            保存环境
        '''
        if not self.eod_flag:
            self.logger.debug(u'保存执行状态.....................')
            file_prefix = self.folder
            order.save_order_list(self.scur_day, self.ref2order, file_prefix)
            order.save_trade_list(self.scur_day, self.ref2trade, file_prefix)
        return
    
    def update_instrument(self, tick):      
        inst = tick.instID    
        curr_tick = tick.tick_id
        self.instruments[inst].up_limit   = tick.upLimit
        self.instruments[inst].down_limit = tick.downLimit        
        tick.askPrice1 = min(tick.askPrice1, tick.upLimit)
        tick.bidPrice1 = max(tick.bidPrice1, tick.downLimit)
        self.instruments[inst].last_update = curr_tick
        self.instruments[inst].bid_price1 = tick.bidPrice1
        self.instruments[inst].ask_price1 = tick.askPrice1
        self.instruments[inst].mid_price = (tick.askPrice1 + tick.bidPrice1)/2.0
        self.instruments[inst].bid_vol1   = tick.bidVol1
        self.instruments[inst].ask_vol1   = tick.askVol1
        self.instruments[inst].open_interest = tick.openInterest
        last_volume = self.instruments[inst].volume
        #self.logger.debug(u'MD:收到行情，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume, last_volume))
        if tick.volume > last_volume:
            self.instruments[inst].price  = tick.price
            self.instruments[inst].volume = tick.volume
            self.instruments[inst].last_traded = curr_tick    
        return True
    
    def get_bar_id(self, tick_id):
        return int(tick_id/1000)
    
    def conv_bar_id(self, bar_id):
        return int(bar_id/100)*60 + bar_id % 100 + 1
            
    def update_min_bar(self, tick):
        inst = tick.instID
        tick_dt = tick.timestamp
        tick_id = tick.tick_id
        tick_min = self.get_bar_id(tick_id)
        if (self.cur_min[inst]['min_id'] > tick_min):
            return False
        if (tick_min == self.cur_min[inst]['min_id']):
            self.tick_data[inst].append(tick)
            self.cur_min[inst]['close'] = tick.price
            if self.cur_min[inst]['high'] < tick.price:
                self.cur_min[inst]['high'] = tick.price
            if self.cur_min[inst]['low'] > tick.price:
                self.cur_min[inst]['low'] = tick.price
        else:
            if (len(self.tick_data[inst]) > 0):
                last_tick = self.tick_data[inst][-1]
                self.cur_min[inst]['volume'] = last_tick.volume - self.cur_min[inst]['volume']
                self.cur_min[inst]['openInterest'] = last_tick.openInterest
                if (self.instruments[inst].ptype != instrument.ProductType.Option):
                    self.min_switch(inst)
                else:
                    if self.save_flag:
                        mysqlaccess.bulkinsert_tick_data(inst, self.tick_data[inst], dbtable = self.tick_db_table)              
                self.cur_min[inst]['volume'] = last_tick.volume                                
            self.tick_data[inst] = []
            self.cur_min[inst]['open']  = tick.price
            self.cur_min[inst]['close'] = tick.price
            self.cur_min[inst]['high']  = tick.price
            self.cur_min[inst]['low']   = tick.price
            self.cur_min[inst]['min_id']  = tick_min
            self.cur_min[inst]['openInterest'] = tick.openInterest
            self.cur_min[inst]['datetime'] = tick_dt.replace(second=0, microsecond=0)
            if ((tick_min>0) and (tick.price>0)): 
                self.tick_data[inst].append(tick)

        for strat_name in self.inst2strat[inst]:
            self.strategies[strat_name].run_tick(tick)
        return True  
    
    def min_switch(self, inst):
        if self.cur_min[inst]['close'] == 0:
            return
        if self.cur_min[inst]['low'] == 0:
            self.cur_min[inst]['low'] = self.cur_min[inst]['close']
        if self.cur_min[inst]['high'] >= MKT_DATA_BIGNUMBER - 1000:
            self.cur_min[inst]['high'] = self.cur_min[inst]['close']
        min_id = self.cur_min[inst]['min_id']
        min_sn = self.conv_bar_id(min_id)
        df = self.min_data[inst][1]
        mysqlaccess.insert_min_data_to_df(df, self.cur_min[inst])
        for m in self.min_data_func[inst]:
            df_m = self.min_data[inst][m]
            if m > 1 and min_sn % m == 0:
                s_start = self.cur_min[inst]['datetime'] - datetime.timedelta(minutes=m)
                slices = df[df.index>s_start]
                new_data = {'open':slices['open'][0],'high':max(slices['high']), \
                            'low': min(slices['low']),'close': slices['close'][-1],\
                            'volume': sum(slices['volume']), 'min_id':slices['min_id'][0]}
                df_m.loc[s_start] = pd.Series(new_data)
                #print df_m.loc[s_start]
            if min_sn % m == 0:
                for fobj in self.min_data_func[inst][m]:
                    fobj.rfunc(df_m)
        if self.save_flag:
            #print 'insert min data inst = %s, min = %s' % (inst, min_id)
            mysqlaccess.bulkinsert_tick_data(inst, self.tick_data[inst], dbtable = self.tick_db_table)
            mysqlaccess.insert_min_data(inst, self.cur_min[inst], dbtable = self.min_db_table)        
        for strat_name in self.inst2strat[inst]:
            for m in self.inst2strat[inst][strat_name]:
                if min_sn % m == 0:
                    self.strategies[strat_name].run_min(inst, m)
        return
        
    def day_finalize(self, insts):        
        for inst in insts:
            if not self.instruments[inst].day_finalized:
                self.instruments[inst].day_finalized = True
                self.logger.debug('finalizing the day for market data = %s, scur_date=%s' % (inst, self.scur_day))
                if (len(self.tick_data[inst]) > 0) :
                    last_tick = self.tick_data[inst][-1]
                    self.cur_min[inst]['volume'] = last_tick.volume - self.cur_min[inst]['volume']
                    self.cur_min[inst]['openInterest'] = last_tick.openInterest
                    if (self.instruments[inst].ptype != instrument.ProductType.Option):
                        self.min_switch(inst)
                    else:
                        if self.save_flag:
                            mysqlaccess.bulkinsert_tick_data(inst, self.tick_data[inst], dbtable = self.tick_db_table)  
                if (self.cur_day[inst]['close']>0):
                    mysqlaccess.insert_daily_data_to_df(self.day_data[inst], self.cur_day[inst])
                    df = self.day_data[inst]
                    if (self.instruments[inst].ptype != instrument.ProductType.Option):
                        for fobj in self.day_data_func[inst]:
                            fobj.rfunc(df)
                    if self.save_flag:
                        mysqlaccess.insert_daily_data(inst, self.cur_day[inst], dbtable = self.daily_db_table)
        return
    
    def run_eod(self):
        self.day_finalize(self.instruments.keys())
        if self.trader == None:
            return
        self.save_state()
        print 'run EOD process'
        self.eod_flag = True
        pfilled_dict = {}
        for trade_id in self.ref2trade:
            etrade = self.ref2trade[trade_id]
            etrade.update()
            if etrade.status == order.ETradeStatus.Pending or etrade.status == order.ETradeStatus.Processed:
                etrade.status = order.ETradeStatus.Cancelled
                strat = self.strategies[etrade.strategy]
                strat.on_trade(etrade)
            elif etrade.status == order.ETradeStatus.PFilled:
                etrade.status = order.ETradeStatus.Cancelled
                self.logger.warning('Still partially filled after close. trade id= %s' % trade_id)
                pfilled_dict[trade_id] = etrade
        if len(pfilled_dict)>0:
            file_prefix = self.folder + 'PFILLED_'
            order.save_trade_list(self.scur_day, pfilled_dict, file_prefix)    
        for strat_name in self.strat_list:
            strat = self.strategies[strat_name]
            strat.day_finalize()
            strat.initialize()
        self.calc_margin()
        self.save_eod_positions()
        eod_pos = {}
        for inst in self.positions:
            pos = self.positions[inst]
            eod_pos[inst] = [pos.curr_pos.long, pos.curr_pos.short]
        self.ref2trade = {}
        self.ref2order = {}
        self.positions= dict([(inst, order.Position(self.instruments[inst])) for inst in self.instruments])
        self.order_stats = dict([(inst,{'submitted': 0, 'cancelled':0, 'failed': 0, 'status': True }) for inst in self.instruments])
        self.total_submitted = 0
        self.total_cancelled = 0
        self.prev_capital = self.curr_capital
        for inst in self.positions:
            self.positions[inst].pos_yday.long = eod_pos[inst][0] 
            self.positions[inst].pos_yday.short = eod_pos[inst][1]
            self.positions[inst].re_calc()
            self.instruments[inst].prev_close = self.cur_day[inst]['close']
            self.instruments[inst].volume = 0            
        self.initialized = False

    def day_switch(self, event):
        newday = event.dict['date']
        if newday <= self.scur_day:
            return
        self.logger.info('switching the trading day from %s to %s, reset tick_id=%s to 0' % (self.scur_day, newday, self.tick_id))
        self.day_finalize(self.instruments.keys())
        self.isSettlementInfoConfirmed = False
        if not self.eod_flag:
            self.run_eod()
        self.scur_day = newday
        for inst in self.instruments:
            if len(self.day_data[inst]) > 0:
                d_start = workdays.workday(self.scur_day, -self.daily_data_days, CHN_Holidays)
                df = self.day_data[inst]
                self.day_data[inst] = df[df.index >= d_start]
            m_start = workdays.workday(self.scur_day, -self.min_data_days, CHN_Holidays)
            for m in self.min_data[inst]:
                if len(self.min_data[inst][m]) > 0:
                    mdf = self.min_data[inst][m]
                    self.min_data[inst][m] = mdf[mdf.index.date >= m_start]
        self.tick_id = 0
        self.timer_count = 0
        for inst in self.instruments:
            self.tick_data[inst] = []
            self.cur_min[inst] = dict([(item, 0) for item in min_data_list])
            self.cur_day[inst] = dict([(item, 0) for item in day_data_list])
            self.cur_day[inst]['date'] = newday
            self.cur_min[inst]['datetime'] = datetime.datetime.fromordinal(newday.toordinal())
            self.instruments[inst].day_finalized = False
        self.eod_flag = False
                
    def init_init(self):    #init中的init,用于子类的处理
        self.eventEngine.register(EVENT_ORDER, self.rtn_order)
        self.eventEngine.register(EVENT_TRADE, self.rtn_trade)
        self.eventEngine.register(EVENT_ERRORDERINSERT, self.err_order_insert)
        self.eventEngine.register(EVENT_ERRORDERCANCEL, self.err_order_action)
        self.eventEngine.register(EVENT_MARGINRATE, self.rsp_qry_instrument_marginrate)
        self.eventEngine.register(EVENT_ACCOUNT, self.rsp_qry_trading_account)
        self.eventEngine.register(EVENT_INSTRUMENT, self.rsp_qry_instrument)
        self.eventEngine.register(EVENT_POSITION, self.rsp_qry_position)
        self.eventEngine.register(EVENT_QRYORDER, self.rsp_qry_order)
        self.eventEngine.register(EVENT_QRYTRADE, self.rsp_qry_trade)
        self.eventEngine.register(EVENT_TDLOGIN, self.initialize)
        #self.eventEngine.register(EVENT_TDDISCONNECTED, self.td_disconnected)
        self.eventEngine.register(EVENT_TIMER, self.time_scheduler)

    def add_mdapi(self, api):
        self.mdapis.append(api)

    def set_spi(self,spi):
        self.spi = spi
    
    def rtn_tick(self, event):#行情处理主循环
        ctick = event.dict['data']
        if self.live_trading:
            now_ticknum = get_tick_num(datetime.datetime.now())
            cur_ticknum = get_tick_num(ctick.timestamp)
            if abs(cur_ticknum - now_ticknum)> MAX_REALTIME_DIFF:
                self.logger.warning('the tick timestamp has more than 10sec diff from the system time, inst=%s, ticknum= %s, now_ticknum=%s' % (ctick.instID, cur_ticknum, now_ticknum))
                return 0
            
        if (not self.update_instrument(ctick)):
            return 0
        inst = ctick.instID
        if (self.cur_day[inst]['open'] == 0.0):
            self.cur_day[inst]['open'] = ctick.price
            self.logger.debug('open data is received for inst=%s, price = %s, tick_id = %s' % (inst, ctick.price, ctick.tick_id))
        self.cur_day[inst]['close'] = ctick.price
        self.cur_day[inst]['high']  = ctick.high
        self.cur_day[inst]['low']   = ctick.low
        self.cur_day[inst]['openInterest'] = ctick.openInterest
        self.cur_day[inst]['volume'] = ctick.volume
        self.cur_day[inst]['date'] = ctick.timestamp.date()
        if( not self.update_min_bar(ctick)):
            return 0
        return 1

    def process_trade(self, exec_trade):
        all_orders = {}
        pending_orders = []
        order_prices = []
        trade_ref = exec_trade.id
        for inst, v, tick in zip(exec_trade.instIDs, exec_trade.volumes, exec_trade.slip_ticks):
            if v>0:
                order_prices.append(self.instruments[inst].bid_price1+self.instruments[inst].tick_base*tick)
            else:
                order_prices.append(self.instruments[inst].ask_price1-self.instruments[inst].tick_base*tick)    
        curr_price = sum([p*v*cf for p, v, cf in zip(order_prices, exec_trade.volumes, exec_trade.conv_f)])/exec_trade.price_unit
        if curr_price <= exec_trade.limit_price: 
            required_margin = 0
            for idx, (inst, v, otype) in enumerate(zip(exec_trade.instIDs, exec_trade.volumes, exec_trade.order_types)):
                orders = []
                pos = self.positions[inst]
                pos.re_calc()
                self.calc_margin()
                if ((v>0) and (v > pos.can_close.long + pos.can_yclose.long + pos.can_open.long)) or \
                        ((v<0) and (-v > pos.can_close.short + pos.can_yclose.short + pos.can_open.short)):
                    self.logger.warning("ETrade %s is cancelled due to position limit on leg %s: %s" % (exec_trade.id, idx, inst))
                    exec_trade.status = order.ETradeStatus.Cancelled
                    strat = self.strategies[exec_trade.strategy]
                    strat.on_trade(exec_trade)
                    return False

                if v>0:
                    direction = ORDER_BUY
                    vol = max(min(v, pos.can_close.long),0)
                    remained = v - vol
                else:
                    direction = ORDER_SELL
                    vol = max(min(-v,pos.can_close.short),0)
                    remained = v + vol
                    
                if vol > 0:
                    cond = {}
                    if (idx>0) and (exec_trade.order_types[idx-1] == OPT_LIMIT_ORDER):
                        cond = { o:order.OrderStatus.Done for o in all_orders[exec_trade.instIDs[idx-1]]}
                    order_type = OF_CLOSE
                    if (self.instruments[inst].exchange == "SHFE"):
                        order_type = OF_CLOSE_TDAY                        
                    iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, order_type, direction, otype, cond, trade_ref )
                    orders.append(iorder)
                  
                if (self.instruments[inst].exchange == "SHFE") and (abs(remained)>0) and (pos.can_yclose.short+pos.can_yclose.long>0):
                    if remained>0:
                        direction = ORDER_BUY
                        vol = max(min(remained, pos.can_yclose.long),0)
                        remained -= vol
                    else:
                        direction = ORDER_SELL
                        vol = max(min(-remained,pos.can_yclose.short),0)
                        remained += vol
                        
                    if vol > 0:
                        cond = {}
                        if (idx>0) and (exec_trade.order_types[idx-1] == OPT_LIMIT_ORDER):
                            cond = { o:order.OrderStatus.Done for o in all_orders[exec_trade.instIDs[idx-1]]}
                        iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, OF_CLOSE_YDAY, direction, otype, cond, trade_ref )
                        orders.append(iorder)
                
                vol = abs(remained)
                if vol > 0:                   
                    if remained >0:
                        direction = ORDER_BUY
                    else:
                        direction = ORDER_SELL
                    under_price = 0.0
                    if (self.instruments[inst].ptype == instrument.ProductType.Option):
                        under_price = self.instruments[self.instruments[inst].underlying].price
                    required_margin += vol * self.instruments[inst].calc_margin_amount(direction, under_price)
                    cond = {}
                    if (idx>0) and (exec_trade.order_types[idx-1] == OPT_LIMIT_ORDER):
                        cond = { o:order.OrderStatus.Done for o in all_orders[exec_trade.instIDs[idx-1]]}
                    iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, OF_OPEN, direction, otype, cond, trade_ref )
                    orders.append(iorder)
                all_orders[inst] = orders
                
            if required_margin + self.locked_margin > self.margin_cap:
                self.logger.warning("ETrade %s is cancelled due to margin cap: %s" % (exec_trade.id, inst))
                exec_trade.status = order.ETradeStatus.Cancelled
                strat = self.strategies[exec_trade.strategy]
                strat.on_trade(exec_trade)
                return False

            exec_trade.order_dict = all_orders
            for inst in exec_trade.instIDs:
                pos = self.positions[inst]
                for iorder in all_orders[inst]:
                    pos.add_order(iorder)
                    self.ref2order[iorder.order_ref] = iorder
                    if iorder.status == order.OrderStatus.Ready:
                        pending_orders.append(iorder.order_ref)
            exec_trade.status = order.ETradeStatus.Processed
            return pending_orders
        else:
            #self.logger.debug("do not meet the limit price,etrade_id=%s, etrade_inst=%s,  curr price = %s, limit price = %s" % \
            #                 (exec_trade.id, exec_trade.instIDs, curr_price, exec_trade.limit_price))
            return pending_orders
        
    def check_trade(self, exec_trade):
        pending_orders = []
        trade_ref = exec_trade.id
        if exec_trade.id not in self.ref2trade:
            self.ref2trade[exec_trade.id] = exec_trade
        if exec_trade.status == order.ETradeStatus.Pending:
            if exec_trade.valid_time < self.tick_id:
                exec_trade.status = order.ETradeStatus.Cancelled
                strat = self.strategies[exec_trade.strategy]
                strat.on_trade(exec_trade)
            else:
                pending_orders = self.process_trade(exec_trade)
        elif (exec_trade.status == order.ETradeStatus.Processed) or (exec_trade.status == order.ETradeStatus.PFilled):
            #exec_trade.update()
            if exec_trade.valid_time < self.tick_id:
                if exec_trade.status != order.ETradeStatus.Done:
                    exec_trade.valid_time = self.tick_id + self.cancel_protect_period
                    new_orders = {}
                    for inst in exec_trade.instIDs:
                        orders = []
                        for iorder in exec_trade.order_dict[inst]:
                            if (iorder.volume > iorder.filled_volume):
                                if ( iorder.status == order.OrderStatus.Waiting) \
                                        or (iorder.status == order.OrderStatus.Ready):
                                    iorder.on_cancel()
                                    self.trade_update(iorder)
                                else:
                                    self.cancel_order(iorder)
                                if exec_trade.status == order.ETradeStatus.PFilled:                                        
                                    cond = {iorder:order.OrderStatus.Cancelled}
                                    norder = order.Order(iorder.position,
                                                0,
                                                0, # fill in the volume when the dependent order is cancelled
                                                self.tick_id,
                                                iorder.action_type,
                                                iorder.direction,
                                                OPT_MARKET_ORDER,
                                                cond,
                                                trade_ref)
                                    orders.append(norder)
                        if len(orders)>0:
                            new_orders[inst] = orders
                    for inst in new_orders:
                        pos = self.positions[inst]
                        for iorder in new_orders[inst]:
                            exec_trade.order_dict[inst].append(iorder)
                            pos.add_order(iorder)
                            self.ref2order[iorder.order_ref] = iorder
                            if iorder.status == order.OrderStatus.Ready:
                                pending_orders.append(iorder.order_ref)
        #print pending_orders
        if (len(pending_orders) > 0):
            for order_ref in pending_orders:
                self.send_order(self.ref2order[order_ref])
            self.save_state()
    

    def trade_update(self, myorder):
        trade_ref = myorder.trade_ref
        mytrade = self.ref2trade[trade_ref]
        pending_orders = mytrade.update()
        if (mytrade.status == order.ETradeStatus.Done) or (mytrade.status == order.ETradeStatus.Cancelled):            
            strat = self.strategies[mytrade.strategy]
            strat.on_trade(mytrade)
            self.save_state()
        else:
            if len(pending_orders) > 0:
                for order_ref in pending_orders:
                    self.send_order(self.ref2order[order_ref])
                self.save_state()
            
    def exit(self):
        """退出"""
        # 停止事件驱动引擎
        self.eventEngine.stop()
        self.logger.info('stopped the engine, exiting the agent ...')
        self.save_state()
        for strat_name in self.strat_list:
            strat = self.strategies[strat_name]
            strat.save_state()
        # 销毁API对象
        self.trader = None
        self.mdapis = []
        #self.eventEngine = None

class SaveAgent(Agent):
    def init_init(self):
        self.save_flag = True
        self.live_trading = False
        self.prepare_data_env(mid_day = True)
        self.eventEngine.register(EVENT_TIMER, self.time_scheduler)

    def resume(self):
        self.eventEngine.start()

    def exit(self):
        self.eventEngine.stop()
        self.trader = None
        self.mdapis = []

if __name__=="__main__":
    pass
