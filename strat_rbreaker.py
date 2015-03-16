#-*- coding:utf-8 -*-
#from base import *
from misc import *
from strategy import *
 
class RBreakerTrader(Strategy):
    def __init__(self, name, underliers, volumes, agent = None, trade_unit = [], ratios = [], min_rng = [], trail_loss = 0.0, freq = 1, email_notify = None):
        Strategy.__init__(self, name, underliers, volumes, trade_unit, agent, email_notify)
        num_assets = len(underliers)
        self.ratios = [[0.4, 0.1, 0.1] for _ in underliers]
        if len(ratios) > 1:
            self.ratio = ratios
        elif len(ratios) == 1: 
            self.ratio = ratios*num_assets
        self.min_rng = [1.0]*num_assets
        if len(min_rng) == num_assets:
            self.min_rng = min_rng
        elif len(min_rng) == 1: 
            self.min_rng = min_rng * num_assets
        self.ssetup = [0.0]*num_assets
        self.bsetup = [0.0]*num_assets
        self.senter = [0.0]*num_assets
        self.benter = [0.0]*num_assets
        self.sbreak = [0.0]*num_assets
        self.bbreak = [0.0]*num_assets
        self.start_min_id = [1503] * num_assets
        self.daily_close_buffer = 5
        self.freq = freq
        self.trail_loss = trail_loss
        self.entry_limit = 2

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
            min_id = self.agent.instruments[inst].last_tick_id/1000
            min_id = int(min_id/100)*60 + min_id % 100 - self.daily_close_buffer
            self.last_min_id[idx] = int(min_id/60)*100 + min_id % 60   
            min_id = self.agent.instruments[inst].start_tick_id/1000
            min_id = int(min_id/100)*60 + min_id % 100 + self.daily_close_buffer
            self.start_min_id[idx] = int(min_id/60)*100 + min_id % 60   
        self.save_state()
        return         

    def save_local_variables(self, file_writer):
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            row = ['NumTrade', str(inst), self.num_entries[idx], self.num_exits[idx]]
            file_writer.writerow(row)
        for idx, underlier in enumerate(self.underliers):
            inst = underlier[0]
            row = ['Signals', str(inst), self.bbreak[idx], self.ssetup[idx], self.senter[idx], self.benter[idx], self.bsetup[idx], self.sbreak[idx]]
            file_writer.writerow(row)
        return
    
    def load_local_variables(self, row):
        if row[0] == 'NumTrade':
            inst = str(row[1])
            idx = self.get_index([inst])
            if idx >=0:
                self.num_entries[idx] = int(row[2])
                self.num_exits[idx] =int(row[3]) 
        return
        
    def run_min(self, inst):
        min_id = self.agent.cur_min[inst]['min_id']
        if min_id <= 300 or min_id >= 2115:
            return
        idx = self.get_index([inst])
        if idx < 0:
            self.logger.warning('the inst=%s is not in this strategy = %s' % (inst, self.name))
            return
        save_status = self.update_positions(idx)
        num_pos = len(self.positions[idx])
        curr_pos = None
        curr_min = int(min_id/100)*60+ min_id % 100 + 1        
        if (curr_min % self.freq != 0) or (min_id < self.start_min_id[idx]):
            if save_status:
                self.save_state()
            return
        inst_obj = self.agent.instruments[inst]
        #print inst, len(self.positions[idx]), len(self.submitted_pos[idx]), self.agent.cur_min[inst]['min_id'], self.agent.tick_id, self.last_min_id[idx]
        tick_base = inst_obj.tick_base
        dhigh = self.agent.cur_day[inst]['high']
        dlow  = self.agent.cur_day[inst]['low']
        curr_price = (inst_obj.ask_price1 + inst_obj.bid_price1)/2.0                
        if num_pos > 1:
            if len(self.submitted_pos[idx]) == 0:
                self.logger.warning('something wrong with position management - submitted trade is empty but trade position is more than 1')
            elif (min_id >= self.last_min_id[idx]):
                for etrade in self.submitted_pos[idx]:
                    self.speedup(etrade)                
            return
        elif num_pos == 1:
            curr_pos = self.positions[idx][0]
            if self.trail_loss > 0:
                if curr_pos.trail_loss(curr_price, curr_pos.entry_price * self.trail_loss):
                    msg = 'R-Breaker to close position after hitting trail loss for inst = %s, direction=%s, volume=%s, current min_id = %s, current price = %s, exit_target = %s' \
                                    % (inst, buysell, self.trade_unit[idx], min_id, curr_price, curr_pos.exit_target)
                    self.close_tradepos(idx, curr_pos, curr_price - buysell * self.num_tick * tick_base)
                    self.status_notifier(msg)
                    self.save_state()
                    return 
        #print inst, curr_min, curr_price, self.bbreak[idx], self.ssetup[idx], self.senter[idx], self.benter[idx], self.bsetup[idx],self.sbreak[idx]
        buysell = 0 if curr_pos == None else curr_pos.direction
        if ((min_id >= self.last_min_id[idx]) or self.check_price_limit(inst, curr_price, 5)): 
            if (buysell != 0) and (len(self.submitted_pos[idx]) == 0):
                msg = 'R-Breaker to close position before EOD or hitting price limit for inst = %s, direction=%s, volume=%s, current min_id = %s, current price = %s' \
                                    % (inst, buysell, self.trade_unit[idx], min_id, curr_price)
                self.close_tradepos(idx, curr_pos, curr_price - buysell * self.num_tick * tick_base)
                self.save_state()
                self.status_notifier(msg)
            elif (len(self.submitted_pos[idx]) > 0):
                for etrade in self.submitted_pos[idx]:
                    self.speedup(etrade)
            return 
        if len(self.submitted_pos[idx]) > 0:
            return         
        if ((curr_price >= self.bbreak[idx]) and (buysell <=0)) or ((curr_price <= self.sbreak[idx]) and (buysell >= 0)):
            if curr_pos != None:
                self.close_tradepos(idx, curr_pos, curr_price - buysell * self.num_tick * tick_base)
                save_status = True
                msg = 'R-Breaker to close position for inst = %s, direction=%s, volume=%s, current min_id = %s' \
                                    % (inst, buysell, self.trade_unit[idx], min_id)
                self.status_notifier(msg)     
            if self.num_entries[idx] < self.entry_limit:   
                if  (curr_price >= self.bbreak[idx]):
                    buysell = 1
                else:
                    buysell = -1
                msg = 'R-Breaker to open position for inst = %s, bbreak=%s, sbreak=%s, curr_price= %s, direction=%s, volume=%s' \
                        % (inst, self.bbreak[idx], self.sbreak[idx], curr_price, buysell, self.trade_unit[idx])
                self.open_tradepos(idx, buysell, curr_price + buysell * self.num_tick * tick_base)
                save_status = True
                self.status_notifier(msg)
        elif ((dhigh< self.bbreak[idx]) and (dhigh >= self.ssetup[idx]) and (curr_price < self.senter[idx]) and (buysell >=0)) or \
                 ((dlow > self.sbreak[idx]) and (dlow  <= self.bsetup[idx]) and (curr_price > self.benter[idx]) and (buysell <=0)):
            if curr_pos != None:
                self.close_tradepos(idx, curr_pos, curr_price - buysell * self.num_tick * tick_base)
                save_status = True
                msg = 'R-Breaker to close position for inst = %s, direction=%s, volume=%s, current min_id = %s' \
                                    % (inst, buysell, self.trade_unit[idx], min_id)
                self.status_notifier(msg)
            if self.num_entries[idx] < self.entry_limit:
                if  (curr_price < self.senter[idx]):
                    buysell = -1
                else:
                    buysell = 1
                self.open_tradepos(idx, buysell, curr_price + buysell * self.num_tick * tick_base)
                save_status = True
                msg = 'R-Breaker to open position for inst = %s, open= %s, buy_trig=%s, sell_trig=%s, curr_price= %s, direction=%s, volume=%s' \
                                    % (inst, tday_open, buy_trig, sell_trig, curr_price, buysell, self.trade_unit[idx])
                self.status_notifier(msg)
        if save_status:
            self.save_state()
        return 
        
    def update_trade_unit(self):
        pass
