#-*- coding:utf-8 -*-
import instrument
import tradeagent as agent
import strategy

def get_option_map(underliers, cont_mths, strikes):
    opt_map = {}
    for under, cmth, ks in zip(underliers, cont_mths, strikes):
        for otype in ['C', 'P']:
            for strike in ks:
                #cont_mth = int(under[-4:]) + 200000
                key = (str(under), cmth, otype, strike)
                instID = under
                if instID[:2] == "IF":
                    instID = instID.replace('IF', 'IO')
                instID = instID + '-' + otype + '-' + str(strike)
                opt_map[key] = instID
    return opt_map
    
class OptionArbStrat(strategy.Strategy):
    def __init__(self, name, future_conts, cont_mths, strikes, agent = None, email_notify = []):
        self.option_map = get_option_map(future_conts, cont_mths, strikes)
        underliers = []
        volumes = []
        trade_units = []
        self.future_conts = future_conts
        self.cont_mths = cont_mths
        self.strikes = strikes
        self.cp_parity = {}
        self.call_spread = {}
        self.put_spread = {}
        self.call_bfly = {}
        self.put_bfly = {}
        idx = 0
        for fut, cmth, strike_list in zip(future_conts, cont_mths, strikes):
            slen = len(strike_list)
            for i, strike in enumerate(strike_list):
                call_key = (fut, cmth, 'C', strike)
                put_key  = (fut, cmth, 'P', strike)
                underliers.append([self.option_map[call_key], self.option_map[put_key], fut])
                volumes.append([3, -3, -1])
                trade_units.append(1)
                self.cp_parity[(fut, strike)] = {'idx':idx }
                idx += 1
                if (i < slen - 1):
                    next_call = (fut, cmth, 'C', strike_list[i+1])
                    underliers.append([self.option_map[call_key], self.option_map[next_call]])
                    volumes.append([1, -1])
                    trade_units.append(1)
                    self.call_spread[(cmth, strike)] = {'idx':idx }
                    idx += 1
                    next_put = (fut, 'P', strike_list[i+1])
                    underliers.append([self.option_map[next_put], self.option_map[put_key]])
                    volumes.append([1, -1])
                    trade_units.append(1)
                    self.put_spread[(cmth, strike)] = {'idx':idx }
                    idx += 1
                    if i > 0:
                        prev_call = (fut, cmth, 'C', strike_list[i-1])
                        underliers.append([self.option_map[prev_call], self.option_map[call_key], self.option_map[next_call]])
                        volumes.append([1, -2, 1])
                        trade_units.append(1)
                        self.call_bfly[(cmth, strike)] = {'idx':idx }
                        idx += 1
                        prev_put = (fut, cmth, 'P', strike_list[i-1])
                        underliers.append([self.option_map[prev_put], self.option_map[put_key], self.option_map[next_put]])
                        volumes.append([1, -2, 1])
                        trade_units.append(1)
                        self.put_bfly[(cmth, strike)] = {'idx':idx }
                        idx += 1
        strategy.Strategy.__init__(self, name, underliers, volumes, trade_units, agent, rmail_notify = email_notify)
        self.profit_ratio = 0
    
    def initialize(self):
        self.load_state()
        pass 
        
    def load_local_variables(self, row):
        pass
    
    def save_local_variables(self, file_writer):
        pass
    
    def tick_run(self, ctick):
        instID = ctick.instID
        inst = self.agent.instruments[instID]
        if (inst.ptype == instrument.ProductType.Future) or (inst.ptype == instrument.ProductType.Stock):
            pass
        if self.update_positions(idx):
            self.save_state()
        self.run_tick(idx, ctick)
        return                
            
        
