#-*- coding:utf-8 -*-
from base import *
from misc import *
from strategy import *
import pandas as pd
import data_handler
import order as order
 
class DTTrader(Strategy):
    def __init__(self, name, underliers,  capital, agent = None):
        Strategy.__init__(name, underliers, agent)
        self.data_func = [
				('d', BaseObject(name = 'DONCH_H1', sfunc=fcustom(data_handler.DONCH_H, n=1), rfunc=fcustom(data_handler.donch_h, n=1))),\
                ('d', BaseObject(name = 'DONCH_L1', sfunc=fcustom(data_handler.DONCH_L, n=1), rfunc=fcustom(data_handler.donch_l, n=1))),\
                ('d', BaseObject(name = 'DONCH_C1', sfunc=fcustom(data_handler.DONCH_C, n=1), rfunc=fcustom(data_handler.donch_c, n=1)))]   
        self.capital = capital 
        self.up_ratio = 1.0
		self.down_ratio = 1.0
		self.order_type = OPT_LIMIT_ORDER
    
    def run_tick(self, ctick):
        inst = ctick.instID
        df = self.agent.day_data[inst]
        cur_rng = max(df.ix[-1,'DONCH_H1'] - df.ix[-1,'DONCH_C1'], df.ix[-1,'DONCH_C1'] - df.ix[-1,'DONCH_L1'])
		tday_open = self.cur_day[inst]['open']
		buy_trig = tday_open + self.up_ratio * cur_rng
		sell_trig = tday_open - self.down_ratio * cur_rng
        idx = self.get_index([inst])
		if idx < 0:
			self.logger.warning('the inst=%s is not in this strategy = %s' % (inst, self.name))
			return 
		self.update_positions(idx)
        ask = ctick.askPrice1 
		bid = ctick.bidPrice1
        if len(self.submitted_pos[idx]) == 0:
			direction = 0
			if len(self.positions[inst])>0:
				direction = self.positions[inst][0].direction
			if (ask > buy_trig) and (direction <=0):
				
            if len(self.positions[inst]) == 0: 
                buysell = 0
                if (cur_price > hh[0]):
                    buysell = 1
                elif (cur_price < ll[0]):
                    buysell = -1                 
                if buysell !=0:
                    valid_time = self.agent.tick_id + 600
                    etrade = order.ETrade( [inst], [self.trade_unit[idx][0]*buysell], \
                                           [self.order_type], cur_price, [5],  \
                                           valid_time, self.name, self.agent.name)
                    tradepos = TradePos([inst], self.trade_unit[idx], buysell, \
                                        cur_price, cur_price - cur_atr*self.stop_loss*buysell)
                    tradepos.entry_tradeid = etrade.id
                    self.submitted_pos[idx].append(etrade)
                    self.positions[inst].append(tradepos)
                    self.agent.submit_trade(etrade)
                    return 1
            else:
                buysell = self.positions[idx][0].direction
                units = len(self.positions[idx])
                for tradepos in self.positions[idx]:
                    if (cur_price < ll[1] and buysell == 1) or (cur_price > hh[1] and buysell == -1) \
                        or ((cur_price - tradepos.exit_target)*buysell < 0):
                        valid_time = self.agent.tick_id + 600
                        etrade = order.ETrade( [inst], [-self.trade_unit[idx][0]*buysell], \
                                               [self.order_type], cur_price, [5], \
                                               valid_time, self.name, self.agent.name)
                        tradepos.exit_tradeid = etrade.id
                        self.submitted_pos[idx].append(etrade)
                        self.agent.submit_trade(etrade)
                    elif  units < 4 and (cur_price - self.positions[idx][-1].entry_price)*buysell >= cur_atr/2.0:
						for pos in self.positions[idx]:
							pos.exit_target = cur_price - cur_atr*self.stop_loss*buysell
                        valid_time = self.agent.tick_id + 600
                        etrade = order.ETrade( [inst], [self.trade_unit[idx][0]*buysell], \
                                               [self.order_type], cur_price, [5],  \
                                               valid_time, self.name, self.agent.name)
                        tradepos = TradePos([inst], self.trade_unit[idx], buysell, \
                                            cur_price, cur_price - cur_atr*self.stop_loss*buysell)
                        tradepos.entry_tradeid = etrade.id
                        self.submitted_pos[idx].append(etrade)
                        self.positions[inst].append(tradepos)
                        self.agent.submit_trade(etrade)                  
                    return 1
