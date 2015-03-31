import misc
import logging
import sys
import strat_dual_thrust as strat_dt
import strat_rbreaker as strat_rb

def prod_test(tday, name='prod_test'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    #trader_cfg = TEST_TRADER
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
    strategies = [rb_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':2, \
                 'min_data_days':1 }
    all_insts = ins_setup.keys()
    myagent, my_trader = emulator.create_agent_with_mocktrader(agent_name, all_insts, strat_cfg, tday)
    fut_api.make_user(myagent,user_cfg)
    myagent.resume()

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