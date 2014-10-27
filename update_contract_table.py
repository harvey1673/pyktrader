#-*- coding=utf-8 -*-
from ctp.futures import ApiStruct, TraderApi
import time
import traceback
import threading
import datetime
import mysqlaccess

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
        '''�����ѯ������Ϣȷ����Ӧ'''
        print u"TD:���㵥ȷ����Ϣ��ѯ��Ӧ:rspInfo=%s,���㵥ȷ��=%s, reqID=%s, isLast=%s" % (pRspInfo,pSettlementInfoConfirm, nRequestID, bIsLast)
        self.query_settlement_info()

    def query_settlement_info(self):
        #�������ڱ�ʾȡ��һ����㵥,������Ӧ������ȷ��
        print u'TD:ȡ��һ�ս��㵥��Ϣ��ȷ��,BrokerID=%s,investorID=%s' % (self.broker_id,self.investor_id)
        req = ApiStruct.QrySettlementInfo(BrokerID=self.broker_id,InvestorID=self.investor_id,TradingDay=u'')
        #print req.BrokerID,req.InvestorID,req.TradingDay
        #time.sleep(0.5)
        self.requestid += 1
        self.ReqQrySettlementInfo(req,self.requestid)

    def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
        '''�����ѯͶ���߽�����Ϣ��Ӧ'''
        print u'Rsp ���㵥��ѯ'
        if(self.resp_common(pRspInfo,bIsLast,u'���㵥��ѯ')>0):
            print u'���㵥��ѯ���,׼��ȷ��'
            try:
                print u'TD:���㵥����:%s' % pSettlementInfo.Content
            except Exception,inst:
                print u'TD-ORQSI-A ���㵥���ݴ���:%s' % str(inst)
            self.confirm_settlement_info()
        else:  #������δ��ɷ�֧,��Ҫֱ�Ӻ���
            try:
                print u'TD:���㵥������...:%s' % pSettlementInfo.Content
            except Exception,inst:
                print u'TD-ORQSI-B ���㵥���ݴ���:%s' % str(inst)
            #self.agent.initialize()
            pass
        
    def confirm_settlement_info(self):
        print u'TD-CSI:׼��ȷ�Ͻ��㵥'
        req = ApiStruct.SettlementInfoConfirm(BrokerID=self.broker_id,InvestorID=self.investor_id)
        self.requestid += 1
        self.ReqSettlementInfoConfirm(req,self.requestid)
    
    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        '''Ͷ���߽�����ȷ����Ӧ'''
        if(self.resp_common(pRspInfo,bIsLast,u'���㵥ȷ��')>0):
            print u'TD:���㵥ȷ��ʱ��: %s-%s' %(pSettlementInfoConfirm.ConfirmDate,pSettlementInfoConfirm.ConfirmTime)
        print "start initialized"
            
    def isRspSuccess(self,RspInfo):
        return RspInfo == None or RspInfo.ErrorID == 0
    
    def resp_common(self,rsp_info,bIsLast,name='Ĭ��'):
        #self.logger.debug("resp: %s" % str(rsp_info))
        if not self.isRspSuccess(rsp_info):
            print u"TD:%sʧ��" % name
            return -1
        elif bIsLast and self.isRspSuccess(rsp_info):
            print u"TD:%s�ɹ�" % name
            return 1
        else:
            print u"TD:%s���: �ȴ���ݽ�����ȫ..." % name
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
        print u'A:��ѯ��֤����%s, ���������ֵ:%s' % (instrument_id, r)

    def OnRspQryInstrumentMarginRate(self, pInstrumentMarginRate, pRspInfo, nRequestID, bIsLast):
        '''
            ��֤���ʻر������صı�Ȼ�Ǿ��ֵ
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
        print u'A:��ѯ��Լ, ���������ֵ:%s' % r
        
    def OnRspQryInstrument(self, pInst, pRspInfo, nRequestID, bIsLast):
        '''
            ��Լ�ر���
        '''
        if bIsLast and self.isRspSuccess(pRspInfo):
            if (pInst.ExchangeID in self.instruments) and (pInst.ProductClass=='1'):
                self.instruments[pInst.ExchangeID].append(pInst)
                #print pInst
            #print self.instruments
            #print pInstrument
        else:
            if (pInst.ExchangeID in self.instruments) and (pInst.ProductClass=='1'):
                self.instruments[pInst.ExchangeID].append(pInst)
                #print pInst
            #print pInstrument, pRspInfo, bIsLast  #ģ���ѯ�Ľ��,����˶����Լ����ݣ�ֻ�����һ����bLast��True
 
    def OnRtnOrder(self, pOrder):
        print pOrder
        
    def fetch_trading_account(self):
        #��ȡ�ʽ��ʻ�
        
        print u'A:��ȡ�ʽ��ʻ�..'
        req = ApiStruct.QryTradingAccount(BrokerID=self.broker_id, InvestorID=self.investor_id)
        self.requestid += 1
        r=self.ReqQryTradingAccount(req,self.requestid)
        #logging.info(u'A:��ѯ�ʽ��˻�, ���������ֵ:%s' % r)

    def fetch_investor_position(self,instrument_id):
        #��ȡ��Լ�ĵ�ǰ�ֲ�
        print u'A:��ȡ��Լ%s�ĵ�ǰ�ֲ�..' % (instrument_id,)
        req = ApiStruct.QryInvestorPosition(BrokerID=self.broker_id, InvestorID=self.investor_id,InstrumentID=instrument_id)
        self.requestid += 1
        r=self.ReqQryInvestorPosition(req,self.requestid)
        #logging.info(u'A:��ѯ�ֲ�, ���������ֵ:%s' % rP)
    
    def fetch_investor_position_detail(self,instrument_id):
        '''
            ��ȡ��Լ�ĵ�ǰ�ֲ���ϸ��Ŀǰû��
        '''
        
        print u'A:��ȡ��Լ%s�ĵ�ǰ�ֲ�..' % (instrument_id,)
        req = ApiStruct.QryInvestorPositionDetail(BrokerID=self.broker_id, InvestorID=self.investor_id,InstrumentID=instrument_id)
        self.requestid += 1
        r=self.ReqQryInvestorPositionDetail(req,self.requestid)
        #logging.info(u'A:��ѯ�ֲ�, ���������ֵ:%s' % r)
    #def OnRspSubMarketData(self, spec_instrument, info, requestid, islast):
    #    print "OnRspSubMarketData"

    #def OnRspUnSubMarketData(self, spec_instrument, info, requestid, islast):
    #    print "OnRspUnSubMarketData"

    def fetch_order(self, t_start='09:00:00', t_end='15:15:00'):
        req = ApiStruct.QryOrder(
                        BrokerID=self.broker_id, 
                        InvestorID=self.investor_id,
                        InstrumentID='',
                        ExchangeID = '', #���������, char[9]
                        #OrderSysID = '', #�������, char[21]
                        InsertTimeStart = '', #��ʼʱ��, char[9]
                        InsertTimeEnd = '', #����ʱ��, char[9]
                )
        self.requestid += 1
        r = self.ReqQryOrder(req, self.requestid)

    def fetch_trade(self, t_start='09:00:00', t_end='15:15:00'):
        req = ApiStruct.QryTrade(
                        BrokerID=self.broker_id, 
                        InvestorID=self.investor_id,
                        InstrumentID='',
                        ExchangeID ='', #���������, char[9]
                        #TradeID = '', #�������, char[21]
                        TradeTimeStart = '', #��ʼʱ��, char[9]
                        TradeTimeEnd = '', #����ʱ��, char[9]
                )
        self.requestid += 1
        r = self.ReqQryTrade(req, self.requestid)
        
    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        '''
            �����ѯ�ʽ��˻���Ӧ
        '''
        print u'��ѯ�ʽ��˻���Ӧ', pTradingAccount
        if bIsLast and self.isRspSuccess(pRspInfo):
            print pTradingAccount
        else:
            #logging
            pass

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        '''�����ѯͶ���ֲ߳���Ӧ'''
        self.event.set()
        if self.isRspSuccess(pRspInfo): #ÿ��һ����������ݱ�
            print pInvestorPosition, "True"
        else:
            #logging
            print pInvestorPosition, "False"
            pass

    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
        print u'�����ѯͶ���ֲ߳���ϸ��Ӧ'
        self.event.set()
        if self.isRspSuccess(pRspInfo): #ÿ��һ����������ݱ�
            print pInvestorPositionDetail
        else:
            #logging
            pass

    def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ������Ӧ'''
        if bIsLast and self.isRspSuccess(pRspInfo):
            print 'last:%s' % pOrder
        else:
            print 'first: %s' % pOrder

    def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ�ɽ���Ӧ'''
        if bIsLast and self.isRspSuccess(pRspInfo):
            print 'last:%s' % pTrade
        else:
            print 'first: %s' % pTrade

    def fetch_instruments_by_exchange(self,exchange_id):
        '''���ܵ�����exchange_id,���û������
        '''
        req = ApiStruct.QryInstrument(
                        ExchangeID=exchange_id,
                )
        self.requestid += 1
        r = self.ReqQryInstrument(req,self.requestid)
        print u'A:��ѯ��Լ, ���������ֵ:%s' % r
        
    def OnRtnDepthMarketData(self, depth_market_data):
        print "OnRtnDepthMarketData"
        print depth_market_data.BidPrice1,depth_market_data.BidVolume1,depth_market_data.AskPrice1,depth_market_data.AskVolume1,depth_market_data.LastPrice,depth_market_data.Volume,depth_market_data.UpdateTime,depth_market_data.UpdateMillisec,depth_market_data.InstrumentID

#inst=[u'al1008', u'al1009', u'al1010', u'al1011', u'al1012', u'al1101', u'al1102', u'al1103', u'al1104', u'al1105', u'al1106', u'al1107', u'au1008', u'au1009', u'au1010', u'au1011', u'au1012', u'au1101', u'au1102', u'au1103', u'au1104', u'au1105', u'au1106', u'au1107', u'cu1008', u'cu1009', u'cu1010', u'cu1011', u'cu1012', u'cu1101', u'cu1102', u'cu1103', u'cu1104', u'cu1105', u'cu1106', u'cu1107', u'fu1009', u'fu1010', u'fu1011', u'fu1012', u'fu1101', u'fu1103', u'fu1104', u'fu1105', u'fu1106', u'fu1107', u'fu1108', u'rb1008', u'rb1009', u'rb1010', u'rb1011', u'rb1012', u'rb1101', u'rb1102', u'rb1103', u'rb1104', u'rb1105', u'rb1106', u'rb1107', u'ru1008', u'ru1009', u'ru1010', u'ru1011', u'ru1101', u'ru1103', u'ru1104', u'ru1105', u'ru1106', u'ru1107', u'wr1008', u'wr1009', u'wr1010', u'wr1011', u'wr1012', u'wr1101', u'wr1102', u'wr1103', u'wr1104', u'wr1105', u'wr1106', u'wr1107', u'zn1008', u'zn1009', u'zn1010', u'zn1011', u'zn1012', u'zn1101', u'zn1102', u'zn1103', u'zn1104', u'zn1105', u'zn1106']
def main():
    
    #user = MyTraderApi(broker_id="8000",investor_id="24661668",passwd="121862")
    user = MyTraderApi(broker_id="8070",investor_id="750305",passwd="801289")
    user.Create("trader")
    user.SubscribePublicTopic(THOST_TERT_QUICK)
    user.SubscribePrivateTopic(THOST_TERT_QUICK)
    #user.RegisterFront("tcp://qqfz-front1.ctp.shcifco.com:32305")
    #user.RegisterFront("tcp://zjzx-front20.ctp.shcifco.com:41205")
    user.RegisterFront("tcp://zjzx-front12.ctp.shcifco.com:41205")
    user.Init()

    time.sleep(3)
    user.fetch_instruments_by_exchange('')
    time.sleep(20)
    for exch in user.instruments:
        for inst in user.instruments[exch]:
            if inst.ExchangeID in ['CZCE','DCE','SHFE','CFFEX']:
                print inst
                cont = {}
                cont['instID'] = inst.InstrumentID
                cont['margin_l'] = inst.LongMarginRatio
                cont['margin_s'] = inst.ShortMarginRatio
                cont['start_date'] = datetime.datetime.strptime(inst.OpenDate,'%Y%M%d').date()
                cont['expiry'] = datetime.datetime.strptime(inst.ExpireDate,'%Y%M%d').date()
                cont['product_code'] = inst.ProductID
                mysqlaccess.insert_cont_data(cont)

if __name__=="__main__": main()
