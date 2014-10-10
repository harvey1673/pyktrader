#-*- coding:utf-8 -*-
import tradeagent as agent
from ctp.futures import ApiStruct

class TraderMock(object):
    def __init__(self,myagent):
        self.myagent = myagent
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
                    TradeID=oid,
                    OrderSysID=oid,
                    BrokerOrderSeq=oid,
                    OrderLocalID = oid,
                    TradeTime = time.strftime('%H%M%S'),
                )
        if order.CombOffsetFlag == ApiStruct.OF_Open:
            self.available -= order.LimitPrice * 300 * 0.17
        else:
            self.available += order.LimitPrice * 300 * 0.17
        fl_open = strategy.MAX_OPEN_OVERFLOW * 0.2
        fl_close = strategy.MAX_CLOSE_OVERFLOW * 0.2
        if order.CombOffsetFlag == ApiStruct.OF_Open:
            trade.Price += -fl_open if order.Direction == ApiStruct.D_Buy else fl_open
        else:
            trade.Price += -fl_close if order.Direction == ApiStruct.D_Buy else fl_close
        self.myagent.rtn_trade(trade)

    def ReqOrderAction(self, corder, request_id):
        #print u'in cancel'
        oid = corder.OrderRef
        rorder = ApiStruct.Order(
                    InstrumentID = corder.InstrumentID,
                    OrderRef = corder.OrderRef,
                    OrderStatus = ApiStruct.OST_Canceled,
                )
        #self.myagent.rtn_order(rorder)
        self.myagent.err_order_action(rorder.OrderRef,rorder.InstrumentID,u'26',u'测试撤单--报单已成交')

    def ReqQryTradingAccount(self,req,req_id=0):
        logging.info(u'查询帐户余额')
        account = BaseObject(Available=self.available) 
        self.myagent.rsp_qry_trading_account(account)

    def ReqQryInstrument(self,req,req_id=0):#只有唯一一个合约
        logging.info(u'查询合约')
        ins = BaseObject(InstrumentID = req.InstrumentID,VolumeMultiple = 300,PriceTick=0.2)
        self.myagent.rsp_qry_instrument(ins)

    def ReqQryInstrumentMarginRate(self,req,req_id=0):
        logging.info(u'查询保证金')
        mgr = BaseObject(InstrumentID = req.InstrumentID,LongMarginRatioByMoney=0.17,ShortMarginRatioByMoney=0.17)
        self.myagent.rsp_qry_instrument_marginrate(mgr)

    def ReqQryInvestorPosition(self,req,req_id=0):
        #暂默认无持仓
        pass

    def confirm_settlement_info(self):
        self.myagent.isSettlementInfoConfirmed = True


class MarketDataMock(object):
    '''简单起见，只模拟一个合约，用于功能测试
    '''
    def __init__(self,instruments, agent):
        self.instIDs = instruments
		self.data_freq = 'tick'
        self.agent = agent.Agent(None,None,instruments,{})

    def play(self,tday=0):
        ticks = hreader.read_ticks(self.instrument,tday)
        for tick in ticks:
            self.agent.RtnTick(tick)
            #self.agent.RtnTick(tick)

def create_agent_with_mocktrader(instrument,tday,sname='strategy_mock.ini'):
    trader = TraderMock(None)
    print sname
    strategy_cfg = config.parse_strategy(name=sname)

    ##这里没有考虑现场恢复，state中需注明当日
    cuser = BaseObject(broker_id='test',port=1111,investor_id='test',passwd='test')
    myagent = agent.Agent(trader,cuser,[instrument],strategy_cfg,tday=tday) 
    trader.myagent = myagent

    req = BaseObject(InstrumentID=instrument)
    trader.ReqQryInstrumentMarginRate(req)
    trader.ReqQryInstrument(req)
    trader.ReqQryTradingAccount(req)
    return myagent

def run_ticks(ticks,myagent):
    for tick in ticks:
        myagent.inc_tick()
        #print tick.min1

def trade_mock(instrument='IF1108'):
    #logging.basicConfig(filename="ctp_trade_mock.log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')

    tday = 20110726
    myagent = create_agent_with_mocktrader(instrument,-1)    #不需要tday的当日数据
    myagent.scur_day = tday
    myagent.save_flag = True
    ticks = hreader.read_ticks(instrument,tday)    #不加载当日数据
    #for tick in ticks:myagent.inc_tick(),myagent.RtnTick(tick)
    #for tick in ticks:
    #    myagent.inc_tick()
    #    myagent.RtnTick(tick)
    run_ticks(ticks,myagent)

def semi_mock(instrument='IF1110',base_name='mybase.ini',base='Base'):
    ''' 半模拟
        实际行情，mock交易
    '''
    logging.basicConfig(filename="ctp_semi_mock.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')    
    tday = int(time.strftime('%Y%m%d'))
    myagent = create_agent_with_mocktrader(instrument,tday)    #不需要tday的当日数据

    myagent.resume()

    base_cfg = config.parse_base(base_name,base)
    for user in base_cfg.users:
        agent.make_user(myagent,base_cfg.users[user],user)
    
    return myagent

def comp_mock(base_name='mybase.ini',base='Base',strategy_name='strategy_trader.ini'):
    ''' 全模拟
        实际行情，模拟交易
    '''
    logging.basicConfig(filename="ctp_comp_mock.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')    
    #tday = int(time.strftime('%Y%m%d'))
    #myagent = create_agent_with_mocktrader(instrument,tday)    #不需要tday的当日数据
    trader,myagent = agent.create_trader(name='mybase.ini',base='Base_Mock',sname=strategy_name)

    myagent.resume()

    #用实际行情
    base_cfg = config.parse_base(base_name,'Base_Mock')
    for user in base_cfg.users:
        agent.make_user(myagent,base_cfg.users[user],user)
    
    return myagent

def comp_real(base_name='mybase.ini',base='Base',strategy_name='strategy_trader.ini'):
    ''' 实际交易
    '''
    logging.basicConfig(filename="ctp_comp_real.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')    
    #tday = int(time.strftime('%Y%m%d'))
    #myagent = create_agent_with_mocktrader(instrument,tday)    #不需要tday的当日数据
    trader,myagent = agent.create_trader(name='mybase.ini',base='BASE_REAL',sname=strategy_name)

    myagent.resume()

    #用实际行情
    base_cfg = config.parse_base(base_name,'BASE_REAL')
    for user in base_cfg.users:
        agent.make_user(myagent,base_cfg.users[user],user)
    
    return myagent

def comp_real2(base_name='mybase.ini',base='Base',strategy_name='strategy_trader.ini',t2order=t2order_if):
    ''' 实际交易
    '''
    logging.basicConfig(filename="ctp_comp_real.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')    
    #tday = int(time.strftime('%Y%m%d'))
    #myagent = create_agent_with_mocktrader(instrument,tday)    #不需要tday的当日数据
    trader,myagent = agent.create_trader(name=base_name,base=base,sname=strategy_name,t2order=t2order)

    myagent.resume()

    #用实际行情
    base_cfg = config.parse_base(base_name,base)
    for user in base_cfg.users:
        agent.make_user(myagent,base_cfg.users[user],user)
    
    return myagent


if __name__ == '__main__':
    log_config()
    trade_mock()
