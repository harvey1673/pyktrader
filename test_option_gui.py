from agent_gui import * 
import agent
import datetime
import misc
import logging
import sys
import optionarb
import strat_dual_thrust as strat_dt
import strat_rbreaker as strat_rb
import strat_turtle as strat_tl
import optstrat

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
    
def main(tday, name='option_test'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = misc.TEST_TRADER
    user_cfg = misc.TEST_USER
    #opt_strat = optionarb.OptionArbStrat(name, 
    #                                ['IF1507', 'IF1508', 'IF1509'], 
    #                                [201507, 201508, 201509],
    #                                [[4100, 4200, 4250, 4300, 4350, 4400, 4450, 4500, 4600]]*3)
    ins_setup = {'IF1507':1}
    insts = ins_setup.keys()
    units_tl = [ins_setup[inst] for inst in insts]
    under_tl = [[inst] for inst in insts]
    vol_tl = [[1] for inst in insts]
    tl_strat = strat_tl.TurtleTrader('ProdTL', under_tl, vol_tl, trade_unit = units_tl,
                                 agent = None, email_notify = [])
    
    ins_setup = {'IF1507':(0, 0.7, 0.0, 1, False)}
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
    ins_setup = {'IF1507': [[0.3, 0.07, 0.2], 1, 30, 1]}
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
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':21, \
                 'min_data_days':1,
                 'enable_option': True }
    
    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = False)
    myGui = Gui(myApp)
    myGui.mainloop()
    
def m_opt_sim(tday, name='Soymeal_Opt'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = misc.HT_OPTSIM_TRADER
    user_cfg = misc.HT_OPTSIM_USER
    opt_strat = optstrat.CommodOptStrat(name, 
                                    ['m1509', 'm1601'], 
                                    [datetime.datetime(2015, 8, 7, 15, 0, 0), 
                                     datetime.datetime(2015, 12,7, 15, 0, 0)],
                                    [[2600 + 50 * i for i in range(10)],
                                     [2500 + 50 * i for i in range(13)]])
    insts_dt = ['m1509']
    units_dt = [2]*len(insts_dt)
    under_dt = [[inst] for inst in insts_dt]
    vols_dt = [[1]]*len(insts_dt)
    lookbacks_dt = [0]*len(insts_dt)
    ratios = [[0.4, 0.5]]*len(insts_dt)
    dt_strat = strat_dt.DTTrader('DT_test', under_dt, vols_dt, trade_unit = units_dt, ratios= ratios, lookbacks = lookbacks_dt, agent = None, daily_close = [False], email_notify = [])
    
    ins_setup = {'m1509': [[0.35, 0.07, 0.25], 2,  30]}
    insts_rb = ins_setup.keys()
    units_rb = [ins_setup[inst][1] for inst in insts_rb]
    under_rb = [[inst] for inst in insts_rb]
    vol_rb = [[1] for inst in insts_rb]
    ratios = [ins_setup[inst][0] for inst in insts_rb]
    min_rng = [ins_setup[inst][2] for inst in insts_rb]
    stop_loss = 0.0
    rb_strat = strat_rb.RBreakerTrader('RBreaker', under_rb, vol_rb, trade_unit = units_rb,
                                 ratios = ratios, min_rng = min_rng, trail_loss = stop_loss, freq = 1, 
                                 agent = None, email_notify = [])
    strategies = [opt_strat, dt_strat, rb_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':5, \
                 'min_data_days':1 }
    
    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = True)
    myGui = Gui(myApp)
    #myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
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

    #m_opt_sim(tday, app_name)    
    main(tday, app_name)