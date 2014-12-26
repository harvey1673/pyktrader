#-*- coding:utf-8 -*-
from base import *
from misc import *
from strategy import *
import pandas as pd
import data_handler
import order as order
import agent
 
class DTTrader(Strategy):
    def __init__(self, name, underliers, agent = None, trade_unit = [], ratios = [], stop_loss = []):
        Strategy.__init__(self, name, underliers, trade_unit, agent)
        self.data_func = [
                ('d', BaseObject(name = 'DONCH_H1', sfunc=fcustom(data_handler.DONCH_H, n=1), rfunc=fcustom(data_handler.donch_h, n=1))),\
                ('d', BaseObject(name = 'DONCH_L1', sfunc=fcustom(data_handler.DONCH_L, n=1), rfunc=fcustom(data_handler.donch_l, n=1))),\
                ('d', BaseObject(name = 'DONCH_C1', sfunc=fcustom(data_handler.DONCH_C, n=1), rfunc=fcustom(data_handler.donch_c, n=1)))]   
        self.ratios = [(0.7,0.7)]*len(underliers)
        if len(ratios) > 1:
            self.ratio = ratios
        elif len(ratios) == 1: 
            self.ratio = ratios*len(underliers)
        self.order_type = OPT_LIMIT_ORDER
        self.stop_loss = stop_loss
        self.lookback = 1
        self.last_tick_id = 2056000
        self.close_tday = [False]*len(underliers)
    
    def run_tick(self, ctick):
        inst = ctick.instID
        tick_id = agent.get_tick_id(ctick.timestamp)
        df = self.agent.day_data[inst]
        cur_rng = max(df.ix[-1,'DONCH_H1'] - df.ix[-1,'DONCH_C1'], df.ix[-1,'DONCH_C1'] - df.ix[-1,'DONCH_L1'])
        tday_open = self.agent.cur_day[inst]['open']
        if tday_open <= 0.0:
            return 
        idx = self.get_index([inst])
        if idx < 0:
            self.logger.warning('the inst=%s is not in this strategy = %s' % (inst, self.name))
            return
        buy_trig = tday_open + self.ratios[idx][0] * cur_rng
        sell_trig = tday_open - self.ratios[idx][1] * cur_rng
        self.update_positions(idx)
        curr_price = (ctick.askPrice1 + ctick.bidPrice1)/2.0
        curr_pos = None
        buysell = 0
        if len(self.positions[idx])>0:
            curr_pos = self.positions[idx][0]
            buysell = curr_pos.direction
        if (tick_id >= self.last_tick_id):
            if (buysell!=0) and (self.close_tday[idx]):
                valid_time = self.agent.tick_id + 600
                etrade = order.ETrade( [inst], [-self.trade_unit[idx][0]*buysell], \
                                               [self.order_type], -curr_price*buysell, [0], \
                                               valid_time, self.name, self.agent.name)
                curr_pos.exit_tradeid = etrade.id
                self.save_state()
                self.submitted_pos[idx].append(etrade)
                self.agent.submit_trade(etrade)
                self.logger.info('DT EOD close position for inst = %s, direction=%s, volume=%s, trade_id = %s' \
                                                            % (inst, buysell,self.trade_unit[idx][0], etrade.id))
        elif len(self.submitted_pos[idx]) == 0:
            if ((curr_price >= buy_trig) and (buysell <=0)) or ((curr_price <= sell_trig) and (buysell >=0)):
                if buysell!=0:
                    valid_time = self.agent.tick_id + 600
                    etrade = order.ETrade( [inst], [-self.trade_unit[idx][0]*buysell], \
                                               [self.order_type], -curr_price*buysell, [0], \
                                               valid_time, self.name, self.agent.name)
                    curr_pos.exit_tradeid = etrade.id
                    self.save_state()
                    self.submitted_pos[idx].append(etrade)
                    self.agent.submit_trade(etrade)
                    self.logger.info('DT EOD close position for inst = %s, direction=%s, volume=%s, trade_id = %s' \
                                                            % (inst, buysell,self.trade_unit[idx][0], etrade.id))
                if  (curr_price >= buy_trig):
                    buysell = 1
                else:
                    buysell = -1
                valid_time = self.agent.tick_id + 600
                etrade = order.ETrade( [inst], [self.trade_unit[idx][0]*buysell], \
                                       [self.order_type], buysell * curr_price, [0],  \
                                       valid_time, self.name, self.agent.name)
                tradepos = TradePos([inst], self.trade_unit[idx], buysell, \
                                        curr_price, 0)
                tradepos.entry_tradeid = etrade.id
                self.submitted_pos[idx].append(etrade)
                self.positions[idx].append(tradepos)
                self.save_state()
                self.agent.submit_trade(etrade)
                self.logger.info('DT EOD open position for inst = %s, direction=%s, volume=%s, trade_id = %s' \
                                                            % (inst, buysell,self.trade_unit[idx][0], etrade.id))
        return 
        
    def update_trade_unit(self):
        pass
