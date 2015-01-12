import agent as agent
import fut_api
import lts_api
import base
import time
import logging
import mysqlaccess
import datetime
import misc

save_insts = ['IF1411','IF1412','IF1501','IF1502','IF1503','IF1506',
			  'TF1411','TF1412','TF1501','TF1502','TF1503','TF1506',
			  'cu1411','cu1412','cu1501','cu1502','cu1503','cu1504',
			  'cu1505','cu1506','cu1507','cu1508','cu1509','cu1510',
			  'al1411','al1412','al1501','al1502','al1503','al1504',
			  'al1505','al1506','al1507','al1508','al1509','al1510',
			  'zn1411','zn1412','zn1501','zn1502','zn1503','zn1504',
			  'zn1505','zn1506','zn1507','zn1508','zn1509','zn1510',
			  'pb1411','pb1412','pb1501','pb1502','pb1503','pb1504',
			  'pb1505','pb1506','pb1507','pb1508','pb1509','pb1510',
			  'ru1501','ru1505','ru1509','au1412','au1506','au1512','ag1412','ag1506','ag1512',
			  'rb1501','rb1505','rb1510','bu1501','bu1505','bu1509',
			  'hc1501','hc1505','hc1509',
			  'c1501','c1505','c1509','c1601','c1605','c1609',
			  'a1501','a1505','a1509','a1601','a1605','a1609',
			  'm1501','m1505','m1509','y1501','y1505','y1509',
			  'p1501','p1505','p1509','l1501','l1505','l1509',
			  'v1501','v1505','v1509','j1501','j1505','j1509',
			  'jm1501','jm1505','jm1509','i1501','i1505','i1509',
			  'jd1501','jd1505','jd1509','fb1501','fb1505','fb1509',
			  'bb1501','bb1505','bb1509','pp1501','pp1505','pp1509',
			  'WH501','WH505','WH509','CF501','CF505','CF509',
			  'SR501','SR505','SR509','SR601','SR605','SR609',
			  'OI501','OI505','OI509','TA501','TA505','TA509',
			  'TC501','TC505','TC509','ME501','ME505','ME509',
			  'FG501','FG505','FG509','RS501','RS505','RS509',
			  'RM501','RM505','RM509','PM501','PM505','PM509',
			  'RI501','RI505','RI509','JR501','JR505','JR509',
			  'LR501','LR505','LR509','SM501','SM505','SM509',
			  'SF501','SF505','SF509' ]

option_insts=['IO1409-C-2500','IO1409-P-2500','IO1409-C-2450','IO1409-P-2450','IO1409-C-2400','IO1409-P-2400',
              'IO1409-C-2350','IO1409-P-2350','IO1409-C-2300','IO1409-P-2300','IO1409-C-2250','IO1409-P-2250',
              'IO1409-C-2200','IO1409-P-2200']

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
def save_main(user, insts, run_date):
    app_name = 'SaveAgent'
    my_agent = agent.SaveAgent(name = app_name, trader = None, cuser = None, instruments=insts, daily_data_days=0, min_data_days=0, tday = run_date)
    fut_api.make_user(my_agent,user)
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        my_agent.mdapis = []; my_agent.trader = None

def save_LTS(user, insts, run_date):
    app_name = 'SaveAgent'
    my_agent = agent.SaveAgent(name = app_name, trader = None, cuser = None, instruments=insts, daily_data_days=0, min_data_days=0, tday = run_date)
    lts_api.make_user(my_agent, user, insts)
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        my_agent.mdapis = []; my_agent.trader = None
        
# 		
# def create_agent(usercfg, tradercfg, insts):
#     agent_name = 'TradeAgent'
#     trader, my_agent = fut_api.create_trader(tradercfg, insts)
#     fut_api.make_user(my_agent,usercfg,agent_name)
#     return my_agent

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
    save_main(misc.PROD_USER,save_insts, tday)
    pass

def save_lts_test(tday):
    logging.basicConfig(filename="save_lts_test.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    save_insts = ['600104', '000300', '510180', '600104C1412M01400', '600104C1412A01400', '399001', '399004', '399007']
    save_LTS(misc.LTS_SO_USER,save_insts)
    pass
   
def save_option():
    logging.basicConfig(filename="save_option_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    save_main(test_user,option_insts)
    pass

if __name__ == '__main__':
    save_all()
    pass