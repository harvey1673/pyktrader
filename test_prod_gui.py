#-*- coding:utf-8 -*-
import misc
import logging
import sys
import strat_dual_thrust as strat_dt
import strat_rbreaker as strat_rb
from agent_gui import *

def create_trader(trader_cfg, instruments, strat_cfg, agent_name, tday=datetime.date.today()):
    #logging.basicConfig(filename="ctp_trade.log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    #logging.info(u'broker_id=%s,investor_id=%s,passwd=%s' % (trader_cfg.broker_id,trader_cfg.investor_id,trader_cfg.passwd))
    strategies = strat_cfg['strategies']
    folder = strat_cfg['folder']
    daily_days = strat_cfg['daily_data_days']
    min_days = strat_cfg['min_data_days']
    myagent = Agent(agent_name, None, None, instruments, strategies, tday, folder, daily_days, min_days) 
    if trader_cfg == None:
		myagent, trader = emulator.create_agent_with_mocktrader(agent_name, instruments, strat_cfg, tday)
	else:
		myagent.trader = trader = TraderSpiDelegate(instruments=myagent.instruments, 
                             broker_id=trader_cfg.broker_id,
                             investor_id= trader_cfg.investor_id,
                             passwd= trader_cfg.passwd,
                             agent = myagent,
                       )
		trader.Create('trader')
		trader.SubscribePublicTopic(trader.ApiStruct.TERT_QUICK)
		trader.SubscribePrivateTopic(trader.ApiStruct.TERT_QUICK)
		for port in trader_cfg.ports:
			trader.RegisterFront(port)
		trader.Init()
    return trader, myagent
	
def prod_test(tday, name='prod_test'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = None
    user_cfg = PROD_USER
    agent_name = name
    ins_setup = {'IF1504': [[0.35, 0.07, 0.25], 1,  30],
                'ru1509':  [[0.35, 0.07, 0.25], 1,  120],
                'rb1510':  [[0.35, 0.07, 0.25], 10, 20],
                'RM509' :  [[0.35, 0.07, 0.25], 8,  20],
                'm1509' :  [[0.35, 0.07, 0.25], 8,  30],
                'ag1506': [[0.35, 0.07, 0.25], 8,  40],
                'y1509' : [[0.35, 0.07, 0.25], 8,  60]}
    insts = ins_setup.keys()
    units_rb = [ins_setup[inst][1] for inst in insts]
    under_rb = [[inst] for inst in insts]
    vol_rb = [[1] for inst in insts]
    ratios = [ins_setup[inst][0] for inst in insts]
    min_rng = [ins_setup[inst][2] for inst in insts]
    stop_loss = 0.0
    rb_strat = strat_rb.RBreakerTrader('RBreaker', under_rb, vol_rb, trade_unit = units_rb,
                                 ratios = ratios, min_rng = min_rng, trail_loss = stop_loss, freq = 1, 
                                 agent = None, email_notify = ['harvey_wwu@hotmail.com'])
	ins_setup = {'m1505':(0, 0.5, 8, False),
                'RM505':(0, 0.5, 10, False),
                'rb1505':(0,0.5, 10, False),
                'y1505':(0, 0.5, 4, False), 
                'l1505':(0, 0.5, 4, False),
                'pp1505':(0,0.5, 4, False),
                'ru1505':(0, 0.5, 1, False),
                'ag1506':(0, 0.5, 6, False),
                'au1506':(0, 0.5, 1, False),
                'j1505':(0, 0.5,  2, False),
                'al1505':(0, 0.5, 5, False),
                'IF1504':(0, 0.5, 1, True)}
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][2] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][1]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][3] for inst in insts]

    dt_strat = strat_dt.DTTrader('ProdDT', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks, 
                                 agent = None, daily_close = daily_close, 
                                 email_notify = ['harvey_wwu@hotmail.com'])
    strategies = [rb_strat, dt_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':2, \
                 'min_data_days':1 }

    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None)
    myGui = Gui(myApp)
    myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
    myGui.mainloop()

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        app_name = 'prod_test'
    else:
        app_name = args[1]       
    if len(args) < 1:
        tday = datetime.date.today()
    else:
        tday = datetime.datetime.strptime(args[0], '%Y%m%d').date()

    prod_test(tday, app_name) 
