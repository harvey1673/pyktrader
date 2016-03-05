#-*- coding:utf-8 -*-
import workdays
import json
import datetime
import logging
import bisect
import mysqlaccess
import order as order
import os
import instrument
import ctp
from gateway import *
import pandas as pd
from base import *
from misc import *
import data_handler
import backtest
from eventType import *
from eventEngine import *

min_data_list = ['datetime', 'min_id', 'open', 'high','low', 'close', 'volume', 'openInterest'] 
day_data_list = ['date', 'open', 'high','low', 'close', 'volume', 'openInterest']

def get_tick_num(dt):
    return ((dt.hour+6)%24)*36000+dt.minute*600+dt.second*10+dt.microsecond/100000

def get_min_id(dt):
    return ((dt.hour+6)%24)*100+dt.minute

class MktDataMixin(object):

    def __init__(self, config):
        self.tick_data  = {}
        self.day_data  = {}
        self.min_data  = {}
        self.cur_min = {}
        self.cur_day = {}  		
        self.day_data_func = {}
        self.min_data_func = {}
        self.daily_data_days = config.get('daily_data_days', 25)
        self.min_data_days = config.get('min_data_days', 1)
        self.tick_db_table = config.get('tick_db_table', 'fut_tick')
        self.min_db_table  = config.get('min_db_table', 'fut_min')
        self.daily_db_table = config.get('daily_db_table', 'fut_daily')
        self.calc_func_dict = {}

    def add_instrument(self, name):
        self.tick_data[name] = []
        self.day_data[name]  = pd.DataFrame(columns=['open', 'high','low','close','volume','openInterest'])
        self.min_data[name]  = {1: pd.DataFrame(columns=['open', 'high','low','close','volume','openInterest','min_id'])}
        self.cur_day[name]   = dict([(item, 0) for item in day_data_list])
        self.cur_min[name]   = dict([(item, 0) for item in min_data_list])
        self.day_data_func[name] = []
        self.min_data_func[name] = {}
        self.cur_min[name]['datetime'] = datetime.datetime.fromordinal(self.scur_day.toordinal())
        self.cur_day[name]['date'] = self.scur_day

    def register_data_func(self, inst, freq, fobj):
        if inst not in self.day_data_func:
            self.day_data_func[inst] = []
            self.min_data_func[inst] = {}
        if fobj.name not in self.calc_func_dict:
            self.calc_func_dict[fobj.name] = fobj
        if 'd' in freq:
            for func in self.day_data_func[inst]:
                if fobj.name == func.name:
                    return False
            self.day_data_func[inst].append(self.calc_func_dict[fobj.name])
        else:
            mins = int(freq[:-1])
            if mins not in self.min_data_func[inst]:
                self.min_data_func[inst][mins] = []
            for func in self.min_data_func[inst][mins]:
                if fobj.name == func.name:
                    return False            
            if fobj != None:
                self.min_data_func[inst][mins].append(self.calc_func_dict[fobj.name])
        return self.calc_func_dict[fobj.name]

    def get_min_id(self, tick_id):
        return int(tick_id/1000)
    
    def conv_bar_id(self, min_id):
        return int(min_id/100)*60 + min_id % 100 + 1
            
    def update_min_bar(self, tick):
        inst = tick.instID
        tick_dt = tick.timestamp
        tick_id = tick.tick_id
        tick_min = self.get_min_id(tick_id)
        if (self.cur_min[inst]['min_id'] > tick_min):
            return False
        if (self.cur_day[inst]['open'] == 0.0):
            self.cur_day[inst]['open'] = tick.price
            self.logger.debug('open data is received for inst=%s, price = %s, tick_id = %s' % (inst, tick.price, tick.tick_id))
        self.cur_day[inst]['close'] = tick.price
        self.cur_day[inst]['high']  = tick.high
        self.cur_day[inst]['low']   = tick.low
        self.cur_day[inst]['openInterest'] = tick.openInterest
        self.cur_day[inst]['volume'] = tick.volume
        self.cur_day[inst]['date'] = tick_dt.date()
        if (tick_min == self.cur_min[inst]['min_id']):
            self.tick_data[inst].append(tick)
            self.cur_min[inst]['close'] = tick.price
            if self.cur_min[inst]['high'] < tick.price:
                self.cur_min[inst]['high'] = tick.price
            if self.cur_min[inst]['low'] > tick.price:
                self.cur_min[inst]['low'] = tick.price
        else:
            last_vol = self.cur_min[inst]['volume']
            if (len(self.tick_data[inst]) > 0):
                last_tick = self.tick_data[inst][-1]
                self.cur_min[inst]['volume'] = last_tick.volume - self.cur_min[inst]['volume']
                self.cur_min[inst]['openInterest'] = last_tick.openInterest
                self.min_switch(inst)
                last_vol = last_tick.volume
            self.tick_data[inst] = []
            self.cur_min[inst] = {}
            self.cur_min[inst]['open']  = tick.price
            self.cur_min[inst]['close'] = tick.price
            self.cur_min[inst]['high']  = tick.price
            self.cur_min[inst]['low']   = tick.price
            self.cur_min[inst]['min_id']  = tick_min
            self.cur_min[inst]['volume']  = last_vol
            self.cur_min[inst]['openInterest'] = tick.openInterest
            self.cur_min[inst]['datetime'] = tick_dt.replace(second=0, microsecond=0)
            if ((tick_min>0) and (tick.price>0)): 
                self.tick_data[inst].append(tick)
        return True
    
    def min_switch(self, inst):
        if self.cur_min[inst]['close'] == 0:
            return
        if self.cur_min[inst]['low'] == 0:
            self.cur_min[inst]['low'] = self.cur_min[inst]['close']
        if self.cur_min[inst]['high'] >= MKT_DATA_BIGNUMBER - 1000:
            self.cur_min[inst]['high'] = self.cur_min[inst]['close']
        min_id = self.cur_min[inst]['min_id']
        bar_id = self.conv_bar_id(min_id)
        df = self.min_data[inst][1]
        mysqlaccess.insert_min_data_to_df(df, self.cur_min[inst])
        for m in self.min_data_func[inst]:
            df_m = self.min_data[inst][m]
            if m > 1 and bar_id % m == 0:
                s_start = self.cur_min[inst]['datetime'] - datetime.timedelta(minutes=m)
                slices = df[df.index>s_start]
                new_data = {'open':slices['open'][0],'high':max(slices['high']), \
                            'low': min(slices['low']),'close': slices['close'][-1],\
                            'volume': sum(slices['volume']), 'min_id':slices['min_id'][0]}
                df_m.loc[s_start] = pd.Series(new_data)
            if bar_id % m == 0:
                for fobj in self.min_data_func[inst][m]:
                    fobj.rfunc(df_m)
        #event = Event(type=EVENT_MIN_BAR, priority = 10)
        #event.dict['min_id'] = min_id
        #event.dict['bar_id'] = bar_id
        #event.dict['instID'] = inst
        #self.eventEngine.put(event)
        self.run_min(inst, bar_id)
        if self.save_flag:
            event1 = Event(type=EVENT_DB_WRITE, priority = 500)
            event1.dict['data'] = self.tick_data[inst]
            event1.dict['type'] = EVENT_TICK
            event1.dict['instID'] = inst
            self.eventEngine.put(event1)
            event2 = Event(type=EVENT_DB_WRITE, priority = 500)
            event2.dict['data'] = self.cur_min[inst]
            event2.dict['type'] = EVENT_MIN_BAR
            event2.dict['instID'] = inst
            self.eventEngine.put(event2)
        return

    def mkt_data_sod(self, tday):
        for inst in self.instruments:
            self.tick_data[inst] = []
            self.cur_min[inst] = dict([(item, 0) for item in min_data_list])
            self.cur_day[inst] = dict([(item, 0) for item in day_data_list])
            self.cur_day[inst]['date'] = tday
            self.cur_min[inst]['datetime'] = datetime.datetime.fromordinal(tday.toordinal())

    def mkt_data_eod(self):
        for inst in self.instruments:
            if (len(self.tick_data[inst]) > 0) :
                last_tick = self.tick_data[inst][-1]
                self.cur_min[inst]['volume'] = last_tick.volume - self.cur_min[inst]['volume']
                self.cur_min[inst]['openInterest'] = last_tick.openInterest
                self.min_switch(inst)
            if (self.cur_day[inst]['close']>0):
                mysqlaccess.insert_daily_data_to_df(self.day_data[inst], self.cur_day[inst])
                df = self.day_data[inst]
                for fobj in self.day_data_func[inst]:
                    fobj.rfunc(df)
                if self.save_flag:
                    event = Event(type=EVENT_DB_WRITE, priority = 500)
                    event.dict['data'] = self.cur_day[inst]
                    event.dict['type'] = EVENT_MKTDATA_EOD
                    event.dict['instID'] = inst
                    self.eventEngine.put(event)

            if len(self.day_data[inst]) > 0:
                d_start = workdays.workday(self.scur_day, -self.daily_data_days, CHN_Holidays)
                df = self.day_data[inst]
                self.day_data[inst] = df[df.index >= d_start]
            m_start = workdays.workday(self.scur_day, -self.min_data_days, CHN_Holidays)
            for m in self.min_data[inst]:
                if len(self.min_data[inst][m]) > 0:
                    mdf = self.min_data[inst][m]
                    self.min_data[inst][m] = mdf[mdf.index.date >= m_start]

    def write_mkt_data(self, event):
        inst = event.dict['instID']
        type = event.dict['type']
        data = event.dict['data']
        if type == EVENT_MIN_BAR:
            mysqlaccess.insert_min_data(inst, data, dbtable = self.min_db_table)
        elif type == EVENT_TICK:
            mysqlaccess.bulkinsert_tick_data(inst, data, dbtable = self.tick_db_table)
        elif type == EVENT_MKTDATA_EOD:
            mysqlaccess.insert_daily_data(inst, data, dbtable = self.daily_db_table)
        else:
            pass

    def register_event_handler(self):
        self.eventEngine.register(EVENT_DB_WRITE, self.write_mkt_data)

class Agent(MktDataMixin):
 
    def __init__(self, name, tday=datetime.date.today(), config = {}):
        '''
            trader为交易对象
            tday为当前日,为0则为当日
        '''
        self.tick_id = 0
        self.timer_count = 0
        self.name = name
        self.sched_commands = []
        self.folder = str(config.get('folder', self.name + os.path.sep))
        self.live_trading = config.get('live_trading', False)
        self.realtime_tick_diff = config.get('realtime_tick_diff', 100)
        self.logger = logging.getLogger('.'.join([name, 'agent']))
        self.eod_flag = False
        self.save_flag = False
        self.scur_day = tday
        super(Agent, self).__init__(config)
        self.event_period = config.get('event_period', 1.0)
        self.eventEngine = EventEngine(self.event_period)
        self.instruments = {}
        self.positions = {}
        self.gateways = {}
        gateway_dict = config.get('gateway', {})
        for gateway_name in gateway_dict:
            gway_str = gateway_dict[gateway_name]['class']
            str_list = gway_str.split('.')
            gateway_class = __import__(str(str_list[0]), fromlist = [str(str_list[1])])
            for mod_name in str_list[1:]:
                gateway_class = getattr(gateway_class, mod_name)
            self.add_gateway(gateway_class, gateway_name)
        self.type2gateway = {}
        self.inst2strat = {}
        self.inst2gateway = {}
        self.strat_list = []
        self.strategies = {}
        self.ref2order = {}
        self.ref2trade = {}
        strat_files = config.get('strat_files', [])
        for sfile in strat_files:
            strat_conf = {}
            with open(sfile, 'r') as fp:
                strat_conf = json.load(fp)
            class_str = strat_conf['class']
            strat_mod = class_str.split('.')
            if len(strat_mod) > 1:
                strat_class = getattr(__import__(str(strat_mod[0])), str(strat_mod[1]))
            else:
                strat_class = eval(class_str)
            strat_args  = strat_conf.get('config', {})
            strat = strat_class(strat_args, self)
            self.add_strategy(strat)

        ###交易
        self.ref2order = {}    #orderref==>order
        self.ref2trade = {}
        self.cancel_protect_period = config.get('cancel_protect_period', 200)
        self.market_order_tick_multiple = config.get('market_order_tick_multiple', 5)
        self.init_init()    #init中的init,用于子类的处理

    def register_event_handler(self):
        for key in self.gateways:
            gateway = self.gateways[key]
            gateway.register_event_handler()
        self.eventEngine.register(EVENT_DB_WRITE, self.write_mkt_data)
        self.eventEngine.register(EVENT_LOG, self.log_handler)
        self.eventEngine.register(EVENT_TICK, self.run_tick)
        #self.eventEngine.register(EVENT_MIN_BAR, self.run_min)
        self.eventEngine.register(EVENT_ETRADEUPDATE, self.trade_update)
        self.eventEngine.register(EVENT_DAYSWITCH, self.day_switch)
        self.eventEngine.register(EVENT_TIMER, self.check_commands)

    def put_command(self, timestamp, command, arg = {} ): #按顺序插入
        stamps = [tstamp for (tstamp,cmd, fargs) in self.sched_commands]
        ii = bisect.bisect(stamps, timestamp)
        self.sched_commands.insert(ii,(timestamp, command, arg))

    def check_commands(self, event):
        l = len(self.sched_commands)
        curr_time = datetime.datetime.now()
        i = 0
        while(i<l and curr_time >= self.sched_commands[i][0]):
            logging.info(u'exec command:,i=%s,time=%s,command[i][1]=%s' % (i, curr_time, self.sched_commands[i][1].__name__))
            arg = self.sched_commands[i][2]
            self.sched_commands[i][1](**arg)
            i += 1
        if i>0:
            del self.sched_commands[0:i]

    def gateway_map(self, instID):
        exch = self.instruments[instID].exchange
        if exch in ['CZCE', 'DCE', 'SHFE', 'CFFEX']:
            for key in self.gateways:
                gateway = self.gateways[key]
                gway_class = type(gateway).__name__
                if 'Ctp' in gway_class:
                    return gateway
        return None

    def add_instrument(self, name):
        if name not in self.instruments:
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
            self.instruments[name].update_param(self.scur_day)
            if name not in self.inst2strat:
                self.inst2strat[name] = {}
            if name not in self.inst2gateway:
                gateway = self.gateway_map(name)
                if gateway != None:
                    self.inst2gateway[name] = gateway
                    subreq = VtSubscribeReq()
                    subreq.symbol = name
                    subreq.exchange = self.instruments[name].exchange
                    subreq.productClass = self.instruments[name].ptype
                    subreq.currency = self.instruments[name].ccy
                    subreq.expiry = self.instruments[name].expiry
                    gateway.subscribe(subreq)
                else:
                    self.logger.warning("No Gateway is assigned to instID = %s" % name)
            super(Agent, self).add_instrument(name)

    def add_strategy(self, strat):
        if strat.name not in self.strat_list:
            self.strat_list.append(strat.name)
            self.strategies[strat.name] = strat
            strat.agent = self
        for instID in strat.dep_instIDs():
            self.add_instrument(instID)
            self.inst2strat[instID][strat.name] = []
        strat.reset()

    def add_gateway(self, gateway, gateway_name=None):
        """创建接口"""
        if gateway_name not in self.gateways:
            self.gateways[gateway_name] = gateway(self, gateway_name)

    def connect(self, gateway_name):
        """连接特定名称的接口"""
        if gateway_name in self.gateways:
            gateway = self.gateways[gateway_name]
            gateway.connect()
        else:
            self.logger.warning(u'接口不存在：%s' % gateway_name)
        
    #----------------------------------------------------------------------
    def subscribe(self, subscribeReq, gateway_name):
        """订阅特定接口的行情"""
        if gateway_name in self.gateways:
            gateway = self.gateways[gateway_name]
            gateway.subscribe(subscribeReq)
        else:
            self.logger.warning(u'接口不存在：%s' %gateway_name)        
        
    #----------------------------------------------------------------------
    def send_order(self, iorder):
        """对特定接口发单"""
        gateway_name = iorder.gateway
        if gateway_name not in self.gateways:
            self.logger.warning(u'接口不存在：%s' % gateway_name)
            gateway = self.inst2gateway[iorder.instID]
        else:
            gateway = self.gateways[gateway_name]
        gateway.sendOrder(iorder)
    
    #----------------------------------------------------------------------
    def cancel_order(self, iorder):
        """对特定接口撤单"""
        gateway_name = iorder.gateway
        if gateway_name in self.gateways:
            gateway = self.gateways[gateway_name]
            gateway.cancelOrder(iorder)
        else:
            self.logger.warning(u'接口不存在：%s' % gateway_name)

    def log_handler(self, event):
        lvl = event.dict['level']
        self.logger.log(lvl, event.dict['data'])

    def get_eod_positions(self):
        for name in self.gateways:
            self.gateways[name].load_local_positions(self.scur_day)

    def get_all_orders(self):
        self.ref2order = {}
        for name in self.gateways:
            self.gateways[name].load_order_list(self.scur_day)
            order_dict = self.gateways[name].id2order
            for local_id in order_dict:
                iorder = order_dict[local_id]
                iorder.gateway = name
                self.ref2order[iorder.order_ref] = iorder
        keys = self.ref2order.keys()
        if len(keys) > 1:
            keys.sort()
        for key in keys:
            iorder =  self.ref2order[key]			
            if len(iorder.conditionals)>0:
                self.ref2order[key].conditionals = dict([(self.ref2order[o_id], iorder.conditionals[o_id]) 
                                                         for o_id in iorder.conditionals])

    def prepare_data_env(self, inst, mid_day = True):
        if  self.instruments[inst].ptype == instrument.ProductType.Option:
            return
        if self.daily_data_days > 0 or mid_day:
            self.logger.debug('Updating historical daily data for %s' % self.scur_day.strftime('%Y-%m-%d'))
            daily_start = workdays.workday(self.scur_day, -self.daily_data_days, CHN_Holidays)
            daily_end = self.scur_day
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
            min_start = int(self.instruments[inst].start_tick_id/1000)
            min_end = int(self.instruments[inst].last_tick_id/1000)+1
            mindata = mysqlaccess.load_min_data_to_df('fut_min', inst, d_start, d_end, minid_start=min_start, minid_end=min_end, database = 'blueshale')
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

    def restart(self):
        self.logger.debug('Prepare trade environment for %s' % self.scur_day.strftime('%y%m%d'))
        for inst in self.instruments:
            self.prepare_data_env(inst, mid_day = True)
        self.get_eod_positions()
        self.get_all_orders()
        self.ref2trade = order.load_trade_list(self.scur_day, self.folder)
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
            
        for gway in self.gateways:
            gateway = self.gateways[gway]
            for inst in gateway.positions:
                gateway.positions[inst].re_calc()
            gateway.calc_margin()
            gateway.connect()
        self.eventEngine.start()

    def check_price_limit(self, inst, num_tick):
        inst_obj = self.instruments[inst]
        tick_base = inst_obj.tick_base
        if (inst_obj.ask_price1 >= inst_obj.up_limit - num_tick * tick_base) or (inst_obj.bid_price1 <= inst_obj.down_limit + num_tick * tick_base):
            return True
        else:
            return False
 
    def save_state(self):
        '''
            保存环境
        '''
        trade_refs = []
        for trade_id in self.ref2trade:
            etrade = self.ref2trade[trade_id]
            if (etrade.status == order.ETradeStatus.StratConfirm) and (sum([abs(v) for v in etrade.filled_vol]) == 0):
                for inst in etrade.order_dict:
                    for iorder in etrade.order_dict[inst]:
                        self.ref2order.pop(iorder.order_ref, None)
                        self.gateways[iorder.gateway].id2order.pop(iorder.order_ref, None)
                trade_refs.append(etrade.id)
        for trade_id in trade_refs:
            self.ref2trade.pop(trade_id, None)
        if not self.eod_flag:
            self.logger.debug(u'保存执行状态.....................')
            for gway in self.gateways:
                self.gateways[gway].save_order_list(self.scur_day)
            order.save_trade_list(self.scur_day, self.ref2trade, self.folder)
    
    def run_eod(self):
        if self.eod_flag:
            return
        print 'run EOD process'
        self.mkt_data_eod()
        if len(self.strat_list) == 0:
            self.eod_flag = True
            return
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
        self.save_state()
        self.eod_flag = True
        for name in self.gateways:
            self.gateways[name].day_finalize(self.scur_day)
        self.ref2trade = {}
        self.ref2order = {}
        for inst in self.instruments:
            self.instruments[inst].prev_close = self.cur_day[inst]['close']
            self.instruments[inst].volume = 0            

    def day_switch(self, event):
        newday = event.dict['date']
        if newday <= self.scur_day:
            return
        self.logger.info('switching the trading day from %s to %s, reset tick_id=%s to 0' % (self.scur_day, newday, self.tick_id))
        if not self.eod_flag:
            self.run_eod()
        self.scur_day = newday
        self.tick_id = 0
        self.timer_count = 0
        super(Agent, self).mkt_data_sod(newday)
        self.eod_flag = False
        eod_time = datetime.datetime.combine(newday, datetime.time(15, 20, 0))
        self.put_command(eod_time, self.run_eod)
                
    def init_init(self):    #init中的init,用于子类的处理
        self.register_event_handler()

    def update_instrument(self, tick):      
        inst = tick.instID    
        curr_tick = tick.tick_id
        self.tick_id = max(curr_tick, self.tick_id)
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
        if tick.volume > last_volume:
            self.instruments[inst].price  = tick.price
            self.instruments[inst].volume = tick.volume
            self.instruments[inst].last_traded = curr_tick

    def run_tick(self, event):#行情处理主循环
        tick = event.dict['data']
        if self.live_trading:
            now_ticknum = get_tick_num(datetime.datetime.now())
            cur_ticknum = get_tick_num(tick.timestamp)
            if abs(cur_ticknum - now_ticknum)> self.realtime_tick_diff:
                self.logger.warning('the tick timestamp has more than 10sec diff from the system time, inst=%s, ticknum= %s, now_ticknum=%s' % (tick.instID, cur_ticknum, now_ticknum))
        self.update_instrument(tick)
        if self.update_min_bar(tick):
            for strat_name in self.inst2strat[tick.instID]:
                self.strategies[strat_name].run_tick(tick)

    def run_min(self, inst, bar_id):
        for strat_name in self.inst2strat[inst]:
            for m in self.inst2strat[inst][strat_name]:
                if bar_id % m == 0:
                    self.strategies[strat_name].run_min(inst, m)

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
                gateway = self.inst2gateway[inst]
                pos = gateway.positions[inst]
                pos.re_calc()
                gateway.calc_margin()
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
                    iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, order_type, direction, otype, cond, trade_ref, gateway = gateway.gatewayName )
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
                        iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, OF_CLOSE_YDAY, direction, otype, cond, trade_ref, gateway = gateway.gatewayName )
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
                    iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, OF_OPEN, direction, otype, cond, trade_ref, gateway = gateway.gatewayName )
                    orders.append(iorder)
                all_orders[inst] = orders
            exec_trade.order_dict = all_orders
            for inst in exec_trade.instIDs:
                for iorder in all_orders[inst]:
                    pos = self.gateways[iorder.gateway].positions[inst]
                    pos.add_order(iorder)
                    self.ref2order[iorder.order_ref] = iorder
                    if iorder.status == order.OrderStatus.Ready:
                        pending_orders.append(iorder.order_ref)
            exec_trade.status = order.ETradeStatus.Processed
            return pending_orders
        else:
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
                                    event = Event(type=EVENT_ETRADEUPDATE)
                                    event.dict['trade_ref'] = iorder.trade_ref
                                    self.trade_update(event)
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
                                                trade_ref, gateway = iorder.gateway)
                                    orders.append(norder)
                        if len(orders)>0:
                            new_orders[inst] = orders
                    for inst in new_orders:
                        gateway = self.inst2gateway[inst]
                        pos = gateway.positions[inst]
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

    def trade_update(self, event):
        trade_ref = event.dict['trade_ref']
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
        for name in self.gateways:
            gateway = self.gateways[name]
            gateway.close()
            gateway.mdApi = None
            gateway.tdApi = None

class SaveAgent(Agent):
    def init_init(self):
        self.save_flag = True
        self.live_trading = False
        #self.prepare_data_env(mid_day = True)
        for key in self.gateways:
            gateway = self.gateways[key]
            gway_class = type(gateway).__name__
            if 'Ctp' in gway_class:
                self.type2gateway['CTP'] = gateway
            elif 'Lts' in gway_class:
                self.type2gateway['LTS'] = gateway
            elif 'Ib' in gway_class:
                self.type2gateway['IB'] = gateway
            elif 'Ksgold' in gway_class:
                self.type2gateway['KSGOLD'] = gateway
            elif 'Ksotp' in gway_class:
                self.type2gateway['KSOTP'] = gateway
            elif 'Femas' in gway_class:
                self.type2gateway['FEMAS'] = gateway
        self.register_event_handler()

    def restart(self):
        self.eventEngine.start()
        for gway in self.gateways:
            gateway = self.gateways[gway]
            gateway.connect()

    def register_event_handler(self):
        for key in self.gateways:
            gateway = self.gateways[key]
            gateway.register_event_handler()
        self.eventEngine.register(EVENT_DB_WRITE, self.write_mkt_data)
        self.eventEngine.register(EVENT_LOG, self.log_handler)
        self.eventEngine.register(EVENT_TICK, self.run_tick)
        self.eventEngine.register(EVENT_DAYSWITCH, self.day_switch)
        self.eventEngine.register(EVENT_TIMER, self.check_commands)
        if 'CTP' in self.type2gateway:
            self.eventEngine.register(EVENT_TDLOGIN + self.type2gateway['CTP'].gatewayName, self.ctp_qry_instruments)
            self.eventEngine.register(EVENT_QRYINSTRUMENT + self.type2gateway['CTP'].gatewayName, self.add_ctp_instruments)
            self.type2gateway['CTP'].setAutoDbUpdated(True)

    def ctp_qry_instruments(self, event):
        dtime = datetime.datetime.now()
        min_id = get_min_id(dtime)
        if min_id < 250:
            gateway = self.type2gateway['CTP']
            gateway.qry_commands.append(gateway.tdApi.qryInstrument)

    def add_ctp_instruments(self, event):
        data = event.dict['data']
        last = event.dict['last']
        if last:
            gateway = self.type2gateway['CTP']
            for symbol in gateway.qry_instruments:
                if symbol not in self.instruments:
                    self.add_instrument(symbol)

    def exit(self):
        self.eventEngine.stop()
        for name in self.gateways:
            gateway = self.gateways[name]
            gateway.close()
            gateway.mdApi = None
            gateway.tdApi = None

if __name__=="__main__":
    pass
