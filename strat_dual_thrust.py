#-*- coding:utf-8 -*-
from base import *
from misc import *
from strategy import *
 
class DTTrader(Strategy):
    def __init__(self, name, underliers, volumes, agent = None, trade_unit = [], ratios = [], lookbacks=[], daily_close = False, email_notify = None):
        Strategy.__init__(self, name, underliers, volumes, trade_unit, agent, email_notify)
        self.lookbacks = lookbacks
        self.data_func = []   
        numAssets = len(underliers)
        self.ratios = [(0.7,0.7)] * numAssets
        if len(ratios) > 1:
            self.ratio = ratios
        elif len(ratios) == 1: 
            self.ratio = ratios * numAssets
        if len(lookbacks) > 0:
            self.lookbacks = lookbacks
        else: 
            self.lookbacks = [0] * numAssets
        self.order_type = OPT_LIMIT_ORDER
        self.daily_close_buffer = 3000
        self.tday_open = [0.0] * numAssets
        self.cur_rng = [0.0] * numAssets
        self.close_tday = [daily_close] * numAssets

    def initialize(self):
        self.load_state()
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            ddf = self.agent.day_data[inst]
            win = self.lookbacks[idx]
            if win > 0:
                self.cur_rng[idx] = max(max(ddf.ix[-win:,'high'])- min(ddf.ix[-win:,'close']), max(ddf.ix[-win:,'close']) - min(ddf.ix[-win:,'low']))
            else:
                self.cur_rng[idx] = max(max(ddf.ix[-2:,'high'])- min(ddf.ix[-2:,'close']), max(ddf.ix[-2:,'close']) - min(ddf.ix[-2:,'low']))
                self.cur_rng[idx] = max(self.cur_rng[idx] * 0.5, ddf.ix[-1,'high']-ddf.ix[-1,'close'],ddf.ix[-1,'close']-ddf.ix[-1,'low'])
        return

    def save_local_variables(self, file_writer):
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            row = ['CurrRange', str(inst), self.cur_rng[idx]]
            file_writer.writerow(row)
        return
    
    def load_local_variables(self, row):
        if row[0] == 'CurrRange':
            inst = str(row[1])
            idx = self.get_index([inst])
            if idx >=0:
                self.cur_rng[idx] = float(row[2])
        return
        
    def run_tick(self, ctick):
        inst = ctick.instID
        tick_id = ctick.tick_id
        tday_open = self.agent.cur_day[inst]['open']
        idx = self.get_index([inst]) 
        if idx < 0:
            self.logger.warning('the inst=%s is not in this strategy = %s' % (inst, self.name))
            return
        save_status = self.update_positions(idx)
        if len(self.submitted_pos[idx]) > 0:
            return
        num_pos = len(self.positions[idx])
        buysell = 0
        if num_pos > 1:
            self.logger.warning('something wrong with position management - submitted trade is empty but trade position is more than 1')
            return
        elif num_pos == 1:
            buysell = self.positions[idx][0].direction
        if (tday_open <= 0.0) or (self.cur_rng[idx] <= 0):
            self.logger.warning("warning: open price =0.0 or range = 0.0 for inst=%s for stat = %s" % (inst, self.name))
            return
        last_tick_id = self.agent.instruments[inst].last_tick_id - self.daily_close_buffer
        tick_base = self.agent.instruments[inst].tick_base
        buy_trig  = tday_open + self.ratios[idx][0] * self.cur_rng[idx]
        sell_trig = tday_open - self.ratios[idx][1] * self.cur_rng[idx]
        curr_price = (ctick.askPrice1+ctick.bidPrice1)/2.0
        if curr_price < 0.01 or curr_price > 100000:
            self.logger.info('something wrong with the price for inst = %s, bid ask price = %s %s' % (inst, ctick.bidPrice1,  + ctick.askPrice1))
            return 
        if (tick_id >= last_tick_id):
            if (buysell!=0) and (self.close_tday[idx]):
                msg = 'DT to close position before EOD for inst = %s, direction=%s, volume=%s, current tick_id = %s' \
                                    % (inst, buysell, self.trade_unit[idx], tick_id)
                self.close_tradepos(idx, self.positions[idx][0], curr_price - buysell * self.num_tick * tick_base)
                self.status_notifier(msg)
                self.save_state()
                return
        if ((curr_price >= buy_trig) and (buysell <=0)) or ((curr_price <= sell_trig) and (buysell >=0)):
            if buysell!=0:
                msg = 'DT to close position for inst = %s, open= %s, buy_trig=%s, sell_trig=%s, curr_price= %s, direction=%s, volume=%s' \
                                    % (inst, tday_open, buy_trig, sell_trig, curr_price, buysell, self.trade_unit[idx])
                self.close_tradepos(idx, self.positions[idx][0], curr_price - buysell * self.num_tick * tick_base)
                self.status_notifier(msg)
            if  (curr_price >= buy_trig):
                buysell = 1
            else:
                buysell = -1
            msg = 'DT to open position for inst = %s, open= %s, buy_trig=%s, sell_trig=%s, curr_price= %s, direction=%s, volume=%s' \
                                    % (inst, tday_open, buy_trig, sell_trig, curr_price, buysell, self.trade_unit[idx])
            self.open_tradepos(idx, buysell, curr_price + buysell * self.num_tick * tick_base)
            self.status_notifier(msg)
            save_status = True
        if save_status: 
            self.save_state()
        return 
        
    def update_trade_unit(self):
        pass
