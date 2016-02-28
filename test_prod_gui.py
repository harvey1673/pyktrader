#-*- coding:utf-8 -*-
import misc
import numpy as np
import logging
import base
import sys
import json
import data_handler
from agent_gui import *
   
def prod_test(tday, name='prod_test'):
    base.config_logging("ctp_" + name + ".log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    trader_cfg = None
    user_cfg = misc.HT_PROD_MD
    # ins_setup = {'ru1605':  [[0.35, 0.08, 0.25], 1,  120, 3],
    #              'rb1605':  [[0.25, 0.05, 0.15], 5, 20, 3],
    #              'RM605' :  [[0.35, 0.07, 0.25], 4,  20, 1],
    #              'm1605' :  [[0.35, 0.07, 0.25], 4,  30, 3],
    #              'ag1606': [[0.4, 0.1, 0.3], 4,  40, 5],
    #              'y1605' : [[0.25, 0.05, 0.15], 4,  60, 1],
    #              'cu1603': [[0.25, 0.05, 0.15], 1,  700, 1]}
    # insts = ins_setup.keys()
    # units_rb = [ins_setup[inst][1] for inst in insts]
    # under_rb = [[inst] for inst in insts]
    # vol_rb = [[1] for inst in insts]
    # ratios = [ins_setup[inst][0] for inst in insts]
    # min_rng = [ins_setup[inst][2] for inst in insts]
    # freq = [ins_setup[inst][3] for inst in insts]
    # stop_loss = 0.015
    # rb_strat = strat_rb.RBreakerTrader('ProdRB', under_rb, vol_rb, trade_unit = units_rb,
    #                              ratios = ratios, min_rng = min_rng, trail_loss = stop_loss, freq = freq,
    #                              agent = None, email_notify = [])
    ins_setup ={
                'TF1603':(2, 0.5, 0.0, 1, False, 0.0),
                'm1605': (0,0.8, 0.0, 2, False, 0.004),
                'RM605': (0,0.8, 0.0, 2, False, 0.004),
                'y1605': (0,0.7, 0.0, 2, False, 0.004),
                'p1605': (0,0.9, 0.0, 2, False, 0.004),
                'a1605' :(0,1.0, 0.0, 2, False, 0.004),
                'rb1605':(0,0.7, 0.5, 4, False, 0.004),
                'l1605': (2,0.4, 0.0, 4, False, 0.004),
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
    #dt_strat = dt_bar.DTBarTrader('ProdDT', under_dt, vol_dt, trade_unit = units_dt,
    #                             ratios = ratios, lookbacks = lookbacks,
    #                             agent = None, daily_close = daily_close, ma_win = 10,
    #                             email_notify = [], min_rng = min_rng)
    ins_setup = {
                'TF1603': (2, 0.6, 0.0, 1, False, 0.0),
                'm1605':  (0, 0.7, 0.0, 2, False, 0.004),
                'RM605':  (0, 0.6, 0.0, 2, False, 0.004),
                'y1605':  (0, 0.6, 0.0, 2, False, 0.004),
                'p1605':  (0, 1.1, 0.0, 2, False, 0.004),
                'a1605' : (0, 0.8, 0.0, 2, False, 0.004),
                'rb1605': (0, 0.6, 0.0, 4, False, 0.004),
                'l1605':  (0, 0.7, 0.0, 4, False, 0.004),
                'pp1605': (4, 0.35, 0.0, 2, False, 0.004),
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
    #dtma_strat = dt_bar.DTBarTrader('DTMA10', under_dt, vol_dt, trade_unit = units_dt,
    #                             ratios = ratios, lookbacks = lookbacks,
    #                             agent = None, daily_close = daily_close,
    #                             email_notify = [], min_rng = min_rng)

    ins_setup = {
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
    #dtsplit_strat1 = dt_split.DTSplitTrader('DTSp1', under_dt, vol_dt, trade_unit = units_dt,
    #                             ratios = ratios, lookbacks = lookbacks,
    #                             agent = None, daily_close = daily_close, ma_win = 10,
    #                             email_notify = [], min_rng = [0.004])
    ins_setup = {
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
    #dtsplit_strat2 = dt_split.DTSplitTrader('DTSp2', under_dt, vol_dt, trade_unit = units_dt,
    #                             ratios = ratios, lookbacks = lookbacks,
    #                             agent = None, daily_close = daily_close, ma_win = 10,
    #                             email_notify = [], min_rng = [0.004])

    ins_setup = {
                 'p1605':  (1, 0.9, 0.0, 2, False),
                 'rb1605': (0, 0.7, 0.0, 2, False),
                 'pp1605': (2, 0.25,0.0, 1, False),
                 'TF1603': (2, 0.5, 0.0, 1, False),
                 'MA605' : (2, 0.25,0.0, 3, False),
                 'SR605' : (1, 0.9, 0.0, 2, False),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    chan_func ={'high_func': max,
                'high_args': {},
                'low_func': min,
                'low_args': {}}
    #dtchan5_sp1 = dt_dfilter.DTSplitChanFilter('DTChan5Sp1',
    #                                            under_dt,
    #                                            vol_dt,
    #                                            trade_unit = units_dt,
    #                                            ratios = ratios,
    #                                            lookbacks = lookbacks,
    #                                            agent = None,
    #                                            daily_close = daily_close,
    #                                            chan_func = chan_func,
    #                                            channels = [5],
    #                                            open_period = [300, 2115],
    #                                            email_notify = [],
    #                                            min_rng = [0.003])
    ins_setup = {
                 'p1605':  (1, 1.0, 0.0, 2, False),
                 'rb1605': (0, 0.6, 0.0, 2, False),
                 'pp1605': (2, 0.3, 0.0, 1, False),
                 'TF1603': (1, 0.7, 0.0, 1, False),
                 'MA605' : (2, 0.3, 0.0, 3, False),
                 'SR605' : (1, 1.0, 0.0, 2, False),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    #dtchan5_sp2 = dt_dfilter.DTSplitChanFilter('DTChan5Sp2',
    #                                            under_dt,
    #                                            vol_dt,
    #                                             trade_unit = units_dt,
    #                                             ratios = ratios,
    #                                             lookbacks = lookbacks,
    #                                             agent = None,
    #                                             daily_close = daily_close,
    #                                             chan_func = chan_func,
    #                                             channels = [5],
    #                                             open_period = [300, 2115],
    #                                             email_notify = [],
    #                                             min_rng = [0.003])
    ins_setup = {
                 'cs1605': (1, 1.1, 0.0, 3, False),
                 'l1605':  (0, 0.7, 0.0, 1, False),
                 'i1605':  (0, 0.7, 0.0, 2, False),
                 'j1605':  (2, 0.35,0.0, 2, False),
                 'cu1603': (1, 0.6, 0.0, 1, False),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    chan_func ={'high_func': np.percentile,
                'high_args': {'q':90,},
                'low_func': np.percentile,
                'low_args':  {'q':10,}}
    # dtchan10_sp1 = dt_dfilter.DTSplitChanFilter('DTChan10Sp1',
    #                                             under_dt,
    #                                             vol_dt,
    #                                             trade_unit = units_dt,
    #                                             ratios = ratios,
    #                                             lookbacks = lookbacks,
    #                                             agent = None,
    #                                             daily_close = daily_close,
    #                                             chan_func = chan_func,
    #                                             channels = [10],
    #                                             open_period = [300, 2115],
    #                                             email_notify = [],
    #                                             min_rng = [0.003])

    ins_setup = {
                 'cs1605': (1, 1.0, 0.0, 3, False),
                 'l1605':  (2, 0.4, 0.0, 1, False),
                 'i1605':  (0, 0.9, 0.0, 2, False),
                 'j1605':  (2, 0.4, 0.0, 2, False),
                 'cu1603': (2,0.35, 0.0, 1, False),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    chan_func ={'high_func': np.percentile,
                'high_args': {'q':80,},
                'low_func': np.percentile,
                'low_args':  {'q':20,}}
    # dtchan10_sp2 = dt_dfilter.DTSplitChanFilter('DTChan10Sp2',
    #                                             under_dt,
    #                                             vol_dt,
    #                                             trade_unit = units_dt,
    #                                             ratios = ratios,
    #                                             lookbacks = lookbacks,
    #                                             agent = None,
    #                                             daily_close = daily_close,
    #                                             chan_func = chan_func,
    #                                             channels = [10],
    #                                             open_period = [300, 2115],
    #                                             email_notify = [],
    #                                             min_rng = [0.003])
    ins_setup = {
                 'm1605':  (1, 0.7, 0.0, 3, False),
                 'RM605':  (2,0.25, 0.0, 3, False),
                 'y1605':  (1, 0.8, 0.0, 2, False),
                 'l1605':  (0, 0.7, 0.0, 1, False),
                 'TF1603': (2, 0.45,0.0, 1, False),
                 'TA605' : (0, 0.7, 0.0, 2, False),
                 'i1605' : (2, 0.35,0.0, 2, False),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    chan_func ={'high_func': np.percentile,
                'high_args': {'q':90,},
                'low_func': np.percentile,
                'low_args':  {'q':10,}}
    # dtchan20_sp1 = dt_dfilter.DTSplitChanFilter('DTChan20Sp1',
    #                                             under_dt,
    #                                             vol_dt,
    #                                             trade_unit = units_dt,
    #                                             ratios = ratios,
    #                                             lookbacks = lookbacks,
    #                                             agent = None,
    #                                             daily_close = daily_close,
    #                                             chan_func = chan_func,
    #                                             channels = [20],
    #                                             open_period = [300, 2115],
    #                                             email_notify = [],
    #                                             min_rng = [0.003])

    ins_setup = {
                 'm1605':  (1, 0.8, 0.0, 3, False),
                 'RM605':  (2, 0.3, 0.0, 3, False),
                 'y1605':  (1, 1.0, 0.0, 2, False),
                 'l1605':  (0, 1.0, 0.0, 1, False),
                 'TF1603': (2, 0.5, 0.0, 1, False),
                 'TA605' : (1, 0.8, 0.0, 2, False),
                 'i1605' : (2, 0.4, 0.0, 2, False),
                }
    insts = ins_setup.keys()
    units_dt = [ins_setup[inst][3] for inst in insts]
    under_dt = [[inst] for inst in insts]
    vol_dt = [[1] for inst in insts]
    ratios = [[ins_setup[inst][1], ins_setup[inst][2]] for inst in insts]
    lookbacks = [ins_setup[inst][0] for inst in insts]
    daily_close = [ins_setup[inst][4] for inst in insts]
    chan_func ={'high_func': np.percentile,
                'high_args': {'q':80,},
                'low_func': np.percentile,
                'low_args':  {'q':20,}}
    # dtchan20_sp2 = dt_dfilter.DTSplitChanFilter('DTChan20Sp2',
    #                                             under_dt,
    #                                             vol_dt,
    #                                             trade_unit = units_dt,
    #                                             ratios = ratios,
    #                                             lookbacks = lookbacks,
    #                                             agent = None,
    #                                             daily_close = daily_close,
    #                                             chan_func = chan_func,
    #                                             channels = [20],
    #                                             open_period = [300, 2115],
    #                                             email_notify = [],
    #                                             min_rng = [0.003])

    ins_setup = {
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
    # tl_strat = strat_tl.TurtleTrader('ProdTL', under_tl, vol_tl, trade_unit = units_tl,
    #                                 agent = None, email_notify = ['harvey_wwu@hotmail.com'],
    #                                  windows = [5, 15],
    #                                  max_pos = max_pos,
    #                                  trail_loss = trail_loss)
    ins_setup = {
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
    # tl_strat2 = strat_tl.TurtleTrader('ProdTL2', under_tl, vol_tl, trade_unit = units_tl,
    #                                 agent = None, email_notify = ['harvey_wwu@hotmail.com'],
    #                                 windows = [10, 20],
    #                                 max_pos = max_pos,
    #                                 trail_loss = trail_loss )
    # strategies = [dt_strat, dtma_strat,\
    #               tl_strat, tl_strat2, \
    #               dtsplit_strat1, dtsplit_strat2, \
    #               dtchan5_sp1, dtchan5_sp2, \
    #               dtchan10_sp1, dtchan10_sp2, \
    #               dtchan20_sp1, dtchan20_sp2]
    # folder = misc.get_prod_folder()
    # strat_cfg = {'strategies': strategies, \
    #              'folder': folder, \
    #              'daily_data_days':22, \
    #              'min_data_days':4 }
    # myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = False)
    # myGui = Gui(myApp)
    # #myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
    # myGui.mainloop()

def prod_test_strats():
    ins_setup ={
                'TF1603':(2, 0.5, 1, False, 0.0),
                'm1605': (0, 0.8, 2, False, 0.004),
                'RM605': (0, 0.8, 2, False, 0.004),
                'y1605': (0, 0.7, 2, False, 0.004),
                'p1605': (0, 0.9, 2, False, 0.004),
                'a1605' :(0, 1.0, 2, False, 0.004),
                'rb1605':(0, 0.7, 4, False, 0.004),
                'l1605': (2, 0.4, 4, False, 0.004),
                'pp1605':(4, 0.4, 2, False, 0.004),
                'TA605' :(0, 0.6, 3, False, 0.004),
                'MA605' :(0, 0.8, 3, False, 0.004),
                'jd1605':(4, 0.4, 4, False, 0.004),
                'SR605': (1, 0.9, 2, False, 0.004),
                'i1605' :(2, 0.4, 2, False, 0.004),
                'cs1605':(0, 1.0, 3, False, 0.004),
                }
    config = {'name': 'DT1',
              'trade_valid_time': 600,
              'num_tick': 1,
              'daily_close_buffer':5,
              'use_chan': False,
              'open_period': [300, 2115],
              'filename': 'StratDT1.json',
              'input_keys': ['lookbacks', 'ratios', 'trade_unit', 'close_tday', 'min_rng'],
              }
    create_strat_file(config, ins_setup)

    ins_setup = {
                'TF1603': (2, 0.6, 1, False, 0.0),
                'm1605':  (0, 0.7, 2, False, 0.004),
                'RM605':  (0, 0.6, 2, False, 0.004),
                'y1605':  (0, 0.6, 2, False, 0.004),
                'p1605':  (0, 1.1, 2, False, 0.004),
                'a1605' : (0, 0.8, 2, False, 0.004),
                'rb1605': (0, 0.6, 4, False, 0.004),
                'l1605':  (0, 0.7, 4, False, 0.004),
                'pp1605': (4, 0.35, 2, False, 0.004),
                'TA605' : (0, 1.0, 3, False, 0.004),
                'MA605' : (0, 0.9, 3, False, 0.004),
                'jd1605': (4, 0.3, 4, False, 0.004),
                'SR605':  (1, 0.8, 2, False, 0.004),
                'i1605' : (2, 0.5, 2, False, 0.004),
                'cs1605' :(0, 1.1, 3, False, 0.004),
                }

    config = {'name': 'DT2',
              'trade_valid_time': 600,
              'num_tick': 1,
              'daily_close_buffer':5,
              'use_chan': False,
              'open_period': [300, 2115],
              'filename': 'StratDT2.json',
              'input_keys': ['lookbacks', 'ratios', 'trade_unit', 'close_tday', 'min_rng'],
              }
    create_strat_file(config, ins_setup)

    ins_setup = {
                 'ag1606': (1, 0.8, 2, False, 0.003),
                 'm1605':  (0, 0.8, 2, False, 0.003),
                 'RM605':  (0, 0.8, 2, False, 0.003),
                 'y1605':  (0, 0.9, 2, False, 0.003),
                 'p1605':  (1, 1.0, 2, False, 0.003),
                 'a1605':  (1, 0.9, 2, False, 0.003),
                 'rb1605': (2, 0.5, 4, False, 0.003),
                 'TA605' : (1, 0.7, 3, False, 0.003),
                 'MA605' : (1, 0.7, 3, False, 0.003),
                 'SR605' : (2, 0.9, 2, False, 0.003),
                 'i1605' : (4, 0.4, 2, False, 0.003),
                }
    config = {'name': 'DTSp1',
              'trade_valid_time': 600,
              'num_tick': 1,
              'daily_close_buffer':5,
              'use_chan': False,
              'open_period': [300, 1500, 2115],
              'filename': 'StratDTSp1.json',
              'input_keys': ['lookbacks', 'ratios', 'trade_unit', 'close_tday', 'min_rng'],
              }
    create_strat_file(config, ins_setup)

    ins_setup = {
                 'ag1606': (1, 1.1, 2, False, 0.003),
                 'm1605':  (0, 1.0, 2, False, 0.003),
                 'RM605':  (0, 1.0, 2, False, 0.003),
                 'y1605':  (0, 1.0, 2, False, 0.003),
                 'p1605':  (1, 1.1, 2, False, 0.003),
                 'a1605':  (1, 1.1, 2, False, 0.003),
                 'rb1605': (0, 0.9, 4, False, 0.003),
                 'TA605' : (1, 0.9, 3, False, 0.003),
                 'MA605' : (1, 0.9, 3, False, 0.003),
                 'SR605' : (4,0.45, 2, False, 0.003),
                 'i1605' : (4, 0.5, 2, False, 0.003),
                }
    config = {'name': 'DTSp2',
              'trade_valid_time': 600,
              'num_tick': 1,
              'daily_close_buffer':5,
              'use_chan': False,
              'open_period': [300, 1500, 2115],
              'filename': 'StratDTSp2.json',
              'input_keys': ['lookbacks', 'ratios', 'trade_unit', 'close_tday', 'min_rng'],
              }
    create_strat_file(config, ins_setup)


def create_strat_file(config, ins_setup):
    insts = ins_setup.keys()
    config_list = []
    for inst in insts:
        asset_dict = {}
        asset_dict['underliers'] = [inst]
        asset_dict['volumes'] = [1]
        for key, val in zip(config['input_keys'], ins_setup[inst]) :
            asset_dict[key] = val
        config_list.append(asset_dict)
    strat_conf = {
        'class': 'strat_dt_dfilter.DTSplitDChanFilter',
        'config': {'name': config['name'],
                    'num_tick': config.get('num_tick', 0),
                    'trade_valid_time':  config.get('trade_valid_time', 300),
                    'use_chan': config.get('use_chan', False),
                    'open_period': config.get('open_period', [300, 2115]),
                    'assets': config_list}
    }
    fname = config['filename']
    try:
        with open(fname, 'w') as ofile:
            json.dump(strat_conf, ofile)
    except:
        print "error with json output"

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
