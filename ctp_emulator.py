#-*- coding:utf-8 -*-
import tradeagent as agent
import time
import logging 
import mysqlaccess as mdb
import datetime
from base import * 
from misc import *
import strategy as strat
import data_handler
import itertools
from ctp.futures import ApiStruct

class CTPOrderMixin(object):
    def send_order(self, iorder):
        req = ApiStruct.InputOrder(
                InstrumentID = iorder.instrument.name,
                Direction = iorder.direction,
                OrderRef = str(iorder.order_ref),
                LimitPrice = iorder.limit_price,   #有个疑问，double类型如何保证舍入舍出，在服务器端取整?
                VolumeTotalOriginal = iorder.volume,
                OrderPriceType = iorder.price_type,
                BrokerID = self.broker_id,
                InvestorID = self.investor_id,
                CombOffsetFlag = iorder.action_type,         #开仓 5位字符,但是只用到第0位
                CombHedgeFlag = ApiStruct.HF_Speculation,   #投机 5位字符,但是只用到第0位
                VolumeCondition = ApiStruct.VC_AV,
                MinVolume = 1,  #这个作用有点不确定,有的文档设成0了
                ForceCloseReason = ApiStruct.FCC_NotForceClose,
                IsAutoSuspend = 1,
                UserForceClose = 0,
                TimeCondition = ApiStruct.TC_GFD,
                )
        r = self.ReqOrderInsert(req,self.agent.inc_request_id())
        return r

    def cancel_order(self, iorder):
        inst = iorder.instrument
        req = ApiStruct.InputOrderAction(
                InstrumentID = inst.name,
                OrderRef = str(iorder.order_ref),
                BrokerID = self.broker_id,
                InvestorID = self.investor_id,
                FrontID = self.front_id,
                SessionID = self.session_id,
                ActionFlag = ApiStruct.AF_Delete,
                #OrderActionRef = self.inc_order_ref()  #没用,不关心这个，每次撤单成功都需要去查资金
            )
        r = self.ReqOrderAction(req,self.agent.inc_request_id())
        return r

    def query_trade( self, startTime = '', endTime = '' ):
        req = ApiStruct.QryTrade(
                        BrokerID=self.broker_id, 
                        InvestorID=self.investor_id,
                        InstrumentID='',
                        ExchangeID ='', #交易所代码, char[9]
                        TradeTimeStart = startTime, #开始时间, char[9]
                        TradeTimeEnd = endTime, #结束时间, char[9]
                )
        r = self.ReqQryTrade(req, self.agent.inc_request_id())
        return r
    
    def query_order(self, startTime = '', endTime = ''):
        req = ApiStruct.QryOrder(
                        BrokerID = self.broker_id, 
                        InvestorID = self.investor_id,
                        InstrumentID ='',
                        ExchangeID = '', #交易所代码, char[9]
                        InsertTimeStart = startTime, #开始时间, char[9]
                        InsertTimeEnd = endTime, #结束时间, char[9]
                )
        r = self.ReqQryOrder(req, self.agent.inc_request_id())
        return r
    
    def query_investor_position_detail(self, instrument_id):
        req = ApiStruct.QryInvestorPositionDetail(BrokerID=self.broker_id, InvestorID=self.investor_id, InstrumentID=instrument_id)
        r=self.ReqQryInvestorPositionDetail(req, self.agent.inc_request_id())
        return r

    def query_investor_position(self, instrument_id):
        req = ApiStruct.QryInvestorPosition(BrokerID=self.broker_id, InvestorID=self.investor_id,InstrumentID=instrument_id)
        r=self.ReqQryInvestorPosition(req,self.agent.inc_request_id())
        return r

    def query_trading_account(self):            
        req = ApiStruct.QryTradingAccount(BrokerID=self.trader.broker_id, InvestorID=self.trader.investor_id)
        r=self.ReqQryTradingAccount(req,self.agent.inc_request_id())
        #self.logger.info(u'A:查询资金账户, 函数发出返回值:%s' % r)
        return r

    def query_instrument(self, instrument_id):
        req = ApiStruct.QryInstrument(
                        InstrumentID=instrument_id,
                )
        r = self.ReqQryInstrument(req, self.agent.inc_request_id())
        return r
        
    def query_instruments_by_exch(self, exchange_id):
        req = ApiStruct.QryInstrument(
                        ExchangeID=exchange_id,
                )
        r = self.ReqQryInstrument(req, self.agent.inc_request_id())
        return r

    def query_instrument_marginrate(self, instrument_id):
        req = ApiStruct.QryInstrumentMarginRate(BrokerID=self.broker_id,
                        InvestorID=self.investor_id,
                        InstrumentID=instrument_id,
                        HedgeFlag = ApiStruct.HF_Speculation
                )
        r = self.ReqQryInstrumentMarginRate(req,self.agent.inc_request_id())
        return r
    
class TraderMock(CTPOrderMixin):
    def __init__(self,myagent):
        self.broker_id = '0'
        self.investor_id = '0'
        self.front_id = '0'
        self.session_id = '0'
        
        self.agent = myagent
        self.available = 1000000    #初始100W

        # self.myspi = BaseObject(is_logged=True,confirm_settlement_info=self.confirm_settlement_info)
        
    def ReqOrderInsert(self, order, request_id):
        logging.info(u'报单')
        oid = order.OrderRef
        trade = ApiStruct.Trade(
                    InstrumentID = order.InstrumentID,
                    Direction=order.Direction,
                    Price = order.LimitPrice,
                    Volume = order.VolumeTotalOriginal,
                    OrderRef = oid,
                    TradeID = oid,
                    OrderSysID= oid,
                    BrokerOrderSeq= int(oid),
                    OrderLocalID = oid,
                    TradeTime = time.strftime('%H%M%S')
                )
        inst = self.agent.instruments[order.InstrumentID]
        if order.CombOffsetFlag == ApiStruct.OF_Open:
            self.available -= order.LimitPrice * inst.multiple * inst.marginrate[0]
        else:
            self.available += order.LimitPrice * inst.multiple * inst.marginrate[0]

        self.agent.rtn_trade(trade)

    def ReqOrderAction(self, corder, request_id):
        #print u'in cancel'
        oid = corder.OrderRef
        rorder = ApiStruct.Order(
                    InstrumentID = corder.InstrumentID,
                    OrderRef = corder.OrderRef,
                    OrderStatus = ApiStruct.OST_Canceled,
                )
        #self.agent.rtn_order(rorder)
        self.agent.err_order_action(rorder.OrderRef,rorder.InstrumentID,u'26',u'测试撤单--报单已成交')

    def ReqQryTradingAccount(self,req,req_id=0):
        logging.info(u'查询帐户余额')
        account = BaseObject(Available=self.available) 
        self.agent.rsp_qry_trading_account(account)

    def ReqQryInstrument(self,req,req_id=0):#只有唯一一个合约
        logging.info(u'查询合约')
        instID = req.InstrumentID
        inst = self.agent.instruments[instID]
        ins = BaseObject(InstrumentID = instID, VolumeMultiple = inst.multiple, PriceTick=inst.tick_base)
        self.agent.rsp_qry_instrument(ins)

    def ReqQryInstrumentMarginRate(self,req,req_id=0):
        logging.info(u'查询保证金')
        instID = req.InstrumentID
        inst = self.agent.instruments[instID]
        mgr = BaseObject(InstrumentID = instID,LongMarginRatioByMoney=inst.marginrate[0],ShortMarginRatioByMoney=inst.marginrate[0])
        self.agent.rsp_qry_instrument_marginrate(mgr)

    def ReqQryInvestorPosition(self,req,req_id=0):
        #暂默认无持仓
        pass

    def confirm_settlement_info(self):
        self.agent.isSettlementInfoConfirmed = True

    def check_order_status(self):
        pass

class MarketDataMock(object):
    '''简单起见，只模拟一个合约，用于功能测试
    '''
    def __init__(self,agent):
        self.instIDs = agent.instruments.keys()
        self.data_freq = 'tick'
        self.agent = agent

    def play_tick(self, tday=0):
        tick_data = mdb.load_tick_data('fut_tick', self.instIDs, tday, tday)
        for tick in tick_data:
            ctick = agent.TickData(instID=str(tick['instID']), 
                           high=float(tick['high']), 
                           low =float(tick['low']), 
                           price=float(tick['price']), 
                           volume=int(tick['volume']), 
                           openInterest=int(tick['openInterest']), 
                           bidPrice1=float(tick['bidPrice1']), 
                           bidVol1=int(tick['bidVol1']), 
                           askPrice1=float(tick['askPrice1']), 
                           askVol1=int(tick['askVol1']), 
                           timestamp=tick['timestamp'])
            self.agent.RtnTick(ctick)

def create_agent_with_mocktrader(agent_name, instruments, strat_cfg, tday):
    strategies = strat_cfg['strategies']
    folder = strat_cfg['folder']
    daily_days = strat_cfg['daily_data_days']
    min_days = strat_cfg['min_data_days']
    myagent = agent.Agent(agent_name, None, None, instruments, strategies, tday, folder, daily_days, min_days) 
    myagent.trader = trader = TraderMock(myagent)
    return myagent, trader

def trade_mock( curr_date, insts = [['IF1412', 'IF1503']]):
    logging.basicConfig(filename="ctp_trade_mock.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')    
    instruments = list(set(itertools.chain(*insts)))
    data_func = [ 
            ('d', BaseObject(name = 'ATR_20', sfunc=fcustom(data_handler.ATR, n=20), rfunc=fcustom(data_handler.atr, n=20))), \
            ('d', BaseObject(name = 'DONCH_L10', sfunc=fcustom(data_handler.DONCH_L, n=10), rfunc=fcustom(data_handler.donch_l, n=10))),\
            ('d', BaseObject(name = 'DONCH_H10', sfunc=fcustom(data_handler.DONCH_H, n=10), rfunc=fcustom(data_handler.donch_h, n=10))),\
            ('d', BaseObject(name = 'DONCH_L20', sfunc=fcustom(data_handler.DONCH_L, n=20), rfunc=fcustom(data_handler.donch_l, n=20))),\
            ('d', BaseObject(name = 'DONCH_H20', sfunc=fcustom(data_handler.DONCH_H, n=20), rfunc=fcustom(data_handler.donch_h, n=20))),\
            ('1m',BaseObject(name = 'EMA_3',     sfunc=fcustom(data_handler.EMA, n=3),      rfunc=fcustom(data_handler.ema, n=3))), \
            ('1m',BaseObject(name = 'EMA_30',    sfunc=fcustom(data_handler.EMA, n=30),     rfunc=fcustom(data_handler.ema, n=30))) \
        ]
    test_strat = strat.Strategy('TestStrat', [insts], None, data_func, [[1,-1]])
    strat_cfg = {'strategies': [test_strat], \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':25, \
                 'min_data_days':2 }

    agent_name = "Test" 
    tday = curr_date
    my_agent, my_trader = create_agent_with_mocktrader(agent_name, instruments, strat_cfg, tday)
    my_user  = MarketDataMock(my_agent)
    req = BaseObject(InstrumentID='IF1412')  
    my_agent.resume()
    my_user.play_tick(tday)

def semi_mock(curr_date, user_cfg, insts = [['IF1412', 'IF1503']]):
    ''' 半模拟
        实际行情，mock交易
    '''
    logging.basicConfig(filename="ctp_semi_mock.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')    
    instruments = list(set(itertools.chain(*insts)))
    data_func = [ 
            ('d', BaseObject(name = 'ATR_20', sfunc=fcustom(data_handler.ATR, n=20), rfunc=fcustom(data_handler.atr, n=20))), \
            ('d', BaseObject(name = 'DONCH_L10', sfunc=fcustom(data_handler.DONCH_L, n=10), rfunc=fcustom(data_handler.donch_l, n=10))),\
            ('d', BaseObject(name = 'DONCH_H10', sfunc=fcustom(data_handler.DONCH_H, n=10), rfunc=fcustom(data_handler.donch_h, n=10))),\
            ('d', BaseObject(name = 'DONCH_L20', sfunc=fcustom(data_handler.DONCH_L, n=20), rfunc=fcustom(data_handler.donch_l, n=20))),\
            ('d', BaseObject(name = 'DONCH_H20', sfunc=fcustom(data_handler.DONCH_H, n=20), rfunc=fcustom(data_handler.donch_h, n=20))),\
            ('1m',BaseObject(name = 'EMA_3',     sfunc=fcustom(data_handler.EMA, n=3),      rfunc=fcustom(data_handler.ema, n=3))), \
            ('1m',BaseObject(name = 'EMA_30',    sfunc=fcustom(data_handler.EMA, n=30),     rfunc=fcustom(data_handler.ema, n=30))) \
        ]
    test_strat = strat.Strategy('TestStrat', [insts], None, data_func, [[1,-1]])
    strat_cfg = {'strategies': [test_strat], \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':25, \
                 'min_data_days':2 }

    agent_name = "Test" 
    tday = curr_date
    my_agent, my_trader = create_agent_with_mocktrader(agent_name, instruments, strat_cfg, tday)
    agent.make_user(my_agent,user_cfg)
    
    req = BaseObject(InstrumentID='IF1412')
    my_trader.ReqQryInstrumentMarginRate(req)
    my_trader.ReqQryInstrument(req)
    my_trader.ReqQryTradingAccount(req)    
    
    my_agent.resume()
    
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        my_agent.mdapis = []; 
        my_agent.trader = None
    pass
    
if __name__ == '__main__':
    tday = datetime.date(2014,11,21)
    insts = [['IF1412'], ['IF1503']]
    semi_mock(tday, PROD_USER)
    trade_mock(tday)
