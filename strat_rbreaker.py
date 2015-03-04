#-*- coding:utf-8 -*-
from base import *
from misc import *
from strategy import *
import pandas as pd
import data_handler
import order as order
import agent
 
class RBreakerTrader(Strategy):
    def __init__(self, name, underliers, agent = None, trade_unit = [], ratios = [], min_rng = [], stop_loss = 0, trail_profit = 0):
        Strategy.__init__(name, underliers, trade_unit, agent)
        self.data_func = []   
        num_assets = len(underliers)
        self.ratios = [(0.4, 0.1, 0.1)]*num_assets
        if len(ratios) > 1:
            self.ratio = ratios
        elif len(ratios) == 1: 
            self.ratio = ratios*num_assets
        self.min_rng = [1.0]*num_assets
		if len(ratios) == num_assets:
            self.min_rng = min_rng
        elif len(ratios) == 1: 
            self.min_rng = min_rng * num_assets
        self.order_type = OPT_MARKET_ORDER
        self.ssetup = [0.0]*num_assets
        self.bsetup = [0.0]*num_assets
        self.senter = [0.0]*num_assets
        self.benter = [0.0]*num_assets
        self.sbreak = [0.0]*num_assets
        self.bbreak = [0.0]*num_assets
        self.start_min_id = 1505
        self.end_min_id = 2055
        self.freq = 1
        self.stop_loss = stop_loss
        self.trail_profit = trail_profit

    def initialize(self):
        self.load_state()
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            ddf = self.agent.day_data[inst]
            (a, b, c) = self.ratios[idx]
            dhigh = ddf.ix[-1,'high']
            dlow = ddf.ix[-1,'low']
            dclose = ddf.ix[-1,'close']
            self.ssetup[idx] = dhigh + a*(dclose - dlow)
            self.bsetup[idx] = dlow  - a*(dhigh -  dclose)
            self.senter[idx] = (1 + b)*(dhigh + dclose)/2.0 - b*dlow
            self.benter[idx] = (1 + b)*(dlow  + dclose)/2.0 - b*dhigh
            self.bbreak[idx] = self.ssetup[idx] + c * (self.ssetup[idx] - self.bsetup[idx])
            self.sbreak[idx] = self.bsetup[idx] - c * (self.ssetup[idx] - self.bsetup[idx])    
        pass         

    def save_local_variables(self, file_writer):
        for idx, underlier in enumerate(self.underliers):
			inst = underlier[0]
			row = ['NumTrade', str(inst), self.num_daytrades[idx][0],self.num_daytrades[idx][1]]
			file_writer.writerow(row)
		return
    
    def load_local_variables(self, row):
        if row[0] == 'NumTrade':
			inst = str(row[1])
			idx = self.get_index([inst])
			if idx >=0:
				self.num_daytrades[idx] = (int(row[2]), int(row[3])) 
        return
		
    def run_min(self, inst):
        min_id = self.agent.cur_min[inst]['min_id']
        idx = self.get_index([inst])
        if idx < 0:
            self.logger.warning('the inst=%s is not in this strategy = %s' % (inst, self.name))
            return
        save_status = self.update_positions(idx)
        if len(self.submitted_pos[idx]) > 0:
            return
        num_pos = len(self.positions[idx])
        curr_pos = None
        if num_pos > 1:
            self.logger.warning('something wrong with position management - submitted trade is empty but trade position is more than 1')
            return
        elif num_pos == 1:
            curr_pos = self.positions[idx][0]
            
        curr_min = int(min_id/100)*60+ min_id % 100
        if (curr_min % self.freq != 0) or (min_id < self.start_min_id):
            return
        inst_obj = self.agent.instruments[inst]
		last_tick_id = inst_obj.last_tick_id - self.daily_close_buffer
		tick_base = inst_obj.tick_base
        dhigh = self.cur_day[inst].high
        dlow  = self.cur_day[inst].low
        curr_price = (inst_obj.ask_price1 + inst_obj.bid_price1)/2.0
        if curr_price < 0.001 or curr_price > 1000000:
            self.logger.info('something wrong with the price for inst = %s, bid ask price = %s %s' % (inst, inst_obj.bid_price1,  inst_obj.ask_price1))
            return 
		buysell = 0 if curr_pos == None else curr_pos.direction
        if ((min_id >= last_tick_id) or self.check_price_limit(inst, curr_price, 5)): 
            if (curr_pos != None):
                self.close_tradepos(idx, curr_pos, curr_price - buysell * self.num_tick * tick_base)
                save_status = True
                msg = 'R-Breaker to close position before EOD or hitting price limit for inst = %s, direction=%s, volume=%s, current min_id = %s, current price = %s' \
                                    % (inst, buysell, self.trade_unit[idx], min_id, curr_price)
                self.status_notifier(msg)
            return          
        if ((curr_price >= self.bbreak[idx]) or (curr_price <= self.sbreak[idx])) and (buysell == 0):
            if  (curr_price >= self.bbreak[idx]):
                buysell = 1
            else:
                buysell = -1
            self.open_tradepos(idx, buysell, curr_price + buysell * self.num_tick * tick_base)
            save_status = True
            msg = 'R-Breaker to open position for inst = %s, open= %s, buy_trig=%s, sell_trig=%s, curr_price= %s, direction=%s, volume=%s' \
                    % (inst, tday_open, buy_trig, sell_trig, curr_price, buysell, self.trade_unit[idx])
			self.status_notifier(msg)
            elif ((dhigh< self.bbreak[idx]) and (dhigh >= self.ssetup[idx]) and (curr_price < self.senter[idx]) and (buysell >=0)) or \
                 ((dlow > self.sbreak[idx]) and (dlow  <= self.bsetup[idx]) and (curr_price > self.benter[idx]) and (buysell <=0)):
                if curr_pos != None:
					self.close_tradepos(idx, curr_pos, curr_price - buysell * self.num_tick * tick_base)
					save_status = True
					msg = 'R-Breaker to close position before EOD for inst = %s, direction=%s, volume=%s, current tick_id = %s' \
                                    % (inst, buysell, self.trade_unit[idx], tick_id)
					self.status_notifier(msg)
                if  (curr_price < self.senter[idx]):
                    buysell = -1
                else:
                    buysell = 1
                self.open_tradepos(idx, buysell, curr_price + buysell * self.num_tick * tick_base)
                save_status = True
                msg = 'R-Breaker to open position for inst = %s, open= %s, buy_trig=%s, sell_trig=%s, curr_price= %s, direction=%s, volume=%s' \
                                    % (inst, tday_open, buy_trig, sell_trig, curr_price, buysell, self.trade_unit[idx])
				self.status_notifier(msg)
        return 
        
    def update_trade_unit(self):
        pass
