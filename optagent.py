#-*- coding:utf-8 -*-
'''
optstrat.py
Created on Feb 03, 2015
@author: Harvey
'''
import time
import agent
import fut_api
import lts_api
import ctp_emulator as emulator
import logging
import optstrat
import order
from misc import *
from base import *

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
    opt_strat = optstrat.OptionStrategy(name, 
                                    ['IF1502', 'IF1503'], 
                                    [datetime.datetime(2015, 2, 25, 15, 0, 0), datetime.datetime(2015,3,20,15,0,0)],
                                    [[3400, 3450, 3500, 3550, 3600, 3650]]*2)
    strategies = [opt_strat]
    all_insts = opt_strat.instIDs
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':2, \
                 'min_data_days':2 }
    #myagent, my_trader = emulator.create_agent_with_mocktrader(agent_name, all_insts, strat_cfg, tday)
    myagent = fut_api.create_agent(agent_name, user_cfg, trader_cfg, all_insts, strat_cfg, tday)
    #fut_api.make_user(myagent,user_cfg)
    myagent.resume()
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        myagent.mdapis = [] 
        myagent.trader = None    


if __name__=="__main__":
    test_main(datetime.date(2015,2,25), 'test_trade')