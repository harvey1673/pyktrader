#-*- coding:utf-8 -*-
import workdays
import sched
import time
import datetime
import logging
import threading
import bisect
import mysqlaccess
import misc
import order as order
import math
import os
import csv

from base import *

from ctp.futures import ApiStruct, MdApi, TraderApi

CANCEL_PROTECT_PERIOD = 20
#数据定义中唯一一个enum
THOST_TERT_RESTART  = ApiStruct.TERT_RESTART
THOST_TERT_RESUME   = ApiStruct.TERT_RESUME
THOST_TERT_QUICK    = ApiStruct.TERT_QUICK

min_data_list = ['datetime', 'min_id', 'open', 'high','low', 'close', 'volume', 'openInterest'] 
day_data_list = ['date', 'open', 'high','low', 'close', 'volume', 'openInterest']

def get_tick_id(dt):
    return ((dt.hour+6)%24)*100000+dt.minute*1000+dt.second*10+dt.microsecond/100000

class TickData:
    def __init__(self, instID='IF1412', high=0.0, low=0.0, price=0.0, volume=0, openInterest=0, 
                 bidPrice1=0.0, bidVol1=0, askPrice1=0.0, askVol1=0, timestamp=datetime.datetime.now()):
        self.instID = instID
        self.high = high
        self.low = low
        self.price = price
        self.volume = volume
        self.openInterest = openInterest
        self.bidPrice1 = bidPrice1
        self.bidVol1 = bidVol1
        self.askPrice1 = askPrice1
        self.askVol1 = askVol1
        self.timestamp = timestamp
        self.hour = timestamp.hour
        self.min  = timestamp.minute
        self.sec  = timestamp.second
        self.msec = timestamp.microsecond/1000
        self.date = timestamp.date().strftime('%Y%m%d')
        pass

        
class MdSpiDelegate(MdApi):
    '''
        将行情信息转发到Agent
        并自行处理杂务
    '''
    logger = logging.getLogger('ctp.MdSpiDelegate')

    def __init__(self,
            instruments, #合约映射 name ==>c_instrument
            broker_id,   #期货公司ID
            investor_id, #投资者ID
            passwd, #口令
            agent,  #实际操作对象
        ):        
        self.instruments = set([name for name in instruments])
        self.broker_id =broker_id
        self.investor_id = investor_id
        self.passwd = passwd
        self.agent = agent
        ##必须在每日重新连接时初始化它. 这一点用到了生产行情服务器收盘后关闭的特点(模拟的不关闭)
        self.last_received = dict([(inst, datetime.datetime.now()) for inst in instruments])
        self.last_day = 0
        agent.add_mdapi(self)
        pass

    def checkErrorRspInfo(self, info):
        if info.ErrorID !=0:
            self.logger.error(u"MD:ErrorID:%s,ErrorMsg:%s" %(info.ErrorID,info.ErrorMsg))
        return info.ErrorID !=0

    def OnRspError(self, info, RequestId, IsLast):
        self.logger.error(u'MD:requestID:%s,IsLast:%s,info:%s' % (RequestId,IsLast,str(info)))
        pass
    
    def OnFrontDisConnected(self, reason):
        self.logger.info(u'MD:front disconnected,reason:%s' % (reason,))
        pass
    
    def OnFrontConnected(self):
        self.logger.info(u'MD:front connected')
        self.user_login(self.broker_id, self.investor_id, self.passwd)

    def user_login(self, broker_id, investor_id, passwd):
        req = ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=passwd)
        r=self.ReqUserLogin(req,self.agent.inc_request_id())
        pass
    
    def OnRspUserLogin(self, userlogin, info, rid, is_last):
        self.logger.info(u'MD:user login,info:%s,rid:%s,is_last:%s' % (info,rid,is_last))
        scur_day = datetime.date.today()
        if scur_day > self.agent.scur_day:    #换日,重新设置volume
            self.logger.info(u'MD:换日, %s-->%s' % (self.agent.scur_day,scur_day))
            #self.agent.scur_day = scur_day
            self.agent.day_switch(scur_day) 
        if is_last and not self.checkErrorRspInfo(info):
            self.logger.info(u"MD:get today's trading day:%s" % repr(self.GetTradingDay()))
            self.subscribe_market_data(self.instruments)

    def subscribe_market_data(self, instruments):
        self.SubscribeMarketData(list(instruments))

    def OnRtnDepthMarketData(self, dp):
        try:
            if dp.LastPrice > 999999 or dp.LastPrice < 0.1:
                self.logger.warning(u'MD:收到的行情数据有误:%s,LastPrice=:%s' %(dp.InstrumentID,dp.LastPrice))
            if dp.InstrumentID not in self.instruments:
                self.logger.warning(u'MD:收到未订阅的行情:%s' %(dp.InstrumentID,))
                
            timestr = str(dp.UpdateTime) + ' ' + str(dp.UpdateMillisec) + '000'
            if len(dp.TradingDay.strip()) > 0:
                timestr = str(dp.TradingDay) + ' ' + timestr
            else:
                timestr = str(self.last_day) + ' ' + timestr
            
            timestamp = datetime.datetime.strptime(timestr, '%Y%m%d %H:%M:%S %f')
            self.last_day = timestamp.year*10000+timestamp.month*100+timestamp.day
            if timestamp <= self.last_received[dp.InstrumentID]:
                self.logger.warning(u'MD:receive late tick data:%s arriving at %s later than %s' %(dp.InstrumentID, timestr,self.last_received[dp.InstrumentID]))
                return
            tick = self.market_data2tick(dp, timestamp)
            self.agent.RtnTick(tick)
        finally:
            pass

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
            self.logger.warning(u'MD:%s 行情数据转换错误:updateTime="%s",msec="%s",tday="%s"' % (dp.InstrumentID, timestamp))
        return rev

class TraderSpiDelegate(TraderApi):
    '''
        将服务器回应转发到Agent
        并自行处理杂务
    '''
    logger = logging.getLogger('ctp.TraderSpiDelegate')    
    def __init__(self,
            instruments, #合约映射 name ==>c_instrument 
            broker_id,   #期货公司ID
            investor_id, #投资者ID
            passwd, #口令
            agent,  #实际操作对象
        ):        
        self.instruments = set([name for name in instruments])
        self.broker_id =broker_id
        self.investor_id = investor_id
        self.passwd = passwd
        self.agent = agent
        self.agent.set_spi(self)
        self.is_logged = False
 
    def isRspSuccess(self,RspInfo):
        return RspInfo == None or RspInfo.ErrorID == 0

    def login(self):
        TraderSpiDelegate.logger.info(u'try login...')
        self.user_login(self.broker_id, self.investor_id, self.passwd)

    ##交易初始化
    def OnFrontConnected(self):
        '''
            当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
        '''
        TraderSpiDelegate.logger.info(u'TD:trader front connected')
        self.login()

    def OnFrontDisconnected(self, nReason):
        TraderSpiDelegate.logger.info(u'TD:trader front disconnected,reason=%s' % (nReason,))

    def user_login(self, broker_id, investor_id, passwd):
        req = ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=passwd)
        r=self.ReqUserLogin(req,self.agent.inc_request_id())

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        TraderSpiDelegate.logger.info(u'TD:trader login')
        TraderSpiDelegate.logger.debug(u"TD:loggin %s" % str(pRspInfo))
        if not self.isRspSuccess(pRspInfo):
            self.logger.warning(u'TD:trader login failed, errMsg=%s' %(pRspInfo.ErrorMsg,))
            print u'综合交易平台登陆失败，请检查网络或用户名/口令'
            self.is_logged = False
            return
        self.is_logged = True
        TraderSpiDelegate.logger.info(u'TD:trader login success')
        self.agent.login_success(pRspUserLogin.FrontID,pRspUserLogin.SessionID,pRspUserLogin.MaxOrderRef)
        #self.settlementInfoConfirm()
        #self.agent.set_trading_day(self.GetTradingDay())
        #self.query_settlement_info()
        #self.query_settlement_confirm() 
        self.confirm_settlement_info()

    def queryDepthMarketData(self, instrument):
        req = ApiStruct.QryDepthMarketData(InstrumentID=instrument)
        r=self.ReqQryDepthMarketData(req, self.agent.inc_request_id())
    
    def OnRspQryDepthMarketData(self, depth_market_data, pRspInfo, nRequestID, bIsLast):
        pass
    
    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        '''登出请求响应'''
        TraderSpiDelegate.logger.info(u'TD:trader logout')
        self.is_logged = False

    def resp_common(self,rsp_info,bIsLast,name='默认'):
        #TraderSpiDelegate.logger.debug("resp: %s" % str(rsp_info))
        if not self.isRspSuccess(rsp_info):
            TraderSpiDelegate.logger.info(u"TD:%s失败" % name)
            return -1
        elif bIsLast and self.isRspSuccess(rsp_info):
            TraderSpiDelegate.logger.info(u"TD:%s成功" % name)
            return 1
        else:
            TraderSpiDelegate.logger.info(u"TD:%s结果: 等待数据接收完全..." % name)
            return 0

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
        req = ApiStruct.QrySettlementInfoConfirm(BrokerID=self.broker_id,InvestorID=self.investor_id)
        self.ReqQrySettlementInfoConfirm(req,self.agent.inc_request_id())

    def query_settlement_info(self):
        #不填日期表示取上一天结算单,并在响应函数中确认
        TraderSpiDelegate.logger.info(u'TD:取上一日结算单信息并确认,BrokerID=%s,investorID=%s' % (self.broker_id,self.investor_id))
        req = ApiStruct.QrySettlementInfo(BrokerID=self.broker_id,InvestorID=self.investor_id,TradingDay=u'')
        #print req.BrokerID,req.InvestorID,req.TradingDay
        time.sleep(1)
        self.ReqQrySettlementInfo(req,self.agent.inc_request_id())

    def confirm_settlement_info(self):
        TraderSpiDelegate.logger.info(u'TD-CSI:准备确认结算单')
        req = ApiStruct.SettlementInfoConfirm(BrokerID=self.broker_id,InvestorID=self.investor_id)
        self.ReqSettlementInfoConfirm(req,self.agent.inc_request_id())

    def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
        '''请求查询投资者结算信息响应'''
        print u'Rsp 结算单查询'
        if(self.resp_common(pRspInfo,bIsLast,u'结算单查询')>0):
            TraderSpiDelegate.logger.info(u'结算单查询完成,准备确认')
            try:
                TraderSpiDelegate.logger.info(u'TD:结算单内容:%s' % pSettlementInfo.Content)
            except Exception,inst:
                TraderSpiDelegate.logger.warning(u'TD-ORQSI-A 结算单内容错误:%s' % str(inst))
            self.confirm_settlement_info()
        else:  #这里是未完成分支,需要直接忽略
            try:
                TraderSpiDelegate.logger.info(u'TD:结算单接收中...:%s' % pSettlementInfo.Content)
            except Exception,inst:
                TraderSpiDelegate.logger.warning(u'TD-ORQSI-B 结算单内容错误:%s' % str(inst))
            #self.agent.initialize()
            pass
            

    def OnRspQrySettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        '''请求查询结算信息确认响应'''
        TraderSpiDelegate.logger.debug(u"TD:结算单确认信息查询响应:rspInfo=%s,结算单确认=%s" % (pRspInfo,pSettlementInfoConfirm))
        #self.query_settlement_info()
        if(self.resp_common(pRspInfo,bIsLast,u'结算单确认情况查询')>0):
            if(pSettlementInfoConfirm == None or int(pSettlementInfoConfirm.ConfirmDate) < int(self.agent.scur_day.strftime('%Y%m%d'))):
                #其实这个判断是不对的，如果周日对周五的结果进行了确认，那么周一实际上已经不需要再次确认了
                if(pSettlementInfoConfirm != None):
                    TraderSpiDelegate.logger.info(u'TD:最新结算单未确认，需查询后再确认,最后确认时间=%s,scur_day:%s' % (pSettlementInfoConfirm.ConfirmDate,self.agent.scur_day))
                else:
                    TraderSpiDelegate.logger.info(u'TD:结算单确认结果为None')
                self.query_settlement_info()
            else:
                self.agent.isSettlementInfoConfirmed = True
                TraderSpiDelegate.logger.info(u'TD:最新结算单已确认，不需再次确认,最后确认时间=%s,scur_day:%s' % (pSettlementInfoConfirm.ConfirmDate,self.agent.scur_day))
                self.agent.initialize()


    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        '''投资者结算结果确认响应'''
        if(self.resp_common(pRspInfo,bIsLast,u'结算单确认')>0):
            self.agent.isSettlementInfoConfirmed = True
            TraderSpiDelegate.logger.info(u'TD:结算单确认时间: %s-%s' %(pSettlementInfoConfirm.ConfirmDate,pSettlementInfoConfirm.ConfirmTime))
        self.agent.initialize()


    ###交易准备
    def OnRspQryInstrumentMarginRate(self, pInstrumentMarginRate, pRspInfo, nRequestID, bIsLast):
        '''
            保证金率回报。返回的必然是绝对值
        '''
        if bIsLast and self.isRspSuccess(pRspInfo):
            self.agent.rsp_qry_instrument_marginrate(pInstrumentMarginRate)
        else:
            #logging
            pass

    def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
        '''
            合约回报。
        '''
        if bIsLast and self.isRspSuccess(pRspInfo):
            self.agent.rsp_qry_instrument(pInstrument)
            #print pInstrument
        else:
            #logging
            #print pInstrument
            self.agent.rsp_qry_instrument(pInstrument)  #模糊查询的结果,获得了多个合约的数据，只有最后一个的bLast是True


    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        '''
            请求查询资金账户响应
        '''
        print u'查询资金账户响应'
        TraderSpiDelegate.logger.info(u'TD:资金账户响应:%s' % pTradingAccount)
        if bIsLast and self.isRspSuccess(pRspInfo):
            self.agent.rsp_qry_trading_account(pTradingAccount)
        else:
            #logging
            pass

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        '''请求查询投资者持仓响应'''
        print u'查询持仓响应'
        if self.isRspSuccess(pRspInfo): #每次一个单独的数据报
            self.agent.rsp_qry_position(pInvestorPosition)
        else:
            #logging
            pass

    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
        '''请求查询投资者持仓明细响应'''
        TraderSpiDelegate.logger.info(str(pInvestorPositionDetail))
        if self.isRspSuccess(pRspInfo): #每次一个单独的数据报
            self.agent.rsp_qry_position_detail(pInvestorPositionDetail)
        else:
            #logging
            pass

    def OnRspError(self, info, RequestId, IsLast):
        ''' 错误应答
        '''
        TraderSpiDelegate.logger.error(u'TD:requestID:%s,IsLast:%s,info:%s' % (RequestId,IsLast,str(info)))

    def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
        '''请求查询报单响应'''
        if bIsLast and self.isRspSuccess(pRspInfo):
            self.agent.rsp_qry_order(pOrder)
        else:
            TraderSpiDelegate.logger.error(u'TD:requestID:%s,IsLast:%s,info:%s' % (nRequestID,bIsLast,str(pRspInfo)))
            pass

    def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
        '''请求查询成交响应'''
        if bIsLast and self.isRspSuccess(pRspInfo):
            self.agent.rsp_qry_trade(pTrade)
        else:
            #logging
            pass

    ###交易操作
    def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
        '''
            报单未通过参数校验,被CTP拒绝
            正常情况后不应该出现
        '''
        print pRspInfo,nRequestID
        TraderSpiDelegate.logger.warning(u'TD:CTP报单录入错误回报, 正常后不应该出现,rspInfo=%s'%(str(pRspInfo),))
        #TraderSpiDelegate.logger.warning(u'报单校验错误,ErrorID=%s,ErrorMsg=%s,pRspInfo=%s,bIsLast=%s' % (pRspInfo.ErrorID,pRspInfo.ErrorMsg,str(pRspInfo),bIsLast))
        #self.agent.rsp_order_insert(pInputOrder.OrderRef,pInputOrder.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)
        self.agent.err_order_insert(pInputOrder.OrderRef,pInputOrder.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)
    
    def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
        '''
            交易所报单录入错误回报
            正常情况后不应该出现
            这个回报因为没有request_id,所以没办法对应
        '''
        print u'ERROR Order Insert'
        TraderSpiDelegate.logger.warning(u'TD:交易所报单录入错误回报, 正常后不应该出现,rspInfo=%s'%(str(pRspInfo),))
        self.agent.err_order_insert(pInputOrder.OrderRef,pInputOrder.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)
    
    def OnRtnOrder(self, pOrder):
        ''' 报单通知
            CTP、交易所接受报单
            Agent中不区分，所得信息只用于撤单
        '''
        #print repr(pOrder)
        TraderSpiDelegate.logger.info(u'报单响应,Order=%s' % str(pOrder))
        if pOrder.OrderStatus == 'a':
            #CTP接受，但未发到交易所
            #print u'CTP接受Order，但未发到交易所, BrokerID=%s,BrokerOrderSeq = %s,TraderID=%s, OrderLocalID=%s' % (pOrder.BrokerID,pOrder.BrokerOrderSeq,pOrder.TraderID,pOrder.OrderLocalID)
            TraderSpiDelegate.logger.info(u'TD:CTP接受Order，但未发到交易所, BrokerID=%s,BrokerOrderSeq = %s,TraderID=%s, OrderLocalID=%s' % (pOrder.BrokerID,pOrder.BrokerOrderSeq,pOrder.TraderID,pOrder.OrderLocalID))
            self.agent.rtn_order(pOrder)
        else:
            #print u'交易所接受Order,exchangeID=%s,OrderSysID=%s,TraderID=%s, OrderLocalID=%s' % (pOrder.ExchangeID,pOrder.OrderSysID,pOrder.TraderID,pOrder.OrderLocalID)
            TraderSpiDelegate.logger.info(u'TD:交易所接受Order,exchangeID=%s,OrderSysID=%s,TraderID=%s, OrderLocalID=%s' % (pOrder.ExchangeID,pOrder.OrderSysID,pOrder.TraderID,pOrder.OrderLocalID))
            #self.agent.rtn_order_exchange(pOrder)
            self.agent.rtn_order(pOrder)

    def OnRtnTrade(self, pTrade):
        '''成交通知'''
        TraderSpiDelegate.logger.info(u'TD:成交通知,BrokerID=%s,BrokerOrderSeq = %s,exchangeID=%s,OrderSysID=%s,TraderID=%s, OrderLocalID=%s' %(pTrade.BrokerID,pTrade.BrokerOrderSeq,pTrade.ExchangeID,pTrade.OrderSysID,pTrade.TraderID,pTrade.OrderLocalID))
        TraderSpiDelegate.logger.info(u'TD:成交回报,Trade=%s' % repr(pTrade))
        self.agent.rtn_trade(pTrade)

    def OnRspOrderAction(self, pInputOrderAction, pRspInfo, nRequestID, bIsLast):
        '''
            ctp撤单校验错误
        '''
        TraderSpiDelegate.logger.warning(u'TD:CTP撤单录入错误回报, 正常后不应该出现,rspInfo=%s'%(str(pRspInfo),))
        #self.agent.rsp_order_action(pInputOrderAction.OrderRef,pInputOrderAction.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)
        self.agent.err_order_action(pInputOrderAction.OrderRef,pInputOrderAction.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)

    def OnErrRtnOrderAction(self, pOrderAction, pRspInfo):
        ''' 
            交易所撤单操作错误回报
            正常情况后不应该出现
        '''
        TraderSpiDelegate.logger.warning(u'TD:交易所撤单录入错误回报, 可能已经成交,rspInfo=%s'%(str(pRspInfo),))
        self.agent.err_order_action(pOrderAction.OrderRef,pOrderAction.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)

class Instrument(object):
    @staticmethod
    def create_instruments(names):
        '''根据名称序列和策略序列创建instrument
           其中策略序列的结构为:
           [总最大持仓量,策略1,策略2...] 
        '''
        objs = dict([(name,Instrument(name)) for name in names])
        for name in names:
            objs[name].get_inst_info()
            objs[name].get_brokerfee()            

        return objs
    
    def __init__(self,name):
        self.name = name
        self.exchange = 'CFFEX'
        self.product = 'IF'
        self.broker_fee = 0.0
        #保证金率
        self.marginrate = (0,0) #(多,空)
        #合约乘数
        self.multiple = 0
        #最小跳动
        self.tick_base = 0  #单位为0.1
        self.start_tick_id = 0
        self.last_tick_id = 0
        # market snapshot
        self.price = 0.0
        self.volume = 0
        self.open_interest = 0
        self.last_update = datetime.datetime.now()
        self.ask_price1 = 0.0
        self.ask_vol1 = 0
        self.bid_price1 = 0.0
        self.bid_vol1 = 0
        self.last_traded = datetime.datetime.now()
        self.max_holding = (10, 10)
        #self.is_busy = False
    
    def get_inst_info(self):
        self.product = misc.inst2product(self.name)
 
        for exch in misc.product_code.keys():
            if self.product in misc.product_code[exch]:
                self.exchange = exch
                if exch == 'CFFEX':
                    self.start_tick_id = 1515000
                    self.last_tick_id  = 2115000
                else:
                    self.last_tick_id = 2100000
                    if self.product in misc.night_session_markets:
                        self.start_tick_id = 300000
                    else:
                        self.start_tick_id = 1500000                
     
                self.multiple = misc.product_lotsize[self.product]
                self.tick_base = misc.product_ticksize[self.product]
                return
        
    def get_brokerfee(self):
        self.broker_fee = 0

    def calc_margin_amount(self,price,direction):   
        my_marginrate = self.marginrate[0] if direction == LONG else self.marginrate[1]
        #print 'self.name=%s,price=%s,multiple=%s,my_marginrate=%s' % (self.name,price,self.multiple,my_marginrate)
        return price * self.multiple * my_marginrate * 1.05
     
class AbsAgent(object):
    ''' 抽取与交易无关的功能，便于单独测试
    '''
    def __init__(self):
        ##命令队列(不区分查询和交易)
        self.commands = []  #每个元素为(trigger_tick,func), 用于当tick==trigger_tick时触发func
        self.tick_id = 0
        
    def put_command(self,trigger_tick,command): #按顺序插入
        #print func_name(command)
        cticks = [ttick for ttick,cmd in self.commands] #不要用command这个名称，否则会覆盖传入的参数,导致后面的插入操作始终插入的是原序列最后一个command的拷贝
        ii = bisect.bisect(cticks,trigger_tick)
        #print 'trigger_tick=%s,cticks=%s,len(command)=%s' % (trigger_tick,str(cticks),len(self.commands))
        self.commands.insert(ii,(trigger_tick,command))
        self.logger.debug(u'AA_P:trigger_tick=%s,cticks=%s,len(command)=%s' % (trigger_tick,str(cticks),len(self.commands)))

    def check_commands(self):   
        '''
            执行命令队列中触发时间<=当前tick的命令. 注意一个tick=0.5s
            以后考虑一个tick只触发一个命令?
        '''
        #print 'in check command'
        l = len(self.commands)
        i = 0
        #if l>0:
        #    pass
        #    print 'in check command,len=%s,self.tick=%s,command time=%s' % (l,self.tick,self.commands[-1][0])
        while(i<l and self.tick_id >= self.commands[i][0]):
            self.logger.info(u'AA_C:exec command,i=%s,tick=%s,command[i][0]=%s' % (i,self.tick,self.commands[i][0]))
            self.commands[i][1]()
            i += 1
        if i>0:
            #print 'del execed command'
            del self.commands[0:i]
        #print len(self.commands)


class Agent(AbsAgent):
    

    def __init__(self, name, trader,cuser,instruments, tday=datetime.date.today(), 
                 folder = 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\'):
        '''
            trader为交易对象
            tday为当前日,为0则为当日
        '''
        AbsAgent.__init__(self)
        ##计时, 用来激发队列
        ##
        self.logger = logging.getLogger('ctp.agent')
        self.mdapis = []
        self.trader = trader
        self.name = name
        self.folder = folder
        self.cuser = cuser
        self.instruments = Instrument.create_instruments(instruments)
        self.request_id = 1
        self.initialized = False
        
        # market data
        self.tick_data  = dict([(inst, []) for inst in instruments])
        self.min_data   = dict([(inst, []) for inst in instruments])
        self.day_data   = dict([(inst, []) for inst in instruments])
        self.cur_min = dict([(inst, dict([(item, 0) for item in min_data_list])) for inst in instruments])
        self.cur_day = dict([(inst, dict([(item, 0) for item in day_data_list])) for inst in instruments])
        for inst in instruments:
            self.cur_day[inst]['date'] = tday
            self.cur_min[inst]['datetime'] = datetime.datetime.fromordinal(tday.toordinal())
        
        ###交易
        self.ref2order = {}    #orderref==>order
        #self.queued_orders = []     #因为保证金原因等待发出的指令(合约、策略族、基准价、基准时间(到秒))
        self.front_id = None
        self.session_id = None
        self.scur_day = tday
        #当前资金/持仓
        self.available = 0  #可用资金
        #positions
        self.positions= dict([(inst, order.Position(self.instruments[inst])) for inst in instruments])
        ##查询命令队列
        self.qry_commands = []  #每个元素为查询命令，用于初始化时查询相关数据
        
        #调度器
        #self.scheduler = sched.scheduler(time.time, time.sleep)
        #保存锁
        self.event = threading.Event()
        self.timer_flag = False
        #保存分钟数据标志
        self.save_flag = False  #默认不保存

        #actions
        self.etrades = []

        self.init_init()    #init中的init,用于子类的处理

        #结算单
        self.isSettlementInfoConfirmed = False  #结算单未确认


    def initialize(self):
        '''
            初始化，如保证金率，账户资金等
        '''
        ##必须先把持仓初始化成配置值或者0
        #time.sleep(12)
        self.qry_commands.append(self.fetch_trading_account)
        #self.qry_commands.append(fcustom(self.fetch_investor_position,instrument_id=''))
        self.qry_commands.append(fcustom(self.fetch_instruments_by_exchange,exchange_id = ''))
        time.sleep(1)   #保险起见
        self.check_qry_commands()
        self.initialized = True #避免因为断开后自动重连造成的重复访问

    def resume(self):
        self.prepare_trade_env()
        self.prepare_data_env()
        
    def check_qry_commands(self):
        #必然是在rsp中要发出另一个查询
        if len(self.qry_commands)>0:
            time.sleep(1)   #这个只用于非行情期的执行. 
            self.qry_commands[0]()
            del self.qry_commands[0]
        self.logger.debug(u'查询命令序列长度:%s' % (len(self.qry_commands),))
        
    def get_eod_positions(self):
        file_prefix = self.folder + self.name
        last_bday = workdays.workday(self.scur_day, -1, misc.CHN_Holidays)
        logfile = file_prefix + '_eodpos_' + last_bday.strftime('%y%m%d')+'.csv'
        if not os.path.isfile(logfile):
            return False
        with open(logfile, 'rb') as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if idx > 0:
                    inst = row[0]
                    if inst in self.positions:
                        self.positions[inst].pos_yday.long = row[1] 
                        self.positions[inst].pos_yday.short = row[2]
        return True
    
    def save_eod_positions(self):
        file_prefix = self.folder + self.name
        logfile = file_prefix + '_eodpos_' + self.scur_day.strftime('%y%m%d')+'.csv'
        with open(logfile,'wb') as log_file:
            file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL);
            file_writer.writerow(['instID', 'long', 'short'])
            for inst in self.positions:
                pos = self.positions[inst]
                pos.re_calc()
                file_writer.writerow([inst, pos.pos_tday.long, pos.pos_tday.short])
        return True
        
    def prepare_trade_env(self):
        self.get_eod_positions()
        file_prefix = self.folder + self.name
        self.ref2order = order.load_order_list(self.scur_day, file_prefix, self.positions)
        keys = self.ref2order.keys()
        if len(keys) > 1:
            keys.sort()
        for key in keys:
            iorder =  self.ref2order[key]
            if len(iorder.conditionals)>0:
                self.ref2order[key].conditionals = dict([(self.ref2order[o_id], iorder.conditionals[o_id]) 
                                                         for o_id in iorder.conditionals])
        self.etrades = order.load_trade_list(self.scur_day, file_prefix)
        for etrade in self.etrades:
            orderdict = etrade.order_dict
            for inst in orderdict:
                etrade.order_dict[inst] = [ self.ref2order[order_ref] for order_ref in orderdict[inst] ]
        
        for inst in self.positions:
            self.positions[inst].re_calc()
    
    def prepare_data_env(self):
        pass
 
 
    def save_state(self):
        '''
            保存环境
        '''
        self.logger.info(u'保存执行状态.....................')
        file_prefix = self.folder + self.name
        order.save_order_list(self.scur_day, self.ref2order, file_prefix)
        order.save_trade_list(self.scur_day, self.etrades, file_prefix)
        return
       
    def update_instrument(self, tick):
        #if ctick.timestamp <= self.instruments[ctick.instID].last_update:
        #    return 
        inst = tick.instID    
        if inst not in self.instruments:
            self.logger.info(u'接收到未订阅的合约数据:%s' % (inst,))
            return False
        
        curr_tick = get_tick_id(tick.timestamp)
        if self.scur_day > tick.timestamp.date():
            return False
        
        if self.scur_day < tick.timestamp.date():
            self.scur_day = tick.timestamp.date()
            self.day_finalize(self.instruments.keys())
        
        if (curr_tick < self.instruments[inst].start_tick_id-5):
            return False
        if (curr_tick > self.instruments[inst].last_tick_id+5):
            return False
            
        if (self.instruments[inst].last_update >= tick.timestamp):
            self.logger.warning('Instrument %s has received late tick, curr tick: %s, received tick: %s' % (tick.instID, self.instruments[tick.instID].last_update, tick.timestamp,))
            return False
        
        if self.tick_id < curr_tick:
            self.tick_id = curr_tick
        self.instruments[tick.instID].last_update = tick.timestamp
        self.instruments[tick.instID].bid_price1 = tick.bidPrice1
        self.instruments[tick.instID].ask_price1 = tick.askPrice1
        self.instruments[tick.instID].bid_vol1   = tick.bidVol1
        self.instruments[tick.instID].ask_vol1   = tick.askVol1
        self.instruments[tick.instID].open_interest = tick.openInterest
        last_volume = self.instruments[tick.instID].volume
        #self.logger.debug(u'MD:收到行情，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume, last_volume))
        if tick.volume > last_volume:
            self.instruments[tick.instID].price  = tick.price
            self.instruments[tick.instID].high   = tick.high
            self.instruments[tick.instID].low    = tick.low
            self.instruments[tick.instID].volume = tick.volume
            self.instruments[tick.instID].last_traded = tick.timestamp
        
        return True
        
    def update_hist_data(self, tick):
        tick_dt = tick.timestamp
        tick_id = get_tick_id(tick_dt)
        tick_min = math.ceil(tick_id/1000.0)
        inst = tick.instID

        if ((self.cur_min[tick.instID]['datetime'].date() > tick_dt.date()) or (self.cur_min[tick.instID]['min_id'] > tick_min)):
            return False
        
        if self.cur_day[inst]['date'] != tick_dt.date():
            self.logger.warning('the daily data date is not same as tick data')
            return False
        
        if (tick_id - self.instruments[inst].start_tick_id < 10) and (self.cur_day[inst]['open']==0.0):
            self.cur_day[inst]['open']=tick.price
        
        self.cur_day[inst]['close'] = tick.price
        self.cur_day[inst]['high']  = tick.high
        self.cur_day[inst]['low']   = tick.low
        self.cur_day[inst]['openInterest'] = tick.openInterest
        self.cur_day[inst]['volume'] = tick.volume
        self.cur_day[inst]['date'] = tick.timestamp.date()
        
        if (tick_min == self.cur_min[inst]['min_id']):
            self.tick_data[inst].append(tick)
            self.cur_min[inst]['close'] = tick.price
            if self.cur_min[inst]['high'] < tick.price:
                self.cur_min[inst]['high'] = tick.price
            if self.cur_min[inst]['low'] > tick.price:
                self.cur_min[inst]['low'] = tick.price
        else:
            if (len(self.tick_data[inst]) > 0) :
                last_tick = self.tick_data[inst][-1]
                self.cur_min[inst]['volume'] = last_tick.volume - self.cur_min[inst]['volume']
                self.cur_min[inst]['openInterest'] = last_tick.openInterest
                self.min_data[inst].append(self.cur_min[inst])
                if self.save_flag:
                    mysqlaccess.bulkinsert_tick_data('fut_tick', self.tick_data[inst])
                    mysqlaccess.insert_min_data('fut_min', tick.instID, self.cur_min[inst])
                
                self.cur_min[inst]['volume'] = last_tick.volume                    
            else:
                self.cur_min[inst]['volume'] = 0
            
            self.tick_data[inst] = []
            self.cur_min[inst]['open']  = tick.price
            self.cur_min[inst]['close'] = tick.price
            self.cur_min[inst]['high']  = tick.price
            self.cur_min[inst]['low']   = tick.price
            self.cur_min[inst]['min_id']  = tick_min
            self.cur_min[inst]['openInterest'] = tick.openInterest
            self.cur_min[inst]['datetime'] = tick_dt.replace(second=0, microsecond=0)
            if ((tick_min>0) and (tick.price>0)): 
                self.tick_data[inst].append(tick)
        
        if tick_id > self.instruments[inst].last_tick_id-5:
            self.day_finalize([inst])
                       
        return True  
    
    def day_finalize(self, insts):
        for inst in insts:
            if (len(self.tick_data[inst]) > 0) :
                last_tick = self.tick_data[inst][-1]
                self.cur_min[inst]['volume'] = last_tick.volume - self.cur_min[inst]['volume']
                self.cur_min[inst]['openInterest'] = last_tick.openInterest
                self.min_data[inst].append(self.cur_min[inst])
                self.day_data[inst].append(self.cur_day[inst])
                if self.save_flag:
                    mysqlaccess.bulkinsert_tick_data('fut_tick', self.tick_data[inst])
                    mysqlaccess.insert_min_data('fut_min', inst, self.cur_min[inst])
                    mysqlaccess.insert_daily_data('fut_daily', inst, self.cur_day[inst])
            
            self.tick_data[inst] = []
            self.cur_min[inst] = dict([(item, 0) for item in min_data_list])
            self.cur_day[inst] = dict([(item, 0) for item in day_data_list])
            self.cur_day[inst]['date'] = self.scur_day
            self.cur_min[inst]['datetime'] = datetime.datetime.fromordinal(self.scur_day.toordinal())
        self.save_eod_positions()

    def day_switch(self,scur_day):  #重新初始化opener
        self.scur_day = scur_day
        self.day_finalize(self.instruments.keys())
        self.isSettlementInfoConfirmed = False
                
    def init_init(self):    #init中的init,用于子类的处理
        pass

    def add_mdapi(self, api):
        self.mdapis.append(api)

    def set_spi(self,spi):
        self.spi = spi

    def inc_request_id(self):
        self.request_id += 1
        return self.request_id

    def login_success(self,frontID,sessionID,max_order_ref):
        self.front_id = frontID
        self.session_id = sessionID
        #self.order_ref = int(max_order_ref)

    ##内务处理
    def fetch_trading_account(self):
        #获取资金帐户
        self.logger.info(u'A:获取资金帐户..')
        req = ApiStruct.QryTradingAccount(BrokerID=self.trader.broker_id, InvestorID=self.trader.investor_id)
        r=self.trader.ReqQryTradingAccount(req,self.inc_request_id())
        #self.logger.info(u'A:查询资金账户, 函数发出返回值:%s' % r)

    def fetch_investor_position(self,instrument_id):
        #获取合约的当前持仓
        self.logger.info(u'A:获取合约%s的当前持仓..' % (instrument_id,))
        req = ApiStruct.QryInvestorPosition(BrokerID=self.trader.broker_id, InvestorID=self.trader.investor_id,InstrumentID=instrument_id)
        r=self.trader.ReqQryInvestorPosition(req,self.inc_request_id())
        #self.logger.info(u'A:查询持仓, 函数发出返回值:%s' % rP)
    
    def fetch_investor_position_detail(self,instrument_id):
        '''
            获取合约的当前持仓明细，目前没用
        '''
        self.logger.info(u'A:获取合约%s的当前持仓..' % (instrument_id,))
        req = ApiStruct.QryInvestorPositionDetail(BrokerID=self.trader.broker_id, InvestorID=self.trader.investor_id,InstrumentID=instrument_id)
        r=self.trader.ReqQryInvestorPositionDetail(req,self.inc_request_id())
        #self.logger.info(u'A:查询持仓, 函数发出返回值:%s' % r)

    def fetch_instrument_marginrate(self,instrument_id):
        req = ApiStruct.QryInstrumentMarginRate(BrokerID=self.trader.broker_id,
                        InvestorID=self.trader.investor_id,
                        InstrumentID=instrument_id,
                        HedgeFlag = ApiStruct.HF_Speculation
                )
        r = self.trader.ReqQryInstrumentMarginRate(req,self.inc_request_id())
        self.logger.info(u'A:查询保证金率, 函数发出返回值:%s' % r)

    def fetch_instrument(self,instrument_id):
        req = ApiStruct.QryInstrument(
                        InstrumentID=instrument_id,
                )
        time.sleep(1)
        r = self.trader.ReqQryInstrument(req,self.inc_request_id())
        self.logger.info(u'A:查询合约, 函数发出返回值:%s' % r)

    def fetch_instruments_by_exchange(self,exchange_id):
        '''不能单独用exchange_id,因此没有意义
        '''
        req = ApiStruct.QryInstrument(
                        ExchangeID=exchange_id,
                )
        r = self.trader.ReqQryInstrument(req,self.inc_request_id())
        self.logger.info(u'A:查询合约, 函数发出返回值:%s' % r)

    ##交易处理
    def RtnTick(self,ctick):#行情处理主循环
        if (not self.update_instrument(ctick)):
            return 0
        if( not self.update_hist_data(ctick)):
            return 0
        
        self.trade_on_tick(ctick)   
        #self.process_trade_list()
        return 1
                
    def trade_on_tick(self, ctick):
        pass
    
    def process_trade(self, exec_trade):
        all_orders = {}
        order_prices = []
        if len(exec_trade.instIDs) == 1:
            inst = exec_trade.instIDs[0]
            order_prices.append(exec_trade.limit_price)
            if exec_trade.volumes[0] > 0:
                curr_price = self.instruments[inst].bid_price1
            else:
                curr_price = self.instruments[inst].ask_price1
        else:
            for inst, v, tick in zip(exec_trade.instIDs, exec_trade.volumes, exec_trade.slip_ticks):
                if v>0:
                    order_prices.append(self.instruments[inst].bid_price1+self.instruments[inst].tick_base*tick)
                else:
                    order_prices.append(self.instruments[inst].ask_price1-self.instruments[inst].tick_base*tick)
    
            curr_price = sum([p*v for p, v in zip(order_prices, exec_trade.volumes)])
        if curr_price <= exec_trade.limit_price: 
            for idx, (inst, v, otype) in enumerate(zip(exec_trade.instIDs, exec_trade.volumes, exec_trade.order_types)):
                orders = []
                pos = self.positions[inst]
                pos.re_calc()
                if ((v>0) and (v > pos.can_close.long + pos.can_yclose.long + pos.can_open.long)) or \
                        ((v<0) and (-v > pos.can_close.short + pos.can_yclose.short + pos.can_open.short)):
                    self.logger.warning("ETrade %s is cancelled due to position limit on leg %s: %s" % (exec_trade.id, idx, inst))
                    exec_trade.status = order.ETradeStatus.Cancelled
                    return False

                if v>0:
                    direction = ApiStruct.D_Buy
                    vol = max(min(v, pos.can_close.long),0)
                    remained = v - vol
                else:
                    direction = ApiStruct.D_Sell
                    vol = max(min(-v,pos.can_close.short),0)
                    remained = v + vol
                    
                if vol > 0:
                    cond = {}
                    if (idx>0) and (exec_trade.order_types[idx-1] == ApiStruct.OPT_LimitPrice):
                        cond = { o:order.OrderStatus.Done for o in all_orders[exec_trade.instIDs[idx-1]]}
                    iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, ApiStruct.OF_CloseToday, direction, otype, cond )
                    orders.append(iorder)
                  
                if (self.instruments[inst].exchange == "SHFE") and (abs(remained)>0) and (pos.can_yclose.short+pos.can_yclose.long>0):
                    if remained>0:
                        direction = ApiStruct.D_Buy
                        vol = max(min(remained, pos.can_yclose.long),0)
                        remained -= vol
                    else:
                        direction = ApiStruct.D_Sell
                        vol = max(min(-remained,pos.can_yclose.short),0)
                        remained += vol
                        
                    if vol > 0:
                        cond = {}
                        if (idx>0) and (exec_trade.order_types[idx-1] == ApiStruct.OPT_LimitPrice):
                            cond = { o:order.OrderStatus.Done for o in all_orders[exec_trade.instIDs[idx-1]]}
                        iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, ApiStruct.OF_CloseYesterday, direction, otype, cond )
                        orders.append(iorder)
                
                vol = abs(remained)
                if vol > 0:                    
                    if remained >0:
                        direction = ApiStruct.D_Buy
                    else:
                        direction = ApiStruct.D_Sell
                    
                    cond = {}
                    if (idx>0) and (exec_trade.order_types[idx-1] == ApiStruct.OPT_LimitPrice):
                        cond = { o:order.OrderStatus.Done for o in all_orders[exec_trade.instIDs[idx-1]]}
                    iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, ApiStruct.OF_Open, direction, otype, cond )
                    orders.append(iorder)
                all_orders[inst] = orders
            exec_trade.order_dict = all_orders
            for inst in exec_trade.instIDs:
                pos = self.positions[inst]
                pos.add_orders(all_orders[inst])
                for iorder in all_orders[inst]:
                    self.ref2order[iorder.order_ref] = iorder
                    if iorder.status == order.OrderStatus.Ready:
                        self.send_order(iorder)
                        iorder.status = order.OrderStatus.Sent
            exec_trade.status = order.ETradeStatus.Processed
            self.save_state()
            return True
        else:
            return False    
        
    def process_trade_list(self):
        for exec_trade in self.etrades:
            if exec_trade.status == order.ETradeStatus.Done:
                continue
            elif exec_trade.status == order.ETradeStatus.Pending:
                self.process_trade(exec_trade)
                continue
            else:
                exec_trade.update()
                if (exec_trade.valid_time < self.tick_id): 
                    if exec_trade.status == order.ETradeStatus.Done:
                        continue
                    else:
                        # cancel first, if PFilled, market order the unfilled.
                        exec_trade.valid_time = self.tick_id + CANCEL_PROTECT_PERIOD
                        for inst in exec_trade.instIDs:
                            for iorder in exec_trade.order_dict[inst]:
                                if iorder.status == order.OrderStatus.Sent:
                                    self.cancel_order(iorder)
                                    if (exec_trade.status == order.ETradeStatus.PFilled) and (iorder.volume - iorder.filled_volume>0):
                                        cond = {iorder:order.OrderStatus.Cancelled}
                                        norder =   order.Order(iorder.position, 
                                                         iorder.limit_price, 
                                                         iorder.volume - iorder.filled_volume, 
                                                         self.tick_id, 
                                                         iorder.action_type, 
                                                         iorder.direction, 
                                                         ApiStruct.OPT_AnyPrice, 
                                                         cond )
                                        exec_trade.order_dict[inst].append( norder )
                        

    def send_order(self,iorder):
        ''' 
            发出下单指令
        '''
        self.logger.info(u'A_CC:开仓平仓命令')
        req = ApiStruct.InputOrder(
                InstrumentID = iorder.instrument.name,
                Direction = iorder.direction,
                OrderRef = str(iorder.order_ref),
                LimitPrice = iorder.limit_price,   #有个疑问，double类型如何保证舍入舍出，在服务器端取整?
                VolumeTotalOriginal = iorder.volume,
                OrderPriceType = iorder.price_type,
                
                BrokerID = self.trader.broker_id,
                InvestorID = self.trader.investor_id,
                CombOffsetFlag = iorder.action_type,         #开仓 5位字符,但是只用到第0位
                CombHedgeFlag = ApiStruct.HF_Speculation,   #投机 5位字符,但是只用到第0位

                VolumeCondition = ApiStruct.VC_AV,
                MinVolume = 1,  #这个作用有点不确定,有的文档设成0了
                ForceCloseReason = ApiStruct.FCC_NotForceClose,
                IsAutoSuspend = 1,
                UserForceClose = 0,
                TimeCondition = ApiStruct.TC_GFD,
                )
        self.logger.info(u'下单: instrument=%s,开关=%s,方向=%s,数量=%s,价格=%s ->%s' % 
                         (iorder.instrument,
                          iorder.action_type,
                          u'多' if iorder.direction==ApiStruct.D_Buy else u'空',
                          iorder.volume,
                          iorder.limit_price, 
                          iorder.price_type))
        #r = self.trader.ReqOrderInsert(req,self.inc_request_id())

    def cancel_order(self,iorder):
        '''
            发出撤单指令  
        '''
        #print 'in cancel command'
        self.logger.info(u'A_CC:取消命令')
        req = ApiStruct.InputOrderAction(
                InstrumentID = iorder.instrument,
                OrderRef = str(iorder.order_ref),
                BrokerID = self.cuser.broker_id,
                InvestorID = self.cuser.investor_id,
                FrontID = self.front_id,
                SessionID = self.session_id,
                ActionFlag = ApiStruct.AF_Delete,
                #OrderActionRef = self.inc_order_ref()  #没用,不关心这个，每次撤单成功都需要去查资金
            )
        r = self.trader.ReqOrderAction(req,self.inc_request_id())
    
    def submit_trade(self, etrade):
        self.etrades.append(etrade)
    
    def cancel_trade(self, etrade):
        pass
         
    ###回应
    def rtn_trade(self,strade):
        '''
            成交回报
            #TODO: 必须考虑出现平仓信号时，position还没完全成交的情况
                   在OnTrade中进行position的细致处理 
            #TODO: 必须处理策略分类持仓汇总和持仓总数不匹配时的问题
        '''
        self.logger.info(u'A_RT1:成交回报,%s:orderref=%s,orders=%s,price=%s' % (strade.InstrumentID,strade.OrderRef,self.ref2order,strade.Price))
        if int(strade.OrderRef) not in self.ref2order or strade.InstrumentID not in self.instruments:
            self.logger.warning(u'A_RT2:收到非本程序发出的成交回报:%s-%s' % (strade.InstrumentID,strade.OrderRef))
            return 
        cur_inst = self.instruments[strade.InstrumentID]
        myorder = self.ref2order[int(strade.OrderRef)]
        if myorder.action_type == XOPEN:#开仓, 也可用pTrade.OffsetFlag判断
            is_completed = myorder.on_trade(price=strade.Price,volume=strade.Volume,trade_time=strade.TradeTime)
            self.logger.info(u'A_RT31,开仓回报');
        else:
            myorder.on_close(price=strade.Price,volume=strade.Volume,trade_time=strade.TradeTime)
            self.logger.info(u'A_RT32,平仓回报,price=%s,time=%s' % (strade.Price,strade.TradeTime));
        self.save_state()
        ##查询可用资金
        #print 'fetch_trading_account'
        #if myorder.action_type == XCLOSE or is_completed:#平仓或者开仓完全成交
        #    self.put_command(self.get_tick()+1,self.fetch_trading_account)
        #self.put_command(self.get_tick()+1,self.fetch_trading_account)  #不完全成交也可以，也就是多查询几次。有可能被抑制


    def rtn_order(self,sorder):
        '''
            交易所接受下单回报(CTP接受的已经被过滤)
            暂时只处理撤单的回报. 
        '''
        #print str(sorder)
        self.logger.info(u'成交/撤单回报:%s' % (str(sorder,)))
        if sorder.OrderStatus == ApiStruct.OST_Canceled or sorder.OrderStatus == ApiStruct.OST_PartTradedNotQueueing:   #完整撤单或部成部撤
            self.logger.info(u'撤单, 撤销开/平仓单')
            ##查询可用资金
            self.put_command(self.tick_id+5,self.fetch_trading_account)
            ##处理相关Order
            myorder = self.ref2order[int(sorder.OrderRef)]
            if myorder.action_type == XOPEN:    #开仓指令cancel时需要处理，平仓指令cancel时不需要处理
                self.logger.info(u'撤销开仓单')
                myorder.on_cancel()
                #self.process_trade_list()
    def err_order_insert(self,order_ref,instrument_id,error_id,error_msg):
        '''
            ctp/交易所下单错误回报，不区分ctp和交易所
            正常情况下不应当出现
        '''
        print "order insert error"
        #self.process_trade_list()
        pass    #可以忽略

    def err_order_action(self,order_ref,instrument_id,error_id,error_msg):
        '''
            ctp/交易所撤单错误回报，不区分ctp和交易所
            必须处理，如果已成交，撤单后必然到达这个位置
        '''
        self.logger.info(u'撤单时已成交，error_id=%s,error_msg=%s' %(error_id,error_msg))
        myorder = self.ref2order[int(order_ref)]
        if myorder.action_type == XOPEN and int(error_id) == 26:
            #开仓指令cancel时需要处理，平仓指令cancel时不需要处理
            self.logger.info(u'撤销开仓单')
            myorder.on_cancel()
            self.process_trade_list()
    
    ###辅助   
    def rsp_qry_position(self,position):
        '''
            查询持仓回报, 每个合约最多得到4个持仓回报，历史多/空、今日多/空
        '''
        self.logger.info(u'agent 持仓:%s' % str(position))
        if (position != None) and (position.InstrumentID in self.positions):    
            cur_position = self.positions[position.InstrumentID]
            if position.PosiDirection == ApiStruct.PD_Long:
                if position.PositionDate == ApiStruct.PSD_Today:
                    cur_position.pos_tday.long = position.Position  #TodayPosition
                else:
                    cur_position.pos_yday.long = position.Position  #YdPosition
            else:#空头
                if position.PositionDate == ApiStruct.PSD_Today:
                    cur_position.pos_tday.short = position.Position #TodayPosition
                else:
                    cur_position.pos_yday.short = position.Position #YdPosition
        else:#无持仓信息，保持默认设置
            pass
        self.check_qry_commands() 

    def rsp_qry_instrument_marginrate(self,marginRate):
        '''
            查询保证金率回报. 
        '''
        self.instruments[marginRate.InstrumentID].marginrate = (marginRate.LongMarginRatioByMoney,marginRate.ShortMarginRatioByMoney)
        #print marginRate.InstrumentID,self.instruments[marginRate.InstrumentID].marginrate
        self.check_qry_commands()

    def rsp_qry_trading_account(self,account):
        '''
            查询资金帐户回报
        '''
        self.available = account.Available
        self.check_qry_commands()        
    
    def rsp_qry_instrument(self,pinstrument):
        '''
            获得合约数量乘数. 
            这里的保证金率应该是和期货公司无关，所以不能使用
        '''
        if pinstrument.InstrumentID not in self.instruments:
            #self.logger.warning(u'A_RQI:收到未监控的合约查询:%s' % (pinstrument.InstrumentID))
            return
        self.instruments[pinstrument.InstrumentID].multiple = pinstrument.VolumeMultiple
        self.instruments[pinstrument.InstrumentID].tick_base = pinstrument.PriceTick
        self.instruments[pinstrument.InstrumentID].marginrate = (pinstrument.LongMarginRatio, pinstrument.ShortMarginRatio)
        #print 'tick_base = %s' % (pinstrument.PriceTick,)
        self.check_qry_commands()

    def rsp_qry_position_detail(self,position_detail):
        '''
            查询持仓明细回报, 得到每一次成交的持仓,其中若已经平仓,则持量为0,平仓量>=1
            必须忽略
        '''
        print str(position_detail)
        self.check_qry_commands()

    def rsp_qry_order(self,sorder):
        '''
            查询报单
            可以忽略
        '''
        self.check_qry_commands()

    def rsp_qry_trade(self,strade):
        '''
            查询成交
            可以忽略
        '''
        self.check_qry_commands()
        

class SaveAgent(Agent):
    def init_init(self):
        Agent.init_init(self)
        self.save_flag = True

        
def make_user(my_agent,hq_user):
    #print my_agent.instruments
    user = MdSpiDelegate(instruments=my_agent.instruments, 
                             broker_id=hq_user.broker_id,
                             investor_id= hq_user.investor_id,
                             passwd= hq_user.passwd,
                             agent = my_agent,
                    )
    user.Create(my_agent.name)
    user.RegisterFront(hq_user.port)
    
    user.Init()


def create_trader(trader_cfg, instruments, agent_name):
    logging.basicConfig(filename="ctp_trade.log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')

    logging.info(u'broker_id=%s,investor_id=%s,passwd=%s' % (trader_cfg.broker_id,trader_cfg.investor_id,trader_cfg.passwd))

    myagent = Agent(agent_name, None, trader_cfg, instruments) 
    myagent.trader = trader = TraderSpiDelegate(instruments=myagent.instruments, 
                             broker_id=trader_cfg.broker_id,
                             investor_id= trader_cfg.investor_id,
                             passwd= trader_cfg.passwd,
                             agent = myagent,
                       )
    trader.Create('trader')
    trader.SubscribePublicTopic(THOST_TERT_QUICK)
    trader.SubscribePrivateTopic(THOST_TERT_QUICK)
    for port in trader_cfg.ports:
        trader.RegisterFront(port)
    trader.Init()
    
    return trader, myagent

def create_agent(agent_name, usercfg, tradercfg, insts):
    trader, my_agent = create_trader(tradercfg, insts, agent_name)
    make_user(my_agent,usercfg)
    return my_agent

def test_main(name='test_trade'):
    '''
    import agent
    trader,myagent = agent.trade_test_main()
    #开仓
    
    ##释放连接
    trader.RegisterSpi(None)
    '''
    logging.basicConfig(filename="ctp_trade.log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')

    prod_user = BaseObject( broker_id="8070", 
                                 investor_id="*", 
                                 passwd="*", 
                                 port="tcp://zjzx-md11.ctp.shcifco.com:41213")
    prod_trader = BaseObject( broker_id="8070", 
                                   investor_id="750305", 
                                   passwd="801289", 
                                   ports= ["tcp://zjzx-front11.ctp.shcifco.com:41205", 
                                           "tcp://zjzx-front12.ctp.shcifco.com:41205",
                                           "tcp://zjzx-front12.ctp.shcifco.com:41205"])
    test_user = BaseObject( broker_id="8000", 
                                 investor_id="*", 
                                 passwd="*", 
                                 port="tcp://qqfz-md1.ctp.shcifco.com:32313"
                                 )
    test_trader = BaseObject( broker_id="8000", 
                                 investor_id="24661668", 
                                 passwd ="121862", 
                                 ports  = ["tcp://qqfz-front1.ctp.shcifco.com:32305",
                                           "tcp://qqfz-front2.ctp.shcifco.com:32305",
                                           "tcp://qqfz-front3.ctp.shcifco.com:32305"])
    
    insts = ['ag1506','ag1412']
    trader_cfg = prod_trader
    user_cfg = prod_user
    agent_name = name
    myagent = create_agent(agent_name, user_cfg, trader_cfg, insts)
    try:
        myagent.resume()
        
        valid_time = myagent.tick_id + 100
        etrade =  order.ETrade( ['ag1506', 'ag1412'], [1, -1], [ApiStruct.OPT_LimitPrice,ApiStruct.OPT_LimitPrice], -22.0, [1,1], valid_time, myagent.name, 'test')
        myagent.submit_trade(etrade)
        myagent.process_trade_list() 
        #测试报单
#         morder = agent.BaseObject(instrument='IF1103',direction='0',order_ref=myagent.inc_order_ref(),price=3280,volume=1)
#         myagent.open_position(morder)
#         morder = agent.BaseObject(instrument='IF1103',direction='0',order_ref=myagent.inc_order_ref(),price=3280,volume=20)
#         
#         #平仓
#         corder = agent.BaseObject(instrument='IF1103',direction='1',order_ref=myagent.inc_order_ref(),price=3220,volume=1)
#         myagent.close_position(corder)
#         
#         cref = myagent.inc_order_ref()
#         morder = agent.BaseObject(instrument='IF1104',direction='0',order_ref=cref,price=3180,volume=1)
#         myagent.open_position(morder)
#         
#         rorder = agent.BaseObject(instrument='IF1103',order_ref=cref)
#         myagent.cancel_command(rorder)
        
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        myagent.mdapis = [] 
        myagent.trader = None    


if __name__=="__main__":
    test_main()
