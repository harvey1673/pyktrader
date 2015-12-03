#-*- coding:utf-8 -*-
from base import *
from misc import *
import data_handler as dh
import copy
from strategy import *
 
class DTChanMinTrader(Strategy):
    def __init__(self, name, underliers, volumes,
                 agent = None,
                 trade_unit = [],
                 ratios = [],
                 lookbacks=[],
                 daily_close = False,
                 email_notify = None,
                 freq = 15,
                 chan_freq = 'd',
                 chan_func = {'func_high': [data_handler.DONCH_H, data_handler.donch_h], 'high_name': 'DONCH_H',
                              'func_low': [data_handler.DONCH_L, data_handler.donch_l],  'low_name': 'DONCH_L',
                              'func_args': {'n': 10}},
                 min_rng = [0.00]):
        Strategy.__init__(self, name, underliers, volumes, trade_unit, agent, email_notify)
        func_args = chan_func['func_args']
        self.channel = func_args['n']
        self.chan_freq = chan_freq
        self.data_func = [ 
                (chan_freq, BaseObject(name = chan_func['low_name'] + str(self.channel), \
                                       sfunc=fcustom(chan_func['func_low'][0], **func_args),  \
                                       rfunc=fcustom(chan_func['func_low'][1], **func_args))),\
                (chan_freq, BaseObject(name = chan_func['high_name'] + str(self.channel), \
                                       sfunc=fcustom(chan_func['func_high'][0], **func_args), \
                                       rfunc=fcustom(chan_func['func_high'][1], **func_args))),\
                ]
        if 'm' in chan_freq:
            mins = int(chan_freq[:-1])
            if mins != self.freq:
                min_str = str(freq)+'m'
                self.data_func.append((min_str, None))
        self.lookbacks = lookbacks
        numAssets = len(underliers)
        self.ratios = [[0.5, 0.5]] * numAssets
        if len(ratios) > 1:
            self.ratios = ratios
        elif len(ratios) == 1: 
            self.ratios = ratios * numAssets
        if len(lookbacks) > 0:
            self.lookbacks = lookbacks
        else: 
            self.lookbacks = [0] * numAssets
        self.freq = freq		
        self.cur_rng = [0.0] * numAssets
        self.chan_high = [0.0] * numAssets
        self.chan_low  = [0.0] * numAssets
        self.tday_open = [0.0] * numAssets
        self.tick_base = [0.0] * numAssets
        self.order_type = OPT_LIMIT_ORDER
        self.daily_close_buffer = 3
        self.close_tday = [False] * numAssets
        if len(daily_close) > 1:
            self.close_tday = daily_close
        elif len(daily_close) == 1: 
            self.close_tday = daily_close * numAssets 
        self.num_tick = 1
        self.min_rng = [0.0] * numAssets
        if len(min_rng) > 1:
            self.min_rng = min_rng
        elif len(min_rng) == 1:
            self.min_rng = min_rng * numAssets

    def initialize(self):
        self.load_state()
        low_str = self.data_func[0][1].name
        high_str = self.data_func[1][1].name
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            self.tick_base[idx] = self.agent.instruments[inst].tick_base
            min_id = self.agent.instruments[inst].last_tick_id/1000
            min_id = int(min_id/100)*60 + min_id % 100 - self.daily_close_buffer
            self.last_min_id[idx] = int(min_id/60)*100 + min_id % 60
            if self.chan_freq == 'd':
                ddf = self.agent.day_data[inst]
            else:
                mins = int(self.chan_freq[:-1])
                ddf = self.agent.min_data[inst][mins]
            mdf = self.agent.min_data[inst][1]
            self.chan_high[idx] = ddf.ix[-1, high_str]
            self.chan_low[idx]  = ddf.ix[-1, low_str]
            self.tday_open[idx] = mdf['close'][-1]
            self.recalc_rng(idx, ddf)
        self.save_state()
        return

    def recalc_rng(self, idx, ddf):
        win = self.lookbacks[idx]
        if win > 0:
            self.cur_rng[idx] = max(max(ddf.ix[-win:,'high'])- min(ddf.ix[-win:,'close']), max(ddf.ix[-win:,'close']) - min(ddf.ix[-win:,'low']))
        elif win == 0:
            self.cur_rng[idx] = max(max(ddf.ix[-2:,'high'])- min(ddf.ix[-2:,'close']), max(ddf.ix[-2:,'close']) - min(ddf.ix[-2:,'low']))
            self.cur_rng[idx] = max(self.cur_rng[idx] * 0.5, ddf.ix[-1,'high']-ddf.ix[-1,'close'],ddf.ix[-1,'close']-ddf.ix[-1,'low'])
        else:
            self.cur_rng[idx] = max(ddf.ix[-1,'high']- ddf.ix[-1,'low'], abs(ddf.ix[-1,'close'] - ddf.ix[-2,'close']))

    def save_local_variables(self, file_writer):
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            row = ['CurrRange', str(inst), self.cur_rng[idx]]
            file_writer.writerow(row)
        return
    
    def load_local_variables(self, row):
        if row[0] == 'CurrRange':
            inst = str(row[1])
            idx = self.under2idx[inst]
            if idx >= 0:
                self.cur_rng[idx] = float(row[2])
        return

    def register_bar_freq(self):
        for idx, under in enumerate(self.underliers):
            inst = under[0]
            self.agent.inst2strat[inst][self.name].append(self.freq)
            #self.logger.debug("stat = %s register bar event for inst=%s freq = 1" % (self.name, inst, ))

    def on_bar(self, idx, freq):
        inst = self.underliers[idx][0]
        min_id = self.agent.cur_min[inst]['min_id']
        curr_min = self.agent.instruments[inst].last_update/1000
        self.recalc_rng(idx, self.agent.min_data[inst][self.freq])
        self.tday_open[idx] = self.agent.instruments[inst].price
        #self.logger.info("Note: the new split open is set to %s for inst=%s for stat = %s" % (self.tday_open[idx], inst, self.name, ))

    def on_tick(self, idx, ctick):
        if len(self.submitted_trades[idx]) > 0:
            return
        inst = self.underliers[idx][0]
        if self.open_idx[idx] == 0:
            self.tday_open[idx] = self.agent.cur_day[inst]['open']
        if (self.tday_open[idx] <= 0.0) or (self.cur_rng[idx] <= 0) or (self.curr_prices[idx] <= 0.001):
            self.logger.warning("warning: open price =0.0 or range = 0.0 or curr_price=0 for inst=%s for stat = %s" % (inst, self.name))
            return
        min_id = self.agent.tick_id/1000.0
        num_pos = len(self.positions[idx])
        buysell = 0
        if num_pos > 1:
            self.logger.warning('something wrong with position management - submitted trade is empty but trade position is more than 1')
            return
        elif num_pos == 1:
            buysell = self.positions[idx][0].direction
        tick_base = self.tick_base[idx]
        t_open = self.tday_open[idx]
        rng = max(self.cur_rng[idx] * self.ratios[idx][0], t_open * self.min_rng[idx])
        buy_trig  = t_open + rng
        sell_trig = t_open - rng
        if (min_id >= self.last_min_id[idx]):
            if (buysell!=0) and (self.close_tday[idx]):
                msg = 'DT to close position before EOD for inst = %s, direction=%s, volume=%s, current tick_id = %s' \
                        % (inst, buysell, self.trade_unit[idx], min_id)
                self.close_tradepos(idx, self.positions[idx][0], self.curr_prices[idx] - buysell * self.num_tick * tick_base)
                self.status_notifier(msg)
                self.save_state()
            return

        if ((self.curr_prices[idx] >= buy_trig) and (buysell <=0)) or ((self.curr_prices[idx] <= sell_trig) and (buysell >=0)):
            save_status = False
            if buysell!=0:
                msg = 'DT to close position for inst = %s, open= %s, buy_trig=%s, sell_trig=%s, curr_price= %s, direction=%s, volume=%s' \
                                    % (inst, t_open, buy_trig, sell_trig, self.curr_prices[idx], buysell, self.trade_unit[idx])
                self.close_tradepos(idx, self.positions[idx][0], self.curr_prices[idx] - buysell * self.num_tick * tick_base)
                self.status_notifier(msg)
                save_status = True
            if self.trade_unit[idx] <= 0:
                self.save_state()
                return
            if  (self.curr_prices[idx] >= buy_trig):
                buysell = 1
            else:
                buysell = -1
            if self.curr_prices[idx] >= max(buy_trig, self.chan_high[idx]) or self.curr_prices[idx] <= min(sell_trig, self.chan_low[idx]):
                msg = 'DT to open position for inst = %s, open= %s, buy_trig=%s, sell_trig=%s, curr_price= %s, direction=%s, volume=%s' \
                                        % (inst, t_open, buy_trig, sell_trig, self.curr_prices[idx], buysell, self.trade_unit[idx])
                self.open_tradepos(idx, buysell, self.curr_prices[idx] + buysell * self.num_tick * tick_base)
                self.status_notifier(msg)
                save_status = True
            if save_status:
                self.save_state()
        return 
        
    def update_trade_unit(self):
        pass
