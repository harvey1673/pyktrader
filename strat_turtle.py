#-*- coding:utf-8 -*-
from base import *
from misc import *
from strategy import *
import data_handler
 
class TurtleTrader(Strategy):
    def __init__(self, name, underliers,  volumes, trade_unit = [], agent = None, email_notify = None, datafreq = 'd', freq = 1, windows = [4, 8], max_pos = [4], trail_loss = [2.0]):
        Strategy.__init__(self, name, underliers, volumes, trade_unit, agent, email_notify)
        self.data_func = [ 
                (datafreq, BaseObject(name = 'ATR_' + str(windows[1]), sfunc=fcustom(data_handler.ATR, n=windows[1]), rfunc=fcustom(data_handler.atr, n=windows[1]))), \
                (datafreq, BaseObject(name = 'DONCH_L' + str(windows[0]), sfunc=fcustom(data_handler.DONCH_L, n=windows[0]), rfunc=fcustom(data_handler.donch_l, n=windows[0]))),\
                (datafreq, BaseObject(name = 'DONCH_H' + str(windows[0]), sfunc=fcustom(data_handler.DONCH_H, n=windows[0]), rfunc=fcustom(data_handler.donch_h, n=windows[0]))),\
                (datafreq, BaseObject(name = 'DONCH_L' + str(windows[1]), sfunc=fcustom(data_handler.DONCH_L, n=windows[1]), rfunc=fcustom(data_handler.donch_l, n=windows[1]))),\
                (datafreq, BaseObject(name = 'DONCH_H' + str(windows[1]), sfunc=fcustom(data_handler.DONCH_H, n=windows[1]), rfunc=fcustom(data_handler.donch_h, n=windows[1]))),\
                #(freq, BaseObject(name = 'DONCH_L55', sfunc=fcustom(data_handler.DONCH_L, n=windows[2]), rfunc=fcustom(data_handler.donch_l, n=windows[2]))),\
                #(freq, BaseObject(name = 'DONCH_H55', sfunc=fcustom(data_handler.DONCH_H, n=windows[2]), rfunc=fcustom(data_handler.donch_h, n=windows[2]))),\
                ]    
        self.curr_atr   = [0.0] * len(underliers)
        self.entry_high = [0.0] * len(underliers)
        self.entry_low  = [0.0] * len(underliers)
        self.exit_high  = [0.0] * len(underliers)
        self.exit_low   = [0.0] * len(underliers)
        self.tick_base  = [0.0] * len(underliers)
        if len(trail_loss) > 1:
            self.trail_loss = trail_loss
        elif len(trail_loss) == 1:
            self.trail_loss = trail_loss * len(underliers)
        self.channels = windows
        self.freq = freq
        if len(max_pos) > 1:
            self.max_pos = max_pos
        elif len(max_pos) == 1:
            self.max_pos = max_pos * len(underliers)
    
    def initialize(self):
        self.load_state()
        atr_str = 'ATR_' + str(self.channels[1])
        bb_str = 'DONCH_H' + str(self.channels[1])
        sb_str = 'DONCH_L' + str(self.channels[1])
        bs_str = 'DONCH_H' + str(self.channels[0])
        ss_str = 'DONCH_L' + str(self.channels[0])        
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            self.tick_base[idx] = self.agent.instruments[inst].tick_base
            df = self.agent.day_data[inst]
            self.entry_high[idx] = df.ix[-1, bb_str]
            self.entry_low[idx]  = df.ix[-1, sb_str]
            self.exit_high[idx] = df.ix[-1, bs_str]
            self.exit_low[idx]  = df.ix[-1, ss_str]           
            if len(self.positions[idx]) == 0:
                self.curr_atr[idx] = df.ix[-1, atr_str]
        pass       

    def register_bar_freq(self):
        for instID in self.instIDs:
            self.agent.inst2strat[instID][self.name].append(self.freq)

    def save_local_variables(self, file_writer):
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            row = ['ATR', str(inst), self.curr_atr[idx]]
            file_writer.writerow(row)
        return
    
    def load_local_variables(self, row):
        if row[0] == 'ATR':
            inst = str(row[1])
            idx = self.under2idx[inst]
            if idx >=0:
                self.curr_atr[idx] = float(row[2])
        return
            
    def on_bar(self, idx, freq):
        if (freq != self.freq):
            return
        inst = self.underliers[idx][0]
        if self.curr_prices[idx] < 0.01 or self.curr_prices[idx] > 100000:
            inst_obj = self.agent.instruments[inst]
            self.logger.info('something wrong with the price for inst = %s, bid ask price = %s %s' % (inst, inst_obj.bid_price1,  inst_obj.ask_price1))
            return 
        if len(self.submitted_trades[idx]) > 0:
            return
        inst = self.underliers[idx][0]
        tick_base = self.tick_base[idx]
        buysell = 0
        if len(self.positions[idx]) == 0:
            buysell = 0
            if self.curr_prices[idx] > self.entry_high[idx]:
                buysell = 1
            elif self.curr_prices[idx] < self.entry_low[idx]:
                buysell = -1                 
            if buysell !=0:
                msg = 'Turtle to open a new position for inst = %s, curr_price=%s, chanhigh=%s, chanlow=%s, direction=%s, vol=%s is sent for processing' \
                        % (inst, self.curr_prices[idx], self.entry_high[idx], self.entry_low[idx], buysell, self.trade_unit[idx])
                self.open_tradepos(idx, buysell, self.curr_prices[idx] + buysell * self.num_tick * tick_base)
                self.status_notifier(msg)
                self.save_state()
        else:
            buysell = self.positions[idx][0].direction
            units = len(self.positions[idx])
            exit_pos = False
            for tradepos in reversed(self.positions[idx]):
                if (tradepos.entry_target != tradepos.entry_price) and (tradepos.entry_target == tradepos.exit_target):
                    tradepos.entry_target = tradepos.entry_price
                if (self.curr_prices[idx] < self.exit_low[idx] and buysell == 1) or (self.curr_prices[idx] > self.exit_high[idx] and buysell == -1) \
                        or ((tradepos.entry_target-self.curr_prices[idx])*buysell >= self.trail_loss[idx]*self.curr_atr[idx]):
                    msg = 'Turtle to close a position for inst = %s, curr_price = %s, chanhigh=%s, chanlow=%s, direction=%s, vol=%s , target=%s, ATR=%s' \
                            % (inst, self.curr_prices[idx], self.exit_high[idx], self.exit_low[idx], buysell, self.trade_unit[idx], tradepos.entry_target, self.curr_atr[idx])
                    self.close_tradepos(idx, tradepos, self.curr_prices[idx] - buysell * self.num_tick * tick_base)
                    self.status_notifier(msg)
                    exit_pos = True
            if exit_pos:
                self.save_state()
                return
            if  units < self.max_pos[idx] and (self.curr_prices[idx] - self.positions[idx][-1].entry_price)*buysell >= self.curr_atr[idx]*self.trail_loss[idx]/self.max_pos[idx]:
                last_entry = self.positions[idx][-1].entry_price
                for pos in self.positions[idx]:
                    pos.entry_target = self.curr_prices[idx]                
                msg = 'Turtle to add a new position after 0.5 ATR increase for inst = %s, curr_price=%s, last_entry=%s, direction=%s, vol=%s is sent for processing' \
                        % (inst, self.curr_prices[idx], last_entry, buysell, self.trade_unit[idx])
                self.open_tradepos(idx, buysell, self.curr_prices[idx] + buysell * self.num_tick * tick_base)
                self.status_notifier(msg)
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
