import tradeagent as agent
import base
import time
import logging

prod_user = base.BaseObject( broker_id="8070", 
                             investor_id="*", 
                             passwd="*", 
                             port="tcp://zjzx-md11.ctp.shcifco.com:41213")
prod_trader = base.BaseObject( broker_id="8070", 
                               investor_id="750305", 
                               passwd="801289", 
                               port="tcp://zjzx-front12.ctp.shcifco.com:41205")
test_user = base.BaseObject( broker_id="8000", 
                             investor_id="*", 
                             passwd="*", 
                             port="tcp://qqfz-md1.ctp.shcifco.com:32313"
                             )
test_trader = base.BaseObject( broker_id="8000", 
                             investor_id="24661668", 
                             passwd="121862", 
                             port="tcp://qqfz-front1.ctp.shcifco.com:32305")
        
def test_trade():
    logging.basicConfig(filename="test_trade_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trade_insts = ['RM501','m1501','al1410']
    
    my_agent = agent.Agent(None, None, trade_insts)

    usercfg = test_user
        
    tradercfg = test_trader

    my_agent.cuser = user = agent.MdSpiDelegate(instruments=my_agent.instruments, 
                             broker_id=usercfg.broker_id,
                             investor_id= usercfg.investor_id,
                             passwd= usercfg.passwd,
                             agent = my_agent,
                             )
    user.Create('TestTrader-user')
    user.RegisterFront(usercfg.port)
    user.Init()
    
    my_agent.trader = trader = agent.TraderSpiDelegate(instruments=my_agent.instruments, 
                             broker_id=tradercfg.broker_id,
                             investor_id= tradercfg.investor_id,
                             passwd= tradercfg.passwd,
                             agent = my_agent,
                       )
    trader.Create('TestTrader-trader')
    #trader.SubscribePublicTopic(agent.THOST_TERT_QUICK)
    #trader.SubscribePrivateTopic(agent.THOST_TERT_QUICK)
    trader.RegisterFront(tradercfg.port)
    trader.Init()
    

    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        my_agent.mdapis = [] 
        my_agent.trader = None

if __name__ == '__main__':
    test_trade()