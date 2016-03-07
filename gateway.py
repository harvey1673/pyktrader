# encoding: UTF-8

import time
import os
import instrument
import csv
import workdays
import json
import order
from misc import *
from eventEngine import *
from vtConstant import *

########################################################################
class Gateway(object):
    """交易接口"""

    #----------------------------------------------------------------------
    def __init__(self, agent, gatewayName = 'Gateway'):
        """Constructor"""
        self.gatewayName = gatewayName
        self.agent = agent
        self.eventEngine = agent.eventEngine
        self.file_prefix = agent.folder + gatewayName + '_'
        self.qry_account = {}
        self.qry_pos = {}
        self.id2order = {}
        self.positions = {}
        self.instruments = []      # 已订阅合约代码
        self.eod_flag = False
        self.account_info = {'available': 0,
                            'locked_margin': 0,
                            'used_margin': 0,
                            'curr_capital': 1000000,
                            'prev_capital': 1000000,
                            'pnl_total': 0,
                            'yday_pnl': 0,
                            'tday_pnl': 0,
                            }							
        self.order_stats = {'total_submit': 0, 'total_failure': 0, 'total_cancel':0 }
        self.order_constraints = {	'total_submit': 2000, 'total_cancel': 2000, 'total_failure':500, \
                                    'submit_limit': 200,  'cancel_limit': 200,  'failure_limit': 200 }
    #----------------------------------------------------------------------
    def initialize(self):
        pass

    def day_finalize(self, tday):
        self.save_local_positions(tday)
        eod_pos = {}
        for inst in self.positions:
            pos = self.positions[inst]
            eod_pos[inst] = [pos.curr_pos.long, pos.curr_pos.short]
        self.id2order  = {}
        self.positions = {}
        self.order_stats = {'total_submit': 0, 'total_failure': 0, 'total_cancel':0 }
        for inst in self.instruments:
            self.order_stats[inst] = {'submit': 0, 'cancel':0, 'failure': 0, 'status': True }
            self.positions[inst] = order.Position(self.agent.instruments[inst], self)
            self.positions[inst].pos_yday.long = eod_pos[inst][0]
            self.positions[inst].pos_yday.short = eod_pos[inst][1]
            self.positions[inst].re_calc()
        self.account_info['prev_capital'] = self.account_info['curr_capital']

    def add_instrument(self, instID):
        self.instruments.append(instID)
        if instID not in self.positions:
            self.positions[instID] = order.Position(self.agent.instruments[instID], self)
        if instID not in self.order_stats:
            self.order_stats[instID] = {'submit': 0, 'cancel':0, 'failure': 0, 'status': True }
        if instID not in self.qry_pos:
            self.qry_pos[instID]   = {'tday': [0, 0], 'yday': [0, 0]}

    def event_subscribe(self):
        pass

    def onTick(self, tick):
        """市场行情推送"""
        # 通用事件
        event1 = Event(type=EVENT_TICK)
        event1.dict['data'] = tick
        self.eventEngine.put(event1)
        
        # 特定合约代码的事件
        event2 = Event(type=EVENT_TICK + tick.instID)
        event2.dict['data'] = tick
        self.eventEngine.put(event2)
    
    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """成交信息推送"""
        # 通用事件
        event1 = Event(type=EVENT_TRADE)
        event1.dict['data'] = trade
        self.eventEngine.put(event1)
        
        # 特定合约的成交事件
        event2 = Event(type=EVENT_TRADE + trade.order_ref)
        event2.dict['data'] = trade
        self.eventEngine.put(event2)        
    
    #----------------------------------------------------------------------
    def onOrder(self, order):
        """订单变化推送"""
        # 通用事件
        event1 = Event(type=EVENT_ORDER)
        event1.dict['data'] = order
        self.eventEngine.put(event1)
        
        # 特定订单编号的事件
        event2 = Event(type=EVENT_ORDER + order.order_ref)
        event2.dict['data'] = order
        self.eventEngine.put(event2)
    
    #----------------------------------------------------------------------
    def onPosition(self, position):
        """持仓信息推送"""
        # 通用事件
        event1 = Event(type=EVENT_POSITION)
        event1.dict['data'] = position
        self.eventEngine.put(event1)
        
        # 特定合约代码的事件
        event2 = Event(type=EVENT_POSITION+position.instID)
        event2.dict['data'] = position
        self.eventEngine.put(event2)
    
    #----------------------------------------------------------------------
    def onAccount(self, account):
        """账户信息推送"""
        # 通用事件
        event1 = Event(type=EVENT_ACCOUNT)
        event1.dict['data'] = account
        self.eventEngine.put(event1)
        
        # 特定合约代码的事件
        event2 = Event(type=EVENT_ACCOUNT+account.vtAccountID)
        event2.dict['data'] = account
        self.eventEngine.put(event2)
    
    #----------------------------------------------------------------------
    def onError(self, error):
        """错误信息推送"""
        # 通用事件
        logContent = error.errorMsg
        self.onLog(logContent, level = logging.WARNING)
        
    #----------------------------------------------------------------------
    def onLog(self, log_content, level = logging.DEBUG):
        """日志推送"""
        # 通用事件
        event = Event(type=EVENT_LOG)
        event.dict['data'] = log_content
        event.dict['gateway'] = self.gatewayName
        event.dict['level'] = level
        self.eventEngine.put(event)
        
    #----------------------------------------------------------------------
    def onContract(self, contract):
        """合约基础信息推送"""
        # 通用事件
        event1 = Event(type=EVENT_CONTRACT)
        event1.dict['data'] = contract
        self.eventEngine.put(event1)        
    
    def save_order_list(self, tday):
        order.save_order_list(tday, self.id2order, self.file_prefix)

    def load_order_list(self, tday):
        self.id2order = order.load_order_list(tday, self.file_prefix, self.positions)

    def load_local_positions(self, tday):
        pos_date = tday
        logfile = self.file_prefix + 'EODPos_' + pos_date.strftime('%y%m%d')+'.csv'
        if not os.path.isfile(logfile):
            pos_date = workdays.workday(pos_date, -1, CHN_Holidays)
            logfile = self.file_prefix + 'EODPos_' + pos_date.strftime('%y%m%d')+'.csv'
            if not os.path.isfile(logfile):
                logContent = "no prior position file is found"
                self.onLog(logContent, level = logging.INFO)
                return False
        else:
            self.eod_flag = True
        with open(logfile, 'rb') as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if row[0] == 'capital':
                    self.account_info['prev_capital'] = float(row[1])
                elif row[0] == 'pos':
                    inst = row[1]
                    if inst in self.instruments:
                        if inst not in self.positions:
                            self.positions[inst] = order.Position(self.agent.instruments[inst], self)
                        self.positions[inst].pos_yday.long = int(row[2])
                        self.positions[inst].pos_yday.short = int(row[3])
        return True

    def save_local_positions(self, tday):
        file_prefix = self.file_prefix
        logfile = file_prefix + 'EODPos_' + tday.strftime('%y%m%d')+'.csv'
        if os.path.isfile(logfile):
            return False
        else:
            with open(logfile,'wb') as log_file:
                file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL);
                for inst in self.positions:
                    pos = self.positions[inst]
                    pos.re_calc()
                self.calc_margin()
                file_writer.writerow(['capital', self.account_info['curr_capital']])
                for inst in self.positions:
                    pos = self.positions[inst]
                    if abs(pos.curr_pos.long) + abs(pos.curr_pos.short) > 0:
                        file_writer.writerow(['pos', inst, pos.curr_pos.long, pos.curr_pos.short])
            return True

    def calc_margin(self):
        locked_margin = 0
        used_margin = 0
        yday_pnl = 0
        tday_pnl = 0
        for instID in self.positions:
            inst = self.agent.instruments[instID]
            pos = self.positions[instID]
            under_price = 0.0
            if (inst.ptype == instrument.ProductType.Option):
                under_price = self.agent.instruments[inst.underlying].price
            locked_margin += pos.locked_pos.long * inst.calc_margin_amount(ORDER_BUY, under_price)
            locked_margin += pos.locked_pos.short * inst.calc_margin_amount(ORDER_SELL, under_price) 
            used_margin += pos.curr_pos.long * inst.calc_margin_amount(ORDER_BUY, under_price)
            used_margin += pos.curr_pos.short * inst.calc_margin_amount(ORDER_SELL, under_price)
            yday_pnl += (pos.pos_yday.long - pos.pos_yday.short) * (inst.price - inst.prev_close) * inst.multiple
            tday_pnl += pos.tday_pos.long * (inst.price-pos.tday_avp.long) * inst.multiple
            tday_pnl -= pos.tday_pos.short * (inst.price-pos.tday_avp.short) * inst.multiple            
        self.account_info['locked_margin'] = locked_margin
        self.account_info['used_margin'] = used_margin
        self.account_info['pnl_total'] = yday_pnl + tday_pnl
        self.account_info['curr_capital'] = self.account_info['prev_capital'] + self.account_info['pnl_total']
        self.account_info['available'] = self.account_info['curr_capital'] - self.account_info['locked_margin']

    #----------------------------------------------------------------------
    def connect(self):
        """连接"""
        pass
    
    #----------------------------------------------------------------------
    def subscribe(self, subscribeReq):
        """订阅行情"""
        pass
    
    #----------------------------------------------------------------------
    def sendOrder(self, orderReq):
        """发单"""
        pass
    
    #----------------------------------------------------------------------
    def cancelOrder(self, cancelOrderReq):
        """撤单"""
        pass
    
    #----------------------------------------------------------------------
    def qryAccount(self):
        """查询账户资金"""
        pass
    
    #----------------------------------------------------------------------
    def qryPosition(self):
        """查询持仓"""
        pass
    
    #----------------------------------------------------------------------
    def close(self):
        """关闭"""
        pass

    def register_event_handler(self):
        pass

########################################################################
class VtBaseData(object):
    """回调函数推送数据的基础类，其他数据类继承于此"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.gatewayName = EMPTY_STRING         # Gateway名称        
        self.rawData = None                     # 原始数据
        
        
########################################################################
class VtTickData(VtBaseData):
    """Tick行情数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtTickData, self).__init__()
        
        # 代码相关
        self.symbol = EMPTY_STRING              # 合约代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.instID = EMPTY_STRING            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        
        # 成交数据
        self.lastPrice = EMPTY_FLOAT            # 最新成交价
        self.lastVolume = EMPTY_INT             # 最新成交量
        self.volume = EMPTY_INT                 # 今天总成交量
        self.openInterest = EMPTY_INT           # 持仓量
        self.time = EMPTY_STRING                # 时间 11:20:56.5
        self.date = EMPTY_STRING                # 日期 20151009
        
        # 常规行情
        self.openPrice = EMPTY_FLOAT            # 今日开盘价
        self.highPrice = EMPTY_FLOAT            # 今日最高价
        self.lowPrice = EMPTY_FLOAT             # 今日最低价
        self.preClosePrice = EMPTY_FLOAT
        
        self.upperLimit = EMPTY_FLOAT           # 涨停价
        self.lowerLimit = EMPTY_FLOAT           # 跌停价
        
        # 五档行情
        self.bidPrice1 = EMPTY_FLOAT
        self.bidPrice2 = EMPTY_FLOAT
        self.bidPrice3 = EMPTY_FLOAT
        self.bidPrice4 = EMPTY_FLOAT
        self.bidPrice5 = EMPTY_FLOAT
        
        self.askPrice1 = EMPTY_FLOAT
        self.askPrice2 = EMPTY_FLOAT
        self.askPrice3 = EMPTY_FLOAT
        self.askPrice4 = EMPTY_FLOAT
        self.askPrice5 = EMPTY_FLOAT        
        
        self.bidVolume1 = EMPTY_INT
        self.bidVolume2 = EMPTY_INT
        self.bidVolume3 = EMPTY_INT
        self.bidVolume4 = EMPTY_INT
        self.bidVolume5 = EMPTY_INT
        
        self.askVolume1 = EMPTY_INT
        self.askVolume2 = EMPTY_INT
        self.askVolume3 = EMPTY_INT
        self.askVolume4 = EMPTY_INT
        self.askVolume5 = EMPTY_INT         
    
    
########################################################################
class VtTradeData(VtBaseData):
    """成交数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtTradeData, self).__init__()
        
        # 代码编号相关
        self.symbol = EMPTY_STRING              # 合约代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.instID = EMPTY_STRING            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        
        self.tradeID = EMPTY_STRING             # 成交编号
        self.vtTradeID = EMPTY_STRING           # 成交在vt系统中的唯一编号，通常是 Gateway名.成交编号
        
        self.orderID = EMPTY_STRING             # 订单编号
        self.order_ref = EMPTY_STRING           # 订单在vt系统中的唯一编号，通常是 Gateway名.订单编号
        
        # 成交相关
        self.direction = EMPTY_UNICODE          # 成交方向
        self.offset = EMPTY_UNICODE             # 成交开平仓
        self.price = EMPTY_FLOAT                # 成交价格
        self.volume = EMPTY_INT                 # 成交数量
        self.tradeTime = EMPTY_STRING           # 成交时间
   

########################################################################
class VtOrderData(VtBaseData):
    """订单数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtOrderData, self).__init__()
        
        # 代码编号相关
        self.symbol = EMPTY_STRING              # 合约代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.instID = EMPTY_STRING            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        
        self.orderID = EMPTY_STRING             # 订单编号 local order ID
        self.order_ref = EMPTY_STRING           # for Order class object ID
        self.orderSysID = EMPTY_STRING			# remote order ID

        # 报单相关
        self.direction = EMPTY_UNICODE          # 报单方向
        self.offset = EMPTY_UNICODE             # 报单开平仓
        self.price = EMPTY_FLOAT                # 报单价格
        self.totalVolume = EMPTY_INT            # 报单总数量
        self.tradedVolume = EMPTY_INT           # 报单成交数量
        self.status = EMPTY_UNICODE             # 报单状态
        
        self.orderTime = EMPTY_STRING           # 发单时间
        self.cancelTime = EMPTY_STRING          # 撤单时间
        
        # CTP/LTS相关
        self.frontID = EMPTY_INT                # 前置机编号
        self.sessionID = EMPTY_INT              # 连接编号

    
########################################################################
class VtPositionData(VtBaseData):
    """持仓数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtPositionData, self).__init__()
        
        # 代码编号相关
        self.symbol = EMPTY_STRING              # 合约代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.instID = EMPTY_STRING            # 合约在vt系统中的唯一代码，合约代码.交易所代码  
        
        # 持仓相关
        self.direction = EMPTY_STRING           # 持仓方向
        self.position = EMPTY_INT               # 持仓量
        self.frozen = EMPTY_INT                 # 冻结数量
        self.price = EMPTY_FLOAT                # 持仓均价
        self.vtPositionName = EMPTY_STRING      # 持仓在vt系统中的唯一代码，通常是instID.方向
        
        # 20151020添加
        self.ydPosition = EMPTY_INT             # 昨持仓


########################################################################
class VtAccountData(VtBaseData):
    """账户数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtAccountData, self).__init__()
        
        # 账号代码相关
        self.accountID = EMPTY_STRING           # 账户代码
        self.vtAccountID = EMPTY_STRING         # 账户在vt中的唯一代码，通常是 Gateway名.账户代码
        
        # 数值相关
        self.preBalance = EMPTY_FLOAT           # 昨日账户结算净值
        self.balance = EMPTY_FLOAT              # 账户净值
        self.available = EMPTY_FLOAT            # 可用资金
        self.commission = EMPTY_FLOAT           # 今日手续费
        self.margin = EMPTY_FLOAT               # 保证金占用
        self.closeProfit = EMPTY_FLOAT          # 平仓盈亏
        self.positionProfit = EMPTY_FLOAT       # 持仓盈亏
        

########################################################################
class VtErrorData(VtBaseData):
    """错误数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtErrorData, self).__init__()
        
        self.errorID = EMPTY_STRING             # 错误代码
        self.errorMsg = EMPTY_UNICODE           # 错误信息
        self.additionalInfo = EMPTY_UNICODE     # 补充信息


########################################################################
class VtLogData(VtBaseData):
    """日志数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtLogData, self).__init__()
        
        self.logTime = time.strftime('%X', time.localtime())    # 日志生成时间
        self.logContent = EMPTY_UNICODE                         # 日志信息
        self.level = logging.DEBUG


########################################################################
class VtContractData(VtBaseData):
    """合约详细信息类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(VtBaseData, self).__init__()
        
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所代码
        self.instID = EMPTY_STRING            # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        self.name = EMPTY_UNICODE               # 合约中文名
        
        self.productClass = EMPTY_UNICODE       # 合约类型
        self.size = EMPTY_INT                   # 合约大小
        self.priceTick = EMPTY_FLOAT            # 合约最小价格TICK
        
        # 期权相关
        self.strikePrice = EMPTY_FLOAT          # 期权行权价
        self.underlyingSymbol = EMPTY_STRING    # 标的物合约代码
        self.optionType = EMPTY_UNICODE         # 期权类型


########################################################################
class VtSubscribeReq(object):
    """订阅行情时传入的对象类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所
        
        # 以下为IB相关
        self.productClass = EMPTY_UNICODE       # 合约类型
        self.currency = EMPTY_STRING            # 合约货币
        self.expiry = EMPTY_STRING              # 到期日
        self.strikePrice = EMPTY_FLOAT          # 行权价
        self.optionType = EMPTY_UNICODE         # 期权类型


########################################################################
class VtOrderReq(object):
    """发单时传入的对象类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所
        self.price = EMPTY_FLOAT                # 价格
        self.volume = EMPTY_INT                 # 数量
    
        self.priceType = EMPTY_STRING           # 价格类型
        self.direction = EMPTY_STRING           # 买卖
        self.offset = EMPTY_STRING              # 开平
        
        # 以下为IB相关
        self.productClass = EMPTY_UNICODE       # 合约类型
        self.currency = EMPTY_STRING            # 合约货币
        self.expiry = EMPTY_STRING              # 到期日
        self.strikePrice = EMPTY_FLOAT          # 行权价
        self.optionType = EMPTY_UNICODE         # 期权类型        
        

########################################################################
class VtCancelOrderReq(object):
    """撤单时传入的对象类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING              # 代码
        self.exchange = EMPTY_STRING            # 交易所
        
        # 以下字段主要和CTP、LTS类接口相关
        self.orderID = EMPTY_STRING             # 报单号
        self.frontID = EMPTY_STRING             # 前置机号
        self.sessionID = EMPTY_STRING           # 会话号
