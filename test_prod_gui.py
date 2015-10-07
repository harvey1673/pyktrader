#-*- coding:utf-8 -*-
import misc
import logging
import base
import sys
import strat_dual_thrust as strat_dt
import strat_dt_split as dt_split
import strat_rbreaker as strat_rb
import strat_turtle as strat_tl
from agent_gui import *
   
def prod_test(tday, name='prod_test'):
    base.config_logging("ctp_" + name + ".log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    trader_cfg = None
    user_cfg = misc.HT_PROD_MD
    ins_setup = {'IF1510': [[0.3, 0.07, 0.2], 1,  30, 1],
                 'IH1510': [[0.3, 0.07, 0.2], 1,  30, 1],
                'ru1601':  [[0.35, 0.08, 0.25], 1,  120, 3],
                'rb1601':  [[0.25, 0.05, 0.15], 5, 20, 3],
                'RM601' :  [[0.35, 0.07, 0.25], 4,  20, 1],
                'm1601' :  [[0.35, 0.07, 0.25], 4,  30, 3],
                'ag1512': [[0.4, 0.1, 0.3], 4,  40, 5],
                'y1601' : [[0.25, 0.05, 0.15], 4,  60, 1],
                'cu1512': [[0.25, 0.05, 0.15], 1,  700, 1]}
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
                                 agent = None, email_notify = [])
    ins_setup = {'m1601':(0,0.7, 0.0, 8, False, 0.004),
                'RM601': (-1,0.5, 0.0, 8, False, 0.004),
                'rb1601':(0,0.7, 0.0, 8, False, 0.004),
                'l1601': (0,0.7, 0.0, 2, False, 0.004),
                'pp1601':(0,0.7, 0.0, 2, False, 0.004),
                'TA601' :(-1,0.4, 0.0, 4, False, 0.004),
                'ru1601':(0, 0.7, 0.0, 1, False, 0.004),
                'SR601' :(0, 0.7, 0.0, 4, False, 0.004),
                'MA601' :(0, 0.7, 0.0, 3, False, 0.004),
                'au1512':(0, 0.7, 0.0, 1, False, 0.004),
                'i1601' :(2, 0.4, 0.0, 1, False, 0.004),
                'IF1510':(0, 0.6, 0.0, 1, False, 0.004),
                'IH1510':(0, 0.6, 0.0, 1, False, 0.004),
                'y1601': (0,0.7, 0.0, 4, False, 0.004),
                'p1601': (0,0.7, 0.0, 4, False, 0.004),
                 'TF1512':(2, 0.5, 0.0, 1, False, 0.0),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    min_rng = [ins_setup[inst][5] for inst in insts]
    dt_strat = strat_dt.DTTrader('ProdDT', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks, 
                                 agent = None, daily_close = daily_close, ma_win = 10,
                                 email_notify = [], min_rng = min_rng)
    ins_setup = {'rb1601':(1,0.6, 0.5, 4, False, 0.004),
                'l1601' :(0,0.5, 0.5, 1, False, 0.004),
                'pp1601':(0,0.5, 0.5, 1, False, 0.004),
                'TA601' :(0,0.4, 0.5, 2, False, 0.004),
                'MA601' :(-1,0.5, 0.5, 2, False, 0.004),
                'jd1601':(2,0.4, 0.5, 2, False, 0.004),
                'a1601' :(2,0.4, 0.5, 2, False, 0.004),
                'SR601' :(1,0.6, 0.5, 1, False, 0.004),
                'm1601':(2,0.3, 0.5, 2, False, 0.004),
                'RM601' :(-1,0.3, 0.5, 2, False, 0.004),
                'i1601' :(4, 0.3, 0.5, 1, False, 0.004),
                'TF1512':(2, 0.4, 0.5, 1, False, 0.0),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    min_rng = [ins_setup[inst][5] for inst in insts]
    dtma_strat = strat_dt.DTTrader('DTMA10', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks, 
                                 agent = None, daily_close = daily_close, 
                                 email_notify = [], min_rng = min_rng)

    ins_setup = {'m1601': (0, 0.8, 0.0, 2, False),
                 'RM601':  (0, 0.8, 0.0, 2, False),
                 'y1601':  (0, 0.9, 0.0, 2, False),
                 'p1601':  (1, 1.0, 0.0, 2, False),
                 'a1601':  (1, 0.9, 0.0, 3, False),
                 'rb1601': (2, 0.5, 0.0, 5, False),
                 'TA601' : (1, 0.7, 0.0, 3, False),
                 'MA601' : (1, 0.7, 0.0, 5, False),
                 'SR601' : (2, 0.9, 0.0, 3, False),
                 'i1601' : (4, 0.4, 0.0, 1, False),
                 'ag1512': (1, 0.8, 0.0, 2, False),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    dtsplit_strat1 = dt_split.DTSplitTrader('DTSp1', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks,
                                 agent = None, daily_close = daily_close, ma_win = 10,
                                 email_notify = [], min_rng = [0.004])
    ins_setup = {'m1601':  (0, 1.0, 0.0, 2, False),
                 'RM601':  (0, 1.0, 0.0, 2, False),
                 'y1601':  (0, 1.0, 0.0, 2, False),
                 'p1601':  (1, 1.1, 0.0, 2, False),
                 'a1601':  (1, 1.1, 0.0, 3, False),
                 'rb1601': (0, 0.9, 0.0, 5, False),
                 'TA601' : (1, 0.9, 0.0, 3, False),
                 'MA601' : (1, 0.9, 0.0, 5, False),
                 'SR601' : (4,0.45, 0.0, 3, False),
                 'i1601' : (4, 0.5, 0.0, 1, False),
                 'ag1512': (1, 1.1, 0.0, 2, False),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    dtsplit_strat2 = dt_split.DTSplitTrader('DTSp2', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks,
                                 agent = None, daily_close = daily_close, ma_win = 10,
                                 email_notify = [], min_rng = [0.004])

    ins_setup = {'i1601': [2, 2, 2],
                 #'jm1601': [1, 1, 1],
                 'TF1512': [1, 1, 1],
                 'TC601': [2, 4, 1],
                 'TA601': [2, 3, 2],
                 #'bu1512': [1, 1, 1],
                 'CF601': [2, 1, 2],
                 'ru1601': [1, 1, 1],
                 }
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst][2] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    trail_loss = [ins_setup[inst][0] for inst in insts]
    max_pos = [ins_setup[inst][1] for inst in insts]
    tl_strat = strat_tl.TurtleTrader('ProdTL', under_tl, vol_tl, trade_unit = units_tl,
                                    agent = None, email_notify = ['harvey_wwu@hotmail.com'],
                                     windows = [5, 15],
                                     max_pos = max_pos,
                                     trail_loss = trail_loss)
    ins_setup = {'j1601': [1, 1, 1],
                 'rb1601': [1, 1, 1],
                 #'bu1512' :[2, 4, 1],
                 'p1601' :[1, 1, 2],
                 'jd1601':[2, 2, 1],
                 }
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst][2] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    trail_loss = [ins_setup[inst][0] for inst in insts]
    max_pos = [ins_setup[inst][1] for inst in insts]
    tl_strat2 = strat_tl.TurtleTrader('ProdTL2', under_tl, vol_tl, trade_unit = units_tl,
                                    agent = None, email_notify = ['harvey_wwu@hotmail.com'],
                                    windows = [10, 20],
                                    max_pos = max_pos,
                                    trail_loss = trail_loss )
    strategies = [rb_strat, dt_strat, dtma_strat, tl_strat, tl_strat2, dtsplit_strat1, dtsplit_strat2]
    folder = misc.get_prod_folder()
    strat_cfg = {'strategies': strategies, \
                 'folder': folder, \
                 'daily_data_days':21, \
                 'min_data_days':4 }
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
    params = (tday, app_name, )
    getattr(sys.modules[__name__], app_name)(*params) 
