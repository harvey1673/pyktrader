#-*- coding:utf-8 -*-
import workdays
import time
import copy
import datetime
import logging
import bisect
import mysqlaccess
import order as order
import math
import os
import csv
import instrument
import pandas as pd
from base import *
from misc import *
import data_handler
import pyktlib
import numpy as np
from eventType import *
from eventEngine import *

MAX_REALTIME_DIFF = 100
min_data_list = ['datetime', 'min_id', 'open', 'high','low', 'close', 'volume', 'openInterest'] 
day_data_list = ['date', 'open', 'high','low', 'close', 'volume', 'openInterest']

def get_tick_id(dt):
    return ((dt.hour+6)%24)*100000+dt.minute*1000+dt.second*10+dt.microsecond/100000

def get_tick_num(dt):
    return ((dt.hour+6)%24)*36000+dt.minute*600+dt.second*10+dt.microsecond/100000

def get_min_id(dt):
    return ((dt.hour+6)%24)*100+dt.minute

def trading_hours(product, exch):
    hrs = [(1500, 1615), (1630, 1730), (1930, 2100)]
    if exch in ['SSE', 'SZE']:
        hrs = [(1530, 1730), (1900, 2100)]
    elif exch == 'CFFEX':
        hrs = [(1515, 1730), (1900, 2115)]
    else:
        if product in night_session_markets:
            night_idx = night_session_markets[product]
            hrs = [night_trading_hrs[night_idx]] + hrs  
    return hrs 
                    
class TickData:
    def __init__(self, instID='IF1412', high=0.0, low=0.0, price=0.0, volume=0, openInterest=0, 
                 bidPrice1=0.0, bidVol1=0, askPrice1=0.0, askVol1=0, 
                 up_limit = 0.0, down_limit = 0.0, timestamp=datetime.datetime.now()):
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
        self.upLimit = up_limit
        self.downLimit = down_limit
        self.timestamp = timestamp
        self.hour = timestamp.hour
        self.min  = timestamp.minute
        self.sec  = timestamp.second
        self.msec = timestamp.microsecond/1000
        self.tick_id = ((self.hour+6)%24)*100000+self.min*1000+self.sec*10+int(self.msec/100)
        self.date = timestamp.date().strftime('%Y%m%d')
        pass

class StockTick(TickData):
    def __init__(self, instID='IF1412', high=0.0, low=0.0, price=0.0, open=0.0, close=0.0,
                 volume=0, openInterest=0, turnover=0, up_limit = 0.0, down_limit = 0.0, 
                 timestamp=datetime.datetime.now(),
                 bidPrice1=0.0, bidVol1=0, askPrice1=0.0, askVol1=0, 
                 bidPrice2=0.0, bidVol2=0, askPrice2=0.0, askVol2=0, 
                 bidPrice3=0.0, bidVol3=0, askPrice3=0.0, askVol3=0, 
                 bidPrice4=0.0, bidVol4=0, askPrice4=0.0, askVol4=0, 
                 bidPrice5=0.0, bidVol5=0, askPrice5=0.0, askVol5=0):
        TickData.__init__(self, instID, high, low, price, volume, openInterest, 
                          bidPrice1, bidVol1, askPrice1, askVol1, 
                          up_limit, down_limit, timestamp)
        self.turnover = turnover
        self.open = open
        self.close = close
        self.bidPrice2 = bidPrice2
        self.bidVol2 = bidVol2
        self.askPrice2 = askPrice2
        self.askVol2 = askVol2
        
        self.bidPrice3 = bidPrice3
        self.bidVol3 = bidVol3
        self.askPrice3 = askPrice3
        self.askVol3 = askVol3
        
        self.bidPrice4 = bidPrice4
        self.bidVol4 = bidVol4
        self.askPrice4 = askPrice4
        self.askVol4 = askVol4
        
        self.bidPrice5 = bidPrice5
        self.bidVol5 = bidVol5
        self.askPrice5 = askPrice5
        self.askVol5 = askVol5
        pass
        
class CTPMdMixin(object):

    def OnRspError(self, info, RequestId, IsLast):
        """错误回报"""
        event = Event(type=EVENT_LOG)
        log = u'行情错误回报，错误代码：' + unicode(info.ErrorID) + u',' + u'错误信息：' + info.ErrorMsg.decode('gbk')
        event.dict['log'] = log
        event.dict['level'] = logging.WARNING
        self.eventEngine.put(event)
    
    def OnFrontDisConnected(self, reason):
        """服务器断开"""
        event = Event(type=EVENT_LOG)
        event.dict['log'] = u'行情服务器连接断开'
        event.dict['level'] = logging.INFO
        self.eventEngine.put(event)
    
    def OnFrontConnected(self):
        event = Event(type=EVENT_LOG)
        event.dict['log'] = u'行情服务器连接成功'
        event.dict['level'] = logging.INFO
        self.eventEngine.put(event)
        self.user_login(self.broker_id, self.investor_id, self.passwd)

    def user_login(self, broker_id, investor_id, passwd):
        req = self.ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=passwd)
        r=self.ReqUserLogin(req,self.agent.inc_request_id())
        pass
    
    def OnRspUserLogin(self, userlogin, info, rid, is_last):
        event = Event(type=EVENT_LOG)        
        if info.ErrorID == 0:
            log = u'行情服务器登陆成功'
        else:
            log = u'登陆回报，错误代码：' + unicode(info.ErrorID) + u',' + u'错误信息：' + info.ErrorMsg.decode('gbk')        
        event.dict['log'] = log
        event.dict['level'] = logging.INFO
        self.eventEngine.put(event)
        if is_last and (info.ErrorID == 0):
            trade_day_str = self.GetTradingDay()
            trading_day = datetime.date.today()
            if len(trade_day_str) > 0:
                try:
                    trading_day = datetime.datetime.strptime(trade_day_str,'%Y%m%d').date()
                except ValueError:
                    pass
            self.subscribe_market_data(self.instruments)
            if trading_day > self.agent.scur_day:    #换日,重新设置volume
                event = Event(type=EVENT_DAYSWITCH)
                event.dict['log'] = u'换日: %s -> %s' % (self.agent.scur_day, trading_day)
                event.dict['date'] = trading_day
                self.eventEngine.put(event)
                #self.agent.day_switch(trading_day)             

    def OnRtnDepthMarketData(self, dp):
        try:
            if dp.LastPrice > dp.UpperLimitPrice or dp.LastPrice < dp.LowerLimitPrice:
                event = Event(type=EVENT_LOG)
                event.dict['log'] = u'MD:error in market data - last price:%s,LastPrice=:%s' %(dp.InstrumentID,dp.LastPrice)
                event.dict['level'] = logging.DEBUG
                self.eventEngine.put(event)
                return
            if (dp.AskPrice1 > dp.UpperLimitPrice and dp.BidPrice1 <= dp.LowerLimitPrice) or (dp.BidPrice1 >= dp.AskPrice1):
                event = Event(type=EVENT_LOG)
                event.dict['log'] = u'MD:error in market data - bid ask:%s,BidPrice=%s, AskPrice=%s' %(dp.InstrumentID,dp.BidPrice1,dp.AskPrice1)
                event.dict['level'] = logging.DEBUG
                self.eventEngine.put(event)
                return
            timestr = str(dp.UpdateTime) + ' ' + str(dp.UpdateMillisec) + '000'
            if len(dp.TradingDay.strip()) > 0:
                timestr = str(dp.TradingDay) + ' ' + timestr
            else:
                timestr = str(self.last_day) + ' ' + timestr
            
            timestamp = datetime.datetime.strptime(timestr, '%Y%m%d %H:%M:%S %f')
            self.last_day = timestamp.year*10000+timestamp.month*100+timestamp.day
            tick = self.market_data2tick(dp, timestamp)
            event = Event(type=EVENT_MARKETDATA)
            event.dict['data'] = tick
            self.eventEngine.put(event)            
        finally:
            pass
                
class CTPTraderQryMixin(object):
    def query_instrument_marginrate(self, instrument_id):
        req = self.ApiStruct.QryInstrumentMarginRate(BrokerID=self.broker_id,
                        InvestorID=self.investor_id,
                        InstrumentID=instrument_id,
                        HedgeFlag = self.ApiStruct.HF_Speculation
                )
        r = self.ReqQryInstrumentMarginRate(req,self.agent.inc_request_id())
        return r

    def query_instrument(self, instrument_id):
        req = self.ApiStruct.QryInstrument(
                        InstrumentID=instrument_id,
                )
        r = self.ReqQryInstrument(req, self.agent.inc_request_id())
        return r

    def query_instruments_by_exch(self, exchange_id):
        req = self.ApiStruct.QryInstrument(
                        ExchangeID=exchange_id,
                )
        r = self.ReqQryInstrument(req, self.agent.inc_request_id())
        return r

    def query_trading_account(self):            
        req = self.ApiStruct.QryTradingAccount(BrokerID=self.broker_id, InvestorID=self.investor_id)
        r=self.ReqQryTradingAccount(req,self.agent.inc_request_id())
        return r

    def query_investor_position(self, instrument_id):
        req = self.ApiStruct.QryInvestorPosition(BrokerID=self.broker_id, InvestorID=self.investor_id,InstrumentID=instrument_id)
        r=self.ReqQryInvestorPosition(req,self.agent.inc_request_id())
        return r
    
    def query_investor_position_detail(self, instrument_id):
        req = self.ApiStruct.QryInvestorPositionDetail(BrokerID=self.broker_id, InvestorID=self.investor_id, InstrumentID=instrument_id)
        r=self.ReqQryInvestorPositionDetail(req, self.agent.inc_request_id())
        return r
    
    def query_order(self, startTime = '', endTime = ''):
        req = self.ApiStruct.QryOrder(
                        BrokerID = self.broker_id, 
                        InvestorID = self.investor_id,
                        InstrumentID ='',
                        ExchangeID = '', #交易所代码, char[9]
                        InsertTimeStart = startTime, #开始时间, char[9]
                        InsertTimeEnd = endTime, #结束时间, char[9]
                )
        r = self.ReqQryOrder(req, self.agent.inc_request_id())
        return r

    def query_trade( self, startTime = '', endTime = '' ):
        req = self.ApiStruct.QryTrade(
                        BrokerID=self.broker_id, 
                        InvestorID=self.investor_id,
                        InstrumentID='',
                        ExchangeID ='', #交易所代码, char[9]
                        TradeTimeStart = startTime, #开始时间, char[9]
                        TradeTimeEnd = endTime, #结束时间, char[9]
                )
        r = self.ReqQryTrade(req, self.agent.inc_request_id())
        return r

    def queryDepthMarketData(self, instrument):
        req = self.ApiStruct.QryDepthMarketData(InstrumentID=instrument)
        r=self.ReqQryDepthMarketData(req, self.agent.inc_request_id())
        
    ###交易操作
    def send_order(self, iorder):
        if not self.is_logged:
            event = Event(type=EVENT_LOG)
            event.dict['log'] = 'The trader is not logged, cannot send the order, so cancelling order ref = %s, sysid = %s' % (iorder.order_ref, iorder.sys_id)
            event.dict['level'] = logging.WARNING
            self.eventEngine.put(event)
            iorder.on_cancel()
            return False 
        if iorder.direction == ORDER_BUY:
            direction = self.ApiStruct.D_Buy
        else:
            direction = self.ApiStruct.D_Sell
            
        if iorder.price_type == OPT_MARKET_ORDER:
            price_type = self.ApiStruct.OPT_AnyPrice
        elif iorder.price_type == OPT_LIMIT_ORDER:
            price_type = self.ApiStruct.OPT_LimitPrice
        
        if iorder.action_type == OF_OPEN:
            action_type = self.ApiStruct.OF_Open
        elif iorder.action_type == OF_CLOSE:
            action_type = self.ApiStruct.OF_Close
        elif iorder.action_type == OF_CLOSE_TDAY:
            action_type = self.ApiStruct.OF_CloseToday
        elif iorder.action_type == OF_CLOSE_YDAY:
            action_type = self.ApiStruct.OF_CloseYesterday
            
        limit_price = iorder.limit_price
        if self.name == 'LTS-TD':
            limit_price = str(limit_price)
        req = self.ApiStruct.InputOrder(
                InstrumentID = iorder.instrument.name,
                Direction = direction,
                OrderRef = str(iorder.order_ref),
                LimitPrice = limit_price,   #LTS uses char, CTP uses double
                VolumeTotalOriginal = iorder.volume,
                OrderPriceType = price_type,
                BrokerID = self.broker_id,
                InvestorID = self.investor_id,
                CombOffsetFlag = action_type,         #开仓 5位字符,但是只用到第0位
                CombHedgeFlag = self.ApiStruct.HF_Speculation,   #投机 5位字符,但是只用到第0位
                VolumeCondition = self.ApiStruct.VC_AV,
                MinVolume = 1,  #这个作用有点不确定,有的文档设成0了
                ForceCloseReason = self.ApiStruct.FCC_NotForceClose,
                IsAutoSuspend = 1,
                UserForceClose = 0,
                TimeCondition = self.ApiStruct.TC_GFD,
                )
        event = Event(type=EVENT_LOG)
        event.dict['log'] = u'下单: order_ref=%s, instrument=%s,开关=%s,方向=%s,数量=%s,价格=%s ->%s' % (iorder.order_ref, \
                          iorder.instrument.name,
                          'open' if iorder.action_type == OF_OPEN else 'close',
                          u'多' if iorder.direction==ORDER_BUY else u'空',
                          iorder.volume,
                          iorder.limit_price, 
                          iorder.price_type)
        event.dict['level'] = logging.DEBUG
        self.eventEngine.put(event) 
        r = self.ReqOrderInsert(req,self.agent.inc_request_id())
        return r
    
    def cancel_order(self, iorder):
        inst = iorder.instrument
        event = Event(type=EVENT_LOG)
        event.dict['log'] = u'A_CC:取消命令: OrderRef=%s, OrderSysID=%s, exchange=%s, instID=%s, volume=%s, filled=%s, cancelled=%s' % (iorder.order_ref, \
                            iorder.sys_id, inst.exchange, inst.name, iorder.volume, iorder.filled_volume, iorder.cancelled_volume)
        event.dict['level'] = logging.DEBUG
        self.eventEngine.put(event)         
        if len(iorder.sys_id) >0:
            exch = inst.exchange
            req = self.ApiStruct.InputOrderAction(
                InstrumentID = inst.name,
                BrokerID = self.broker_id,
                InvestorID = self.investor_id,
                ExchangeID = exch,
                OrderSysID = iorder.sys_id,
                ActionFlag = self.ApiStruct.AF_Delete,
            )
        else:
            event = Event(type=EVENT_LOG)
            event.dict['log'] = 'order=%s has no OrderSysID, using Order_ref to cancel' % (iorder.order_ref)
            event.dict['level'] = logging.INFO
            self.eventEngine.put(event)         
            req = self.ApiStruct.InputOrderAction(
                InstrumentID = inst.name,
                OrderRef = str(iorder.order_ref),
                BrokerID = self.broker_id,
                InvestorID = self.investor_id,
                FrontID = self.front_id,
                SessionID = self.session_id,
                ActionFlag = self.ApiStruct.AF_Delete,
            )
        r = self.ReqOrderAction(req,self.agent.inc_request_id())
        return r

class CTPTraderRspMixin(object):
    def isRspSuccess(self, RspInfo):
        return RspInfo == None or RspInfo.ErrorID == 0

    def login(self):
        self.user_login(self.broker_id, self.investor_id, self.passwd)

    ##交易初始化
    def OnFrontConnected(self):
        '''
            当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
        '''
        """服务器连接"""
        event = Event(type=EVENT_LOG)
        event.dict['log'] = u'交易服务器连接成功'
        event.dict['level'] = logging.INFO
        self.eventEngine.put(event)
        self.login()

    def OnFrontDisconnected(self, nReason):
        """服务器断开"""
        self.is_logged = False
        event = Event(type=EVENT_LOG)
        event.dict['log'] = u'交易服务器连接断开'
        event.dict['level'] = logging.INFO
        self.eventEngine.put(event)

        event2 = Event(type=EVENT_TDDISCONNECTED)
        event2.dict['log'] = u'交易服务器连接断开'
        self.eventEngine.put(event2)        

    def user_login(self, broker_id, investor_id, passwd):
        req = self.ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=passwd)
        r=self.ReqUserLogin(req,self.agent.inc_request_id())

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        event = Event(type=EVENT_LOG)        
        if pRspInfo.ErrorID == 0:
            log = u'交易服务器登陆成功'
        else:
            log = u'登陆回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')        
        event.dict['log'] = log
        event.dict['level'] = logging.INFO
        self.eventEngine.put(event)
        
        if pRspInfo.ErrorID == 0:
            self.is_logged = True
            self.front_id = pRspUserLogin.FrontID
            self.session_id = pRspUserLogin.SessionID
        else:
            self.is_logged = False
            time.sleep(30)
            self.login()
    
    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        '''登出请求响应'''
        event = Event(type=EVENT_LOG)        
        if pRspInfo.ErrorID == 0:
            log = u'交易服务器登出成功'
        else:
            log = u'登陆回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')        
        event.dict['log'] = log
        event.dict['level'] = logging.INFO
        self.eventEngine.put(event)
        self.is_logged = False

    def resp_common(self,rsp_info,bIsLast,name='默认'):
        event = Event(type=EVENT_LOG)        
        if not self.isRspSuccess(rsp_info):
            log = u'TD:%s失败' % name
            val = -1
        elif bIsLast and self.isRspSuccess(rsp_info):
            log = u'TD:%s成功' % name
            val = 1
        else:
            log = u'TD:%s结果: 等待数据接收完全...' % name
            val = 0
        event.dict['log'] = log
        event.dict['level'] = logging.INFO
        self.eventEngine.put(event) 
        return val
        
    def OnRspQryDepthMarketData(self, depth_market_data, pRspInfo, nRequestID, bIsLast):
        pass
        
    ###交易准备
    def OnRspQryInstrumentMarginRate(self, pInstMarginRate, pRspInfo, nRequestID, bIsLast):
        '''
            保证金率回报。返回的必然是绝对值
        '''
        if self.isRspSuccess(pRspInfo):
            event = Event(type = EVENT_MARGINRATE)
            event.dict['data'] = copy.copy(pInstMarginRate)
            event.dict['error'] = copy.copy(pRspInfo)
            event.dict['isLast'] = bIsLast
            self.eventEngine.put(event)         
        
    def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
        '''
            获得合约数量乘数. 
            这里的保证金率应该是和期货公司无关，所以不能使用
        '''
        if pInstrument.InstrumentID not in self.agent.instruments:
            return

        if self.isRspSuccess(pRspInfo):
            event = Event(type = EVENT_INSTRUMENT)
            event.dict['data'] = copy.copy(pInstrument)
            event.dict['error'] = copy.copy(pRspInfo)
            event.dict['isLast'] = bIsLast
            self.eventEngine.put(event)     
        else:
            event = Event(type=EVENT_LOG)
            log = u'合约投资者回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)             
        
    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        """资金账户查询回报"""
        if self.isRspSuccess(pRspInfo):
            event = Event(type = EVENT_ACCOUNT)
            event.dict['data'] = copy.copy(pTradingAccount)
            event.dict['error'] = copy.copy(pRspInfo)
            event.dict['isLast'] = bIsLast
            self.eventEngine.put(event)
        else:
            event = Event(type=EVENT_LOG)
            log = u'账户查询回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)

    def OnRspQryInvestor(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        """投资者查询回报"""
        if self.isRspSuccess(pRspInfo):
            event = Event(type=EVENT_INVESTOR)
            event.dict['data'] = copy.copy(pInvestorPosition)
            event.dict['isLast'] = bIsLast
            self.eventEngine.put(event)
        else:
            event = Event(type=EVENT_LOG)
            log = u'合约投资者回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)
            
    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        """持仓查询回报"""
        if self.isRspSuccess(pRspInfo):
            event = Event(type=EVENT_POSITION)
            event.dict['data'] = copy.copy(pInvestorPosition)
            event.dict['isLast'] = bIsLast
            self.eventEngine.put(event)
        else:
            event = Event(type=EVENT_LOG)
            log = u'持仓查询回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)
      
    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
        '''请求查询投资者持仓明细响应'''
        pass
        
    def OnRspError(self, info, RequestId, IsLast):
        """错误回报"""
        event = Event(type=EVENT_LOG)
        log = u'交易错误回报，错误代码：' + unicode(info.ErrorID) + u',' + u'错误信息：' + info.ErrorMsg.decode('gbk')
        event.dict['log'] = log
        event.dict['level'] = logging.INFO
        self.eventEngine.put(event)

    def OnRspQryOrder(self, porder, pRspInfo, nRequestID, bIsLast):
        '''请求查询报单响应'''
        #print porder, pRspInfo, bIsLast
        if self.isRspSuccess(pRspInfo):
            event = Event(type=EVENT_QRYORDER)
            event.dict['data'] = copy.copy(porder)
            event.dict['isLast'] = bIsLast
            self.eventEngine.put(event)         
        else:
            event = Event(type=EVENT_LOG)
            log = u'交易错误回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)
        
    def OnRspQryTrade(self, ptrade, pRspInfo, nRequestID, bIsLast):
        '''请求查询成交响应'''
        #print ptrade, pRspInfo, bIsLast
        if self.isRspSuccess(pRspInfo):
            event = Event(type=EVENT_QRYTRADE)
            event.dict['data'] = copy.copy(ptrade)
            event.dict['isLast'] = bIsLast
            self.eventEngine.put(event)
        else:
            event = Event(type=EVENT_LOG)
            log = u'交易错误回报，错误代码：' + unicode(info.ErrorID) + u',' + u'错误信息：' + info.ErrorMsg.decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)
    
    def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
        '''
            报单未通过参数校验,被CTP拒绝
            正常情况后不应该出现
        '''
        event = Event(type=EVENT_LOG)
        log = u' 发单错误回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')
        event.dict['log'] = log
        event.dict['level'] = logging.WARNING
        self.eventEngine.put(event)
        event2 = Event(type=EVENT_ERRORDERINSERT)
        event2.dict['data'] = copy.copy(pInputOrder)
        event2.dict['error'] = copy.copy(pRspInfo)
        self.eventEngine.put(event2)        
    
    def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
        """发单错误回报（交易所）"""
        event = Event(type=EVENT_LOG)
        log = u'发单错误回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')
        event.dict['log'] = log
        event.dict['level'] = logging.WARNING
        self.eventEngine.put(event)
        
        event2 = Event(type=EVENT_ERRORDERINSERT)
        event2.dict['data'] = copy.copy(pInputOrder)
        event2.dict['error'] = copy.copy(pRspInfo)
        self.eventEngine.put(event2)                
    
    def OnRtnOrder(self, porder):
        ''' 报单通知
            CTP、交易所接受报单(CTP接受的已经被过滤)
            Agent中不区分，所得信息只用于撤单,暂时只处理撤单的回报.
        '''
        # 常规报单事件
        event1 = Event(type=EVENT_ORDER)
        event1.dict['data'] = copy.copy(porder)
        self.eventEngine.put(event1)
        
        # 特定合约行情事件
        event2 = Event(type=(EVENT_ORDER_ORDERREF+porder.OrderRef))
        event2.dict['data'] = copy.copy(porder)
        self.eventEngine.put(event2)

    def OnRtnTrade(self, ptrade):
        '''成交回报
        #TODO: 必须考虑出现平仓信号时，position还没完全成交的情况在OnTrade中进行position的细致处理 
        #TODO: 必须处理策略分类持仓汇总和持仓总数不匹配时的问题
        '''
        # 常规成交事件
        event1 = Event(type=EVENT_TRADE)
        event1.dict['data'] = copy.copy(ptrade)
        self.eventEngine.put(event1)
        
        # 特定合约成交事件
        event2 = Event(type=(EVENT_TRADE_CONTRACT+ptrade.InstrumentID))
        event2.dict['data'] = copy.copy(ptrade)
        self.eventEngine.put(event2)
        
    def OnRspOrderAction(self, pInputOrderAction, pRspInfo, nRequestID, bIsLast):
        '''
            ctp撤单校验错误
        '''
        event = Event(type=EVENT_LOG)
        log = u'撤单错误回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')
        event.dict['log'] = log
        event.dict['level'] = logging.WARNING
        self.eventEngine.put(event)
        
        event2 = Event(type=EVENT_ERRORDERCANCEL)
        event2.dict['data'] = copy.copy(pInputOrderAction)
        event2.dict['error'] = copy.copy(pRspInfo)
        self.eventEngine.put(event2)  

    def OnErrRtnOrderAction(self, pOrderAction, pRspInfo):
        """撤单错误回报（交易所）"""
        event = Event(type=EVENT_LOG)
        log = u'撤单错误回报，错误代码：' + unicode(pRspInfo.ErrorID) + u',' + u'错误信息：' + pRspInfo.ErrorMsg.decode('gbk')
        event.dict['log'] = log
        event.dict['level'] = logging.WARNING
        self.eventEngine.put(event)
        
        event2 = Event(type=EVENT_ERRORDERCANCEL)
        event2.dict['data'] = copy.copy(pOrderAction)
        event2.dict['error'] = copy.copy(pRspInfo)
        self.eventEngine.put(event2)         


class Agent(object):
 
    def __init__(self, name, trader, cuser, instruments, strategies = [], tday=datetime.date.today(), config = {}):
        '''
            trader为交易对象
            tday为当前日,为0则为当日
        '''
        self.tick_id = 0
        self.timer_count = 0
        self.request_id = 1
        folder = 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\'
        if 'folder' in config:
            folder = config['folder']
        daily_data_days = 60
        if 'daily_data_days' in config:
            daily_data_days = config['daily_data_days']   
        min_data_days = 5
        if 'min_data_days' in config:
            min_data_days = config['min_data_days']        
        live_trading = False
        if 'live_trading' in config:
            live_trading = config['live_trading']  
        self.logger = logging.getLogger('ctp.agent')
        self.mdapis = []
        self.trader = trader
        self.name = name
        self.folder = folder + self.name + os.path.sep
        self.cuser = cuser
        self.initialized = False
        self.scur_day = tday
        #保存分钟数据标志
        self.save_flag = False  #默认不保存
        self.live_trading = live_trading
        self.tick_db_table = 'fut_tick'
        self.min_db_table  = 'fut_min'
        self.daily_db_table = 'fut_daily'
        self.eod_flag = False
        # market data
        self.daily_data_days = daily_data_days
        self.min_data_days = min_data_days
        self.instruments = {}
        self.tick_data  = {}
        self.day_data  = {}
        self.min_data  = {}
        self.cur_min = {}
        self.cur_day = {}  
        self.positions= {} 
        self.qry_pos = {}
        self.day_data_func = {}
        self.min_data_func = {}
        self.inst2strat = {}            
        self.add_instruments(instruments, self.scur_day)
        self.strategies = {}
        self.strat_list = []
        for strat in strategies:
            self.add_strategy(strat)
        ###交易
        self.ref2order = {}    #orderref==>order
        self.ref2trade = {}
        #self.queued_orders = []     #因为保证金原因等待发出的指令(合约、策略族、基准价、基准时间(到秒))
        #当前资金/持仓
        self.available = 0  #可用资金
        self.locked_margin = 0
        self.used_margin = 0
        self.margin_cap = 1500000
        self.pnl_total = 0.0
        self.curr_capital = 1000000.0
        self.prev_capital = 1000000.0
        self.ctp_orders = []
        self.eventEngine = EventEngine(1)
        self.eventEngine.register(EVENT_LOG, self.log_handler)
        self.eventEngine.register(EVENT_MARKETDATA, self.rtn_tick)
        self.eventEngine.register(EVENT_TIMER, self.check_qry_commands)
        self.eventEngine.register(EVENT_DAYSWITCH, self.day_switch)
        self.cancel_protect_period = 200
        self.market_order_tick_multiple = 5

        self.order_stats = dict([(inst,{'submitted': 0, 'cancelled':0, 'failed': 0, 'status': True }) for inst in self.instruments])
        self.total_submitted = 0
        self.total_cancelled = 0
        self.total_submitted_limit = 1000
        self.submitted_limit_per_inst = 100
        self.failed_order_limit = 200
        ##查询命令队列
        self.qry_commands = []  #每个元素为查询命令，用于初始化时查询相关数据
        self.init_init()    #init中的init,用于子类的处理
        #结算单
        self.isSettlementInfoConfirmed = False  #结算单未确认

    def set_capital_limit(self, margin_cap):
        self.margin_cap = margin_cap

    def log_handler(self, event):
        lvl = event.dict['level']
        self.logger.log(lvl, event.dict['log'])

    def td_disconnected(self, event):
        pass

    def time_scheduler(self, event):
        if self.timer_count % 1800:
            if self.tick_id >= 2100000-10:
                min_id = get_min_id(datetime.datetime.now())
                if (min_id >= 2116) and (self.eod_flag == False):
                    self.qry_commands.append(self.run_eod)

    def add_instruments(self, names, tday):
        add_names = [ name for name in names if name not in self.instruments]
        for name in add_names:
            if name.isdigit():
                if len(name) == 8:
                    self.instruments[name] = instrument.StockOptionInst(name)
                else:
                    self.instruments[name] = instrument.Stock(name)
            else:
                if len(name) > 10:
                    self.instruments[name] = instrument.FutOptionInst(name)
                else:
                    self.instruments[name] = instrument.Future(name)
            self.instruments[name].update_param(tday)                    
            self.tick_data[name] = []
            self.day_data[name]  = pd.DataFrame(columns=['open', 'high','low','close','volume','openInterest'])
            self.min_data[name]  = {1: pd.DataFrame(columns=['open', 'high','low','close','volume','openInterest','min_id'])}
            self.cur_min[name]   = dict([(item, 0) for item in min_data_list])
            self.cur_day[name]   = dict([(item, 0) for item in day_data_list])  
            self.positions[name] = order.Position(self.instruments[name])
            self.day_data_func[name] = []
            self.min_data_func[name] = {}    
            self.qry_pos[name]   = {'tday': [0, 0], 'yday': [0, 0]}
            self.cur_min[name]['datetime'] = datetime.datetime.fromordinal(self.scur_day.toordinal())
            self.cur_day[name]['date'] = tday
            if name not in self.inst2strat:
                self.inst2strat[name] = {}
        
    def add_strategy(self, strat):
        self.add_instruments(strat.instIDs, self.scur_day)
        for instID in strat.instIDs:
            self.inst2strat[instID][strat.name] = []
        self.strategies[strat.name] = strat
        self.strat_list.append(strat.name)
        strat.agent = self
        strat.reset()
                 
    def initialize(self, event):
        '''
            初始化，如保证金率，账户资金等
        '''
        self.isSettlementInfoConfirmed = True
        if not self.initialized:
            for inst in self.instruments:
                self.instruments[inst].update_param(self.scur_day)
            #self.resume()
        self.qry_commands = []
        self.qry_commands.append(self.fetch_trading_account)
        self.qry_commands.append(self.fetch_investor_position)
        self.qry_commands.append(self.fetch_order)
        self.qry_commands.append(self.fetch_trade)
   
    def register_data_func(self, inst, freq, fobj):
        if inst not in self.day_data_func:
            self.day_data_func[inst] = []
            self.min_data_func[inst] = {}
        if 'd' in freq:
            for func in self.day_data_func[inst]:
                if fobj.name == func.name:
                    return False
            self.day_data_func[inst].append(fobj)
            return True
        else:
            mins = int(freq[:-1])
            if mins not in self.min_data_func[inst]:
                self.min_data_func[inst][mins] = []
            for func in self.min_data_func[inst][mins]:
                if fobj.name == func.name:
                    return False            
            if fobj != None:
                self.min_data_func[inst][mins].append(fobj)
            return True
        
    def prepare_data_env(self, mid_day = True): 
        if self.daily_data_days > 0 or mid_day:
            self.logger.debug('Updating historical daily data for %s' % self.scur_day.strftime('%Y-%m-%d'))
            daily_start = workdays.workday(self.scur_day, -self.daily_data_days, CHN_Holidays)
            daily_end = self.scur_day
            for inst in self.instruments:  
                if (self.instruments[inst].ptype == instrument.ProductType.Option):
                    continue
                self.day_data[inst] = mysqlaccess.load_daily_data_to_df('fut_daily', inst, daily_start, daily_end)
                df = self.day_data[inst]
                if len(df) > 0:
                    self.instruments[inst].price = df['close'][-1]
                    self.instruments[inst].last_update = 0
                    self.instruments[inst].prev_close = df['close'][-1]
                    for fobj in self.day_data_func[inst]:
                        ts = fobj.sfunc(df)
                        df[ts.name]= pd.Series(ts, index=df.index)

        if self.min_data_days > 0 or mid_day:
            self.logger.debug('Updating historical min data for %s' % self.scur_day.strftime('%Y-%m-%d'))
            d_start = workdays.workday(self.scur_day, -self.min_data_days, CHN_Holidays)
            d_end = self.scur_day
            for inst in self.instruments: 
                if (self.instruments[inst].ptype == instrument.ProductType.Option):
                    continue
                min_start = int(self.instruments[inst].start_tick_id/1000)
                min_end = int(self.instruments[inst].last_tick_id/1000)+1
                #print "loading inst = %s" % inst
                mindata = mysqlaccess.load_min_data_to_df('fut_min', inst, d_start, d_end, minid_start=min_start, minid_end=min_end)        
                self.min_data[inst][1] = mindata
                if len(mindata)>0:
                    min_date = mindata.index[-1].date()
                    if (len(self.day_data[inst].index)==0) or (min_date > self.day_data[inst].index[-1]):
                        self.cur_day[inst] = mysqlaccess.get_daily_by_tick(inst, min_date, start_tick=self.instruments[inst].start_tick_id, end_tick=self.instruments[inst].last_tick_id)
                        self.cur_min[inst]['datetime'] = pd.datetime(*mindata.index[-1].timetuple()[0:-3])
                        self.cur_min[inst]['open'] = float(mindata.ix[-1,'open'])
                        self.cur_min[inst]['close'] = float(mindata.ix[-1,'close'])
                        self.cur_min[inst]['high'] = float(mindata.ix[-1,'high'])
                        self.cur_min[inst]['low'] = float(mindata.ix[-1,'low'])
                        self.cur_min[inst]['volume'] = self.cur_day[inst]['volume']
                        self.cur_min[inst]['openInterest'] = self.cur_day[inst]['openInterest']
                        self.cur_min[inst]['min_id'] = int(mindata.ix[-1,'min_id'])
                        self.instruments[inst].price = float(mindata.ix[-1,'close'])
                        self.instruments[inst].last_update = 0
                        self.logger.debug('inst=%s tick data loaded for date=%s' % (inst, min_date))
                    for m in self.min_data_func[inst]:
                        if m != 1:
                            self.min_data[inst][m] = data_handler.conv_ohlc_freq(self.min_data[inst][1], str(m)+'min')
                        df = self.min_data[inst][m]
                        for fobj in self.min_data_func[inst][m]:
                            ts = fobj.sfunc(df)
                            df[ts.name]= pd.Series(ts, index=df.index)
        return

    def resume(self):
        if self.initialized:
            return 
        self.logger.debug('Prepare market data for %s' % self.scur_day.strftime('%y%m%d'))
        self.prepare_data_env(mid_day = True)
        self.get_eod_positions()            
        self.logger.debug('Prepare trade environment for %s' % self.scur_day.strftime('%y%m%d'))
        file_prefix = self.folder
        self.ref2order = order.load_order_list(self.scur_day, file_prefix, self.positions)
        keys = self.ref2order.keys()
        if len(keys) > 1:
            keys.sort()
        for key in keys:
            iorder =  self.ref2order[key]
            if len(iorder.conditionals)>0:
                self.ref2order[key].conditionals = dict([(self.ref2order[o_id], iorder.conditionals[o_id]) 
                                                         for o_id in iorder.conditionals])
        self.ref2trade = order.load_trade_list(self.scur_day, file_prefix)
        for trade_id in self.ref2trade:
            etrade = self.ref2trade[trade_id]
            orderdict = etrade.order_dict
            for inst in orderdict:
                etrade.order_dict[inst] = [ self.ref2order[order_ref] for order_ref in orderdict[inst] ]
            etrade.update()
        
        for strat_name in self.strat_list:
            strat = self.strategies[strat_name]
            strat.initialize()
            strat_trades = [etrade for etrade in self.ref2trade.values() if (etrade.strategy == strat.name) \
                            and (etrade.status != order.ETradeStatus.StratConfirm)]
            for trade in strat_trades:
                strat.add_live_trades(trade)
            
        for inst in self.positions:
            self.positions[inst].re_calc()        
        self.calc_margin()
        self.initialized = True
        self.eventEngine.start()
                
    def check_qry_commands(self, event):
        self.timer_count += 1
        if len(self.qry_commands)>0:
            self.qry_commands[0]()
            del self.qry_commands[0]
            self.logger.debug(u'查询命令序列长度:%s' % (len(self.qry_commands),))

    def check_price_limit(self, inst, num_tick):
        inst_obj = self.instruments[inst]
        tick_base = inst_obj.tick_base
        if (inst_obj.ask_price1 >= inst_obj.up_limit - num_tick * tick_base) or (inst_obj.bid_price1 <= inst_obj.down_limit + num_tick * tick_base):
            return True
        else:
            return False

    def get_eod_positions(self):
        file_prefix = self.folder
        pos_date = self.scur_day
        logfile = file_prefix + 'EOD_Pos_' + pos_date.strftime('%y%m%d')+'.csv'
        if not os.path.isfile(logfile):
            pos_date = workdays.workday(pos_date, -1, CHN_Holidays)
            logfile = file_prefix + 'EOD_Pos_' + pos_date.strftime('%y%m%d')+'.csv'
            if not os.path.isfile(logfile):
                return False
        else:
            self.eod_flag = True
        self.logger.debug('Starting; getting EOD position for %s' % pos_date.strftime('%y%m%d'))
        with open(logfile, 'rb') as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if row[0] == 'capital':
                    self.prev_capital = float(row[1])
                    self.logger.debug('getting prev EOD capital = %s' % row[1])
                elif row[0] == 'pos':
                    inst = row[1]
                    if inst in self.positions:
                        self.positions[inst].pos_yday.long = int(row[2]) 
                        self.positions[inst].pos_yday.short = int(row[3])
                        self.instruments[inst].prev_close = float(row[4])    
                        self.logger.debug('getting prev EOD pos = %s: long=%s, short=%s, price=%s' % (row[1], row[2], row[3], row[4]))
        return True
    
    def save_eod_positions(self):
        file_prefix = self.folder
        logfile = file_prefix + 'EOD_Pos_' + self.scur_day.strftime('%y%m%d')+'.csv'
        self.logger.info('EOD process: saving EOD position for %s' % self.scur_day.strftime('%y%m%d'))
        if os.path.isfile(logfile):
            self.logger.info('EOD position file for %s already exists' % self.scur_day.strftime('%y%m%d'))
            return False
        else:
            with open(logfile,'wb') as log_file:
                file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL);
                for inst in self.positions:
                    pos = self.positions[inst]
                    pos.re_calc()
                self.calc_margin()
                file_writer.writerow(['capital', self.curr_capital])
                for inst in self.positions:
                    price = self.instruments[inst].price
                    pos = self.positions[inst]
                    file_writer.writerow(['pos', inst, pos.curr_pos.long, pos.curr_pos.short, price])
            return True

    def calc_margin(self):
        locked_margin = 0
        used_margin = 0
        yday_pnl = 0
        tday_pnl = 0
        for instID in self.instruments:
            inst = self.instruments[instID]
            pos = self.positions[instID]
            under_price = 0.0
            if (inst.ptype == instrument.ProductType.Option):
                under_price = self.instruments[inst.underlying].price
            #print inst.name, inst.marginrate, inst.calc_margin_amount(ORDER_BUY), inst.calc_margin_amount(ORDER_SELL)
            locked_margin += pos.locked_pos.long * inst.calc_margin_amount(ORDER_BUY, under_price)
            locked_margin += pos.locked_pos.short * inst.calc_margin_amount(ORDER_SELL, under_price) 
            used_margin += pos.curr_pos.long * inst.calc_margin_amount(ORDER_BUY, under_price)
            used_margin += pos.curr_pos.short * inst.calc_margin_amount(ORDER_SELL, under_price)
            yday_pnl += (pos.pos_yday.long - pos.pos_yday.short) * (inst.price - inst.prev_close) * inst.multiple
            tday_pnl += pos.tday_pos.long * (inst.price-pos.tday_avp.long) * inst.multiple
            tday_pnl -= pos.tday_pos.short * (inst.price-pos.tday_avp.short) * inst.multiple
            #print "inst=%s, yday_long=%s, yday_short=%s, tday_long=%s, tday_short=%s" % (instID, pos.pos_yday.long, pos.pos_yday.short, pos.tday_pos.long, pos.tday_pos.short)
        self.locked_margin = locked_margin
        self.used_margin = used_margin
        self.pnl_total = yday_pnl + tday_pnl
        self.curr_capital = self.prev_capital + self.pnl_total
        self.available = self.curr_capital - self.locked_margin
        self.logger.debug('calc_margin: curr_capital=%s, prev_capital=%s, pnl_tday=%s, pnl_yday=%s, locked_margin=%s, used_margin=%s, available=%s' \
                        % (self.curr_capital, self.prev_capital, tday_pnl, yday_pnl, locked_margin, used_margin, self.available))
 
    def save_state(self):
        '''
            保存环境
        '''
        if not self.eod_flag:
            self.logger.debug(u'保存执行状态.....................')
            file_prefix = self.folder
            order.save_order_list(self.scur_day, self.ref2order, file_prefix)
            order.save_trade_list(self.scur_day, self.ref2trade, file_prefix)
        return
    
    def validate_tick(self, tick):
        inst = tick.instID
        if self.instruments[inst].day_finalized:
            return False
        if (self.instruments[inst].exchange == 'CZCE') and \
                (tick.tick_id <= 530000+4) and (tick.tick_id >= 300000-4) and \
                (tick.timestamp.date() == workdays.workday(self.scur_day, -1, CHN_Holidays)):
            tick.timestamp = datetime.datetime.combine(self.scur_day, tick.timestamp.timetz())
            tick.date = self.scur_day.strftime('%Y%m%d')
        tick_date = tick.timestamp.date()
        if (self.scur_day > tick_date) or (tick_date in CHN_Holidays) or (tick_date.weekday()>=5):
            return False
        if self.scur_day < tick_date:
            self.logger.info('tick date is later than scur_day, finalizing the day and run EOD')
            event = Event(type = EVENT_DAYSWITCH)
            event.dict['date'] = tick_date
            event.dict['log'] =  u'换日: %s -> %s' % (self.scur_day, tick_date)
            self.eventEngine.put(event)
            return False
        product = self.instruments[inst].product
        exch = self.instruments[inst].exchange
        hrs = trading_hours(product, exch)
        tick_id = tick.tick_id
        if self.tick_id < tick_id:
            self.tick_id = tick_id
        tick_status = False
        for ptime in hrs:
            if (tick_id>=ptime[0]*1000-5) and (tick_id<=ptime[1]*1000+5):
                tick_status = True
                break
        return tick_status
    
    def update_instrument(self, tick):      
        inst = tick.instID    
        curr_tick = tick.tick_id
        self.instruments[inst].up_limit   = tick.upLimit
        self.instruments[inst].down_limit = tick.downLimit        
        tick.askPrice1 = min(tick.askPrice1, tick.upLimit)
        tick.bidPrice1 = max(tick.bidPrice1, tick.downLimit)
        self.instruments[inst].last_update = curr_tick
        self.instruments[inst].bid_price1 = tick.bidPrice1
        self.instruments[inst].ask_price1 = tick.askPrice1
        self.instruments[inst].mid_price = (tick.askPrice1 + tick.bidPrice1)/2.0
        self.instruments[inst].bid_vol1   = tick.bidVol1
        self.instruments[inst].ask_vol1   = tick.askVol1
        self.instruments[inst].open_interest = tick.openInterest
        last_volume = self.instruments[inst].volume
        #self.logger.debug(u'MD:收到行情，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume, last_volume))
        if tick.volume > last_volume:
            self.instruments[inst].price  = tick.price
            self.instruments[inst].volume = tick.volume
            self.instruments[inst].last_traded = curr_tick    
        return True
    
    def get_bar_id(self, tick_id):
        return int(tick_id/1000)
    
    def conv_bar_id(self, bar_id):
        return int(bar_id/100)*60 + bar_id % 100 + 1
            
    def update_min_bar(self, tick):
        inst = tick.instID
        tick_dt = tick.timestamp
        tick_id = tick.tick_id
        tick_min = self.get_bar_id(tick_id)
        if (self.cur_min[inst]['min_id'] > tick_min):
            return False
        #try:
        if (self.cur_day[inst]['open'] == 0.0):
            self.cur_day[inst]['open'] = tick.price
            self.logger.debug('open data is received for inst=%s, price = %s, tick_id = %s' % (inst, tick.price, tick_id))
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
                if (self.instruments[inst].ptype != instrument.ProductType.Option):
                    self.min_switch(inst)
                else:
                    if self.save_flag:
                        mysqlaccess.bulkinsert_tick_data(inst, self.tick_data[inst], dbtable = self.tick_db_table)              
                self.cur_min[inst]['volume'] = last_tick.volume                                
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

        for strat_name in self.inst2strat[inst]:
            self.strategies[strat_name].run_tick(tick)
        return True  
    
    def min_switch(self, inst):
        if self.cur_min[inst]['close'] == 0:
            return
        if self.cur_min[inst]['low'] == 0:
            self.cur_min[inst]['low'] = self.cur_min[inst]['close']
        if self.cur_min[inst]['high'] >= MKT_DATA_BIGNUMBER - 1000:
            self.cur_min[inst]['high'] = self.cur_min[inst]['close']
        min_id = self.cur_min[inst]['min_id']
        min_sn = self.conv_bar_id(min_id)
        df = self.min_data[inst][1]
        mysqlaccess.insert_min_data_to_df(df, self.cur_min[inst])
        for m in self.min_data_func[inst]:
            df_m = self.min_data[inst][m]
            if m > 1 and min_sn % m == 0:
                s_start = self.cur_min[inst]['datetime'] - datetime.timedelta(minutes=m)
                slices = df[df.index>s_start]
                new_data = {'open':slices['open'][0],'high':max(slices['high']), \
                            'low': min(slices['low']),'close': slices['close'][-1],\
                            'volume': sum(slices['volume']), 'min_id':slices['min_id'][0]}
                df_m.loc[s_start] = pd.Series(new_data)
                #print df_m.loc[s_start]
            if min_sn % m == 0:
                for fobj in self.min_data_func[inst][m]:
                    fobj.rfunc(df_m)
        if self.save_flag:
            #print 'insert min data inst = %s, min = %s' % (inst, min_id)
            mysqlaccess.bulkinsert_tick_data(inst, self.tick_data[inst], dbtable = self.tick_db_table)
            mysqlaccess.insert_min_data(inst, self.cur_min[inst], dbtable = self.min_db_table)        
        for strat_name in self.inst2strat[inst]:
            for m in self.inst2strat[inst][strat_name]:
                if min_sn % m == 0:
                    self.strategies[strat_name].run_min(inst, m)
        return
        
    def day_finalize(self, insts):        
        for inst in insts:
            if not self.instruments[inst].day_finalized:
                self.instruments[inst].day_finalized = True
                self.logger.debug('finalizing the day for market data = %s, scur_date=%s' % (inst, self.scur_day))
                if (len(self.tick_data[inst]) > 0) :
                    last_tick = self.tick_data[inst][-1]
                    self.cur_min[inst]['volume'] = last_tick.volume - self.cur_min[inst]['volume']
                    self.cur_min[inst]['openInterest'] = last_tick.openInterest
                    if (self.instruments[inst].ptype != instrument.ProductType.Option):
                        self.min_switch(inst)
                    else:
                        if self.save_flag:
                            mysqlaccess.bulkinsert_tick_data(inst, self.tick_data[inst], dbtable = self.tick_db_table)  
                if (self.cur_day[inst]['close']>0):
                    mysqlaccess.insert_daily_data_to_df(self.day_data[inst], self.cur_day[inst])
                    df = self.day_data[inst]
                    if (self.instruments[inst].ptype != instrument.ProductType.Option):
                        for fobj in self.day_data_func[inst]:
                            fobj.rfunc(df)
                    if self.save_flag:
                        mysqlaccess.insert_daily_data(inst, self.cur_day[inst], dbtable = self.daily_db_table)
        return
    
    def run_eod(self):
        self.day_finalize(self.instruments.keys())
        if self.trader == None:
            return
        self.save_state()
        print 'run EOD process'
        self.eod_flag = True
        pfilled_dict = {}
        for trade_id in self.ref2trade:
            etrade = self.ref2trade[trade_id]
            etrade.update()
            if etrade.status == order.ETradeStatus.Pending or etrade.status == order.ETradeStatus.Processed:
                etrade.status = order.ETradeStatus.Cancelled
                strat = self.strategies[etrade.strategy]
                strat.on_trade(etrade)
            elif etrade.status == order.ETradeStatus.PFilled:
                etrade.status = order.ETradeStatus.Cancelled
                self.logger.warning('Still partially filled after close. trade id= %s' % trade_id)
                pfilled_dict[trade_id] = etrade
        if len(pfilled_dict)>0:
            file_prefix = self.folder + 'PFILLED_'
            order.save_trade_list(self.scur_day, pfilled_dict, file_prefix)    
        for strat_name in self.strat_list:
            strat = self.strategies[strat_name]
            strat.day_finalize()
            strat.initialize()
        self.calc_margin()
        self.save_eod_positions()
        eod_pos = {}
        for inst in self.positions:
            pos = self.positions[inst]
            eod_pos[inst] = [pos.curr_pos.long, pos.curr_pos.short]
        self.ref2trade = {}
        self.ref2order = {}
        self.positions= dict([(inst, order.Position(self.instruments[inst])) for inst in self.instruments])
        self.order_stats = dict([(inst,{'submitted': 0, 'cancelled':0, 'failed': 0, 'status': True }) for inst in self.instruments])
        self.total_submitted = 0
        self.total_cancelled = 0
        self.prev_capital = self.curr_capital
        for inst in self.positions:
            self.positions[inst].pos_yday.long = eod_pos[inst][0] 
            self.positions[inst].pos_yday.short = eod_pos[inst][1]
            self.positions[inst].re_calc()
            self.instruments[inst].prev_close = self.cur_day[inst]['close']
            self.instruments[inst].volume = 0            
        self.initialized = False

    def day_switch(self, event):
        newday = event.dict['date']
        if newday <= self.scur_day:
            return
        self.logger.info('switching the trading day from %s to %s, reset tick_id=%s to 0' % (self.scur_day, newday, self.tick_id))
        self.day_finalize(self.instruments.keys())
        self.isSettlementInfoConfirmed = False
        if not self.eod_flag:
            self.run_eod()
        self.scur_day = newday
        for inst in self.instruments:
            if len(self.day_data[inst]) > 0:
                d_start = workdays.workday(self.scur_day, -self.daily_data_days, CHN_Holidays)
                df = self.day_data[inst]
                self.day_data[inst] = df[df.index >= d_start]
            m_start = workdays.workday(self.scur_day, -self.min_data_days, CHN_Holidays)
            for m in self.min_data[inst]:
                if len(self.min_data[inst][m]) > 0:
                    mdf = self.min_data[inst][m]
                    self.min_data[inst][m] = mdf[mdf.index.date >= m_start]
        self.tick_id = 0
        self.timer_count = 0
        for inst in self.instruments:
            self.tick_data[inst] = []
            self.cur_min[inst] = dict([(item, 0) for item in min_data_list])
            self.cur_day[inst] = dict([(item, 0) for item in day_data_list])
            self.cur_day[inst]['date'] = newday
            self.cur_min[inst]['datetime'] = datetime.datetime.fromordinal(newday.toordinal())
            self.instruments[inst].day_finalized = False
        self.eod_flag = False
                
    def init_init(self):    #init中的init,用于子类的处理
        self.eventEngine.register(EVENT_ORDER, self.rtn_order)
        self.eventEngine.register(EVENT_TRADE, self.rtn_trade)
        self.eventEngine.register(EVENT_ERRORDERINSERT, self.err_order_insert)
        self.eventEngine.register(EVENT_ERRORDERCANCEL, self.err_order_action)
        self.eventEngine.register(EVENT_MARGINRATE, self.rsp_qry_instrument_marginrate)
        self.eventEngine.register(EVENT_ACCOUNT, self.rsp_qry_trading_account)
        self.eventEngine.register(EVENT_INSTRUMENT, self.rsp_qry_instrument)
        self.eventEngine.register(EVENT_POSITION, self.rsp_qry_position)
        self.eventEngine.register(EVENT_QRYORDER, self.rsp_qry_order)
        self.eventEngine.register(EVENT_QRYTRADE, self.rsp_qry_trade)
        self.eventEngine.register(EVENT_TDLOGIN, self.initialize)
        #self.eventEngine.register(EVENT_TDDISCONNECTED, self.td_disconnected)
        self.eventEngine.register(EVENT_TIMER, self.time_scheduler)

    def add_mdapi(self, api):
        self.mdapis.append(api)

    def set_spi(self,spi):
        self.spi = spi

    def inc_request_id(self):
        self.request_id += 1
        return self.request_id

    def login_success(self,frontID,sessionID,max_order_ref):
        #self.order_ref = int(max_order_ref)
        pass

    ##内务处理
    def fetch_trading_account(self):
        #获取资金帐户
        self.logger.debug('A:getting trading account info..')
        r = self.trader.query_trading_account()
        return r

    def fetch_investor_position(self, instrument_id = ''):
        #获取合约的当前持仓
        self.logger.debug(u'A:获取合约%s的当前持仓..' % (instrument_id,))
        r = self.trader.query_investor_position(instrument_id)
        return r
    
    def fetch_investor_position_detail(self,instrument_id):
        '''
            获取合约的当前持仓明细，目前没用
        '''
        self.logger.debug(u'A:获取合约%s的当前持仓..' % (instrument_id,))
        r = self.trader.query_investor_position_detail(instrument_id)
        self.logger.debug(u'A:查询持仓, 函数发出返回值:%s' % r)
        return r

    def fetch_instrument_marginrate(self,instrument_id):
        r = self.trader.query_instrument_marginrate(instrument_id)
        self.logger.debug(u'A:查询保证金率, 函数发出返回值:%s' % r)
        return r

    def fetch_instrument(self,instrument_id):
        r = self.trader.query_instrument(instrument_id)
        self.logger.debug(u'A:查询合约, 函数发出返回值:%s' % r)
        return r

    def fetch_instruments_by_exchange(self,exchange_id):
        '''不能单独用exchange_id,因此没有意义
        '''
        r = self.trader.query_instruments_by_exch(exchange_id)
        self.logger.debug(u'A:查询合约, 函数发出返回值:%s' % r)
        return r

    def fetch_order(self, start_time='', end_time=''):
        r = self.trader.query_order( start_time, end_time )
        self.logger.debug(u'A:查询报单, 函数发出返回值:%s' % r)
        return r

    def fetch_trade(self, start_time='', end_time=''):
        r = self.trader.query_trade( start_time, end_time )
        self.logger.debug(u'A:查询成交单, 函数发出返回值:%s' % r)
        return r
    
    def rtn_tick(self, event):#行情处理主循环
        ctick = event.dict['data']
        if self.live_trading:
            now_ticknum = get_tick_num(datetime.datetime.now())
            cur_ticknum = get_tick_num(ctick.timestamp)
            if abs(cur_ticknum - now_ticknum)> MAX_REALTIME_DIFF:
                self.logger.warning('the tick timestamp has more than 10sec diff from the system time, inst=%s, ticknum= %s, now_ticknum=%s' % (ctick.instID, cur_ticknum, now_ticknum))
                return 0
            
        if (not self.validate_tick(ctick)):
            #print "stop at validating tick", ctick.instID, ctick.timestamp, ctick.tick_id
            return 0
        
        if (not self.update_instrument(ctick)):
            #print "stop at update inst", ctick.instID, ctick.timestamp, ctick.tick_id
            return 0
     
        if( not self.update_min_bar(ctick)):
            #print "stop at hist data update", ctick.instID, ctick.timestamp, ctick.tick_id
            return 0
        return 1

    def process_trade(self, exec_trade):
        all_orders = {}
        pending_orders = []
        order_prices = []
        trade_ref = exec_trade.id
        for inst, v, tick in zip(exec_trade.instIDs, exec_trade.volumes, exec_trade.slip_ticks):
            if v>0:
                order_prices.append(self.instruments[inst].bid_price1+self.instruments[inst].tick_base*tick)
            else:
                order_prices.append(self.instruments[inst].ask_price1-self.instruments[inst].tick_base*tick)    
        curr_price = sum([p*v*cf for p, v, cf in zip(order_prices, exec_trade.volumes, exec_trade.conv_f)])/exec_trade.price_unit
        if curr_price <= exec_trade.limit_price: 
            required_margin = 0
            for idx, (inst, v, otype) in enumerate(zip(exec_trade.instIDs, exec_trade.volumes, exec_trade.order_types)):
                orders = []
                pos = self.positions[inst]
                pos.re_calc()
                self.calc_margin()
                if ((v>0) and (v > pos.can_close.long + pos.can_yclose.long + pos.can_open.long)) or \
                        ((v<0) and (-v > pos.can_close.short + pos.can_yclose.short + pos.can_open.short)):
                    self.logger.warning("ETrade %s is cancelled due to position limit on leg %s: %s" % (exec_trade.id, idx, inst))
                    exec_trade.status = order.ETradeStatus.Cancelled
                    strat = self.strategies[exec_trade.strategy]
                    strat.on_trade(exec_trade)
                    return False

                if v>0:
                    direction = ORDER_BUY
                    vol = max(min(v, pos.can_close.long),0)
                    remained = v - vol
                else:
                    direction = ORDER_SELL
                    vol = max(min(-v,pos.can_close.short),0)
                    remained = v + vol
                    
                if vol > 0:
                    cond = {}
                    if (idx>0) and (exec_trade.order_types[idx-1] == OPT_LIMIT_ORDER):
                        cond = { o:order.OrderStatus.Done for o in all_orders[exec_trade.instIDs[idx-1]]}
                    order_type = OF_CLOSE
                    if (self.instruments[inst].exchange == "SHFE"):
                        order_type = OF_CLOSE_TDAY                        
                    iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, order_type, direction, otype, cond, trade_ref )
                    orders.append(iorder)
                  
                if (self.instruments[inst].exchange == "SHFE") and (abs(remained)>0) and (pos.can_yclose.short+pos.can_yclose.long>0):
                    if remained>0:
                        direction = ORDER_BUY
                        vol = max(min(remained, pos.can_yclose.long),0)
                        remained -= vol
                    else:
                        direction = ORDER_SELL
                        vol = max(min(-remained,pos.can_yclose.short),0)
                        remained += vol
                        
                    if vol > 0:
                        cond = {}
                        if (idx>0) and (exec_trade.order_types[idx-1] == OPT_LIMIT_ORDER):
                            cond = { o:order.OrderStatus.Done for o in all_orders[exec_trade.instIDs[idx-1]]}
                        iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, OF_CLOSE_YDAY, direction, otype, cond, trade_ref )
                        orders.append(iorder)
                
                vol = abs(remained)
                if vol > 0:                   
                    if remained >0:
                        direction = ORDER_BUY
                    else:
                        direction = ORDER_SELL
                    under_price = 0.0
                    if (self.instruments[inst].ptype == instrument.ProductType.Option):
                        under_price = self.instruments[self.instruments[inst].underlying].price
                    required_margin += vol * self.instruments[inst].calc_margin_amount(direction, under_price)
                    cond = {}
                    if (idx>0) and (exec_trade.order_types[idx-1] == OPT_LIMIT_ORDER):
                        cond = { o:order.OrderStatus.Done for o in all_orders[exec_trade.instIDs[idx-1]]}
                    iorder = order.Order(pos, order_prices[idx], vol, self.tick_id, OF_OPEN, direction, otype, cond, trade_ref )
                    orders.append(iorder)
                all_orders[inst] = orders
                
            if required_margin + self.locked_margin > self.margin_cap:
                self.logger.warning("ETrade %s is cancelled due to margin cap: %s" % (exec_trade.id, inst))
                exec_trade.status = order.ETradeStatus.Cancelled
                strat = self.strategies[exec_trade.strategy]
                strat.on_trade(exec_trade)
                return False

            exec_trade.order_dict = all_orders
            for inst in exec_trade.instIDs:
                pos = self.positions[inst]
                for iorder in all_orders[inst]:
                    pos.add_order(iorder)
                    self.ref2order[iorder.order_ref] = iorder
                    if iorder.status == order.OrderStatus.Ready:
                        pending_orders.append(iorder.order_ref)
            exec_trade.status = order.ETradeStatus.Processed
            return pending_orders
        else:
            #self.logger.debug("do not meet the limit price,etrade_id=%s, etrade_inst=%s,  curr price = %s, limit price = %s" % \
            #                 (exec_trade.id, exec_trade.instIDs, curr_price, exec_trade.limit_price))
            return pending_orders
        
    def check_trade(self, exec_trade):
        pending_orders = []
        trade_ref = exec_trade.id
        if exec_trade.id not in self.ref2trade:
            self.ref2trade[exec_trade.id] = exec_trade
        if exec_trade.status == order.ETradeStatus.Pending:
            if exec_trade.valid_time < self.tick_id:
                exec_trade.status = order.ETradeStatus.Cancelled
                strat = self.strategies[exec_trade.strategy]
                strat.on_trade(exec_trade)
            else:
                pending_orders = self.process_trade(exec_trade)
        elif (exec_trade.status == order.ETradeStatus.Processed) or (exec_trade.status == order.ETradeStatus.PFilled):
            #exec_trade.update()
            if exec_trade.valid_time < self.tick_id:
                if exec_trade.status != order.ETradeStatus.Done:
                    exec_trade.valid_time = self.tick_id + self.cancel_protect_period
                    new_orders = {}
                    for inst in exec_trade.instIDs:
                        orders = []
                        for iorder in exec_trade.order_dict[inst]:
                            if (iorder.volume > iorder.filled_volume):
                                if ( iorder.status == order.OrderStatus.Waiting) \
                                        or (iorder.status == order.OrderStatus.Ready):
                                    iorder.on_cancel()
                                    self.trade_update(iorder)
                                else:
                                    self.cancel_order(iorder)
                                if exec_trade.status == order.ETradeStatus.PFilled:                                        
                                    cond = {iorder:order.OrderStatus.Cancelled}
                                    norder = order.Order(iorder.position,
                                                0,
                                                0, # fill in the volume when the dependent order is cancelled
                                                self.tick_id,
                                                iorder.action_type,
                                                iorder.direction,
                                                OPT_MARKET_ORDER,
                                                cond,
                                                trade_ref)
                                    orders.append(norder)
                        if len(orders)>0:
                            new_orders[inst] = orders
                    for inst in new_orders:
                        pos = self.positions[inst]
                        for iorder in new_orders[inst]:
                            exec_trade.order_dict[inst].append(iorder)
                            pos.add_order(iorder)
                            self.ref2order[iorder.order_ref] = iorder
                            if iorder.status == order.OrderStatus.Ready:
                                pending_orders.append(iorder.order_ref)
        #print pending_orders
        if (len(pending_orders) > 0):
            for order_ref in pending_orders:
                self.send_order(self.ref2order[order_ref])
            self.save_state()
    
    def send_order(self,iorder):
        ''' 发出下单指令
        '''
        self.logger.debug(u'A_CC:开仓平仓命令: order_ref = %s' % iorder.order_ref)
        inst = iorder.instrument.name
        if not self.order_stats[inst]['status']:
            self.logger.warning('Canceling order = %s for instrument = %s is disabled for trading due to position control' % (iorder.order_ref, inst))
            iorder.on_cancel()
            self.trade_update(iorder)
            return
        # 上期所不支持市价单
        if (iorder.price_type == OPT_MARKET_ORDER):
            if (inst.exchange == 'SHFE' or inst.exchange == 'CFFEX'):
                self.logger.debug('sending limiting order_ref=%s inst=%s for SHFE and CFFEX, change to limit order' % (iorder.order_ref, iorder.instrument.name))
                iorder.price_type = OPT_LIMIT_ORDER
                # 以后可以改成涨停,跌停价
                if iorder.direction == ORDER_BUY:
                    iorder.limit_price = min(inst.up_limit, inst.ask_price1 + inst.tick_base * self.market_order_tick_multiple)
                else:
                    iorder.limit_price = max(inst.down_limit, inst.bid_price1 - inst.tick_base * self.market_order_tick_multiple)
            else:
                iorder.limit_price = 0.0
        iorder.status = order.OrderStatus.Sent
        self.trader.send_order(iorder)
        self.order_stats[inst]['submitted'] += 1
        self.total_submitted += 1
        if self.order_stats[inst]['submitted'] >= self.submitted_limit_per_inst:
            self.order_stats[inst]['status'] = False
        if self.total_submitted >= self.total_submitted_limit:
            for inst in self.instruments:
                self.order_stats[inst]['status'] = False
        return

    def cancel_order(self,iorder):
        '''发出撤单指令  
        '''
        self.logger.info(u'A_CC:发出撤单指令: order_ref = %s' % iorder.order_ref)
        self.trader.cancel_order(iorder)
        inst = iorder.instrument.name
        self.order_stats[inst]['cancelled'] += 1
        self.total_cancelled += 1
         
    ###回应
    def rtn_trade(self, event):
        '''成交回报
        #TODO: 必须考虑出现平仓信号时，position还没完全成交的情况在OnTrade中进行position的细致处理 
        #TODO: 必须处理策略分类持仓汇总和持仓总数不匹配时的问题
        '''        
        ptrade = event.dict['data']
        if not ptrade.OrderRef.isdigit():
            return
        else:
            self.logger.debug('trade = %s' % repr(ptrade))
        order_ref = int(ptrade.OrderRef)
        if order_ref in self.ref2order:
            myorder = self.ref2order[order_ref]
            myorder.on_trade(price = ptrade.Price, volume=ptrade.Volume, trade_id = ptrade.TradeID)
            self.trade_update(myorder)
            if myorder.action_type == OF_OPEN:#开仓, 也可用pTrade.OffsetFlag判断
                self.logger.debug(u'A_RT31,开仓回报,price=%s,trade_id=%s' % (ptrade.Price, ptrade.TradeID))
            else:
                self.logger.debug(u'A_RT32,平仓回报,price=%s,trade_id=%s' % (ptrade.Price, ptrade.TradeID))
        else:
            self.logger.info(u'A_RT2:收到非本程序发出的成交回报:%s-%s' % (ptrade.InstrumentID,ptrade.OrderRef))

    def rtn_order(self, event):
        '''交易所接受下单回报(CTP接受的已经被过滤)暂时只处理撤单的回报. 
        '''
        porder = event.dict['data']
        if not porder.OrderRef.isdigit():
            return
        else:
            self.logger.debug('order = %s' % repr(porder))
        order_ref = int(porder.OrderRef)
        if (order_ref in self.ref2order):
            myorder = self.ref2order[order_ref]
            # only update sysID,
            status = myorder.on_order(sys_id = porder.OrderSysID, price = porder.LimitPrice, volume = 0)
            if status:
                self.trade_update(myorder)
            elif porder.OrderStatus in [ self.trader.ApiStruct.OST_Canceled, self.trader.ApiStruct.OST_PartTradedNotQueueing]:   #完整撤单或部成部撤
                self.logger.info('cancel the rest order in order_ref = %s' % order_ref )
                myorder.on_cancel()                
                self.trade_update(myorder) 
        else:
            self.logger.warning('receive order update from other agents, Order=%s' % repr(porder))

    def trade_update(self, myorder):
        trade_ref = myorder.trade_ref
        mytrade = self.ref2trade[trade_ref]
        pending_orders = mytrade.update()
        if (mytrade.status == order.ETradeStatus.Done) or (mytrade.status == order.ETradeStatus.Cancelled):            
            strat = self.strategies[mytrade.strategy]
            strat.on_trade(mytrade)
            self.save_state()
        else:
            if len(pending_orders) > 0:
                for order_ref in pending_orders:
                    self.send_order(self.ref2order[order_ref])
                self.save_state()
            
    def err_order_insert(self, event):
        '''
            ctp/交易所下单错误回报，不区分ctp和交易所正常情况下不应当出现
        '''
        porder = event.dict['data']
        if not porder.OrderRef.isdigit():
            return
        else:
            self.logger.debug('trade update: %s' % porder)
        order_ref = int(porder.OrderRef)
        inst = porder.InstrumentID
        error = event.dict['error']
        if order_ref in self.ref2order:
            myorder = self.ref2order[order_ref]
            myorder.on_cancel()
            self.trade_update(myorder)
            self.logger.warning(u'OrderInsert is not accepted by CTP, order_ref=%s, instrument=%s, error=%s' % (order_ref, inst, error.ErrorMsg))
        else:
            self.logger.info(u'OrderInsert error from other programs, order_ref=%s, instrument=%s, error=%s' % (order_ref, inst, error.ErrorMsg))
        self.order_stats[inst]['failed'] += 1
        if self.order_stats[inst]['failed'] >= self.failed_order_limit:
            self.order_stats[inst]['status'] = False
            self.logger.warning('failed order reaches the limit, disable instrument = %s' % inst)

    def err_order_action(self, event):
        '''
            ctp/交易所撤单错误回报，不区分ctp和交易所必须处理，如果已成交，撤单后必然到达这个位置
        '''
        porder = event.dict['data']
        error = event.dict['error']
        if porder.OrderRef.isdigit():
            order_ref = int(porder.OrderRef)
            self.logger.debug('trade update: %s' % porder)
            myorder = self.ref2order[order_ref]
            if int(error.ErrorID) in [25,26] and myorder.status not in [order.OrderStatus.Cancelled, order.OrderStatus.Done]:
                self.logger.debug('cancel order_ref=%s'% order_ref)
                myorder.on_cancel()
                self.trade_update(myorder) 
        else:
            self.qry_commands.append(self.fetch_order)
            self.qry_commands.append(self.fetch_order)
        inst = porder.InstrumentID
        self.order_stats[inst]['failed'] += 1
        if self.order_stats[inst]['failed'] >= self.failed_order_limit:
            self.order_stats[inst]['status'] = False
            self.logger.warning('failed order reaches the limit, disable instrument = %s' % inst)

    ###辅助   
    def rsp_qry_position(self, event):
        pposition = event.dict['data']
        isLast = event.dict['isLast']
        instID = pposition.InstrumentID
        if (instID in self.qry_pos):
            key = 'yday'
            idx = 1
            if pposition.PosiDirection == self.trader.ApiStruct.PD_Long:
                if pposition.PositionDate == self.trader.ApiStruct.PSD_Today:
                    key = 'tday'
                    idx = 0
                else:
                    idx = 0
            else:
                if pposition.PositionDate == self.trader.ApiStruct.PSD_Today:
                    key = 'tday'
            self.qry_pos[instID][key][idx] = pposition.Position
            self.qry_pos[instID]['yday'][idx] = pposition.YdPosition
        if isLast:
            print self.qry_pos
            pass
        # need to cross check position accuracy

    def rsp_qry_instrument_marginrate(self, event):
        '''查询保证金率回报. '''
        pinst = event.dict['data']
        instID = pinst.InstrumentID
        if instID in self.instruments:
            inst = self.instruments[instID]
            inst.marginrate = (pinst.LongMarginRatio, pinst.ShortMarginRatio)    

    def rsp_qry_trading_account(self, event):
        '''查询资金帐户回报'''
        paccount = event.dict['data']
        self.available = paccount.Available      
    
    def rsp_qry_instrument(self, event):
        pinst = event.dict['data']
        instID = pinst.InstrumentID
        if instID in self.instruments:
            inst = self.instruments[instID]
            inst.multiple = pinst.VolumeMultiple
            inst.tick_base = pinst.PriceTick
            inst.marginrate = (pinst.LongMarginRatio, pinst.ShortMarginRatio)        

    def rsp_qry_position_detail(self,position_detail):
        '''查询持仓明细回报, 得到每一次成交的持仓,其中若已经平仓,则持量为0,平仓量>=1必须忽略
        '''
        pass

    def rsp_qry_order(self, event):
        '''查询报单'''
        sorder = event.dict['data']
        isLast = event.dict['isLast']
        if (sorder == None) or (sorder.InstrumentID not in self.instruments) or (len(sorder.OrderRef) == 0):
            return
        if not sorder.OrderRef.isdigit():
            return
        else:
            self.logger.debug('query order return= %s' % repr(sorder))
        order_ref = int(sorder.OrderRef) 
        if (order_ref in self.ref2order):
            iorder = self.ref2order[order_ref]
            self.ctp_orders.append(order_ref)
            if iorder.status not in [order.OrderStatus.Cancelled, order.OrderStatus.Done]:
                status = iorder.on_order(sys_id = sorder.OrderSysID, price = sorder.LimitPrice, volume = sorder.VolumeTraded)
                if status:
                    self.trade_update(iorder)
                elif sorder.OrderStatus in [self.trader.ApiStruct.OST_NoTradeQueueing, self.trader.ApiStruct.OST_PartTradedQueueing, self.trader.ApiStruct.OST_Unknown]:
                    if iorder.status != order.OrderStatus.Sent or iorder.conditionals != {}:
                        self.logger.info('order status for OrderSysID = %s, Inst=%s is set to %s, but should be waiting in exchange queue' % (iorder.sys_id, iorder.instrument.name, iorder.status))
                        iorder.status = order.OrderStatus.Sent
                        iorder.conditionals = {}
                        #iorpder.position.re_calc()
                elif sorder.OrderStatus in [self.trader.ApiStruct.OST_Canceled, self.trader.ApiStruct.OST_PartTradedNotQueueing, self.trader.ApiStruct.OST_NoTradeNotQueueing]:
                    if iorder.status != order.OrderStatus.Cancelled:
                        self.logger.info('order status for OrderSysID = %s, Inst=%s is set to %s, but should be cancelled' % (iorder.sys_id, iorder.instrument.name, iorder.status))
                        iorder.on_cancel()
                        self.trade_update(iorder)
        if isLast:
            for order_ref in self.ref2order:
                if (order_ref not in self.ctp_orders):
                    iorder = self.ref2order[order_ref]
                    iorder.on_cancel()
                    self.trade_update(iorder)
            self.ctp_orders = []

    def rsp_qry_trade(self, event):
        '''查询成交'''
        strade = event.dict['data']
        if (strade == None) or (strade.InstrumentID not in self.instruments) or (len(strade.OrderRef) == 0):
            return
        self.logger.debug('query trade return= %s' % repr(strade))
        if not strade.OrderRef.isdigit():
            return
        order_ref = int(strade.OrderRef) 
        if (order_ref in self.ref2order):
            iorder = self.ref2order[order_ref]
            if (iorder.status not in [order.OrderStatus.Done, order.OrderStatus.Cancelled]) or (iorder.filled_volume != strade.Volume):
                status = iorder.on_trade(price = strade.Price, volume=strade.Volume, trade_id = strade.TradeID)
                #if status == False:
                #    iorder.on_cancel()
                self.trade_update(iorder)       

    def exit(self):
        """退出"""
        # 停止事件驱动引擎
        self.eventEngine.stop()
        self.logger.info('stopped the engine, exiting the agent ...')
        self.save_state()
        for strat_name in self.strat_list:
            strat = self.strategies[strat_name]
            strat.save_state()
        # 销毁API对象
        self.trader = None
        self.mdapis = []
        #self.eventEngine = None

class SaveAgent(Agent):
    def init_init(self):
        self.save_flag = True 
        self.live_trading = False
        self.prepare_data_env(mid_day = True)
        self.eventEngine.register(EVENT_TIMER, self.time_scheduler)

    def resume(self):
        self.eventEngine.start()

    def exit(self):
        self.eventEngine.stop()
        self.trader = None
        self.mdapis = []

if __name__=="__main__":
    pass
    
