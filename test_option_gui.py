from agent_gui import * 
import agent
import misc
import logging
import sys
import optstrat
import strat_dual_thrust as strat_dt
import strat_rbreaker as strat_rb
 
def main(tday, name='option_test'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = misc.TEST_TRADER
    user_cfg = misc.TEST_USER
    opt_strat = optstrat.IndexFutOptStrat(name, 
                                    ['IF1504', 'IF1506'], 
                                    [datetime.datetime(2015, 4, 17, 15, 0, 0), datetime.datetime(2015,6,19,15,0,0)],
                                    [[3400, 3450, 3500, 3550, 3600, 3650]]*2)
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
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':3, \
                 'min_data_days':1 }
    
    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None)
    myGui = Gui(myApp)
    myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
    myGui.mainloop()
    
def m_opt_sim(tday, name='Soymeal_Opt'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = misc.DCE_OPT_TRADER
    user_cfg = misc.DCE_OPT_USER
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
    myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
    myGui.mainloop()
    
if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        app_name = 'Soymeal_Opt'
    else:
        app_name = args[1]       
    if len(args) < 1:
        tday = datetime.date.today()
    else:
        tday = datetime.datetime.strptime(args[0], '%Y%m%d').date()

    m_opt_sim(tday, app_name)    
    