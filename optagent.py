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
import strategy
import strat_dual_thrust as strat_dt
import order
from misc import *
from base import *

def test_main(tday, name='option_test'):
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
    opt_strat = optstrat.IndexFutOptStrat(name, 
                                    ['IF1504', 'IF1506'], 
                                    [datetime.datetime(2015, 4, 17, 15, 0, 0), datetime.datetime(2015,6,19,15,0,0)],
                                    [[3700, 3750, 3800, 3850, 3900, 3950, 4000, 4050]]*2)

    insts_dt = ['IF1504']
    units_dt = [1]*len(insts_dt)
    under_dt = [[inst] for inst in insts_dt]
    vols_dt = [[1]]*len(insts_dt)
    lookbacks_dt = [0]*len(insts_dt)
    
    insts_daily = ['IF1504']
    under_daily = [[inst] for inst in insts_daily]
    vols_daily = [[1]]*len(insts_daily)
    units_daily = [1]*len(insts_daily)
    lookbacks_daily = [0]*len(insts_daily)

    dt_strat = strat_dt.DTTrader('DT_test', under_dt, vols_dt, trade_unit = units_dt, lookbacks = lookbacks_dt, agent = None, daily_close = False, email_notify = [])
    dt_daily = strat_dt.DTTrader('DT_Daily', under_daily, vols_daily, trade_unit = units_daily, lookbacks = lookbacks_daily, agent = None, daily_close = True, email_notify = ['harvey_wwu@hotmail.com'])
    
    strategies = [dt_strat, dt_daily, opt_strat]
    all_insts = opt_strat.instIDs
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':3, \
                 'min_data_days':1 }
    #myagent, my_trader = emulator.create_agent_with_mocktrader(agent_name, all_insts, strat_cfg, tday)
    myagent = fut_api.create_agent(agent_name, user_cfg, trader_cfg, all_insts, strat_cfg, tday)
    #fut_api.make_user(myagent,user_cfg)
    myagent.resume()
#     myagent.tick_id = 2100000
#     myagent.instruments['IF1503'].day_finalized = False
#     ctick = agent.TickData(instID='IF1503', timestamp=datetime.datetime(2015,3,10,15,0,0), 
#                            openInterest=10000, 
#                            volume=10, price=3520, 
#                            high=3570, low=3500, 
#                            bidPrice1=3519.6, bidVol1=3, 
#                            askPrice1=3520.4, askVol1=2,
#                            up_limit = 3700, down_limit = 3300)
#     myagent.RtnTick(ctick)
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        myagent.mdapis = [] 
        myagent.trader = None    


if __name__=="__main__":
    test_main(datetime.date(2015,3,23), 'option_test')