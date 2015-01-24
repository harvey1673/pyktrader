#-*- coding=utf-8 -*-
from ctp.futures import ApiStruct, TraderApi
import time
import traceback
import threading
import datetime
import mysqlaccess
import misc

THOST_TERT_RESTART  = ApiStruct.TERT_RESTART
THOST_TERT_RESUME   = ApiStruct.TERT_RESUME
THOST_TERT_QUICK    = ApiStruct.TERT_QUICK

class MyTraderApi(TraderApi):
    def __init__(self, broker_id,
                 investor_id, passwd, *args,**kwargs):
        self.requestid=0
        self.broker_id =broker_id
        self.investor_id = investor_id
        self.passwd = passwd
        self.reqID = 0
        self.event = threading.Event()
        self.lastupdate = datetime.datetime.now()
        self.instruments={'CFFEX':[], 'CZCE':[], 'DCE':[], 'SHFE':[]}

    def OnRspError(self, info, RequestId, IsLast):
        print " Error"
        self.isErrorRspInfo(info)

    def isErrorRspInfo(self, info):
        if info.ErrorID !=0:
            print "ErrorID=", info.ErrorID, ", ErrorMsg=", info.ErrorMsg
        return info.ErrorID !=0

    def OnFrontDisConnected(self, reason):
        print "onFrontDisConnected:", reason

    def OnHeartBeatWarning(self, time):
        print "onHeartBeatWarning", time

    def OnFrontConnected(self):
        print "OnFrontConnected:"
        self.user_login(self.broker_id, self.investor_id, self.passwd)

    def user_login(self, broker_id, investor_id, passwd):
        req = ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=passwd)
        self.requestid+=1
        r=self.ReqUserLogin(req, self.requestid)        

    def OnRspUserLogin(self, userlogin, info, rid, is_last):
        print userlogin
        print 'errMsg=%s' %(info.ErrorMsg,)
        #print "OnRspUserLogin", is_last, info
        #if is_last and not self.isErrorRspInfo(info):
        #    print "get today's trading day:", repr(self.GetTradingDay())
        #    self.subscribe_market_data(self.instruments)
        self.query_settlement_confirm() 
        
    def query_settlement_confirm(self):
        req = ApiStruct.QrySettlementInfoConfirm(BrokerID=self.broker_id,InvestorID=self.investor_id)
        self.requestid += 1
        self.ReqQrySettlementInfoConfirm(req,self.requestid)

    def OnRspQrySettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        '''请求查询结算信息确认响应'''
        print u"TD:结算单确认信息查询响应:rspInfo=%s,结算单确认=%s, reqID=%s, isLast=%s" % (pRspInfo,pSettlementInfoConfirm, nRequestID, bIsLast)
        self.query_settlement_info()

    def query_settlement_info(self):
        #不填日期表示取上一天结算单,并在响应函数中确认
        print u'TD:取上一日结算单信息并确认,BrokerID=%s,investorID=%s' % (self.broker_id,self.investor_id)
        req = ApiStruct.QrySettlementInfo(BrokerID=self.broker_id,InvestorID=self.investor_id,TradingDay=u'')
        #print req.BrokerID,req.InvestorID,req.TradingDay
        #time.sleep(0.5)
        self.requestid += 1
        self.ReqQrySettlementInfo(req,self.requestid)

    def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
        '''请求查询投资者结算信息响应'''
        print u'Rsp 结算单查询'
        if(self.resp_common(pRspInfo,bIsLast,u'结算单查询')>0):
            print u'结算单查询完成,准备确认'
            try:
                print u'TD:结算单内容:%s' % pSettlementInfo.Content
            except Exception,inst:
                print u'TD-ORQSI-A 结算单内容错误:%s' % str(inst)
            self.confirm_settlement_info()
        else:  #这里是未完成分支,需要直接忽略
            try:
                print u'TD:结算单接收中...:%s' % pSettlementInfo.Content
            except Exception,inst:
                print u'TD-ORQSI-B 结算单内容错误:%s' % str(inst)
            #self.agent.initialize()
            pass
        
    def confirm_settlement_info(self):
        print u'TD-CSI:准备确认结算单'
        req = ApiStruct.SettlementInfoConfirm(BrokerID=self.broker_id,InvestorID=self.investor_id)
        self.requestid += 1
        self.ReqSettlementInfoConfirm(req,self.requestid)
    
    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        '''投资者结算结果确认响应'''
        if(self.resp_common(pRspInfo,bIsLast,u'结算单确认')>0):
            print u'TD:结算单确认时间: %s-%s' %(pSettlementInfoConfirm.ConfirmDate,pSettlementInfoConfirm.ConfirmTime)
        print "start initialized"
            
    def isRspSuccess(self,RspInfo):
        return RspInfo == None or RspInfo.ErrorID == 0
    
    def resp_common(self,rsp_info,bIsLast,name='默认'):
        #self.logger.debug("resp: %s" % str(rsp_info))
        if not self.isRspSuccess(rsp_info):
            print u"TD:%s失败" % name
            return -1
        elif bIsLast and self.isRspSuccess(rsp_info):
            print u"TD:%s成功" % name
            return 1
        else:
            print u"TD:%s结果: 等待数据接收完全..." % name
            return 0

    def queryDepthMarketData(self, instrument):
        req = ApiStruct.QryDepthMarketData(InstrumentID=instrument)
        self.requestid = self.requestid+1
        self.ReqQryDepthMarketData(req, self.requestid)
    
    def OnRspQryDepthMarketData(self, depth_market_data, pRspInfo, nRequestID, bIsLast):                    
        print nRequestID
        print pRspInfo
        print depth_market_data
        t = datetime.datetime.now()
        print t
        if (t - self.lastupdate)>datetime.timedelta(seconds=1):
            self.lock.release()
            print "release the lock"

    def fetch_instrument_marginrate(self,instrument_id):
        req = ApiStruct.QryInstrumentMarginRate(BrokerID=self.broker_id,
                        InvestorID=self.investor_id,
                        InstrumentID=instrument_id,
                        HedgeFlag = ApiStruct.HF_Speculation
                )
        self.requestid += 1
        r = self.ReqQryInstrumentMarginRate(req,self.requestid)
        print u'A:查询保证金率%s, 函数发出返回值:%s' % (instrument_id, r)

    def OnRspQryInstrumentMarginRate(self, pInstrumentMarginRate, pRspInfo, nRequestID, bIsLast):
        '''
            保证金率回报。返回的必然是绝对值
        '''
        if bIsLast and self.isRspSuccess(pRspInfo):
            print pInstrumentMarginRate
        else:
            #logging
            pass
        
    def fetch_instrument(self,instrument_id):
        req = ApiStruct.QryInstrument(
                        InstrumentID=instrument_id,
                )
        self.requestid += 1
        r = self.ReqQryInstrument(req,self.requestid)
        print u'A:查询合约, 函数发出返回值:%s' % r
        
    def OnRspQryInstrument(self, pInst, pRspInfo, nRequestID, bIsLast):
        '''
            合约回报。
        '''
        if bIsLast and self.isRspSuccess(pRspInfo):
            if (pInst.ExchangeID in self.instruments) and (pInst.ProductClass=='1'):
                cont = {}
                cont['instID'] = pInst.InstrumentID
                cont['margin_l'] = pInst.LongMarginRatio
                cont['margin_s'] = pInst.ShortMarginRatio
                cont['start_date'] = datetime.datetime.strptime(pInst.OpenDate,'%Y%M%d').date()
                cont['expiry'] = datetime.datetime.strptime(pInst.ExpireDate,'%Y%M%d').date()
                cont['product_code'] = pInst.ProductID
                self.instruments[pInst.ExchangeID].append(cont)
        else:
            if (str(pInst.ExchangeID) in self.instruments) and (pInst.ProductClass=='1'):
                cont = {}
                cont['instID'] = pInst.InstrumentID
                cont['margin_l'] = pInst.LongMarginRatio
                cont['margin_s'] = pInst.ShortMarginRatio
                cont['start_date'] = datetime.datetime.strptime(pInst.OpenDate,'%Y%m%d').date()
                cont['expiry'] = datetime.datetime.strptime(pInst.ExpireDate,'%Y%m%d').date()
                cont['product_code'] = pInst.ProductID
                self.instruments[pInst.ExchangeID].append(cont)

    def OnRtnOrder(self, pOrder):
        print pOrder
        
    def fetch_trading_account(self):
        #获取资金帐户
        
        print u'A:获取资金帐户..'
        req = ApiStruct.QryTradingAccount(BrokerID=self.broker_id, InvestorID=self.investor_id)
        self.requestid += 1
        r=self.ReqQryTradingAccount(req,self.requestid)
        #logging.info(u'A:查询资金账户, 函数发出返回值:%s' % r)

    def fetch_investor_position(self,instrument_id):
        #获取合约的当前持仓
        print u'A:获取合约%s的当前持仓..' % (instrument_id,)
        req = ApiStruct.QryInvestorPosition(BrokerID=self.broker_id, InvestorID=self.investor_id,InstrumentID=instrument_id)
        self.requestid += 1
        r=self.ReqQryInvestorPosition(req,self.requestid)
        #logging.info(u'A:查询持仓, 函数发出返回值:%s' % rP)
    
    def fetch_investor_position_detail(self,instrument_id):
        '''
            获取合约的当前持仓明细，目前没用
        '''
        
        print u'A:获取合约%s的当前持仓..' % (instrument_id,)
        req = ApiStruct.QryInvestorPositionDetail(BrokerID=self.broker_id, InvestorID=self.investor_id,InstrumentID=instrument_id)
        self.requestid += 1
        r=self.ReqQryInvestorPositionDetail(req,self.requestid)

    def fetch_order(self, t_start='09:00:00', t_end='15:15:00'):
        req = ApiStruct.QryOrder(
                        BrokerID=self.broker_id, 
                        InvestorID=self.investor_id,
                        InstrumentID='',
                        ExchangeID = '', #交易所代码, char[9]
                        #OrderSysID = '', #报单编号, char[21]
                        InsertTimeStart = '', #开始时间, char[9]
                        InsertTimeEnd = '', #结束时间, char[9]
                )
        self.requestid += 1
        r = self.ReqQryOrder(req, self.requestid)

    def fetch_trade(self, t_start='09:00:00', t_end='15:15:00'):
        req = ApiStruct.QryTrade(
                        BrokerID=self.broker_id, 
                        InvestorID=self.investor_id,
                        InstrumentID='',
                        ExchangeID ='', #交易所代码, char[9]
                        #TradeID = '', #报单编号, char[21]
                        TradeTimeStart = '', #开始时间, char[9]
                        TradeTimeEnd = '', #结束时间, char[9]
                )
        self.requestid += 1
        r = self.ReqQryTrade(req, self.requestid)
        
    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        '''
            请求查询资金账户响应
        '''
        print u'查询资金账户响应', pTradingAccount
        if bIsLast and self.isRspSuccess(pRspInfo):
            print pTradingAccount
        else:
            #logging
            pass

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        '''请求查询投资者持仓响应'''
        self.event.set()
        if self.isRspSuccess(pRspInfo): #每次一个单独的数据报
            print pInvestorPosition, "True"
        else:
            #logging
            print pInvestorPosition, "False"
            pass

    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
        print u'请求查询投资者持仓明细响应'
        self.event.set()
        if self.isRspSuccess(pRspInfo): #每次一个单独的数据报
            print pInvestorPositionDetail
        else:
            #logging
            pass

    def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
        '''请求查询报单响应'''
        if bIsLast and self.isRspSuccess(pRspInfo):
            print 'last:%s' % pOrder
        else:
            print 'first: %s' % pOrder

    def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
        '''请求查询成交响应'''
        if bIsLast and self.isRspSuccess(pRspInfo):
            print 'last:%s' % pTrade
        else:
            print 'first: %s' % pTrade

    def fetch_instruments_by_exchange(self,exchange_id):
        '''不能单独用exchange_id,因此没有意义
        '''
        req = ApiStruct.QryInstrument(
                        ExchangeID=exchange_id,
                )
        self.requestid += 1
        r = self.ReqQryInstrument(req,self.requestid)
        print u'A:查询合约, 函数发出返回值:%s' % r
        
    def OnRtnDepthMarketData(self, depth_market_data):
        print "OnRtnDepthMarketData"
        print depth_market_data.BidPrice1,depth_market_data.BidVolume1,depth_market_data.AskPrice1,depth_market_data.AskVolume1,depth_market_data.LastPrice,depth_market_data.Volume,depth_market_data.UpdateTime,depth_market_data.UpdateMillisec,depth_market_data.InstrumentID


def main():
    
    #user = MyTraderApi(broker_id="8000",investor_id="24661668",passwd="121862")
    user = MyTraderApi(broker_id = misc.PROD_TRADER.broker_id, 
                       investor_id = misc.PROD_TRADER.investor_id, 
                       passwd=misc.PROD_TRADER.passwd)
    user.Create("trader")
    user.SubscribePublicTopic(THOST_TERT_QUICK)
    user.SubscribePrivateTopic(THOST_TERT_QUICK)
    user.RegisterFront("tcp://zjzx-front12.ctp.shcifco.com:41205")
    user.Init()

    time.sleep(3)
    user.fetch_instruments_by_exchange('')
    time.sleep(20)
    for exch in user.instruments:
        for inst in user.instruments[exch]:
            mysqlaccess.insert_cont_data(inst)
            
    return user.instruments

if __name__=="__main__": main()
