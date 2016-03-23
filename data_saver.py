import agent
import datetime
import sys
import ctp_api
import lts_api
import time
import logging
import mysqlaccess
import misc
import base

def filter_main_cont(sdate, filter = True):
    insts, prods  = mysqlaccess.load_alive_cont(sdate)
    if filter:
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
    else:
        return insts
        
def save_ctp(tday):
    prod_md = misc.HT_PROD_MD
    base.config_logging("save_all_agent.log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    save_insts = filter_main_cont(tday, filter = False)
    print "total inst = %s" % len(save_insts)
    app_name = 'SaveAgent'
    config = {'daily_data_days': 0, 'min_data_days': 0}
    my_agent = agent.SaveAgent(name = app_name, trader = None, cuser = None, instruments=save_insts,tday = tday, config = config)
    ctp_api.make_user(my_agent, prod_md)
    try:
        my_agent.resume()
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        my_agent.exit()

def save_lts_test(tday):
    prod_md = misc.LTS_SO_USER
    base.config_logging("save_lts_test.log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    save_insts = ['510050']
    app_name = 'SaveAgent'
    config = {'daily_data_days': 0, 'min_data_days': 0}
    my_agent = agent.SaveAgent(name = app_name, trader = None, cuser = None, instruments=save_insts, tday = tday, config = config)
    lts_api.make_user(my_agent, prod_md)
    try:
        my_agent.resume()
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        my_agent.exit()

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        app_name = 'save_ctp'
    else:
        app_name = args[1]
    if len(args) < 1:
        tday = datetime.date.today()
    else:
        tday = datetime.datetime.strptime(args[0], '%Y%m%d').date()
    params = (tday, )
    getattr(sys.modules[__name__], app_name)(*params)