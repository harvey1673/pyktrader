#-*- coding:utf-8 -*-
import ctp.lts
from agent import *
from base import *
from misc import *
import logging
import order

class LtsMdSpi(CTPMdMixin, ctp.lts.MdApi):
    '''
        将行情信息转发到Agent
        并自行处理杂务
    '''
    logger = logging.getLogger('ctp.LtsMdSpi')
    ApiStruct = ctp.lts.ApiStruct
    def __init__(self,
            instruments, #合约映射 name ==>c_instrument
            broker_id,   #期货公司ID
            investor_id, #投资者ID
            passwd, #口令
            agent,  #实际操作对象
        ):            
        self.instruments = instruments
        self.broker_id =broker_id
        self.investor_id = investor_id
        self.passwd = passwd
        self.front_id = None
        self.session_id = None
        self.agent = agent
        ##必须在每日重新连接时初始化它. 这一点用到了生产行情服务器收盘后关闭的特点(模拟的不关闭)
        self.last_day = datetime.date.today().strftime('%Y%m%d')
        agent.add_mdapi(self)
        pass

    def subscribe_market_data(self, instruments):
        inst_set = set(instruments)
        for exch in CHN_Stock_Exch:
            insts = list(inst_set & set(CHN_Stock_Exch[exch]))
            if len(insts)>0:
                self.SubscribeMarketData(insts, exch)

    def market_data2tick(self, dp, timestamp):
        #print dp
        #market_data的格式转换和整理, 交易数据都转换为整数
        try:
            #rev的后四个字段在模拟行情中经常出错
            rev = StockTick(instID=dp.InstrumentID, timestamp=timestamp, openInterest=dp.OpenInterest, volume=dp.Volume, turnover=dp.Turnover, 
                            price=dp.LastPrice, open=dp.OpenPrice, close=dp.ClosePrice, high=dp.HighestPrice, low=dp.LowestPrice,
                            up_limit = dp.UpperLimitPrice, down_limit = dp.LowerLimitPrice,
                            bidPrice1=dp.BidPrice1, bidVol1=dp.BidVolume1,askPrice1=dp.AskPrice1, askVol1=dp.AskVolume1,
                            bidPrice2=dp.BidPrice2, bidVol2=dp.BidVolume2, askPrice2=dp.AskPrice2, askVol2=dp.AskVolume2,
                            bidPrice3=dp.BidPrice3, bidVol3=dp.BidVolume3, askPrice3=dp.AskPrice3, askVol3=dp.AskVolume3,
                            bidPrice4=dp.BidPrice4, bidVol4=dp.BidVolume4, askPrice4=dp.AskPrice4, askVol4=dp.AskVolume4,
                            bidPrice5=dp.BidPrice5, bidVol5=dp.BidVolume5, askPrice5=dp.AskPrice5, askVol5=dp.AskVolume5 )
        except Exception,inst:
            self.logger.warning(u'MD:%s 行情数据转换错误:updateTime="%s"' % (dp.InstrumentID, timestamp))
        #print rev
        return rev

class LtsTraderSpi(CTPTraderQryMixin, CTPTraderRspMixin, ctp.lts.TraderApi):
    '''
        将服务器回应转发到Agent
        并自行处理杂务
    '''
    logger = logging.getLogger('ctp.LtsTraderSpi')    
    ApiStruct = ctp.lts.ApiStruct
    def __init__(self,
            instruments, #合约映射 name ==>c_instrument 
            broker_id,   #期货公司ID
            investor_id, #投资者ID
            passwd, #口令
            agent,  #实际操作对象
        ):        
        self.name = 'LTS-TD'
        self.instruments = instruments
        self.broker_id = broker_id
        self.investor_id = investor_id
        self.passwd = passwd
        self.agent = agent
        self.agent.set_spi(self)
        self.is_logged = False
        self.ctp_orders = {}
        self.ctp_trades = {}
                
#    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
#        CTPTraderRspMixin.OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast)
#        self.confirm_settlement_info()
        
    def check_order_status(self):
        Is_Set = False
        if len(self.ctp_orders)>0:
            for order_ref in self.ctp_orders:
                if order_ref in self.ref2order:
                    iorder = self.ref2order[order_ref]
                    sorder = self.ctp_orders[order_ref]
                    iorder.sys_id = sorder.OrderSysID
                    if sorder.OrderStatus in [self.ApiStruct.OST_NoTradeQueueing, self.ApiStruct.OST_PartTradedQueueing, self.ApiStruct.OST_Unknown]:
                        if iorder.status != order.OrderStatus.Sent or iorder.conditionals != {}:
                            self.logger.warning('order status for OrderSysID = %s, Inst=%s is set to %s, but should be waiting in exchange queue' % (iorder.sys_id, iorder.instrument.name, iorder.status)) 
                            iorder.status = order.OrderStatus.Sent
                            iorder.conditionals = {}
                            Is_Set = True
                    elif sorder.OrderStatus in [self.ApiStruct.OST_Canceled, self.ApiStruct.OST_PartTradedNotQueueing, self.ApiStruct.OST_NoTradeNotQueueing]:
                        if iorder.status != order.OrderStatus.Cancelled:
                            self.logger.warning('order status for OrderSysID = %s, Inst=%s is set to %s, but should be cancelled' % (iorder.sys_id, iorder.instrument.name, iorder.status)) 
                            iorder.on_cancel()
                            Is_Set = True 

            self.ctp_orders = {} #{ o: self.ctp_orders[o] for o in order_list}
        return Is_Set

def make_user(my_agent,hq_user, insts):
    #print my_agent.instruments
    for port in hq_user.ports:
        user = LtsMdSpi(instruments=insts, 
                             broker_id=hq_user.broker_id,
                             investor_id= hq_user.investor_id,
                             passwd= hq_user.passwd,
                             agent = my_agent,
                    )
        user.Create(my_agent.name)
        user.RegisterFront(port)
        user.Init()

def create_trader(trader_cfg, instruments, strat_cfg, agent_name, tday=datetime.date.today()):
    strategies = strat_cfg['strategies']
    folder = strat_cfg['folder']
    daily_days = strat_cfg['daily_data_days']
    min_days = strat_cfg['min_data_days']
    myagent = Agent(agent_name, None, None, instruments, strategies, tday, folder, daily_days, min_days) 
    myagent.trader = trader = LtsTraderSpi(instruments=myagent.instruments.keys(), 
                             broker_id=trader_cfg.broker_id,
                             investor_id= trader_cfg.investor_id,
                             passwd= trader_cfg.passwd,
                             agent = myagent,
                       )
    trader.Create('trader')
    trader.SubscribePublicTopic(trader.ApiStruct.TERT_QUICK)
    trader.SubscribePrivateTopic(trader.ApiStruct.TERT_QUICK)
    for port in trader_cfg.ports:
        trader.RegisterFront(port)
    trader.Init()
    return trader, myagent

def create_agent(agent_name, usercfg, tradercfg, insts, strat_cfg, tday = datetime.date.today()):
    trader, my_agent = create_trader(tradercfg, insts, strat_cfg, agent_name, tday)
    make_user(my_agent,usercfg, insts)
    return my_agent

if __name__=="__main__":
    pass
    #test_main()
