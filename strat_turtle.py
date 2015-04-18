#-*- coding:utf-8 -*-
from base import *
from misc import *
from strategy import *
import data_handler
 
class TurtleTrader(Strategy):
    def __init__(self, name, underliers,  volumes, trade_unit = [], agent = None, email_notify = None, datafreq = 'd', freq = 1, windows = [10, 20]):
        Strategy.__init__(self, name, underliers, trade_unit, agent, email_notify)
        self.data_func = [ 
                (datafreq, BaseObject(name = 'ATR', sfunc=fcustom(data_handler.ATR, n=windows[1]), rfunc=fcustom(data_handler.atr, n=windows[1]))), \
                (datafreq, BaseObject(name = 'DONCH_L10', sfunc=fcustom(data_handler.DONCH_L, n=windows[0]), rfunc=fcustom(data_handler.donch_l, n=windows[0]))),\
                (datafreq, BaseObject(name = 'DONCH_H10', sfunc=fcustom(data_handler.DONCH_H, n=windows[0]), rfunc=fcustom(data_handler.donch_h, n=windows[0]))),\
                (datafreq, BaseObject(name = 'DONCH_L20', sfunc=fcustom(data_handler.DONCH_L, n=windows[1]), rfunc=fcustom(data_handler.donch_l, n=windows[1]))),\
                (datafreq, BaseObject(name = 'DONCH_H20', sfunc=fcustom(data_handler.DONCH_H, n=windows[1]), rfunc=fcustom(data_handler.donch_h, n=windows[1]))),\
                #(freq, BaseObject(name = 'DONCH_L55', sfunc=fcustom(data_handler.DONCH_L, n=windows[2]), rfunc=fcustom(data_handler.donch_l, n=windows[2]))),\
                #(freq, BaseObject(name = 'DONCH_H55', sfunc=fcustom(data_handler.DONCH_H, n=windows[2]), rfunc=fcustom(data_handler.donch_h, n=windows[2]))),\
                ]    
        self.curr_atr  = [0.0] * len(underliers)
        self.channels = windows
        self.freq = freq
    
    def initialize(self):
        self.load_state()
        atr_str = 'ATR_' + str(self.channels[1])
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            df = self.agent.day_data[inst]
            if len(self.positions[idx]) == 0:
                self.curr_atr[idx] = df.ix[-1, atr_str]
        pass       

    def save_local_variables(self, file_writer):
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            row = ['ATR', str(inst), self.curr_atr[idx]]
            file_writer.writerow(row)
        return
    
    def load_local_variables(self, row):
        if row[0] == 'ATR':
            inst = str(row[1])
            idx = self.get_index([inst])
            if idx >=0:
                self.curr_atr[idx] = float(row[2])
        return
            
    def run_min(self, inst):
        min_id = self.agent.cur_min[inst]['min_id']
        curr_min = int(min_id/100)*60+ min_id % 100
        if (curr_min % self.freq != 0):
            return        
        bb_str = 'DONCH_H' + str(self.channels[1])
        sb_str = 'DONCH_L' + str(self.channels[1])
        bs_str = 'DONCH_H' + str(self.channels[0])
        ss_str = 'DONCH_L' + str(self.channels[0])
        df = self.agent.day_data[inst]
        inst_obj = self.agent.instruments[inst]
        tick_base = inst_obj.tick_base
        
        hh = [df.ix[-1, bb_str],df.ix[-1,bs_str]]
        ll  = [df.ix[-1,sb_str],df.ix[-1,ss_str]]
        idx = self.get_index([inst])
        if idx < 0:
            self.logger.warning('the inst=%s is not in this strategy = %s' % (inst, self.name))
            return 
        self.update_positions(idx)
        if self.curr_prices[idx] < 0.01 or self.curr_prices[idx] > 100000:
            self.logger.info('something wrong with the price for inst = %s, bid ask price = %s %s' % (inst, inst_obj.bidPrice1,  inst_obj.askPrice1))
            return 
        if len(self.submitted_pos[idx]) > 0:
            return
        if len(self.positions[idx]) == 0: 
            buysell = 0
            if (self.curr_prices[idx] > hh[0]):
                buysell = 1
            elif (self.curr_prices[idx] < ll[0]):
                buysell = -1                 
            if buysell !=0:
                msg = 'Turtle to open a new position for inst = %s, curr_price=%s, chanhigh=%s, chanlow=%s, direction=%s, vol=%s is sent for processing' \
                        % (inst, self.curr_prices[idx], hh[0], ll[0], buysell, self.trade_unit[idx])
                self.open_tradepos(idx, buysell, self.curr_prices[idx] + buysell * self.num_tick * tick_base)
                self.status_notifier(msg)
                self.save_state()
        else:
            buysell = self.positions[idx][0].direction
            units = len(self.positions[idx])
            for tradepos in reversed(self.positions[idx]):
                if (self.curr_prices[idx] < ll[1] and buysell == 1) or (self.curr_prices[idx] > hh[1] and buysell == -1) \
                        or ((tradepos.entry_price-self.curr_prices[idx])*buysell >= self.trail_loss[idx]*self.curr_atr[idx]):
                    msg = 'Turtle to close a position for inst = %s, curr_price = %s, chanhigh=%s, chanlow=%s, direction=%s, vol=%s , target=%s, ATR=%s' \
                                % (inst, self.curr_prices[idx], hh[1], ll[1], buysell, self.trade_unit[idx], tradepos.entry_target, self.curr_atr[idx])
                    self.close_tradepos(idx, tradepos, self.curr_prices[idx] - buysell * self.num_tick * tick_base)
                    self.status_notifier(msg)
                    self.save_state()
                    return
            if  units < 4 and (self.curr_prices[idx] - self.positions[idx][-1].entry_price)*buysell >= self.curr_atr[idx]/2.0:
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
