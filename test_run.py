import agent as agent
import fut_api
import lts_api
import base
import time
import logging
import mysqlaccess
import datetime
import misc

def save_LTS(user, insts, run_date):
    app_name = 'SaveAgent'
    my_agent = agent.SaveAgent(name = app_name, trader = None, cuser = None, instruments=insts, daily_data_days=0, min_data_days=0, tday = run_date)
    lts_api.make_user(my_agent, user, insts)
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        my_agent.mdapis = []; my_agent.trader = None

def filter_main_cont(sdate):
    insts, prods  = mysqlaccess.load_alive_cont(sdate)
    main_cont = {}
    for pc in prods:
        main_cont[pc], exch = mysqlaccess.prod_main_cont_exch(pc)
    main_insts = []
    for inst in insts:
        pc = misc.inst2product(inst)
        mth = int(inst[-2:])
        if mth in main_cont[pc]:
            main_insts.append(inst)
    return main_insts
        
def save_all(tday):
    logging.basicConfig(filename="save_all_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    save_insts = filter_main_cont(tday)
    app_name = 'SaveAgent'
    my_agent = agent.SaveAgent(name = app_name, trader = None, cuser = None, instruments=save_insts, daily_data_days=0, min_data_days=0, tday = tday)
    fut_api.make_user(my_agent, misc.PROD_USER)
    try:
        while 1:
            time.sleep(1)
            
    except KeyboardInterrupt:
        my_agent.mdapis = []; my_agent.trader = None

def save_lts_test(tday):
    logging.basicConfig(filename="save_lts_test.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    save_insts = ['510050', '510050C1502M02500', '510050P1502M02500']
    save_LTS(misc.LTS_SO_USER,save_insts)
    pass

if __name__ == '__main__':
    save_all()
    pass