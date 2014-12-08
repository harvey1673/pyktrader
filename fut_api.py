# -*- coding: utf-8 -*-
import ctp.futures
from agent import *
from base import *
import logging
import order

class MdSpiDelegate(CTPMdMixin, ctp.futures.MdApi):
    '''
        将行情信息转发到Agent
        并自行处理杂务
    '''
    logger = logging.getLogger('ctp.MdSpiDelegate')
    ApiStruct = ctp.futures.ApiStruct
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
        self.last_day = 0
        agent.add_mdapi(self)
        pass

    def subscribe_market_data(self, instruments):
        self.SubscribeMarketData(instruments)

    def market_data2tick(self, dp, timestamp):
        #market_data的格式转换和整理, 交易数据都转换为整数
        try:
            #rev的后四个字段在模拟行情中经常出错
            rev = TickData(instID=dp.InstrumentID, timestamp=timestamp, openInterest=dp.OpenInterest, 
                           volume=dp.Volume, price=dp.LastPrice, 
                           high=dp.HighestPrice, low=dp.LowestPrice, 
                           bidPrice1=dp.BidPrice1, bidVol1=dp.BidVolume1, 
                           askPrice1=dp.AskPrice1, askVol1=dp.AskVolume1)
        except Exception,inst:
            self.logger.warning(u'MD:%s 行情数据转换错误:updateTime="%s"' % (dp.InstrumentID, timestamp))
        return rev

class TraderSpiDelegate(CTPTraderQryMixin, CTPTraderRspMixin, ctp.futures.TraderApi):
    '''
        将服务器回应转发到Agent
        并自行处理杂务
    '''
    logger = logging.getLogger('ctp.TraderSpiDelegate')    
    ApiStruct = ctp.futures.ApiStruct
    def __init__(self,
            instruments, #合约映射 name ==>c_instrument 
            broker_id,   #期货公司ID
            investor_id, #投资者ID
            passwd, #口令
            agent,  #实际操作对象
        ):        
        self.instruments = instruments
        self.broker_id = broker_id
        self.investor_id = investor_id
        self.passwd = passwd
        self.agent = agent
        self.agent.set_spi(self)
        self.is_logged = False
        self.ctp_orders = {}
        self.ctp_trades = {}
                
    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        CTPTraderRspMixin.OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast)
        self.confirm_settlement_info()

    def query_settlement_confirm(self):
        '''
            这个基本没用，不如直接确认
            而且需要进一步明确：有史以来第一次确认前查询确认情况还是每天第一次确认查询情况时，返回的响应中
                pSettlementInfoConfirm为空指针. 如果是后者,则建议每日不查询确认情况,或者在generate_struct中对
                CThostFtdcSettlementInfoConfirmField的new_函数进行特殊处理
            CTP写代码的这帮家伙素质太差了，边界条件也不测试，后置断言也不整，空指针乱飞
            2011-3-1 确认每天未确认前查询确认情况时,返回的响应中pSettlementInfoConfirm为空指针
            并且妥善处理空指针之后,仍然有问题,在其中查询结算单无动静
        '''
        req = self.ApiStruct.QrySettlementInfoConfirm(BrokerID=self.broker_id,InvestorID=self.investor_id)
        self.ReqQrySettlementInfoConfirm(req,self.agent.inc_request_id())

    def query_settlement_info(self):
        #不填日期表示取上一天结算单,并在响应函数中确认
        self.logger.info(u'TD:取上一日结算单信息并确认,BrokerID=%s,investorID=%s' % (self.broker_id,self.investor_id))
        req = self.ApiStruct.QrySettlementInfo(BrokerID=self.broker_id,InvestorID=self.investor_id,TradingDay=u'')
        #print req.BrokerID,req.InvestorID,req.TradingDay
        time.sleep(1)
        self.ReqQrySettlementInfo(req,self.agent.inc_request_id())

    def confirm_settlement_info(self):
        self.logger.info(u'TD-CSI:准备确认结算单')
        req = self.ApiStruct.SettlementInfoConfirm(BrokerID=self.broker_id,InvestorID=self.investor_id)
        self.ReqSettlementInfoConfirm(req,self.agent.inc_request_id())

    def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
        '''请求查询投资者结算信息响应'''
        print u'Rsp 结算单查询'
        if(self.resp_common(pRspInfo,bIsLast,u'结算单查询')>0):
            self.logger.info(u'结算单查询完成,准备确认')
            try:
                self.logger.info(u'TD:结算单内容:%s' % pSettlementInfo.Content)
            except Exception,inst:
                self.logger.warning(u'TD-ORQSI-A 结算单内容错误:%s' % str(inst))
            self.confirm_settlement_info()
        else:  #这里是未完成分支,需要直接忽略
            try:
                self.logger.info(u'TD:结算单接收中...:%s' % pSettlementInfo.Content)
            except Exception,inst:
                self.logger.warning(u'TD-ORQSI-B 结算单内容错误:%s' % str(inst))
            #self.agent.initialize()
            pass

    def OnRspQrySettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        '''请求查询结算信息确认响应'''
        self.logger.debug(u"TD:结算单确认信息查询响应:rspInfo=%s,结算单确认=%s" % (pRspInfo,pSettlementInfoConfirm))
        #self.query_settlement_info()
        if(self.resp_common(pRspInfo,bIsLast,u'结算单确认情况查询')>0):
            if(pSettlementInfoConfirm == None or int(pSettlementInfoConfirm.ConfirmDate) < int(self.agent.scur_day.strftime('%Y%m%d'))):
                #其实这个判断是不对的，如果周日对周五的结果进行了确认，那么周一实际上已经不需要再次确认了
                if(pSettlementInfoConfirm != None):
                    self.logger.info(u'TD:最新结算单未确认，需查询后再确认,最后确认时间=%s,scur_day:%s' % (pSettlementInfoConfirm.ConfirmDate,self.agent.scur_day))
                else:
                    self.logger.info(u'TD:结算单确认结果为None')
                self.query_settlement_info()
            else:
                self.agent.isSettlementInfoConfirmed = True
                self.logger.info(u'TD:最新结算单已确认，不需再次确认,最后确认时间=%s,scur_day:%s' % (pSettlementInfoConfirm.ConfirmDate,self.agent.scur_day))
                self.agent.initialize()

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        '''投资者结算结果确认响应'''
        if(self.resp_common(pRspInfo,bIsLast,u'结算单确认')>0):
            self.agent.isSettlementInfoConfirmed = True
            self.logger.info(u'TD:结算单确认时间: %s-%s' %(pSettlementInfoConfirm.ConfirmDate,pSettlementInfoConfirm.ConfirmTime))
        self.agent.initialize()
        
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

def make_user(my_agent,hq_user):
    #print my_agent.instruments
    for port in hq_user.ports:
        user = MdSpiDelegate(instruments=my_agent.instruments.keys(), 
                             broker_id=hq_user.broker_id,
                             investor_id= hq_user.investor_id,
                             passwd= hq_user.passwd,
                             agent = my_agent,
                    )
        user.Create(my_agent.name)
        user.RegisterFront(port)
        user.Init()

def create_trader(trader_cfg, instruments, strat_cfg, agent_name, tday=datetime.date.today()):
    logging.basicConfig(filename="ctp_trade.log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    logging.info(u'broker_id=%s,investor_id=%s,passwd=%s' % (trader_cfg.broker_id,trader_cfg.investor_id,trader_cfg.passwd))
    strategies = strat_cfg['strategies']
    folder = strat_cfg['folder']
    daily_days = strat_cfg['daily_data_days']
    min_days = strat_cfg['min_data_days']
    myagent = Agent(agent_name, None, None, instruments, strategies, tday, folder, daily_days, min_days) 
    myagent.trader = trader = TraderSpiDelegate(instruments=myagent.instruments, 
                             broker_id=trader_cfg.broker_id,
                             investor_id= trader_cfg.investor_id,
                             passwd= trader_cfg.passwd,
                             agent = myagent,
                       )
    trader.Create('trader')
    trader.SubscribePublicTopic(trader.ApiStruct.THOST_TERT_QUICK)
    trader.SubscribePrivateTopic(trader.ApiStruct.THOST_TERT_QUICK)
    for port in trader_cfg.ports:
        trader.RegisterFront(port)
    trader.Init()
    return trader, myagent

def create_agent(agent_name, usercfg, tradercfg, insts, strat_cfg, tday = datetime.date.today()):
    trader, my_agent = create_trader(tradercfg, insts, strat_cfg, agent_name, tday)
    make_user(my_agent,usercfg)
    return my_agent
