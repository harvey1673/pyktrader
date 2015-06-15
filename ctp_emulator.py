# coding=utf-8
import agent
import optagent
import fut_api
import time
import logging 
import mysqlaccess as mdb
import datetime
from base import * 
from misc import *
import strategy as strat
import data_handler
import itertools
import ctp.futures

class TraderMock(agent.CTPTraderQryMixin):
    ApiStruct = ctp.futures.ApiStruct
    logger = logging.getLogger('ctp.MockTrader') 
    def __init__(self,myagent):
        self.name = 'Mock-TD'
        self.broker_id = '0'
        self.investor_id = '0'
        self.front_id = '0'
        self.session_id = '0'
        self.agent = myagent
        self.available = 1000000    #初始100W
        self.is_logged = True
        # self.myspi = BaseObject(is_logged=True,confirm_settlement_info=self.confirm_settlement_info)
        
    def ReqOrderInsert(self, order, request_id):
        logging.info(u'报单')
        oid = order.OrderRef
        trade = self.ApiStruct.Trade(
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
        if order.CombOffsetFlag == self.ApiStruct.OF_Open:
            self.available -= order.LimitPrice * inst.multiple * inst.marginrate[0]
        else:
            self.available += order.LimitPrice * inst.multiple * inst.marginrate[0]
            
        ptrade = BaseObject( instID = trade.InstrumentID,
                            order_ref = int(trade.OrderRef),
                            order_sysid = trade.OrderSysID,
                            price = trade.Price,
                            volume= trade.Volume,
                            trade_id = trade.TradeID )
        self.agent.rtn_trade(ptrade)

    def ReqOrderAction(self, corder, request_id):
        #print u'in cancel'
        oid = corder.OrderRef
        rorder = self.ApiStruct.Order(
                    InstrumentID = corder.InstrumentID,
                    OrderRef = corder.OrderRef,
                    OrderStatus = self.ApiStruct.OST_Canceled,
                )
        #self.agent.rtn_order(rorder)
        self.agent.err_order_action(rorder.OrderRef,rorder.InstrumentID,u'26',u'测试撤单--报单已成交')

    def ReqQryTradingAccount(self,req,req_id=0):
        logging.info(u'查询帐户余额')
        #account = BaseObject(Available=self.available) 
        self.agent.rsp_qry_trading_account(self.available)

    def ReqQryInstrument(self,req,req_id=0):#只有唯一一个合约
        logging.info(u'查询合约')
        instID = req.InstrumentID
        inst = self.agent.instruments[instID]
        ins = BaseObject(instID = instID, multiple = inst.multiple, tick_base=inst.tick_base, marginrate =  (inst.marginrate[0],inst.marginrate[0]) )
        self.agent.rsp_qry_instrument(ins)

    def ReqQryInstrumentMarginRate(self,req,req_id=0):
        logging.info(u'查询保证金')
        instID = req.InstrumentID
        inst = self.agent.instruments[instID]
        mgr = (inst.marginrate[0],inst.marginrate[0])
        self.agent.rsp_qry_instrument_marginrate(instID, mgr)

    def ReqQryInvestorPosition(self,req,req_id=0):
        #暂默认无持仓
        pass

    def confirm_settlement_info(self):
        self.agent.isSettlementInfoConfirmed = True

    def check_order_status(self):
        return False

class MarketDataMock(object):
    '''简单起见，只模拟一个合约，用于功能测试
    '''
    ApiStruct = ctp.futures.ApiStruct
    def __init__(self,myagent):
        self.name = 'Mock-MD'
        self.instIDs = myagent.instruments.keys()
        self.data_freq = 'tick'
        self.agent = myagent

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
    config = {}
    config['folder'] = strat_cfg['folder']
    config['daily_data_days'] = strat_cfg['daily_data_days']
    config['min_data_days']   = strat_cfg['min_data_days']
    if 'enable_option' in strat_cfg:
        config['enable_option'] = strat_cfg['enable_option']
    else:
        config['enable_option'] = False
    agent_class = agent.Agent
    if config['enable_option'] == True:
        agent_class = optagent.OptionAgent    
    myagent = agent_class(agent_name, None, None, instruments, strategies, tday, config) 
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
    req = BaseObject(InstrumentID='cu1502')  
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
    fut_api.make_user(my_agent,user_cfg)
    
    req = BaseObject(InstrumentID='cu1502')
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
    insts = [['cu1502'], ['cu1503']]
    semi_mock(tday, PROD_USER, insts)
    #trade_mock(tday)
