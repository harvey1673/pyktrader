#-*- coding:utf-8 -*-
import misc
import logging
import sys
import strat_dual_thrust as strat_dt
import strat_rbreaker as strat_rb
import strat_turtle as strat_tl
from agent_gui import *
   
def prod_test(tday, name='prod_test'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = None
    user_cfg = misc.PROD_USER
    ins_setup = {'IF1506': [[0.3, 0.07, 0.2], 1,  30, 1],
                'ru1509':  [[0.35, 0.08, 0.25], 1,  120, 3],
                'rb1510':  [[0.25, 0.05, 0.15], 5, 20, 3],
                'RM509' :  [[0.35, 0.07, 0.25], 4,  20, 1],
                'm1509' :  [[0.35, 0.07, 0.25], 4,  30, 3],
                'ag1506': [[0.4, 0.1, 0.3], 4,  40, 5],
                'y1509' : [[0.25, 0.05, 0.15], 4,  60, 1],
                'cu1507': [[0.25, 0.05, 0.15], 1,  700, 1]}
    insts = ins_setup.keys()
    units_rb = [ins_setup[inst][1] for inst in insts]
    under_rb = [[inst] for inst in insts]
    vol_rb = [[1] for inst in insts]
    ratios = [ins_setup[inst][0] for inst in insts]
    min_rng = [ins_setup[inst][2] for inst in insts]
    freq = [ins_setup[inst][3] for inst in insts]
    stop_loss = 0.015
    rb_strat = strat_rb.RBreakerTrader('ProdRB', under_rb, vol_rb, trade_unit = units_rb,
                                 ratios = ratios, min_rng = min_rng, trail_loss = stop_loss, freq = freq, 
                                 agent = None, email_notify = ['harvey_wwu@hotmail.com'])
    ins_setup = {'m1509':(0, 0.4, 0.5, 8, False),
                'RM509':(0, 0.4, 0.5, 10, False),
                'rb1510':(0,0.4, 0.5, 10, False),
                'y1509':(0, 0.4, 0.5, 4, False), 
                'l1509':(0, 0.4, 0.5, 4, False),
                'pp1509':(0,0.4, 0.5, 4, False),
                'ru1509':(0, 0.4, 0.5, 1, False),
                'SR509' :(0, 0.5, 0.5, 8, False),
                'TA509' :(0, 0.5, 0.5, 4, False),
                'MA509' :(0, 0.5, 0.5, 5, False),
                #'ni1507':(0, 0.5, 1, False),
                'au1506':(0, 0.4, 0.5, 1, False),
                'i1509' :(0, 0.4, 0.5, 1, False),
                'IF1506':(0, 0.4, 0.5, 1, True)}
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    dt_strat = strat_dt.DTTrader('ProdDT', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks, 
                                 agent = None, daily_close = daily_close, 
                                 email_notify = ['harvey_wwu@hotmail.com'])
    ins_setup = {'m1509':2,
                'RM509': 2,
                'rb1510':2,
                'y1509': 1, 
                'l1509': 1,
                'pp1509':1,
                'ru1509':1,
                'SR509' :1,
                'TA509' :2,
                'MA509' :1,
                #'ni1507':(0, 0.5, 1, False),
                'au1506':1,
                'i1509' :1,
                'IF1506':1}
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    tl_strat = strat_tl.TurtleTrader('ProdTL', under_tl, vol_tl, trade_unit = units_tl,
                                 agent = None, email_notify = ['harvey_wwu@hotmail.com'])    
    strategies = [rb_strat, dt_strat, tl_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':21, \
                 'min_data_days':1 }

    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = False)
    myGui = Gui(myApp)
    #myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
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
