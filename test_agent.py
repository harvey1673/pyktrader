#-*- coding:utf-8 -*-
import time
import agent
import fut_api
import lts_api
#import strategy
import ctp_emulator as emulator
import logging
#import data_handler
import strategy
import strat_dual_thrust as strat_dt
import strat_turtle
import order
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
    trader_cfg = TEST_TRADER
    user_cfg = TEST_USER
    agent_name = name
    insts_dt = ['IF1503']
    units_dt = [[1]]*len(insts_dt)
    under_dt = [[inst] for inst in insts_dt]
    lookbacks_dt = [0]*len(insts_dt)
    insts_turtle = ['IF1503']
    under_turtle = [[inst] for inst in insts_turtle]
    units_turtle = [[1]]*len(insts_turtle)
    
    insts_daily = ['IF1502']
    under_daily = [[inst] for inst in insts_daily]
    units_daily = [[1]]*len(insts_daily)
    lookbacks_daily = [0]*len(insts_daily)

    dt_strat = strat_dt.DTTrader('DT_test', under_dt, trade_unit = units_dt, lookbacks = lookbacks_dt, agent = None, daily_close = True, email_notify = [])
    dt_daily = strat_dt.DTTrader('DT_Daily', under_daily, trade_unit = units_daily, lookbacks = lookbacks_daily, agent = None, daily_close = True, email_notify = ['harvey_wwu@hotmail.com'])
    turtle_strat = strat_turtle.TurtleTrader('Turtle_test', under_turtle, trade_unit = units_turtle, agent=None, email_notify = ['harvey_wwu@hotmail.com'] )
    strategies = [dt_strat, dt_daily, turtle_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':22, \
                 'min_data_days':2 }
    all_insts = list(set(insts_turtle).union(set(insts_dt)).union(set(insts_daily)))
    #myagent, my_trader = emulator.create_agent_with_mocktrader(agent_name, all_insts, strat_cfg, tday)
    myagent = fut_api.create_agent(agent_name, user_cfg, trader_cfg, all_insts, strat_cfg, tday)
    #fut_api.make_user(myagent,user_cfg)
    myagent.resume()
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        myagent.mdapis = [] 
        myagent.trader = None    

def prod_test(tday, name='prod_test'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    #trader_cfg = TEST_TRADER
    user_cfg = PROD_USER
    agent_name = name
    ins_setup = {'m1505':(1, 0.7, 8),
                'RM505':(0, 0.5, 10),
                'rb1505':(0,0.5, 10),
                'y1505':(0, 0.5, 4), 
                'l1505':(0, 0.5, 4),
                'pp1505':(0,0.5,4),
                'ru1505':(2, 0.5, 1),
                'ag1506':(0, 0.7, 6),
                'au1506':(0, 0.5, 1),
                'j1505':(0, 0.5, 2),
                'al1504':(0, 0.9, 5)}
    units_dt = [[ins_setup[inst][2]] for inst in ins_setup]
    under_dt = [[inst] for inst in ins_setup]
    ratios = [(ins_setup[inst][1], ins_setup[inst][1]) for inst in ins_setup]
    lookbacks = [ins_setup[inst][0] for inst in ins_setup]

    dt_strat = strat_dt.DTTrader('ProdDT', under_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks, 
                                 agent = None, daily_close = False, 
                                 email_notify = ['harvey_wwu@hotmail.com'])
    strategies = [dt_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':3, \
                 'min_data_days':1 }
    #myagent = create_agent(agent_name, user_cfg, trader_cfg, insts, strat_cfg)
    all_insts = ins_setup.keys()
    myagent, my_trader = emulator.create_agent_with_mocktrader(agent_name, all_insts, strat_cfg, tday)
    fut_api.make_user(myagent,user_cfg)
    myagent.resume()
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        myagent.mdapis = [] 
        myagent.trader = None    

def lts_save(tday):
    logging.basicConfig(filename="save_lts_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    app_name = 'lts_save_agent'
    save_insts = [ "510180", "510050", "11000011", "11000016", "11000021", "11000026", "11000031", "11000036"]
    my_agent = agent.SaveAgent(name = app_name, trader = None, cuser = None, instruments=save_insts, daily_data_days=0, min_data_days=0, tday = tday)
    lts_api.make_user(my_agent, LTS_SO_USER, save_insts)
    try:
        while 1:
            time.sleep(1)
            
    except KeyboardInterrupt:
        my_agent.mdapis = []; my_agent.trader = None
 
def lts_test(tday, name='lts_test'):
    logging.basicConfig(filename="lts_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = LTS_SO_TRADER
    user_cfg = LTS_SO_USER
    agent_name = name
    insts = [ "510180", "510050", "11000011", "11000016", "11000021", "11000026", "11000031", "11000036"]
    strat_cfg = {'strategies': [], \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':0, \
                 'min_data_days':0 }
    myagent = lts_api.create_agent(agent_name, user_cfg, trader_cfg, insts, strat_cfg, tday)
    try:
        myagent.resume()

# position/trade test        
        myagent.positions['510050'].pos_tday.long  = 2
        myagent.positions['510050'].pos_tday.short = 2
        #myagent.positions['cu1502'].pos_yday.long  = 0
        #myagent.positions['cu1502'].pos_yday.short = 0
        
        myagent.positions['510050'].re_calc()
        myagent.positions['510050'].re_calc()        
        
        valid_time = myagent.tick_id + 10000
        etrade =  order.ETrade( ['510050'], [1], [OPT_LIMIT_ORDER], 2.50, [0], valid_time, 'test', myagent.name)
        myagent.submit_trade(etrade)
        myagent.process_trade_list() 
        
        #myagent.tick_id = valid_time - 10
        #for o in myagent.positions['cu1501'].orders:
            #o.on_trade(2000,o.volume,141558400)
            #o.on_trade(2010,1,141558500)
        myagent.process_trade_list() 
        myagent.positions['510050'].re_calc()
        myagent.positions['510050'].re_calc()
        
        #while 1: time.sleep(1)
    except KeyboardInterrupt:
        myagent.mdapis = []; myagent.trader = None

        
if __name__=="__main__":
    lts_test(datetime.date(2015,2,4), 'lts_test')
#     args = sys.argv[1:]
#     if len(args) < 2:
#         name= 'test_trade'
#     else:
#         name= args[1]
#     if len(args) < 1:
#         tday = datetime.date.today()
#     else:
#         tday = datetime.datetime.strptime(args[0], '%Y%m%d').date()
#     test_main(tday, name)
    
