#-*- coding:utf-8 -*-
import agent
import fut_api
import strategy
import ctp_emulator as emulator
import logging
import data_handler
import strategy
import strat_dual_thrust as strat_dt
import strat_turtle
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
    trader_cfg = TEST_TRADER
    user_cfg = PROD_USER
    agent_name = name
    tday = datetime.date(2014,12,23)
    insts_dt = ['m1505', 'RM505', 'y1505', 'p1505', 'a1505', 'l1505', 'pp1505', 'j1505', 'jm1505', 'i1505', 'rb1505']
    under_dt = [[inst] for inst in insts_dt]
    insts_turtle = ['m1505', 'RM505', 'y1505', 'p1505', 'a1505', 'l1505', 'pp1505', 'j1505', 'jm1505', 'i1505', 'rb1505']
    under_turtle = [[inst] for inst in insts_turtle]
    dt_strat = strat_dt.DTTrader('DT_test', under_dt, agent = None)
    turtle_strat = strat_turtle.TurtleTrader('Turtle_test', under_turtle, agent=None, trade_unit = [[1]]*len(under_turtle) )
    strategies = [dt_strat, turtle_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':25, \
                 'min_data_days':2 }
    #myagent = create_agent(agent_name, user_cfg, trader_cfg, insts, strat_cfg)
    all_insts = list(set(insts_turtle)+set(insts_dt))
    myagent, my_trader = emulator.create_agent_with_mocktrader(agent_name, all_insts, strat_cfg, tday)
    fut_api.make_user(myagent,user_cfg)
    try:
        myagent.resume()

# position/trade test        
        #=======================================================================
        # myagent.positions['cu1501'].pos_yday.long  = 2
        # myagent.positions['cu1501'].pos_yday.short = 2
        # myagent.positions['cu1502'].pos_yday.long  = 0
        # myagent.positions['cu1502'].pos_yday.short = 0
        # 
        # myagent.positions['cu1501'].re_calc()
        # myagent.positions['cu1502'].re_calc()        
        # 
        # valid_time = myagent.tick_id + 10000
        # etrade =  order.ETrade( ['cu1501','cu1502'], [1, -1], [OPT_LIMIT_ORDER, OPT_LIMIT_ORDER], 500, [0, 0], valid_time, test_strat.name, myagent.name)
        # myagent.submit_trade(etrade)
        # myagent.process_trade_list() 
        # 
        # #myagent.tick_id = valid_time - 10
        # #for o in myagent.positions['cu1501'].orders:
        #     #o.on_trade(2000,o.volume,141558400)
        #     #o.on_trade(2010,1,141558500)
        # myagent.process_trade_list() 
        # myagent.positions['cu1501'].re_calc()
        # myagent.positions['cu1502'].re_calc()
        # #orders = [iorder for iorder in myagent.positions['ag1412'].orders]
        # #myagent.tick_id = valid_time + 10
        # #myagent.process_trade_list()
        # #for o in orders: 
        # #    o.on_cancel()
        # myagent.process_trade_list()
        # print myagent.etrades
        #=======================================================================

    except KeyboardInterrupt:
        myagent.mdapis = [] 
        myagent.trader = None    

if __name__=="__main__":
    test_main()
    
