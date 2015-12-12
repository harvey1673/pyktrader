#-*- coding:utf-8 -*-
import misc
import logging
import base
import sys
import data_handler
import strat_dt_chanfilter as dt_chansplit
import strat_dual_thrust as strat_dt
import strat_dt_split as dt_split
import strat_rbreaker as strat_rb
import strat_turtle as strat_tl
import strat_dt_onbar as dt_bar
from agent_gui import *
   
def prod_test(tday, name='prod_test'):
    base.config_logging("ctp_" + name + ".log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    trader_cfg = None
    user_cfg = misc.HT_PROD_MD
    ins_setup = {'ru1605':  [[0.35, 0.08, 0.25], 1,  120, 3],
                 'rb1605':  [[0.25, 0.05, 0.15], 5, 20, 3],
                 'RM605' :  [[0.35, 0.07, 0.25], 4,  20, 1],
                 'm1605' :  [[0.35, 0.07, 0.25], 4,  30, 3],
                 'ag1606': [[0.4, 0.1, 0.3], 4,  40, 5],
                 'y1605' : [[0.25, 0.05, 0.15], 4,  60, 1],
                 'cu1603': [[0.25, 0.05, 0.15], 1,  700, 1]}
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
    dt_strat = dt_bar.DTBarTrader('ProdDT', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks, 
                                 agent = None, daily_close = daily_close, ma_win = 10,
                                 email_notify = [], min_rng = min_rng)
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
    dtma_strat = dt_bar.DTBarTrader('DTMA10', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks, 
                                 agent = None, daily_close = daily_close, 
                                 email_notify = [], min_rng = min_rng)

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
    dtsplit_strat1 = dt_split.DTSplitTrader('DTSp1', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks,
                                 agent = None, daily_close = daily_close, ma_win = 10,
                                 email_notify = [], min_rng = [0.004])
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
    dtsplit_strat2 = dt_split.DTSplitTrader('DTSp2', under_dt, vol_dt, trade_unit = units_dt,
                                 ratios = ratios, lookbacks = lookbacks,
                                 agent = None, daily_close = daily_close, ma_win = 10,
                                 email_notify = [], min_rng = [0.004])

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
    chan_func ={'func_high': [data_handler.DONCH_H, data_handler.donch_h], 'high_name': 'DONCH_H', \
                'func_low': [data_handler.DONCH_L, data_handler.donch_l],  'low_name': 'DONCH_L',  \
                'func_args': {'n': 5}}
    dtchan5_sp1 = dt_chansplit.DTChanSplitTrader('DTChan5Sp1',
                                                under_dt,
                                                vol_dt,
                                                trade_unit = units_dt,
                                                ratios = ratios,
                                                lookbacks = lookbacks,
                                                agent = None,
                                                daily_close = daily_close,
                                                chan_func = chan_func,
                                                open_period = [300, 2115],
                                                email_notify = [],
                                                min_rng = [0.002])
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
    chan_func ={'func_high': [data_handler.DONCH_H, data_handler.donch_h], 'high_name': 'DONCH_H', \
                'func_low': [data_handler.DONCH_L, data_handler.donch_l],  'low_name': 'DONCH_L',  \
                'func_args': {'n': 5}}
    dtchan5_sp2 = dt_chansplit.DTChanSplitTrader('DTChan5Sp2',
                                                under_dt,
                                                vol_dt,
                                                trade_unit = units_dt,
                                                ratios = ratios,
                                                lookbacks = lookbacks,
                                                agent = None,
                                                daily_close = daily_close,
                                                chan_func = chan_func,
                                                open_period = [300, 2115],
                                                email_notify = [],
                                                min_rng = [0.002])
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
    chan_func ={'func_high': [data_handler.DONCH_H, data_handler.donch_h], 'high_name': 'DONCH_H', \
                'func_low': [data_handler.DONCH_L, data_handler.donch_l],  'low_name': 'DONCH_L',  \
                'func_args': {'n': 10}}
    dtchan10_sp1 = dt_chansplit.DTChanSplitTrader('DTChan10Sp1',
                                                under_dt,
                                                vol_dt,
                                                trade_unit = units_dt,
                                                ratios = ratios,
                                                lookbacks = lookbacks,
                                                agent = None,
                                                daily_close = daily_close,
                                                chan_func = chan_func,
                                                open_period = [300, 2115],
                                                email_notify = [],
                                                min_rng = [0.002])
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
    chan_func ={'func_high': [data_handler.DONCH_H, data_handler.donch_h], 'high_name': 'DONCH_H', \
                'func_low': [data_handler.DONCH_L, data_handler.donch_l],  'low_name': 'DONCH_L',  \
                'func_args': {'n': 10}}
    dtchan10_sp2 = dt_chansplit.DTChanSplitTrader('DTChan10Sp2',
                                                under_dt,
                                                vol_dt,
                                                trade_unit = units_dt,
                                                ratios = ratios,
                                                lookbacks = lookbacks,
                                                agent = None,
                                                daily_close = daily_close,
                                                chan_func = chan_func,
                                                open_period = [300, 2115],
                                                email_notify = [],
                                                min_rng = [0.002])
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
    chan_func ={'func_high': [data_handler.DONCH_H, data_handler.donch_h], 'high_name': 'DONCH_H', \
                'func_low': [data_handler.DONCH_L, data_handler.donch_l],  'low_name': 'DONCH_L',  \
                'func_args': {'n': 20}}
    dtchan20_sp1 = dt_chansplit.DTChanSplitTrader('DTChan20Sp1',
                                                under_dt,
                                                vol_dt,
                                                trade_unit = units_dt,
                                                ratios = ratios,
                                                lookbacks = lookbacks,
                                                agent = None,
                                                daily_close = daily_close,
                                                chan_func = chan_func,
                                                open_period = [300, 2115],
                                                email_notify = [],
                                                min_rng = [0.002])
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
    chan_func ={'func_high': [data_handler.DONCH_H, data_handler.donch_h], 'high_name': 'DONCH_H', \
                'func_low': [data_handler.DONCH_L, data_handler.donch_l],  'low_name': 'DONCH_L',  \
                'func_args': {'n': 20}}
    dtchan20_sp2 = dt_chansplit.DTChanSplitTrader('DTChan20Sp2',
                                                under_dt,
                                                vol_dt,
                                                trade_unit = units_dt,
                                                ratios = ratios,
                                                lookbacks = lookbacks,
                                                agent = None,
                                                daily_close = daily_close,
                                                chan_func = chan_func,
                                                open_period = [300, 2115],
                                                email_notify = [],
                                                min_rng = [0.002])
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
    tl_strat = strat_tl.TurtleTrader('ProdTL', under_tl, vol_tl, trade_unit = units_tl,
                                    agent = None, email_notify = ['harvey_wwu@hotmail.com'],
                                     windows = [5, 15],
                                     max_pos = max_pos,
                                     trail_loss = trail_loss)
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
    tl_strat2 = strat_tl.TurtleTrader('ProdTL2', under_tl, vol_tl, trade_unit = units_tl,
                                    agent = None, email_notify = ['harvey_wwu@hotmail.com'],
                                    windows = [10, 20],
                                    max_pos = max_pos,
                                    trail_loss = trail_loss )
    strategies = [rb_strat, dt_strat, dtma_strat,\
                  tl_strat, tl_strat2, \
                  dtsplit_strat1, dtsplit_strat2, \
                  dtchan5_sp1, dtchan5_sp2, \
                  dtchan10_sp1, dtchan10_sp2, \
                  dtchan20_sp1, dtchan20_sp2]
    folder = misc.get_prod_folder()
    strat_cfg = {'strategies': strategies, \
                 'folder': folder, \
                 'daily_data_days':22, \
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
