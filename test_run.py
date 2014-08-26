import newagent
import base
import time
import logging

save_insts = ['IF1409', 'IF1412', 'IF1408', 'TF1503', 'TF1412', 'TF1409', 
        'SR501', 'RM409', 'RS409', 'WH409', 'SR409', 'FG408', 'ME408', 'TA408',
          'RM408', 'RS408', 'CF409', 'OI409', 'PM409', 'RI409', 'TA409', 'SR503', 'FG409', 
           'ME409', 'JR409', 'JR411', 'TC408', 'TC410', 'FG410', 'WH411', 'TA411', 
           'OI411', 'RI411', 'PM411', 'FG411', 'RM411', 'RS411', 'TC412', 'FG412', 'ME412', 
           'ME410', 'TA410', 'TC411', 'TA412', 'TC409', 'CF411', 'ME411', 'SR505', 
           'TC504', 'RM505', 'TA506', 'CF501', 'WH501', 'FG501', 'CF503', 'TA503', 'FG503', 
           'CF505', 'TA505', 'OI505', 'TC501', 'FG502', 'FG504', 'RI505', 'PM505', 'FG505', 
           'JR505', 'SR511', 'TC506', 'FG506', 'TC503', 'TA504', 'ME504', 'ME505',
           'WH503', 'RM503', 'SR509', 'TC505', 'WH505', 'MA506', 'RI501', 'SR507', 'PM501',
        'TC502', 'ME502', 'TA502', 'TA501', 'OI501', 'ME501', 'RM501', 'JR501', 'OI503', 
            'RI503', 'ME503', 'PM503', 'JR503', 'c1409', 'j1409', 'jm1409', 'l1409', 
            'a1409', 'a1411', 'a1501', 'j1408', 'jm1408', 'l1408', 'm1408', 'p1408', 'v1408', 
            'y1408', 'b1409', 'm1409', 'p1409', 'v1409', 'y1409', 'a1503', 'j1410','l1410', 
            'a1505', 'i1411', 'jd1411', 'jm1410', 'p1410', 'v1410', 'jd1409',  
            'i1408', 'i1409', 'i1410', 'b1411', 'i1412', 'j1412', 'jd1412', 'jm1412', 'l1412', 
            'p1412', 'v1412', 'bb1408', 'jd1410', 'c1411', 'j1411', 'jm1411', 
            'l1411', 'm1411', 'p1411', 'v1411', 'y1411', 'fb1412', 'b1501', 'bb1501', 
            'fb1501', 'jm1501', 'm1501', 'v1501', 'y1501', 'jd1503', 'jm1503', 'v1503', 'y1503',
            'fb1504', 'pp1505', 'y1505', 'a1511', 'm1412', 'y1412', 'bb1412', 'a1509', 'bb1504', 
            'j1504', 'l1504', 'p1504', 'bb1409', 'jd1502', 'fb1502', 'b1503', 'l1503', 
            'pp1503', 'jd1505', 'jm1505', 'm1505', 'p1505', 'v1505', 'bb1410', 'bb1411', 
            'fb1411', 'fb1410', 'fb1408', 'jm1504', 'b1505', 'bb1505', 'bb1506', 'p1503', 
            'i1504', 'jd1504', 'pp1504', 'v1504', 'c1505', 'fb1505', 'i1505', 'j1505', 'l1505',
            'fb1506', 'i1506', 'j1506', 'jd1506', 'p1506', 'pp1506', 'pp1408', 'pp1409', 
            'jm1506', 'l1506', 'v1506', 'a1507', 'c1501', 'i1501', 'j1501', 'jd1501', 
            'l1501', 'p1501', 'i1502', 'j1502', 'jm1502', 'l1502', 'p1502', 'v1502', 'bb1502', 
            'fb1409', 'pp1410', 'pp1411', 'pp1412', 'pp1501', 'pp1502', 'bb1503', 
            'c1503', 'fb1503', 'i1503', 'j1503', 'm1503', 'pb1409', 'ru1409', 'wr1409', 'ag1408',
             'al1408', 'au1408', 'cu1408', 'pb1408', 'rb1408', 'ru1408', 'wr1408', 'zn1408',
             'fu1409', 'fu1410', 'ag1409', 'al1409', 'cu1409', 'rb1409', 'zn1409', 'bu1409', 
        'bu1503', 'rb1410', 'ag1411', 'al1411', 'cu1411',
        'rb1411', 'ru1411', 'zn1411', 'wr1411', 'fu1412', 'ag1412', 'cu1412', 'bu1509',
            'wr1410', 'al1412', 'au1412', 'pb1412', 'rb1412', 'wr1412', 'fu1501', 'bu1412',
             'pb1411', 'zn1412', 'bu1512', 'bu1506', 'ag1410', 'al1410', 'cu1410', 'zn1410',
             'pb1410', 'ru1410', 'au1410', 'fu1411', 'rb1501', 'hc1408', 'fu1505',
              'ag1505', 'cu1505', 'pb1505', 'ag1506', 'al1506', 'al1501', 'cu1501', 'ag1501',
              'al1502', 'rb1502', 'zn1502', 'bu1408', 'ag1503', 'rb1503', 'wr1503', 'au1504',
        'bu1411', 'cu1506', 'fu1503', 'hc1409', 'hc1412', 'hc1503', 'cu1504', 'al1505',
            'zn1505', 'fu1506', 'bu1603', 'wr1504', 'bu1410', 'ru1505', 'rb1505', 'wr1505',
             'hc1505', 'zn1506', 'ru1506', 'wr1506', 'hc1506', 'au1409', 'fu1507', 'ag1502',
              'cu1502', 'pb1502', 'wr1502', 'al1503', 'fu1504', 'pb1504', 'rb1504', 'ru1504',
        'zn1504', 'hc1504', 'wr1501', 'hc1410', 'hc1411', 'hc1501', 'hc1502', 'ag1504',
            'al1504', 'pb1506', 'rb1506', 'bu1606', 'zn1501', 'pb1501', 'ru1501', 
             'au1502', 'cu1503', 'zn1503', 'pb1503', 'ru1503']

option_insts=['IO1408-C-2300','IO1408-P-2300',
              'IO1408-C-2250','IO1408-P-2250','IO1408-C-2200','IO1408-P-2200','IO1408-C-2150','IO1408-P-2150',
              'IO1408-C-2100','IO1408-P-2100','IO1408-C-2050','IO1408-P-2050','IO1408-C-2000','IO1408-P-2000',
              'IO1409-C-2300','IO1409-P-2300','IO1409-C-2250','IO1409-P-2250','IO1409-C-2200','IO1409-P-2200',
              'IO1409-C-2150','IO1409-P-2150','IO1409-C-2100','IO1409-P-2100','IO1409-C-2050','IO1409-P-2050',
              'IO1409-C-2000','IO1409-P-2000']

prod_user = base.BaseObject( broker_id="8070", 
                             investor_id="*", 
                             passwd="*", 
                             port="tcp://zjzx-md11.ctp.shcifco.com:41213")
prod_trader = base.BaseObject( broker_id="8070", 
                               investor_id="750305", 
                               passwd="801289", 
                               ports=["tcp://zjzx-front12.ctp.shcifco.com:41205"])
test_user = base.BaseObject( broker_id="8000", 
                             investor_id="*", 
                             passwd="*", 
                             port="tcp://qqfz-md1.ctp.shcifco.com:32313"
                             )
test_trader = base.BaseObject( broker_id="8000", 
                             investor_id="24661668", 
                             passwd="121862", 
                             ports=["tcp://qqfz-front1.ctp.shcifco.com:32305"])
def save_main(user, insts):
    my_agent = newagent.SaveAgent(None,None,insts)
    app_name = 'SaveAgent'
    newagent.make_user(my_agent,user,app_name)
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        my_agent.mdapis = []; my_agent.trader = None

def create_agent(usercfg, tradercfg, insts):
    agent_name = 'TradeAgent'
    trader, my_agent = newagent.create_trader(tradercfg, insts)
    newagent.make_user(my_agent,usercfg,agent_name)
    return my_agent

        
def save_all():
    logging.basicConfig(filename="save_all_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    save_main(prod_user,save_insts)
    pass

def save_option():
    logging.basicConfig(filename="save_option_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    save_main(test_user,option_insts)
    pass

if __name__ == '__main__':
    insts = ['ag1412','au1412']
    my_agent = create_agent(prod_user, prod_trader, insts)
    
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        my_agent.mdapis = []; my_agent.trader = None
    pass