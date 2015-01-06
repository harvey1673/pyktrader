#-*- coding:utf-8 -*-
from base import *
from misc import *
from strategy import *
import pandas as pd
import data_handler
import order as order
 
class TurtleTrader(Strategy):
    def __init__(self, name, underliers,  trade_unit = [], agent = None):
        Strategy.__init__(self, name, underliers, trade_unit, agent)
        self.data_func = [ 
                ('d', BaseObject(name = 'ATR_20', sfunc=fcustom(data_handler.ATR, n=20), rfunc=fcustom(data_handler.atr, n=20))), \
                ('d', BaseObject(name = 'DONCH_L10', sfunc=fcustom(data_handler.DONCH_L, n=10), rfunc=fcustom(data_handler.donch_l, n=10))),\
                ('d', BaseObject(name = 'DONCH_H10', sfunc=fcustom(data_handler.DONCH_H, n=10), rfunc=fcustom(data_handler.donch_h, n=10))),\
                ('d', BaseObject(name = 'DONCH_L20', sfunc=fcustom(data_handler.DONCH_L, n=20), rfunc=fcustom(data_handler.donch_l, n=20))),\
                ('d', BaseObject(name = 'DONCH_H20', sfunc=fcustom(data_handler.DONCH_H, n=20), rfunc=fcustom(data_handler.donch_h, n=20))),\
                #('d', BaseObject(name = 'DONCH_L55', sfunc=fcustom(data_handler.DONCH_L, n=55), rfunc=fcustom(data_handler.donch_l, n=55))),\
                #('d', BaseObject(name = 'DONCH_H55', sfunc=fcustom(data_handler.DONCH_H, n=55), rfunc=fcustom(data_handler.donch_h, n=55))),\
                ]    
        self.capital = 100000 
        self.pos_ratio = 0.01
        self.stop_loss = 2.0
        self.order_type = OPT_LIMIT_ORDER
        self.trade_unit = trade_unit
        
    def run_tick(self, ctick):
        inst = ctick.instID
        df = self.agent.day_data[inst]
        price_unit = self.agent.instruments[inst].multiple
        cur_atr = df.ix[-1,'ATR_20']
        hh = [df.ix[-1,'DONCH_H20'],df.ix[-1,'DONCH_H10']]
        ll  = [df.ix[-1,'DONCH_L20'],df.ix[-1,'DONCH_L10']]
        idx = self.get_index([inst])
        if idx < 0:
            self.logger.warning('the inst=%s is not in this strategy = %s' % (inst, self.name))
            return 
        save_status = self.update_positions(idx)
        cur_price = (ctick.askPrice1 + ctick.bidPrice1)/2.0
        if cur_price < 0.01 or cur_price > 100000:
            self.logger.info('something wrong with the price for inst = %s, bid ask price = %s %s' % (inst, ctick.bidPrice1,  + ctick.askPrice1))
            return 
        if len(self.submitted_pos[idx]) == 0:
            if len(self.positions[idx]) == 0: 
                buysell = 0
                if (cur_price > hh[0]):
                    buysell = 1
                elif (cur_price < ll[0]):
                    buysell = -1                 
                if buysell !=0:
                    valid_time = self.agent.tick_id + 600
                    etrade = order.ETrade( [inst], [self.trade_unit[idx][0]*buysell], \
                                           [self.order_type], cur_price, [0],  \
                                           valid_time, self.name, self.agent.name, price_unit, [price_unit] )
                    tradepos = TradePos([inst], self.trade_unit[idx], buysell, \
                                        cur_price, cur_price - cur_atr*self.stop_loss*buysell, price_unit)
                    tradepos.entry_tradeid = etrade.id
                    self.submitted_pos[idx].append(etrade)
                    self.positions[idx].append(tradepos)
                    save_status = True
                    self.logger.info('strat %s open a new position on %s, cur_price=%s, chanhigh=%s, chanlow=%s, direction=%s, vol=%s, tradeid=%s is sent for processing, stat status saved' % 
                                     (self.name, inst, cur_price, hh[0], ll[0], buysell, self.trade_unit[idx][0], etrade.id))
                    self.agent.submit_trade(etrade)
            else:
                buysell = self.positions[idx][0].direction
                units = len(self.positions[idx])
                for tradepos in reversed(self.positions[idx]):
                    if (cur_price < ll[1] and buysell == 1) or (cur_price > hh[1] and buysell == -1) \
                            or ((cur_price - tradepos.exit_target)*buysell < 0):
                        valid_time = self.agent.tick_id + 600
                        etrade = order.ETrade( [inst], [-self.trade_unit[idx][0]*buysell], \
                                               [self.order_type], cur_price, [0], \
                                               valid_time, self.name, self.agent.name, price_unit, [price_unit] )
                        tradepos.exit_tradeid = etrade.id
                        save_status = True
                        self.logger.info('strat %s close a position on %s after a reverse breakout, cur_price=%s, chanhigh=%s, exit=%s, chanlow=%s, direction=%s, vol=%s, tradeid=%s is sent for processing' % 
                                     (self.name, inst, cur_price, hh[1], ll[1], tradepos.exit_target, -buysell, self.trade_unit[idx][0], etrade.id))
                        self.submitted_pos[idx].append(etrade)
                        self.agent.submit_trade(etrade)
                        if save_status:
                            self.save_state()
                        return
                if  units < 4 and (cur_price - self.positions[idx][-1].entry_price)*buysell >= cur_atr/2.0:
                    for pos in self.positions[idx]:
                        pos.exit_target = cur_price - cur_atr*self.stop_loss*buysell
                    valid_time = self.agent.tick_id + 600
                    etrade = order.ETrade( [inst], [self.trade_unit[idx][0]*buysell], \
                                           [self.order_type], cur_price, [0],  \
                                           valid_time, self.name, self.agent.name, price_unit, [price_unit] )
                    tradepos = TradePos([inst], self.trade_unit[idx], buysell, \
                                        cur_price, cur_price - cur_atr*self.stop_loss*buysell, price_unit)
                    tradepos.entry_tradeid = etrade.id
                    self.submitted_pos[idx].append(etrade)
                    self.positions[idx].append(tradepos)
                    save_status = True
                    self.logger.info('strat %s build a new position on top on %s, curr_price=%s, last entry=%s, cur_atr=%s, direction=%s, vol=%s, tradeid=%s is sent for processing' % 
                                 (self.name, inst, cur_price, self.positions[idx][-1].entry_price, cur_atr, buysell, self.trade_unit[idx][0], etrade.id))
                    self.agent.submit_trade(etrade)                 
        if save_status:
            self.save_state()
        return
    
    def update_trade_unit(self):
        pass
        #for under, pos in zip(self.underliers,self.positions):
        #    if len(pos) == 0: 
        #        inst = under[0]
        #        pinst  = self.agent.instruments[inst]
        #        df  = self.agent.day_data[inst]                
        #        self.trade_unit = [int(self.capital*self.pos_ratio/(pinst.multiple*df.ix[-1,'ATR_20']))]
