#-*- coding:utf-8 -*-
from base import *
from misc import *
from strategy import *
import data_handler as dh
 
class TurtleTrader(Strategy):
    common_params = Strategy.common_params
    asset_params = dict( {'channels': [10, 20], 'trail_loss': 2, 'max_pos': 4, 'trading_freq': 1, 'data_freq':'d'}, **Strategy.asset_params )
    def __init__(self, config, agent = None):
        Strategy.__init__(self, config, agent)   
        self.curr_atr   = [0.0] * len(self.underliers)
        self.entry_high = [0.0] * len(self.underliers)
        self.entry_low  = [0.0] * len(self.underliers)
        self.exit_high  = [0.0] * len(self.underliers)
        self.exit_low   = [0.0] * len(self.underliers)
        self.tick_base  = [0.0] * len(self.underliers)
    
    def initialize(self):
        self.load_state()       
        for idx, under in enumerate(self.underliers):
            inst = under[0]
            self.tick_base[idx] = self.agent.instruments[inst].tick_base
            df = self.agent.day_data[inst]		
            atr_str = self.data_func[0][0] + str(self.channels[idx][1])
            bb_str = self.data_func[1][0] + str(self.channels[idx][1])
            sb_str = self.data_func[2][0] + str(self.channels[idx][1])
            bs_str = self.data_func[1][0] + str(self.channels[idx][0])
            ss_str = self.data_func[2][0] + str(self.channels[idx][0])
            self.entry_high[idx] = df.ix[-1, bb_str]
            self.entry_low[idx]  = df.ix[-1, sb_str]
            self.exit_high[idx] = df.ix[-1, bs_str]
            self.exit_low[idx]  = df.ix[-1, ss_str]           
            if len(self.positions[idx]) == 0:
                self.curr_atr[idx] = df.ix[-1, atr_str]   

    def register_func_freq(self):
        for under, chan, dfreq in zip(self.underliers, self.channels, self.data_freq):
            for infunc in self.data_func:
                name  = infunc[0]
                sfunc = eval(infunc[1])
                rfunc = eval(infunc[2])
                fobj = BaseObject(name = name + str(chan[1]), sfunc = fcustom(sfunc, n = chan[1]), rfunc = fcustom(rfunc, n = chan[1]))
                self.agent.register_data_func(under[0], dfreq, fobj)				
                if name !='ATR':
                    fobj = BaseObject(name = name + str(chan[0]), sfunc = fcustom(sfunc, n = chan[0]), rfunc = fcustom(rfunc, n = chan[0]))
                    self.agent.register_data_func(under[0], dfreq, fobj)

    def register_bar_freq(self):
        for under, freq in zip(self.underliers, self.trading_freq):
            instID = under[0]
            self.agent.inst2strat[instID][self.name].append(freq)

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
