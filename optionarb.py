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
                key = (str(under), otype, strike)
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
        for fut, strike_list in zip(future_conts, strikes):
            slen = len(strike_list)
            for i, strike in enumerate(strike_list):
                call_key = (fut, 'C', strike)
                put_key  = (fut, 'P', strike)
                underliers.append([self.option_map[call_key], self.option_map[put_key], fut])
                volumes.append([3, -3, -1])
                trade_units.append(1)
                self.cp_parity[(fut, strike)] = {'idx':idx, 'lower': 0, 'upper':0 }
                idx += 1
                if (i < slen - 1):
                    next_call = (fut, 'C', strike_list[i+1])
                    underliers.append([self.option_map[call_key], self.option_map[next_call]])
                    volumes.append([1, -1])
                    trade_units.append(1)
                    self.call_spread[(fut, strike)] = {'idx':idx, 'lower':0, 'upper': strike_list[i+1] - strike }
                    idx += 1
                    next_put = (fut, 'P', strike_list[i+1])
                    underliers.append([self.option_map[next_put], self.option_map[put_key]])
                    volumes.append([1, -1])
                    trade_units.append(1)
                    self.put_spread[(fut, strike)] = {'idx':idx, 'lower':0, 'upper': strike_list[i+1] - strike  }
                    idx += 1
                    if i > 0:
                        prev_call = (fut, 'C', strike_list[i-1])
                        underliers.append([self.option_map[prev_call], self.option_map[call_key], self.option_map[next_call]])
                        volumes.append([1, -2, 1])
                        trade_units.append(1)
                        self.call_bfly[(fut, strike)] = {'idx':idx, 'lower':0, 'upper': None}
                        idx += 1
                        prev_put = (fut, 'P', strike_list[i-1])
                        underliers.append([self.option_map[prev_put], self.option_map[put_key], self.option_map[next_put]])
                        volumes.append([1, -2, 1])
                        trade_units.append(1)
                        self.put_bfly[(fut, strike)] = {'idx':idx, 'lower':0, 'upper': None}
                        idx += 1
        strategy.Strategy.__init__(self, name, underliers, volumes, trade_units, agent, rmail_notify = email_notify)
        self.profit_ratio = 0
        self.buy_prices = [0.0] * len(underliers)
        self.sell_prices = [0.0] * len(underliers)
        self.is_initialized = False
    
    def initialize(self):
        self.load_state()
        pass 
        
    def load_local_variables(self, row):
        pass
    
    def save_local_variables(self, file_writer):
        pass
    
    def setup_trading(self):
        pass

    def calc_curr_price(self, idx):
        conv_f = [ self.agent.instruments[inst].multiple for inst in self.underliers[idx]]
        ask1 = [ self.agent.instruments[inst].ask_price1 for inst in self.underliers[idx]]
        bid1 = [ self.agent.instruments[inst].bid_price1 for inst in self.underliers[idx]]
        volumes = self.volumes[idx]
        self.buy_prices[idx] = sum([p*v*cf for p, v, cf in zip(bid1, volumes, conv_f) if v > 0])
        self.buy_prices[idx] += sum([p*v*cf for p, v, cf in zip(ask1, volumes, conv_f) if v < 0])
        self.buy_prices[idx] = self.buy_prices[idx]/conv_f[-1]
        self.sell_prices[idx] = sum([p*v*cf for p, v, cf in zip(bid1, volumes, conv_f) if v < 0])
        self.sell_prices[idx] += sum([p*v*cf for p, v, cf in zip(ask1, volumes, conv_f) if v > 0])
        self.sell_prices[idx] = self.sell_prices[idx]/conv_f[-1]
        return
    
    def tick_run(self, ctick):
        instID = ctick.instID
        inst = self.agent.instruments[instID]
        if (inst.ptype == instrument.ProductType.Future):
            for i, fut in enumerate(self.future_conts):
                if fut == inst.name:
                    strike_list = self.strikes[i]
                    for strike in strike_list:
                        key = (instID, strike)
                        idx = self.cp_parity[key]['idx']
                        if len(self.submitted_pos[idx]) == 0:
                            self.calc_curr_price(idx)

                    break
                
            
        if self.update_positions(idx):
            self.save_state()
        self.run_tick(idx, ctick)
        return                
            
        
