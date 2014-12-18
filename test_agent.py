#-*- coding:utf-8 -*-
import agent
import fut_api
import strategy
import ctp_emulator
import logging
import data_handler
import strategy
import order
from misc import *
from base import *

class TestStrat(strategy.Strategy):
    def run_min(self, instID):
        pass
    
def test_main(name='test_trade'):
    '''
    import agent
    trader,myagent = agent.trade_test_main()
    #开仓
    
    ##释放连接
    trader.RegisterSpi(None)
    '''
    name='test_trade'
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    insts = ['cu1501','cu1502']
    trader_cfg = TEST_TRADER
    user_cfg = PROD_USER
    agent_name = name
    tday = datetime.date(2014,12,2)
    data_func = [ 
            ('d', BaseObject(name = 'ATR_20', sfunc=fcustom(data_handler.ATR, n=20), rfunc=fcustom(data_handler.atr, n=20))), \
            ('d', BaseObject(name = 'DONCH_L10', sfunc=fcustom(data_handler.DONCH_L, n=10), rfunc=fcustom(data_handler.donch_l, n=10))),\
            ('d', BaseObject(name = 'DONCH_H10', sfunc=fcustom(data_handler.DONCH_H, n=10), rfunc=fcustom(data_handler.donch_h, n=10))),\
            ('d', BaseObject(name = 'DONCH_L20', sfunc=fcustom(data_handler.DONCH_L, n=20), rfunc=fcustom(data_handler.donch_l, n=20))),\
            ('d', BaseObject(name = 'DONCH_H20', sfunc=fcustom(data_handler.DONCH_H, n=20), rfunc=fcustom(data_handler.donch_h, n=20))),\
            ('1m',BaseObject(name = 'EMA_3',     sfunc=fcustom(data_handler.EMA, n=3),      rfunc=fcustom(data_handler.ema, n=3))), \
            ('1m',BaseObject(name = 'EMA_30',    sfunc=fcustom(data_handler.EMA, n=30),     rfunc=fcustom(data_handler.ema, n=30))) \
        ]
    strategies = []
	insts = ['m1505', 'RM505', 'y1505', 'p1505', 'a1505', 'l1505', 'pp1505', 'j1505', 'jm1505', 'i1505', 'rb1505']
	
    test_strat = strategy.Strategy('TurtleTrader1', [insts], None, data_func, [[1,-1]])
    strategies.append(test_strat)
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':25, \
                 'min_data_days':2 }
    #myagent = create_agent(agent_name, user_cfg, trader_cfg, insts, strat_cfg)
    myagent, my_trader = ctp_emulator.create_agent_with_mocktrader(agent_name, insts, strat_cfg, tday)
    fut_api.make_user(myagent,user_cfg)
    try:
        myagent.resume()

# position/trade test        
        myagent.positions['cu1501'].pos_yday.long  = 2
        myagent.positions['cu1501'].pos_yday.short = 2
        myagent.positions['cu1502'].pos_yday.long  = 0
        myagent.positions['cu1502'].pos_yday.short = 0
        
        myagent.positions['cu1501'].re_calc()
        myagent.positions['cu1502'].re_calc()        
        
        valid_time = myagent.tick_id + 10000
        etrade =  order.ETrade( ['cu1501','cu1502'], [1, -1], [OPT_LIMIT_ORDER, OPT_LIMIT_ORDER], 500, [0, 0], valid_time, test_strat.name, myagent.name)
        myagent.submit_trade(etrade)
        myagent.process_trade_list() 
        
        #myagent.tick_id = valid_time - 10
        #for o in myagent.positions['cu1501'].orders:
            #o.on_trade(2000,o.volume,141558400)
            #o.on_trade(2010,1,141558500)
        myagent.process_trade_list() 
        myagent.positions['cu1501'].re_calc()
        myagent.positions['cu1502'].re_calc()
        #orders = [iorder for iorder in myagent.positions['ag1412'].orders]
        #myagent.tick_id = valid_time + 10
        #myagent.process_trade_list()
        #for o in orders: 
        #    o.on_cancel()
        myagent.process_trade_list()
        print myagent.etrades

    except KeyboardInterrupt:
        myagent.mdapis = [] 
        myagent.trader = None    

if __name__=="__main__":
    test_main()
    
