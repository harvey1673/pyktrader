#-*- coding:utf-8 -*-
import sys
import misc
import logging
import strat_dual_thrust as strat_dt
import strat_rbreaker as strat_rb
import strat_turtle as strat_tl
from agent_gui import *
   
def prod_test(tday, name='prod_test'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = None
    user_cfg = misc.PROD_USER
    ins_setup = {'IF1506': [[0.35, 0.07, 0.25], 1,  30],
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
    stop_loss = 0.015
    rb_strat = strat_rb.RBreakerTrader('ProdRB', under_rb, vol_rb, trade_unit = units_rb,
                                 ratios = ratios, min_rng = min_rng, trail_loss = stop_loss, freq = 1, 
                                 agent = None, email_notify = ['harvey_wwu@hotmail.com'])
    ins_setup = {'m1509':(0,0.4, 0.5, 8, False),
                'RM509':(0, 0.4, 0.5, 10, False),
                'rb1510':(0,0.4, 0.5, 10, False),
                'y1509':(0, 0.4, 0.5, 4, False), 
                'l1509':(0, 0.4, 0.5, 4, False),
                'pp1509':(0,0.4, 0.5, 4, False),
                'ru1509':(0,0.4, 0.5, 1, False),
                'SR509' :(0,0.5, 0.5, 8, False),
                'TA509' :(0,0.5, 0.5, 4, False),
                'ag1506':(0,0.4, 0.5, 6, False),
                'au1506':(0,0.4, 0.5, 1, False),
                'i1509' :(0,0.4, 0.5, 1, False),
                'IF1506':(0,0.4, 0.5, 1, False)}
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
    strategies = [rb_strat, dt_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':5, \
                 'min_data_days':1 }

    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = False)
    myGui = Gui(myApp)
    #myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
    myGui.mainloop()

def prod_trade(tday, name='prod_trade'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = misc.PROD_TRADER
    user_cfg = misc.PROD_USER
#    ins_setup = {'ag1506': [[0.4, 0.1, 0.3], 1,  40],
#                 'ru1509':  [[0.35, 0.07, 0.25], 1,  120],
#                 'rb1510':  [[0.35, 0.07, 0.25], 10, 20],
#                 'RM509' :  [[0.35, 0.07, 0.25], 8,  20],
#                 'm1509' :  [[0.35, 0.07, 0.25], 8,  30],
#                 'ag1506': [[0.35, 0.07, 0.25], 8,  40],
#                 'y1509' : [[0.35, 0.07, 0.25], 8,  60]
#                   }
#    insts = ins_setup.keys()
#    units_rb = [ins_setup[inst][1] for inst in insts]
#    under_rb = [[inst] for inst in insts]
#    vol_rb = [[1] for inst in insts]
#    ratios = [ins_setup[inst][0] for inst in insts]
#    min_rng = [ins_setup[inst][2] for inst in insts]
#    stop_loss = 0.015
#    rb_strat = strat_rb.RBreakerTrader('ProdRB', under_rb, vol_rb, trade_unit = units_rb,
#                                 ratios = ratios, min_rng = min_rng, trail_loss = stop_loss, freq = 5, 
#                                 agent = None, email_notify = [])
    ins_setup = {'m1509':(0,0.7, 0.0, 4, False),
                'RM509': (-1,0.5, 0.0, 4, False),
                'rb1510':(0,0.7, 0.0, 4, False),
                'p1509': (0,0.7, 0.0, 2, False),
                'y1509': (0,0.7, 0.0, 2, False), 
                'l1509': (0,0.7, 0.0, 1, False),
                'pp1509':(0,0.7, 0.0, 1, False),
                'TA509' :(-1,0.4, 0.0, 2, False),
                'MA509' :(-1,0.5, 0.5, 2, False),
                'jd1509':(2,0.4, 0.5, 2, False),
                'a1509' :(2,0.4, 0.5, 2, False),
                #'SR509' :(1,0.6, 0.5, 1, False),                
#                'ru1509':(0, 0.5, 1, False),
#                'SR509' :(0, 0.7, 8, False),
#                'i1509' :(2, 0.3, 1, False),
                }
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
                                 email_notify = [])
#     ins_setup = {'rb1510':(1,0.6, 0.5, 4, False),
#                 'l1509' :(0,0.5, 0.5, 1, False),
#                 'pp1509':(0,0.5, 0.5, 1, False),
#                 'TA509' :(0,0.4, 0.5, 2, False),
#                 'MA509' :(-1,0.5, 0.5, 2, False),
#                 'jd1509':(2,0.4, 0.5, 2, False),
#                 'a1509' :(2,0.4, 0.5, 2, False),
#                 'SR509' :(1,0.6, 0.5, 1, False),
#                 #'m1509':(2,0.3, 0.5, 2, False),
#                 #'RM509' :(-1,0.3, 0.5, 2, False),                
# #                'ru1509':(0, 0.5, 1, False),
# #                'i1509' :(2, 0.3, 1, False),
#                 }
    ins_setup = {'m1509':2,
                'RM509': 2,
                'rb1510':2,
                #'y1509': 1, 
                #'l1509': 1,
                #'pp1509':1,
                #'ru1509':1,
                'TA509' :1,
                #'MA509' :1,
                #'au1506':1,
                'i1509' :1}
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    tl_strat = strat_tl.TurtleTrader('ProdTL', under_tl, vol_tl, trade_unit = units_tl,
                                 agent = None, email_notify = []) 
    strategies = [dt_strat, tl_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':21, \
                 'min_data_days':1 }

    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = False)
    myGui = Gui(myApp)
    #myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
    myGui.mainloop()

def prod_trade2(tday, name='prod_trade2'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = misc.HT_PROD_TD
    user_cfg = misc.HT_PROD_MD
#    ins_setup = {'ag1506': [[0.4, 0.1, 0.3], 1,  40],
#                 'ru1509':  [[0.35, 0.07, 0.25], 1,  120],
#                 'rb1510':  [[0.35, 0.07, 0.25], 10, 20],
#                 'RM509' :  [[0.35, 0.07, 0.25], 8,  20],
#                 'm1509' :  [[0.35, 0.07, 0.25], 8,  30],
#                 'ag1506': [[0.35, 0.07, 0.25], 8,  40],
#                 'y1509' : [[0.35, 0.07, 0.25], 8,  60]
#                   }
#    insts = ins_setup.keys()
#    units_rb = [ins_setup[inst][1] for inst in insts]
#    under_rb = [[inst] for inst in insts]
#    vol_rb = [[1] for inst in insts]
#    ratios = [ins_setup[inst][0] for inst in insts]
#    min_rng = [ins_setup[inst][2] for inst in insts]
#    stop_loss = 0.015
#    rb_strat = strat_rb.RBreakerTrader('ProdRB', under_rb, vol_rb, trade_unit = units_rb,
#                                 ratios = ratios, min_rng = min_rng, trail_loss = stop_loss, freq = 5, 
#                                 agent = None, email_notify = [])
    ins_setup = {'m1509':(0,0.7, 0.0, 4, False),
                'RM509': (-1,0.5, 0.0, 4, False),
                'rb1510':(0,0.7, 0.0, 4, False),
                'p1509': (0,0.7, 0.0, 2, False),
                'y1509': (0,0.7, 0.0, 2, False), 
                'l1509': (0,0.7, 0.0, 1, False),
                'pp1509':(0,0.7, 0.0, 1, False),
                'TA509' :(-1,0.4, 0.0, 2, False),
                'MA509' :(-1,0.5, 0.5, 2, False),
                'jd1509':(2,0.4, 0.5, 2, False),
                'a1509' :(2,0.4, 0.5, 2, False),
                #'SR509' :(1,0.6, 0.5, 1, False),                
#                'ru1509':(0, 0.5, 1, False),
#                'SR509' :(0, 0.7, 8, False),
#                'i1509' :(2, 0.3, 1, False),
                }
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
                                 email_notify = [])
#     ins_setup = {'rb1510':(1,0.6, 0.5, 4, False),
#                 'l1509' :(0,0.5, 0.5, 1, False),
#                 'pp1509':(0,0.5, 0.5, 1, False),
#                 'TA509' :(0,0.4, 0.5, 2, False),
#                 'MA509' :(-1,0.5, 0.5, 2, False),
#                 'jd1509':(2,0.4, 0.5, 2, False),
#                 'a1509' :(2,0.4, 0.5, 2, False),
#                 'SR509' :(1,0.6, 0.5, 1, False),
#                 #'m1509':(2,0.3, 0.5, 2, False),
#                 #'RM509' :(-1,0.3, 0.5, 2, False),                
# #                'ru1509':(0, 0.5, 1, False),
# #                'i1509' :(2, 0.3, 1, False),
#                 }
    ins_setup = {'m1509':2,
                'RM509': 2,
                'rb1510':2,
                #'y1509': 1, 
                #'l1509': 1,
                #'pp1509':1,
                #'ru1509':1,
                'TA509' :1,
                #'MA509' :1,
                #'au1506':1,
                'i1509' :1}
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    tl_strat = strat_tl.TurtleTrader('ProdTL', under_tl, vol_tl, trade_unit = units_tl,
                                 agent = None, email_notify = []) 
    strategies = [dt_strat, tl_strat]
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
        app_name = 'prod_trade'
    else:
        app_name = args[1]       
    if len(args) < 1:
        tday = datetime.date.today()
    else:
        tday = datetime.datetime.strptime(args[0], '%Y%m%d').date()
    
    params = (tday, app_name, )
    getattr(sys.modules[__name__], app_name)(*params) 
