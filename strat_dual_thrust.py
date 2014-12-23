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
        Strategy.__init__(name, underliers, trade_unit, agent)
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
        tday_open = self.cur_day[inst]['open']
        idx = self.get_index([inst])
        if idx < 0:
            self.logger.warning('the inst=%s is not in this strategy = %s' % (inst, self.name))
            return
        buy_trig = tday_open + self.ratios[idx][0] * cur_rng
        sell_trig = tday_open - self.ratio[idx][1] * cur_rng
        self.update_positions(idx)
        ask = ctick.askPrice1 
        bid = ctick.bidPrice1
        if (tick_id >= self.last_tick_id) and (self.close_tday[idx]):
            if len(self.positions[idx])>0:
                curr_pos = self.positions[idx][0]
                buysell = curr_pos.direction
                valid_time = self.agent.tick_id + 600
                etrade = order.ETrade( [inst], [-self.trade_unit[idx][0]*buysell], \
                                               [self.order_type], (ask+bid)/2, [5], \
                                               valid_time, self.name, self.agent.name)
                curr_pos.exit_tradeid = etrade.id
                self.submitted_pos[idx].append(etrade)
                self.agent.submit_trade(etrade)
        elif len(self.submitted_pos[idx]) == 0:
            direction = 0
            if len(self.positions[idx])>0:
                direction = self.positions[inst][0].direction
            if (ask > buy_trig) and (direction <=0):
                if direction != 0:

                if len(curr_pos) > 0:
                    curr_pos[0].close(mslice.close+offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
                new_pos = strat.TradePos([mslice.contract], [1], unit, buytrig, 0)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + offset, dd)
                curr_pos.append(new_pos)
                pos = unit
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
            elif (mslice.close <= selltrig) and (pos >=0 ):
                if len(curr_pos) > 0:
                    curr_pos[0].close(mslice.close-offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
                new_pos = strat.TradePos([mslice.contract], [1], -unit, selltrig, 0)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close - offset, dd)
                curr_pos.append(new_pos)
                pos = -unit
                
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
