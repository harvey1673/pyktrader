#-*- coding:utf-8 -*-
from base import *
from misc import *
import data_handler as dh
import copy
from strategy import *
 
class DTSplitDChanFilter(Strategy):
    common_params =  dict({'open_period': [300, 1500, 2100], 'channel_keys': ['DONCH_H', 'DONCH_L'], 'use_chan': True}, **Strategy.common_params)
    asset_params = dict({'lookbacks': 1, 'ratios': 1.0, 'channels': 20, 'min_rng': 0.003, 'daily_close': False, }, **Strategy.asset_params)
    def __init__(self, config, agent = None):
        Strategy.__init__(self, config, agent)
        numAssets = len(self.underliers)
        self.cur_rng = [0.0] * numAssets
        self.chan_high = [0.0] * numAssets
        self.chan_low  = [0.0] * numAssets
        self.tday_open = [0.0] * numAssets
        self.open_idx = [0] * numAssets
        self.tick_base = [0.0] * numAssets
        self.daily_close_buffer = 3
        self.num_tick = 1

    def register_func_freq(self):
        for under, chan in zip(self.underliers, self.channels):
            for infunc in self.data_func:
                name  = infunc[0]
                sfunc = eval(infunc[1])
                rfunc = eval(infunc[2])
                if len(infunc) > 3:
                    fargs = infunc[3]
                else:
                    fargs = {}
                fobj = BaseObject(name = name + str(chan[1]), sfunc = fcustom(sfunc, n = chan, **fargs), rfunc = fcustom(rfunc, n = chan, **fargs))
                self.agent.register_data_func(under[0], 'd', fobj)

    def initialize(self):
        self.load_state()
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            self.tick_base[idx] = self.agent.instruments[inst].tick_base
            min_id = self.agent.instruments[inst].last_tick_id/1000
            min_id = int(min_id/100)*60 + min_id % 100 - self.daily_close_buffer
            self.last_min_id[idx] = int(min_id/60)*100 + min_id % 60
            ddf = self.agent.day_data[inst]
            mdf = self.agent.min_data[inst][1]
            last_date = ddf.index[-1]
            key = self.channel_keys[0] + str(self.channels[idx])
            self.chan_high[idx] = ddf.ix[-1, key]
            key = self.channel_keys[1] + str(self.channels[idx])
            self.chan_low[idx]  = ddf.ix[-1, key]
            self.open_idx[idx] = 0
            if last_date < mdf.index[-1].date():
                last_min = mdf['min_id'][-1]
                pid = 0
                for i in range(1, len(self.open_period)):
                    if self.open_period[i] >= last_min:
                        break
                    else:
                        pid = i
                df = mdf[(mdf.index.date <= last_date)|(mdf['min_id'] < self.open_period[pid])]
                post_df = mdf[(mdf.index.date > last_date) & (mdf['min_id'] >= self.open_period[pid])]
                self.open_idx[idx] = pid
                self.tday_open[idx] = post_df['open'][0]
            else:
                df = mdf
                self.tday_open[idx] = mdf['close'][-1]
            self.recalc_rng(idx, df)
        self.save_state()
        return

    def recalc_rng(self, idx, df):
        mdf = copy.copy(df)
        inst = self.underliers[idx][0]
        mdf.loc[:,'min_idx'] = pd.Series(0, index = mdf.index)
        for i in range(1, len(self.open_period)-1):
            mdf.loc[(mdf['min_id']>= self.open_period[i]) & (mdf['min_id']<self.open_period[i+1]), 'min_idx'] = i
        mdf.loc[:, 'date_idx'] = mdf.index.date
        ddf = mdf.groupby([mdf['date_idx'], mdf['min_idx']]).apply(dh.ohlcsum).reset_index().set_index('datetime')
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
            self.agent.inst2strat[inst][self.name].append(1)
            #self.logger.debug("stat = %s register bar event for inst=%s freq = 1" % (self.name, inst, ))

    def on_bar(self, idx, freq):
        inst = self.underliers[idx][0]
        min_id = self.agent.cur_min[inst]['min_id']
        curr_min = self.agent.instruments[inst].last_update/1000
        pid = self.open_idx[idx]
        if pid < len(self.open_period)-1:
            if (self.open_period[pid+1] > min_id) and (self.open_period[pid+1] <= curr_min):
                self.recalc_rng(idx, self.agent.min_data[inst][1])
                self.tday_open[idx] = self.agent.instruments[inst].price
                self.logger.info("Note: the new split open is set to %s for inst=%s for stat = %s" % (self.tday_open[idx], inst, self.name, ))

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
        rng = max(self.cur_rng[idx] * self.ratios[idx], t_open * self.min_rng[idx])
        buy_trig  = t_open + rng
        sell_trig = t_open - rng
        if self.use_chan == False:
            self.chan_high[idx] = buy_trig
            self.chan_low[idx]  = sell_trig
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
