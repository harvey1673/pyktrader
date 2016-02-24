import tradeagent as agent
import datetime
import sys
import time
import logging
import mysqlaccess
import misc
import base

def filter_main_cont(sdate, filter = False):
    insts, prods  = mysqlaccess.load_alive_cont(sdate)
    if not filter:
        return insts
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
        
def save_ctp(tday, config_file, filter = False):
    base.config_logging("save_all_agent.log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    app_name = 'SaveAgent'
    scur_day = datetime.datetime.strptime(tday, '%Y%m%d').date()
    save_agent = agent.SaveAgent(name = app_name, tday = scur_day, config_file = config_file)
    curr_insts = filter_main_cont(tday, False)
    for inst in curr_insts:
        save_agent.add_instrument(inst)
    try:
        save_agent.restart()
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        save_agent.exit()

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 4:
        filter = False
    else:
        filter = (int(args[3])>=1)
    if len(args) < 3:
        config_file = 'data_saver.json'
    else:
        config_file = args[2]
    if len(args) < 2:
        app_name = 'save_ctp'
    else:
        app_name = args[1]
    if len(args) < 1:
        tday = datetime.date.today().strftime('%Y%m%d')
    else:
        tday = args[0]
    params = (tday, config_file, filter)
    getattr(sys.modules[__name__], app_name)(*params)