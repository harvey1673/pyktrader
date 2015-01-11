#-*- coding:utf-8 -*-
import time
#import agent
import fut_api
#import strategy
import ctp_emulator as emulator
import logging
#import data_handler
import strategy
import strat_dual_thrust as strat_dt
import strat_turtle
#import order
from misc import *
from base import *

class TestStrat(strategy.Strategy):
    def run_min(self, instID):
        pass
    
def test_main(tday, name='test_trade'):
    '''
    import agent
    trader,myagent = agent.trade_test_main()
    #开仓
    
    ##释放连接
    trader.RegisterSpi(None)
    '''
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    #trader_cfg = TEST_TRADER
    user_cfg = PROD_USER
    agent_name = name
    insts_dt = ['m1505', 'RM505', 'y1505', 'p1505', 'a1505', 'l1505', 'pp1505', 'j1505', 'jm1505', 'i1505', 'rb1505', \
                'CF505', 'ME505', 'TA505', 'SR505', 'cu1503', 'al1503', 'zn1503', 'ag1506', 'au1506', 'v1505', 'TC505', \
                'c1505', 'IF1503']
    units_dt = [[1]]*len(insts_dt)
    under_dt = [[inst] for inst in insts_dt]
    insts_turtle = ['m1505', 'RM505', 'y1505', 'p1505', 'a1505', 'l1505', 'pp1505', 'j1505', 'jm1505', 'i1505', 'rb1505', \
                'CF505', 'ME505', 'TA505', 'SR505', 'cu1503', 'al1503', 'zn1503', 'ag1506', 'au1506', 'v1505', 'TC505', \
                'c1505', 'IF1503']
    under_turtle = [[inst] for inst in insts_turtle]
    units_turtle = [[1]]*len(insts_turtle)
    dt_strat = strat_dt.DTTrader('DT_test', under_dt, trade_unit = units_dt, agent = None)
    turtle_strat = strat_turtle.TurtleTrader('Turtle_test', under_turtle, trade_unit = [[1]]*len(under_turtle), agent=None )
    strategies = [dt_strat, turtle_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':22, \
                 'min_data_days':2 }
    #myagent = create_agent(agent_name, user_cfg, trader_cfg, insts, strat_cfg)
    all_insts = list(set(insts_turtle).union(set(insts_dt)))
    myagent, my_trader = emulator.create_agent_with_mocktrader(agent_name, all_insts, strat_cfg, tday)
    fut_api.make_user(myagent,user_cfg)
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
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        myagent.mdapis = [] 
        myagent.trader = None    

if __name__=="__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        name= 'test_trade'
    else:
        name= args[1]
    if len(args) < 1:
        tday = datetime.date.today()
    else:
        tday = datetime.datetime.strptime(args[0], '%Y%m%d').date()
    test_main(tday, name)
    
