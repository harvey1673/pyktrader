import tradeagent as agent
import datetime
import sys
import time
import logging
import mysqlaccess
import misc
import base
import json
from agent_gui import *

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

def save_ctp(name, config_file, tday, filter):
    base.config_logging(name + "_agent.log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    scur_day = datetime.datetime.strptime(tday, '%Y%m%d').date()
    filter_flag = (int(filter)>0)
    config = {}
    with open(config_file, 'r') as infile:
        config = json.load(infile)
    save_agent = agent.SaveAgent(name = name, tday = scur_day, config = config)
    curr_insts = filter_main_cont(tday, filter_flag)
    for inst in curr_insts:
        save_agent.add_instrument(inst)
    try:
        save_agent.restart()
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        save_agent.exit()

def run(name, config_file, tday, agent_class = 'agent.Agent'):
    base.config_logging("ctp_" + name + ".log", level=logging.DEBUG,
                   format = '%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s',
                   to_console = True,
                   console_level = logging.INFO)
    scur_day = datetime.datetime.strptime(tday, '%Y%m%d').date()
    myApp = MainApp(name, scur_day, config_file, agent_class = agent_class, master = None)
    myGui = Gui(myApp)
    # myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
    myGui.mainloop()

if __name__ == '__main__':
    args = sys.argv[1:]
    app_name = args[0]
    params = (args[1], args[2], args[3], args[4], )
    getattr(sys.modules[__name__], app_name)(*params)