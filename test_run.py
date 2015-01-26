import agent as agent
import fut_api
import lts_api
import base
import time
import logging
import mysqlaccess
import datetime
import misc

prod_user = base.BaseObject( broker_id="8070", 
                             investor_id="*", 
                             passwd="*", 
                             ports=["tcp://zjzx-md11.ctp.shcifco.com:41213"])
prod_trader = base.BaseObject( broker_id="8070", 
                               investor_id="750305", 
                               passwd="801289", 
                               ports=["tcp://zjzx-front12.ctp.shcifco.com:41205"])
test_user = base.BaseObject( broker_id="8000", 
                             investor_id="*", 
                             passwd="*", 
                             ports=["tcp://qqfz-md1.ctp.shcifco.com:32313"]
                             )
test_trader = base.BaseObject( broker_id="8000", 
                             investor_id="24661668", 
                             passwd="121862", 
                             ports=["tcp://qqfz-front1.ctp.shcifco.com:32305"])


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