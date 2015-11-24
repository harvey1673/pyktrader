#-*- coding:utf-8 -*-
import sys
import misc
import base
import logging
import strat_dual_thrust as strat_dt
import strat_dt_split as dt_split
#import strat_rbreaker as strat_rb
import strat_turtle as strat_tl
from agent_gui import *

# def prod_trade(tday, name='prod_trade'):
#     base.config_logging("ctp_" + name + ".log", level=logging.DEBUG,
#                    format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
#                    to_console = True,
#                    console_level = logging.INFO)
#     trader_cfg = misc.HT_DN_TD
#     user_cfg = misc.HT_DN_MD
#     ins_setup = {'m1605':(1, 0.7, 0.0, 2, False),
#                 'RM605': (1, 0.6, 0.0, 2, False),
#                 'y1605': (0, 0.8, 0.0, 1, False),
#                 'p1605': (1, 0.9, 0.0, 1, False),
#                 'OI601': (0, 0.7, 0.0, 0, False),
#                 'a1601': (0, 1.0, 0.0, 2, False),
#                 'rb1605':(0, 0.6, 0.0, 4, False),
#                 'l1605': (0, 0.7, 0.0, 1, False),
#                 'pp1601':(4, 0.3, 0.0, 1, False),
#                 'TA601' :(1, 0.6, 0.0, 1, False),
#                 'MA601' :(1, 0.8, 0.0, 2, False),
#                 'jd1601':(1 ,0.8, 0.0, 1, False),
#                 'SR605': (1, 0.8, 0.0, 1, False),
#                 }
#     insts = ins_setup.keys()
#     units_dt = [ins_setup[inst][3] for inst in insts]
#     under_dt = [[inst] for inst in insts]
#     vol_dt = [[1] for inst in insts]
#     ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
#     lookbacks = [ins_setup[inst][0] for inst in insts]
#     daily_close = [ins_setup[inst][4] for inst in insts]
#     dt_strat = strat_dt.DTTrader('ProdDT', under_dt, vol_dt, trade_unit = units_dt,
#                                  ratios = ratios, lookbacks = lookbacks,
#                                  agent = None, daily_close = daily_close,
#                                  email_notify = [], ma_win = 10)
#     strategies = [dt_strat]
#     folder = misc.get_prod_folder()
#     strat_cfg = {'strategies': strategies, \
#                  'folder': folder, \
#                  'daily_data_days':4, \
#                  'min_data_days':1 }
#     myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = False)
#     myGui = Gui(myApp)
#     myGui.mainloop()

def prod_trade2(tday, name='prod_trade2'):
    base.config_logging("ctp_" + name + ".log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    trader_cfg = misc.HT_PROD_TD
    user_cfg = misc.HT_PROD_MD

    ins_setup ={'m1601': (0,0.6, 0.0, 0, False, 0.004),
                'RM601': (0,0.8, 0.0, 0, False, 0.004),
                'y1601': (0,0.7, 0.0, 0, False, 0.004),
                'p1601': (0,0.8, 0.0, 0, False, 0.004),
                'a1601' :(0,1.0, 0.0, 0, False, 0.004),
                'rb1601':(0,0.7, 0.5, 0, False, 0.004),
                'l1601': (4,0.27,0.0, 0, False, 0.004),
                'pp1601':(4,0.4, 0.0, 0, False, 0.004),
                'TA601' :(0, 0.6, 0.0, 0, False, 0.004),
                'MA601' :(0, 0.8, 0.0, 0, False, 0.004),
                'jd1601':(4, 0.4, 0.0, 0, False, 0.004),
                'SR601': (1, 0.9, 0.0, 0, False, 0.004),
                'i1601' :(2, 0.4,0.0, 0, False, 0.004),
                #'TF1512':(2, 0.5, 0.0, 1, False, 0.0),
                'm1605': (0,0.6, 0.0, 2, False, 0.004),
                'RM605': (0,0.8, 0.0, 2, False, 0.004),
                'y1605': (0,0.7, 0.0, 2, False, 0.004),
                'p1605': (0,0.8, 0.0, 2, False, 0.004),
                'a1605' :(0,1.0, 0.0, 2, False, 0.004),
                'rb1605':(0,0.7, 0.5, 4, False, 0.004),
                'l1605': (4,0.27,0.0, 4, False, 0.004),
                'pp1605':(4,0.4, 0.0, 2, False, 0.004),
                'TA605' :(0, 0.6, 0.0, 3, False, 0.004),
                'MA605' :(0, 0.8, 0.0, 3, False, 0.004),
                'jd1605':(4, 0.4, 0.0, 4, False, 0.004),
                'SR605': (1, 0.9, 0.0, 2, False, 0.004),
                'i1605' :(2, 0.4,0.0, 2,  False, 0.004),
                'cs1605' :(0, 1.0, 0.0, 3, False, 0.004),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    min_rng = [ins_setup[inst][5] for inst in insts]
    dt_strat1 = strat_dt.DTTrader('DT1', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks, 
                                 agent = None, daily_close = daily_close, 
                                 email_notify = [], ma_win = 10, min_rng = min_rng)

    ins_setup ={'m1601':  (0, 0.7, 0.0, 0, False, 0.004),
                'RM601':  (0, 0.6, 0.0, 0, False, 0.004),
                'y1601':  (0, 0.6, 0.0, 0, False, 0.004),
                'p1601':  (0, 0.9, 0.0, 0, False, 0.004),
                'a1601' : (0, 0.9, 0.0, 0, False, 0.004),
                'rb1601': (0, 0.6, 0.0, 0, False, 0.004),
                'l1601':  (0, 0.7, 0.0, 0, False, 0.004),
                'pp1601': (2, 0.3, 0.0, 0, False, 0.004),
                'TA601' : (0, 1.0, 0.0, 0, False, 0.004),
                'MA601' : (0, 0.9, 0.0, 0, False, 0.004),
                'jd1601': (4, 0.3, 0.0, 0, False, 0.004),
                'SR601':  (1, 0.8, 0.0, 0, False, 0.004),
                'i1601' : (2, 0.5,0.0, 0, False, 0.004),
                #'TF1512': (2, 0.6, 0.0, 1, False, 0.0),
                'm1605':  (0, 0.7, 0.0, 2, False, 0.004),
                'RM605':  (0, 0.6, 0.0, 2, False, 0.004),
                'y1605':  (0, 0.6, 0.0, 2, False, 0.004),
                'p1605':  (0, 0.9, 0.0, 2, False, 0.004),
                'a1605' : (0, 0.9, 0.0, 2, False, 0.004),
                'rb1605': (0, 0.6, 0.0, 4, False, 0.004),
                'l1605':  (0, 0.7, 0.0, 4, False, 0.004),
                'pp1605': (2, 0.3, 0.0, 2, False, 0.004),
                'TA605' : (0, 1.0, 0.0, 3, False, 0.004),
                'MA605' : (0, 0.9, 0.0, 3, False, 0.004),
                'jd1605': (4, 0.3, 0.0, 4, False, 0.004),
                'SR605':  (1, 0.8, 0.0, 2, False, 0.004),
                'i1605' : (2, 0.5,0.0,  2, False, 0.004),
                'cs1605' :(0, 1.1, 0.0, 3, False, 0.004),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    min_rng = [ins_setup[inst][5] for inst in insts]
    dt_strat2 = strat_dt.DTTrader('DT2', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks,
                                 agent = None, daily_close = daily_close,
                                 email_notify = [], ma_win = 10, min_rng = min_rng)
    ins_setup = {'m1601': (0, 0.8, 0.0, 0, False),
                 'RM601':  (0, 0.8, 0.0, 0, False),
                 'y1601':  (0, 0.9, 0.0, 0, False),
                 'p1601':  (1, 1.0, 0.0, 0, False),
                 'a1601':  (1, 0.9, 0.0, 0, False),
                 'rb1601': (2, 0.5, 0.0, 0, False),
                 'TA601' : (1, 0.7, 0.0, 0, False),
                 'MA601' : (1, 0.7, 0.0, 0, False),
                 'SR601' : (2, 0.9, 0.0, 0, False),
                 'i1601' : (4, 0.4, 0.0, 0, False),
                 'ag1512': (1, 0.6, 0.0, 0, False),
                 'ag1606': (1, 0.8, 0.0, 2, False),
                 'm1605': (0, 0.8, 0.0, 2, False),
                 'RM605':  (0, 0.8, 0.0, 2, False),
                 'y1605':  (0, 0.9, 0.0, 2, False),
                 'p1605':  (1, 1.0, 0.0, 2, False),
                 'a1605':  (1, 0.9, 0.0, 2, False),
                 'rb1605': (2, 0.5, 0.0, 4, False),
                 'TA605' : (1, 0.7, 0.0, 3, False),
                 'MA605' : (1, 0.7, 0.0, 3, False),
                 'SR605' : (2, 0.9, 0.0, 2, False),
                 'i1605' : (4, 0.4, 0.0, 2, False),
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
    ins_setup = {'m1601':  (0, 1.0, 0.0, 0, False),
                 'RM601':  (0, 1.0, 0.0, 0, False),
                 'y1601':  (0, 1.0, 0.0, 0, False),
                 'p1601':  (1, 1.1, 0.0, 0, False),
                 'a1601':  (1, 1.1, 0.0, 0, False),
                 'rb1601': (0, 0.9, 0.0, 0, False),
                 'TA601' : (1, 0.9, 0.0, 0, False),
                 'MA601' : (1, 0.9, 0.0, 0, False),
                 'SR601' : (4,0.45, 0.0, 0, False),
                 'i1601' : (4, 0.5, 0.0, 0, False),
                 'ag1512': (1, 1.1, 0.0, 0, False),
                 'ag1606': (1, 1.1, 0.0, 2, False),
                 'm1605':  (0, 1.0, 0.0, 2, False),
                 'RM605':  (0, 1.0, 0.0, 2, False),
                 'y1605':  (0, 1.0, 0.0, 2, False),
                 'p1605':  (1, 1.1, 0.0, 2, False),
                 'a1605':  (1, 1.1, 0.0, 2, False),
                 'rb1605': (0, 0.9, 0.0, 4, False),
                 'TA605' : (1, 0.9, 0.0, 3, False),
                 'MA605' : (1, 0.9, 0.0, 3, False),
                 'SR605' : (4,0.45, 0.0, 2, False),
                 'i1605' : (4, 0.5, 0.0, 2, False),
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
    ins_setup = {'i1601': [1, 1, 2],
                 'TA601': [2, 2, 2],
                 'bu1512':[2, 1, 1],
                 'bu1601':[2, 1, 1],
                 'i1605': [1, 1, 2],
                 'TA605': [2, 2, 2],
                 'ZC605': [2, 3, 1],
                 }
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst][2] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    trail_loss = [ins_setup[inst][0] for inst in insts]
    max_pos = [ins_setup[inst][1] for inst in insts]
    tl_strat1 = strat_tl.TurtleTrader('TL1', under_tl, vol_tl, trade_unit = units_tl,
                                    agent = None, email_notify = [],
                                     windows = [5, 15],
                                     max_pos = max_pos,
                                     trail_loss = trail_loss)
    ins_setup = {'j1601': [1, 2, 1],
                 #'TC605': [2, 3, 2],
                 'i1601': [2, 2, 1],
                 'j1605': [1, 2, 1],
                 'ZC605': [2, 3, 2],
                 'i1605': [2, 2, 1],
                 }
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst][2] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    trail_loss = [ins_setup[inst][0] for inst in insts]
    max_pos = [ins_setup[inst][1] for inst in insts]
    tl_strat2 = strat_tl.TurtleTrader('TL2', under_tl, vol_tl, trade_unit = units_tl,
                                    agent = None, email_notify = [],
                                    windows = [10, 20],
                                    max_pos = max_pos,
                                    trail_loss = trail_loss )
    strategies = [dtsplit_strat1,  dtsplit_strat2, dt_strat1, dt_strat2, tl_strat1, tl_strat2]
    folder = misc.get_prod_folder()
    strat_cfg = {'strategies': strategies, \
                 'folder': folder, \
                 'daily_data_days':21, \
                 'min_data_days':3 }

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
