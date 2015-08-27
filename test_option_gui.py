from agent_gui import *
import datetime
import misc
import base
import logging
import sys
import optionarb
import strat_dual_thrust as strat_dt
import strat_rbreaker as strat_rb
import strat_turtle as strat_tl

def get_option_map(underliers, expiries, strikes):
    opt_map = {}
    for under, expiry, ks in zip(underliers, expiries, strikes):
        for otype in ['C', 'P']:
            for strike in ks:
                cont_mth = int(under[-4:]) + 200000
                key = (str(under), cont_mth, otype, strike)
                instID = under
                if instID[:2] == "IF":
                    instID = instID.replace('IF', 'IO')
                instID = instID + '-' + otype + '-' + str(strike)
                opt_map[key] = instID
    return opt_map
    
def option_test(tday, name='option_test'):
    base.config_logging("ctp_" + name + ".log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    trader_cfg = misc.TEST_TRADER
    user_cfg = misc.TEST_USER
    opt_strat = optionarb.OptionArbStrat(name,
                                    ['IF1509', 'IF1512'],
                                    [201509, 201512],
                                    [[3400, 3500, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 4000, 4100]]*2)
    ins_setup = {'IF1509':1}
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    tl_strat = strat_tl.TurtleTrader('ProdTL', under_tl, vol_tl, trade_unit = units_tl,
                                 agent = None, email_notify = [])
    
    ins_setup = {'IF1509':(0, 0.7, 0.0, 1, False)}
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
    ins_setup = {'IF1509': [[0.3, 0.07, 0.2], 1, 30, 1]}
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
    strategies = [tl_strat, dt_strat, rb_strat]
    folder = misc.get_prod_folder()
    strat_cfg = {'strategies': strategies, \
                 'folder': folder, \
                 'daily_data_days':21, \
                 'min_data_days':1,
                 'enable_option': True }
    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = False)
    myGui = Gui(myApp)
    myGui.mainloop()
    
def Soymeal_Opt(tday, name='Soymeal_Opt'):
    base.config_logging("ctp_" + name + ".log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    trader_cfg = misc.HT_OPTSIM_TRADER
    user_cfg = misc.HT_OPTSIM_USER
    ins_setup = {'m1601':5,
                 'm1605':5}
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    tl_strat = strat_tl.TurtleTrader('ProdTL', under_tl, vol_tl, trade_unit = units_tl,
                                 agent = None, email_notify = [])

    ins_setup = {'m1601':(0, 0.5, 0.0, 10, False),
                 'm1605':(0, 0.5, 0.0, 10, False)}
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
    ins_setup = {'m1601': [[0.3, 0.07, 0.2], 1, 30, 5],
                 'm1605': [[0.3, 0.07, 0.2], 1, 30, 5]}
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
    strategies = [tl_strat, dt_strat, rb_strat]
    folder = misc.get_prod_folder()
    strat_cfg = {'strategies': strategies, \
                 'folder': folder, \
                 'daily_data_days':21, \
                 'min_data_days':1,
                 'enable_option': True }
    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = True)
    myGui = Gui(myApp)
    myGui.mainloop()
    
if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        app_name = 'option_test'
    else:
        app_name = args[1]       
    if len(args) < 1:
        tday = datetime.date.today()
    else:
        tday = datetime.datetime.strptime(args[0], '%Y%m%d').date()
    params = (tday, app_name, )
    getattr(sys.modules[__name__], app_name)(*params)