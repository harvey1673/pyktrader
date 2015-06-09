#-*- coding:utf-8 -*-
import instrument
import tradeagent as agent
import strategy

def get_option_map(underliers, strikes):
    opt_map = {}
    for under, ks in zip(underliers, strikes):
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
    
class OptionTestStrat(strategy.Strategy):
    def __init__(self, future_conts, strikes):
        self.option_map = get_option_map(future_conts, strikes)
        underliers = []
        volumes = []
        trade_units = []
        for fut, strike_list in zip(future_conts, strikes):
            for strike in strikes:
                call_key = (fut, 'C', strike)
                put_key  = (fut, 'P', strike)
                underliers.append([call_key, put_key, fut])
                volumes.append([1, -1, -1])
                trade_units.append(1)
            
        