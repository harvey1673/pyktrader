'''
Created on 2014Äê10ÔÂ27ÈÕ

@author: Harvey
'''
#-*- coding:utf-8 -*-
import pandas as pd
import data_handler
import logging
import strategy as strat
from base import *
import tradeagent as agent
import datetime

class TestStrat(strat.Strategy):
    def __init__(self, name, instIDs, agent = None):
        strat.Strategy.__init__(name, instIDs, agent)
        
    def run_min(self, inst):
        df = self.agent.day_data[inst]
        if df['EMA_3'] > df['EMA_30']:
            pass
        pass
    
def test_main(name='test_trade'):
    name='test_trade'
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')

    prod_user = BaseObject( broker_id="8070", 
                                 investor_id="*", 
                                 passwd="*", 
                                 ports=["tcp://zjzx-md11.ctp.shcifco.com:41213"])
    prod_trader = BaseObject( broker_id="8070", 
                                   investor_id="750305", 
                                   passwd="801289", 
                                   ports= ["tcp://zjzx-front12.ctp.shcifco.com:41205", 
                                           "tcp://zjzx-front12.ctp.shcifco.com:41205",
                                           "tcp://zjzx-front13.ctp.shcifco.com:41205"])
    wkend_trader = BaseObject( broker_id="8070", 
                                   investor_id="750305", 
                                   passwd="801289", 
                                   ports= ["tcp://zjzx-front20.ctp.shcifco.com:41205"] )
    test_user = BaseObject( broker_id="8000", 
                                 investor_id="*", 
                                 passwd="*", 
                                 ports=["tcp://qqfz-md1.ctp.shcifco.com:32313"]
                                 )
    test_trader = BaseObject( broker_id="8000", 
                                 investor_id="24661668", 
                                 passwd ="121862", 
                                 ports  = ["tcp://qqfz-front1.ctp.shcifco.com:32305"])
    
    insts = ['IF1411','IF1412']
    trader_cfg = test_trader
    user_cfg = test_user
    agent_name = name
    tday = datetime.date(2014,10,27)
    strategies = []
    test_strat = TestStrat('TestStrat', insts)
    test_strat.daily_func = [] 
                #BaseObject(name = 'ATR_20', sfunc=fcustom(data_handler.ATR, n=20), rfunc=fcustom(data_handler.atr, n=20)), \
                #BaseObject(name = 'DONCH_L10', sfunc=fcustom(data_handler.DONCH_L, n=10), rfunc=fcustom(data_handler.donch_l, n=10)),\
                #BaseObject(name = 'DONCH_H10', sfunc=fcustom(data_handler.DONCH_H, n=10), rfunc=fcustom(data_handler.donch_h, n=10)),\
                #BaseObject(name = 'DONCH_L20', sfunc=fcustom(data_handler.DONCH_L, n=20), rfunc=fcustom(data_handler.donch_l, n=20)),\
                #BaseObject(name = 'DONCH_H20', sfunc=fcustom(data_handler.DONCH_H, n=20), rfunc=fcustom(data_handler.donch_h, n=10)),\
                #BaseObject(name = 'DONCH_L55', sfunc=fcustom(data_handler.DONCH_L, n=55), rfunc=fcustom(data_handler.donch_l, n=10)),\
                #BaseObject(name = 'DONCH_H55', sfunc=fcustom(data_handler.DONCH_H, n=55), rfunc=fcustom(data_handler.donch_h, n=55))
                #]    
    test_strat.min_func = {1:[BaseObject(name = 'EMA_3', sfunc=fcustom(data_handler.EMA, n=3), rfunc=fcustom(data_handler.ema, n=3)),
                              BaseObject(name = 'EMA_30', sfunc=fcustom(data_handler.EMA, n=30), rfunc=fcustom(data_handler.ema, n=30))]
                           }
    strategies.append(test_strat)
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':0, \
                 'min_data_days':3 }
    myagent = agent.create_agent(agent_name, user_cfg, trader_cfg, insts, strat_cfg)
    try:
        myagent.resume()

# position/trade test        
        myagent.positions['IF1412'].pos_tday.long  = 0
        myagent.positions['IF1412'].pos_tday.short = 0
        myagent.positions['IF1411'].pos_tday.long  = 0
        myagent.positions['IF1411'].pos_tday.short = 0
        
        #myagent.positions['IF1409'].re_calc()
        #myagent.positions['IF1412'].re_calc()        
        
        valid_time = myagent.tick_id + 10000
        etrade =  order.ETrade( ['IF1412','IF1411'], [-1, 1], [ApiStruct.OPT_AnyPrice, ApiStruct.OPT_AnyPrice], -4, [0, 0], valid_time, test_strat.name, myagent.name)
        myagent.submit_trade(etrade)
        myagent.process_trade_list() 
        
        #myagent.tick_id = valid_time - 10
        #for o in myagent.positions['ag1506'].orders:
        #    o.on_trade(2000,o.volume,141558400)
            #o.on_trade(2010,1,141558500)
        #myagent.process_trade_list() 
        myagent.positions['IF1411'].re_calc()
        myagent.positions['IF1412'].re_calc()
        #orders = [iorder for iorder in myagent.positions['ag1412'].orders]
        #myagent.tick_id = valid_time + 10
        #myagent.process_trade_list()
        #for o in orders: 
        #    o.on_cancel()
        myagent.process_trade_list()
        print myagent.etrades

# order test
#         iorder = order.Order(myagent.positions['ag1412'], 
#                              4100, 1, myagent.tick_id, 
#                              ApiStruct.OF_Open, 
#                              ApiStruct.D_Buy, 
#                              ApiStruct.OPT_LimitPrice, {} )
#         myagent.send_order(iorder)
#         myagent.ref2order[iorder.order_ref] = iorder
#         myagent.cancel_order(iorder)
#         print iorder.status        
        
#        while 1: time.sleep(1)
    except KeyboardInterrupt:
        myagent.mdapis = [] 
        myagent.trader = None    

if __name__=="__main__":
    test_main()
