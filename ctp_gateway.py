# encoding: UTF-8

'''
vn.ctp的gateway接入
考虑到现阶段大部分CTP中的ExchangeID字段返回的都是空值
vtSymbol直接使用symbol
'''


import os
import json

from vnctpmd import MdApi
from vnctptd import TdApi
from ctpDataType import *
from vtGateway import *

# 以下为一些VT类型和CTP类型的映射字典
# 价格类型映射
priceTypeMap = {}
priceTypeMap[PRICETYPE_LIMITPRICE] = defineDict["THOST_FTDC_OPT_LimitPrice"]
priceTypeMap[PRICETYPE_MARKETPRICE] = defineDict["THOST_FTDC_OPT_AnyPrice"]
priceTypeMapReverse = {v: k for k, v in priceTypeMap.items()} 

# 方向类型映射
directionMap = {}
directionMap[DIRECTION_LONG] = defineDict['THOST_FTDC_D_Buy']
directionMap[DIRECTION_SHORT] = defineDict['THOST_FTDC_D_Sell']
directionMapReverse = {v: k for k, v in directionMap.items()}

# 开平类型映射
offsetMap = {}
offsetMap[OFFSET_OPEN] = defineDict['THOST_FTDC_OF_Open']
offsetMap[OFFSET_CLOSE] = defineDict['THOST_FTDC_OF_Close']
offsetMap[OFFSET_CLOSETODAY] = defineDict['THOST_FTDC_OF_CloseToday']
offsetMap[OFFSET_CLOSEYESTERDAY] = defineDict['THOST_FTDC_OF_CloseYesterday']
offsetMapReverse = {v:k for k,v in offsetMap.items()}

# 交易所类型映射
exchangeMap = {}
#exchangeMap[EXCHANGE_CFFEX] = defineDict['THOST_FTDC_EIDT_CFFEX']
#exchangeMap[EXCHANGE_SHFE] = defineDict['THOST_FTDC_EIDT_SHFE']
#exchangeMap[EXCHANGE_CZCE] = defineDict['THOST_FTDC_EIDT_CZCE']
#exchangeMap[EXCHANGE_DCE] = defineDict['THOST_FTDC_EIDT_DCE']
exchangeMap[EXCHANGE_CFFEX] = 'CFFEX'
exchangeMap[EXCHANGE_SHFE] = 'SHFE'
exchangeMap[EXCHANGE_CZCE] = 'CZCE'
exchangeMap[EXCHANGE_DCE] = 'DCE'
exchangeMap[EXCHANGE_UNKNOWN] = ''
exchangeMapReverse = {v:k for k,v in exchangeMap.items()}

# 持仓类型映射
posiDirectionMap = {}
posiDirectionMap[DIRECTION_NET] = defineDict["THOST_FTDC_PD_Net"]
posiDirectionMap[DIRECTION_LONG] = defineDict["THOST_FTDC_PD_Long"]
posiDirectionMap[DIRECTION_SHORT] = defineDict["THOST_FTDC_PD_Short"]
posiDirectionMapReverse = {v:k for k,v in posiDirectionMap.items()}

def get_tick_id(dt):
    return ((dt.hour+6)%24)*100000+dt.minute*1000+dt.second*10+dt.microsecond/100000

########################################################################
class CtpGateway(VtGateway):
    """CTP接口"""

    #----------------------------------------------------------------------
    def __init__(self, agent, gatewayName='CTP'):
        """Constructor"""
        super(CtpGateway, self).__init__(agent, gatewayName)
        
        self.mdApi = CtpMdApi(self)     # 行情API
        self.tdApi = CtpTdApi(self)     # 交易API
        
        self.mdConnected = False        # 行情API连接状态，登录完成后为True
        self.tdConnected = False        # 交易API连接状态
        self.qryEnabled = False         # 是否要启动循环查询
        
    #----------------------------------------------------------------------
    def connect(self):
        """连接"""
        # 载入json文件
        fileName = self.agent.folder + self.gatewayName + '_connect.json'
        try:
            f = file(fileName)
        except IOError:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'读取连接配置出错，请检查'
			log.level = logging.WARNING
            self.onLog(log)
            return
        
        # 解析json文件
        setting = json.load(f)
        try:
            userID = str(setting['userID'])
            password = str(setting['password'])
            brokerID = str(setting['brokerID'])
            tdAddress = str(setting['tdAddress'])
            mdAddress = str(setting['mdAddress'])
        except KeyError:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'连接配置缺少字段，请检查'
			log.level = logging.WARNING
            self.onLog(log)
            return            
        
        # 创建行情和交易接口对象
        self.mdApi.connect(userID, password, brokerID, mdAddress)
        self.tdApi.connect(userID, password, brokerID, tdAddress)
        
        # 初始化并启动查询
        self.initQuery()
    
    #----------------------------------------------------------------------
    def subscribe(self, subscribeReq):
        """订阅行情"""
        self.mdApi.subscribe(subscribeReq)
        
    #----------------------------------------------------------------------
    def sendOrder(self, iorder):
        """发单"""
        return self.tdApi.sendOrder(orderReq)
        
    #----------------------------------------------------------------------
    def cancelOrder(self, iorder):
        """撤单"""
        self.tdApi.cancelOrder(cancelOrderReq)
        
    #----------------------------------------------------------------------
    def qryAccount(self):
        """查询账户资金"""
        self.tdApi.qryAccount()
        
    #----------------------------------------------------------------------
    def qryPosition(self):
        """查询持仓"""
        self.tdApi.qryPosition()
        
    #----------------------------------------------------------------------
    def close(self):
        """关闭"""
        if self.mdConnected:
            self.mdApi.close()
        if self.tdConnected:
            self.tdApi.close()
        
    #----------------------------------------------------------------------
    def initQuery(self):
        """初始化连续查询"""
        if self.qryEnabled:
            # 需要循环的查询函数列表
            self.qryFunctionList = [self.qryAccount, self.qryPosition]
            
            self.qryCount = 0           # 查询触发倒计时
            self.qryTrigger = 2         # 查询触发点
            self.qryNextFunction = 0    # 上次运行的查询函数索引
            
            self.startQuery()
    
    #----------------------------------------------------------------------
    def query(self, event):
        """注册到事件处理引擎上的查询函数"""
        self.qryCount += 1
        
        if self.qryCount > self.qryTrigger:
            # 清空倒计时
            self.qryCount = 0
            
            # 执行查询函数
            function = self.qryFunctionList[self.qryNextFunction]
            function()
            
            # 计算下次查询函数的索引，如果超过了列表长度，则重新设为0
            self.qryNextFunction += 1
            if self.qryNextFunction == len(self.qryFunctionList):
                self.qryNextFunction = 0
    
    #----------------------------------------------------------------------
    def startQuery(self):
        """启动连续查询"""
        self.eventEngine.register(EVENT_TIMER, self.query)
    
    #----------------------------------------------------------------------
    def setQryEnabled(self, qryEnabled):
        """设置是否要启动循环查询"""
        self.qryEnabled = qryEnabled
    
	def setup_gateway_handler(self):
		self.eventEngine.register(EVENT_MARKETDATA+self.gatewayName, self.rsp_market_data)
		self.eventEngine.register(EVENT_QRYACCOUNT+self.gatewayName, self.rsp_qry_account)
		self.eventEngine.register(EVENT_QRYPOSITION+self.gatewayName, self.rsp_qry_position)
		self.eventEngine.register(EVENT_QRYTRADE+self.gatewayName, self.rsp_qry_trade)
		self.eventEngine.register(EVENT_QRYORDER+self.gatewayName, self.rsp_qry_order)
		self.eventEngine.register(EVENT_QRYINVESTOR+self.gatewayName, self.rsp_qry_investor)
		self.eventEngine.register(EVENT_QRYINSTRUMENT+self.gatewayName, self.rsp_qry_instrument)
		
		self.eventEngine.register(EVENT_ERRORDERCANCEL+self.gatewayName, self.err_order_insert)
		self.eventEngine.register(EVENT_ERRORDERINSERT+self.gatewayName, self.err_order_action)
		self.eventEngine.register(EVENT_RTNTRADE+self.gatewayName, self.rtn_trade)
		self.eventEngine.register(EVENT_RTNORDER+self.gatewayName, self.rtn_order)
		
	def onOrder(self, order):
		pass
		
	def onTrade(self, trade):
		pass
		
	def rtn_order(self, event):
		data = event.dict['data']
        newref = data['OrderRef']
		if not newref.isdigit():
			return
		order_ref = int(newref)	
        self.orderRef = max(self.orderRef, order_ref)
        if (order_ref in self.ref2order):
            myorder = self.ref2order[order_ref]
            # only update sysID,
            status = myorder.on_order(sys_id = data['OrderSysID'], price = data['LimitPrice'], volume = 0)
			if data['OrderStatus'] in [ '5', '2']:
				myorder.on_cancel()
				status = True
			if myorder.trade_ref <= 0:
				order = VtOrderData()
				order.gatewayName = self.gatewayName
				# 保存代码和报单号
				order.symbol = data['InstrumentID']
				order.exchange = exchangeMapReverse[data['ExchangeID']]
				order.instID = order.symbol #'.'.join([order.symbol, order.exchange])
				order.orderID = order_ref
				order.orderSysID = data['OrderSysID']
				# 方向
				if data['Direction'] == '0':
					order.direction = DIRECTION_LONG
				elif data['Direction'] == '1':
					order.direction = DIRECTION_SHORT
				else:
					order.direction = DIRECTION_UNKNOWN
				# 开平
				if data['CombOffsetFlag'] == '0':
					order.offset = OFFSET_OPEN
				elif data['CombOffsetFlag'] == '1':
					order.offset = OFFSET_CLOSE
				else:
					order.offset = OFFSET_UNKNOWN
				# 状态
				if data['OrderStatus'] == '0':
					order.status = STATUS_ALLTRADED
				elif data['OrderStatus'] == '1':
					order.status = STATUS_PARTTRADED
				elif data['OrderStatus'] == '3':
					order.status = STATUS_NOTTRADED
				elif data['OrderStatus'] == '5':
					order.status = STATUS_CANCELLED
				else:
					order.status = STATUS_UNKNOWN				
				# 价格、报单量等数值
				order.price = data['LimitPrice']
				order.totalVolume = data['VolumeTotalOriginal']
				order.tradedVolume = data['VolumeTraded']
				order.orderTime = data['InsertTime']
				order.cancelTime = data['CancelTime']
				order.frontID = data['FrontID']
				order.sessionID = data['SessionID']
				order.order_ref = order_ref
				self.gateway.onOrder(order)	
				return				
            else:
				if status:
					event = Event(type=EVENT_ETRADEUPDATE)
					event.dict['trade_ref'] = myorder.trade_ref
					self.eventEngine.put(event)
		else:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = 'receive order update from other agents, InstID=%s, OrderRef=%s' % (data['InstrumentID'], order_ref)
			log.level = logging.WARNING
            self.gateway.onLog(log)
			
	def rtn_trade(self, event):
		data = event.dict['data']
        newref = data['OrderRef']
		if not newref.isdigit():
			return
		order_ref = int(newref)	
        if order_ref in self.ref2order:
            myorder = self.ref2order[order_ref]
            myorder.on_trade(price = data['Price'], volume=data['Volume'], trade_id = data['TradeID'])
			if myorder.trade_ref <= 0:
				trade = VtTradeData()
				trade.gatewayName = self.gatewayName
				# 保存代码和报单号
				trade.symbol = data['InstrumentID']
				trade.exchange = exchangeMapReverse[data['ExchangeID']]
				trade.vtSymbol = trade.symbol #'.'.join([trade.symbol, trade.exchange])
				trade.tradeID = data['TradeID']
				trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID])
				trade.orderID = data['OrderRef']
				trade.order_ref = order_ref
				# 方向
				trade.direction = directionMapReverse.get(data['Direction'], '')
				# 开平
				trade.offset = offsetMapReverse.get(data['OffsetFlag'], '')
				# 价格、报单量等数值
				trade.price = data['Price']
				trade.volume = data['Volume']
				trade.tradeTime = data['TradeTime']
				# 推送
				self.gateway.onTrade(trade)			
			else:
				event = Event(type=EVENT_ETRADEUPDATE)
				event.dict['trade_ref'] = myorder.trade_ref
				self.eventEngine.put(event)
		else:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = 'receive trade update from other agents, InstID=%s, OrderRef=%s' % (data['InstrumentID'], order_ref)
			log.level = logging.WARNING
            self.gateway.onLog(log)
		
	def rsp_market_data(self, event):
		data = event.dict['data']
		if self.trading_day == 0:
			self.trading_day = int(data['TradingDay'])
		timestr = str(self.trading_day) + ' '+ str(data['UpdateTime']) + ' ' + str(data['UpdateMillisec']) + '000'
		try:
			timestamp = datetime.datetime.strptime(timestr, '%Y%m%d %H:%M:%S %f')
		except:
			print "Error to convert timestr = %s" % timestr
			return
		tick_id = get_tick_id(timestamp)
		if data['ExchangeID'] == 'CZCE':
			if (len(data['TradingDay'])>0):				
				if (self.trading_day > int(data['TradingDay'])) and (tick_id >= 600000):
					rtn_error = BaseObject(errorMsg="tick data is wrong, %s" % data)
					self.onError(rtn_error)
					return
		tick = VtTickData()
		tick.gatewayName = self.gatewayName
		tick.symbol = data['InstrumentID']			
		tick.instID = tick.symbol #'.'.join([tick.symbol, EXCHANGE_UNKNOWN])
		tick.exchange = exchangeMapReverse.get(data['ExchangeID'], u'未知')
		product = inst2product(tick.instID)
		hrs = trading_hours(product, exch)
		buffer = 5
		tick_status = True
		for ptime in hrs:
			if (tick_id>=ptime[0]*1000-buffer) and (tick_id< ptime[1]*1000+buffer):
				bad_tick = False
				break
		if bad_tick:
			return
		tick.timestamp = timestamp
		tick.date = timestamp.date
		tick.tick_id = tick_id	
		tick.price = data['LastPrice']
		tick.volume = data['Volume']
		tick.openInterest = data['OpenInterest']
		# CTP只有一档行情
		tick.open = data['OpenPrice']
		tick.high = data['HighestPrice']
		tick.low = data['LowestPrice']
		tick.prev_close = data['PreClosePrice']        
		tick.upLimit = data['UpperLimitPrice']
		tick.downLimit = data['LowerLimitPrice']
		tick.bidPrice1 = data['BidPrice1']
		tick.bidVol1 = data['BidVolume1']
		tick.askPrice1 = data['AskPrice1']
		tick.askVol1 = data['AskVolume1']
        # 通用事件
        event1 = Event(type=EVENT_TICK)
        event1.dict['data'] = tick
        self.eventEngine.put(event1)
        
        # 特定合约代码的事件
        event2 = Event(type=EVENT_TICK+tick.instID)
        event2.dict['data'] = tick
        self.eventEngine.put(event2)

	def rsp_qry_account(self, event):
		data = event.dict['data']
        self.qrt_account['preBalance'] = data['PreBalance']
        self.qrt_account['available'] = data['Available']
        self.qrt_account['commission'] = data['Commission']
        self.qrt_account['margin'] = data['CurrMargin']
        self.qrt_account['closeProfit'] = data['CloseProfit']
        self.qrt_account['positionProfit'] = data['PositionProfit']
        
        # 这里的balance和快期中的账户不确定是否一样，需要测试
        self.qrt_account['balance'] = (data['PreBalance'] - data['PreCredit'] - data['PreMortgage'] +
                           data['Mortgage'] - data['Withdraw'] + data['Deposit'] +
                           data['CloseProfit'] + data['PositionProfit'] + data['CashIn'] -
                           data['Commission'])
    		
	def rsp_qry_instrument(self, event):
		pass
		
	def rsp_qry_position(self, event):
        pposition = event.dict['data']
        isLast = event.dict['last']
        instID = pposition['InstrumentID']
        if (instID not in self.qry_pos):
			self.qry_pos[instID]   = {'tday': [0, 0], 'yday': [0, 0]}
        key = 'yday'
		idx = 1
		if pposition['PosiDirection'] == '2':
			if pposition['PositionDate'] == '1':
				key = 'tday'
				idx = 0
			else:
				idx = 0
		else:
			if pposition.PositionDate == '1':
				key = 'tday'
		self.qry_pos[instID][key][idx] = pposition['Position']
		self.qry_pos[instID]['yday'][idx] = pposition['YdPosition']
        if isLast:
            print self.qry_pos
            pass
	
	def rsp_qry_order(self, event):
        sorder = event.dict['data']
        isLast = event.dict['last']
        if (len(sorder.OrderRef) == 0):
            return
        if not sorder['OrderRef'].isdigit():
            return
        order_ref = int(sorder['OrderRef']
        if (order_ref in self.ref2order):
            iorder = self.ref2order[order_ref]
            self.system_orders.append(order_ref)
            if iorder.status not in [order.OrderStatus.Cancelled, order.OrderStatus.Done]:
                status = iorder.on_order(sys_id = sorder['OrderSysID'], price = sorder['LimitPrice'], volume = sorder['VolumeTraded'])
                if status:
					event = Event(type=EVENT_ETRADEUPDATE)
					event.dict['trade_ref'] = iorder.trade_ref
					self.eventEngine.put(event)
                elif sorder.OrderStatus in ['3', '1', 'a']:
                    if iorder.status != order.OrderStatus.Sent or iorder.conditionals != {}:
                        iorder.status = order.OrderStatus.Sent
                        iorder.conditionals = {}
						log = VtLogData()
						log.gatewayName = self.gatewayName
						log.logContent = 'order status for OrderSysID = %s, Inst=%s is set to %s, but should be waiting in exchange queue' % (iorder.sys_id, iorder.instrument.name, iorder.status)
						log.level = logging.INFO
						self.gateway.onLog(log)
                elif sorder.OrderStatus in ['5', '2', '4']:
                    if iorder.status != order.OrderStatus.Cancelled:
                        iorder.on_cancel()
						event = Event(type=EVENT_ETRADEUPDATE)
						event.dict['trade_ref'] = iorder.trade_ref
						self.eventEngine.put(event)
						log = VtLogData()
						log.gatewayName = self.gatewayName
						log.logContent = 'order status for OrderSysID = %s, Inst=%s is set to %s, but should be waiting in exchange queue' % (iorder.sys_id, iorder.instrument.name, iorder.status)
						log.level = logging.INFO
						self.gateway.onLog(log)

        if isLast:
            for order_ref in self.ref2order:
                if (order_ref not in self.system_orders):
                    iorder = self.ref2order[order_ref]
                    iorder.on_cancel()
					event = Event(type=EVENT_ETRADEUPDATE)
					event.dict['trade_ref'] = iorder.trade_ref
					self.eventEngine.put(event)
            self.system_orders = []
			
    def err_order_insert(self, event):
        '''
            ctp/交易所下单错误回报，不区分ctp和交易所正常情况下不应当出现
        '''
        porder = event.dict['data']
        if not porder['OrderRef'].isdigit():
            return
        order_ref = int(porder['OrderRef'])
        inst = porder['InstrumentID']
        if order_ref in self.ref2order:
            myorder = self.ref2order[order_ref]
            myorder.on_cancel()
			event = Event(type=EVENT_ETRADEUPDATE)
			event.dict['trade_ref'] = iorder.trade_ref
			self.eventEngine.put(event)
		log = VtLogData()
		log.gatewayName = self.gatewayName
		log.logContent = 'OrderInsert is not accepted by CTP, order_ref=%s, instrument=%s, error=%s. ' % (order_ref, inst, error['ErrorMsg'])
		log.level = logging.WARNING
		if inst not in self.order_stats:
			self.order_stats[inst] = {'submitted': 0, 'cancelled':0, 'failed': 0, 'status': True }
        self.order_stats[inst]['failed'] += 1
        if self.order_stats[inst]['failed'] >= self.failed_order_limit:
            self.order_stats[inst]['status'] = False
            log.logContent += 'Failed order reaches the limit, disable instrument = %s' % inst
		self.gateway.onLog(log)
		
    def err_order_action(self, event):
        '''
            ctp/交易所撤单错误回报，不区分ctp和交易所必须处理，如果已成交，撤单后必然到达这个位置
        '''
        porder = event.dict['data']
        error = event.dict['error']
		inst = porder['InstrumentID']
		log = VtLogData()
		log.gatewayName = self.gatewayName
		log.logContent = 'Order Cancel is wrong, order_ref=%s, instrument=%s, error=%s. ' % (porder['OrderRef'], inst, error['ErrorMsg'])
		log.level = logging.WARNING
        if porder['OrderRef'].isdigit():
            order_ref = int(porder['OrderRef'])
            myorder = self.ref2order[order_ref]
            if int(error['ErrorID']) in [25,26] and myorder.status not in [order.OrderStatus.Cancelled, order.OrderStatus.Done]:
                myorder.on_cancel()
				event = Event(type=EVENT_ETRADEUPDATE)
				event.dict['trade_ref'] = myorder.trade_ref
				self.eventEngine.put(event)
        #else:
        #    self.qry_commands.append(self.fetch_order)
        #    self.qry_commands.append(self.fetch_order)
		if inst not in self.order_stats:
			self.order_stats[inst] = {'submitted': 0, 'cancelled':0, 'failed': 0, 'status': True }
        self.order_stats[inst]['failed'] += 1
        if self.order_stats[inst]['failed'] >= self.failed_order_limit:
            self.order_stats[inst]['status'] = False
            log.logContent += 'Failed order reaches the limit, disable instrument = %s' % inst
		self.gateway.onLog(log)
			
########################################################################
class CtpMdApi(MdApi):
    """CTP行情API实现"""

    #----------------------------------------------------------------------
    def __init__(self, gateway):
        """Constructor"""
        super(CtpMdApi, self).__init__()
        
        self.gateway = gateway                  # gateway对象
        self.gatewayName = gateway.gatewayName  # gateway对象名称
        
        self.reqID = EMPTY_INT              # 操作请求编号
        
        self.connectionStatus = False       # 连接状态
        self.loginStatus = False            # 登录状态
        
        self.subscribedSymbols = set()      # 已订阅合约代码        
        
        self.userID = EMPTY_STRING          # 账号
        self.password = EMPTY_STRING        # 密码
        self.brokerID = EMPTY_STRING        # 经纪商代码
        self.address = EMPTY_STRING         # 服务器地址
		self.trading_day = 20160101
        
    #----------------------------------------------------------------------
    def onFrontConnected(self):
        """服务器连接"""
        self.connectionStatus = True
        
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = u'行情服务器连接成功'
		log.level = logging.INFO
        self.gateway.onLog(log)
        self.login()
    
    #----------------------------------------------------------------------  
    def onFrontDisconnected(self, n):
        """服务器断开"""
        self.connectionStatus = False
        self.loginStatus = False
        self.gateway.mdConnected = False
        
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = u'行情服务器连接断开'
		log.level = logging.INFO
        self.gateway.onLog(log)        
        
    #---------------------------------------------------------------------- 
    def onHeartBeatWarning(self, n):
        """心跳报警"""
        # 因为API的心跳报警比较常被触发，且与API工作关系不大，因此选择忽略
        pass
    
    #----------------------------------------------------------------------   
    def onRspError(self, error, n, last):
        """错误回报"""
        err = VtErrorData()
        err.gatewayName = self.gatewayName
        err.errorID = error['ErrorID']
        err.errorMsg = error['ErrorMsg'].decode('gbk')
        self.gateway.onError(err)
        
    #----------------------------------------------------------------------
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""
        # 如果登录成功，推送日志信息
        if (error['ErrorID'] == 0) and last:
            self.loginStatus = True
            self.gateway.mdConnected = True
            
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'行情服务器登录完成'
			log.level = logging.INFO
            self.gateway.onLog(log)
            
            # 重新订阅之前订阅的合约
            for subscribeReq in self.subscribedSymbols:
                self.subscribe(subscribeReq)
            trade_day_str = self.GetTradingDay()
			scur_day = int(self.agent.scur_day.strftime('%Y%m%d'))
            if len(trade_day_str) > 0:
                try:
                    self.trading_day = int(trade_day_str)
					if self.trading_day > scur_day:
						event = Event(type=EVENT_DAYSWITCH)
						event.dict['log'] = u'换日: %s -> %s' % (self.agent.scur_day, trading_day)
						event.dict['date'] = trading_day
						self.eventEngine.put(event)
                except ValueError:
                    pass
        # 否则，推送错误信息
        else:
            err = VtErrorData()
            err.gatewayName = self.gatewayName
            err.errorID = error['ErrorID']
            err.errorMsg = error['ErrorMsg'].decode('gbk')
            self.gateway.onError(err)
                
    #---------------------------------------------------------------------- 
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        # 如果登出成功，推送日志信息
        if error['ErrorID'] == 0:
            self.loginStatus = False
            self.gateway.tdConnected = False
            
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'行情服务器登出完成'
			log.level = logging.INFO
            self.gateway.onLog(log)
                
        # 否则，推送错误信息
        else:
            err = VtErrorData()
            err.gatewayName = self.gatewayName
            err.errorID = error['ErrorID']
            err.errorMsg = error['ErrorMsg'].decode('gbk')
            self.gateway.onError(err)
        
    #----------------------------------------------------------------------  
    def onRspSubMarketData(self, data, error, n, last):
        """订阅合约回报"""
        # 通常不在乎订阅错误，选择忽略
        pass
        
    #----------------------------------------------------------------------  
    def onRspUnSubMarketData(self, data, error, n, last):
        """退订合约回报"""
        # 同上
        pass  
        
    #----------------------------------------------------------------------  
    def onRtnDepthMarketData(self, data):
        """行情推送"""
		if (data['LastPrice'] > data['UpperLimitPrice']) or (data['LastPrice'] < data['LowerLimitPrice']) or \
		   (data['AskPrice1'] >= data['UpperLimitPrice'] and data['BidPrice1'] <= data['LowerLimitPrice']) or \
		   (data['BidPrice1'] > = data['AskPrice1']):
			log = VtLogData()
			log.gatewayName = self.gatewayName
			log.logContent = u'MD:error in market data for %s LastPrice=%s, BidPrice=%s, AskPrice=%s' %(dp.InstrumentID, dp.LastPrice, dp.BidPrice1,dp.AskPrice1)
			log.level = logging.DEBUG
			self.gateway.onLog(log)
			return	
		event = Event(type = EVENT_MARKETDATA + self.gatewayName)
        event.dict['data'] = data
		event.dict['gateway'] = self.gatewayName
        self.eventEngine.put(event)
        
    #---------------------------------------------------------------------- 
    def onRspSubForQuoteRsp(self, data, error, n, last):
        """订阅期权询价"""
        pass
        
    #----------------------------------------------------------------------
    def onRspUnSubForQuoteRsp(self, data, error, n, last):
        """退订期权询价"""
        pass 
        
    #---------------------------------------------------------------------- 
    def onRtnForQuoteRsp(self, data):
        """期权询价推送"""
        pass        
        
    #----------------------------------------------------------------------
    def connect(self, userID, password, brokerID, address):
        """初始化连接"""
        self.userID = userID                # 账号
        self.password = password            # 密码
        self.brokerID = brokerID            # 经纪商代码
        self.address = address              # 服务器地址
        
        # 如果尚未建立服务器连接，则进行连接
        if not self.connectionStatus:
            # 创建C++环境中的API对象，这里传入的参数是需要用来保存.con文件的文件夹路径
            path = os.getcwd() + '\\temp\\' + self.gatewayName + '\\'
            if not os.path.exists(path):
                os.makedirs(path)
            self.createFtdcMdApi(path)
            
            # 注册服务器地址
            self.registerFront(self.address)
            
            # 初始化连接，成功会调用onFrontConnected
            self.init()
            
        # 若已经连接但尚未登录，则进行登录
        else:
            if not self.loginStatus:
                self.login()
        
    #----------------------------------------------------------------------
    def subscribe(self, subscribeReq):
        """订阅合约"""
        # 这里的设计是，如果尚未登录就调用了订阅方法
        # 则先保存订阅请求，登录完成后会自动订阅
        if self.loginStatus:
            self.subscribeMarketData(str(subscribeReq.symbol))
        self.subscribedSymbols.add(subscribeReq)   
        
    #----------------------------------------------------------------------
    def login(self):
        """登录"""
        # 如果填入了用户名密码等，则登录
        if self.userID and self.password and self.brokerID:
            req = {}
            req['UserID'] = self.userID
            req['Password'] = self.password
            req['BrokerID'] = self.brokerID
            self.reqID += 1
            self.reqUserLogin(req, self.reqID)    
    
    #----------------------------------------------------------------------
    def close(self):
        """关闭"""
        self.exit()


########################################################################
class CtpTdApi(TdApi):
    """CTP交易API实现"""
    
    #----------------------------------------------------------------------
    def __init__(self, gateway):
        """API对象的初始化函数"""
        super(CtpTdApi, self).__init__()
        
        self.gateway = gateway                  # gateway对象
        self.gatewayName = gateway.gatewayName  # gateway对象名称
        
        self.reqID = EMPTY_INT              # 操作请求编号
        self.orderRef = EMPTY_INT           # 订单编号
        
        self.connectionStatus = False       # 连接状态
        self.loginStatus = False            # 登录状态
        
        self.userID = EMPTY_STRING          # 账号
        self.password = EMPTY_STRING        # 密码
        self.brokerID = EMPTY_STRING        # 经纪商代码
        self.address = EMPTY_STRING         # 服务器地址
        
        self.frontID = EMPTY_INT            # 前置机编号
        self.sessionID = EMPTY_INT          # 会话编号
        
    #----------------------------------------------------------------------
    def onFrontConnected(self):
        """服务器连接"""
        self.connectionStatus = True
        
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = u'交易服务器连接成功'
		log.level = logging.INFO
        self.gateway.onLog(log)
        
        self.login()
    
    #----------------------------------------------------------------------
    def onFrontDisconnected(self, n):
        """服务器断开"""
        self.connectionStatus = False
        self.loginStatus = False
        self.gateway.tdConnected = False
        
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = u'交易服务器连接断开'
		log.level = logging.INFO
        self.gateway.onLog(log)      
    
    #----------------------------------------------------------------------
    def onHeartBeatWarning(self, n):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspAuthenticate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""
        # 如果登录成功，推送日志信息
        if error['ErrorID'] == 0:
            self.frontID = str(data['FrontID'])
            self.sessionID = str(data['SessionID'])
            self.loginStatus = True
            
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'交易服务器登录完成'
            self.gateway.onLog(log)
            
            # 确认结算信息
            req = {}
            req['BrokerID'] = self.brokerID
            req['InvestorID'] = self.userID
            self.reqID += 1
            self.reqSettlementInfoConfirm(req, self.reqID)			
                
        # 否则，推送错误信息
        else:
            self.loginStatus = False
			self.gateway.tdConnected = False
			err = VtErrorData()
            err.gatewayName = self.gateway
            err.errorID = error['ErrorID']
            err.errorMsg = error['ErrorMsg'].decode('gbk')
            self.gateway.onError(err)			
			time.sleep(30)
			self.login()
    
    #----------------------------------------------------------------------
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        # 如果登出成功，推送日志信息
        if error['ErrorID'] == 0:
            self.loginStatus = False
            self.gateway.tdConnected = False
            
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'交易服务器登出完成'
            self.gateway.onLog(log)
                
        # 否则，推送错误信息
        else:
            err = VtErrorData()
            err.gatewayName = self.gatewayName
            err.errorID = error['ErrorID']
            err.errorMsg = error['ErrorMsg'].decode('gbk')
            self.gateway.onError(err)
    
    #----------------------------------------------------------------------
    def onRspUserPasswordUpdate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspTradingAccountPasswordUpdate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspOrderInsert(self, data, error, n, last):
        """发单错误（柜台）"""
        err = VtErrorData()
        err.gatewayName = self.gatewayName
        err.errorID = error['ErrorID']
        err.errorMsg = error['ErrorMsg'].decode('gbk')
        self.gateway.onError(err)
		
        event2 = Event(type=EVENT_ERRORDERINSERT + self.gatewayName)
        event2.dict['data'] = data
        event2.dict['error'] = error
		event2.dict['gateway'] = self.gatewayName
        self.eventEngine.put(event2) 
 
    
    #----------------------------------------------------------------------
    def onRtnOrder(self, data):
        """报单回报"""
        # 更新最大报单编号
        event = Event(type=EVENT_RTNORDER + self.gatewayName)
        event.dict['data'] = data
        self.eventEngine.put(event)
    
    #----------------------------------------------------------------------
    def onRtnTrade(self, data):
        """成交回报"""
        # 创建报单数据对象
        event = Event(type=EVENT_RTNTRADE+self.gatewayName)
        event.dict['data'] = data
        self.eventEngine.put(event)
    
    #----------------------------------------------------------------------
    def onErrRtnOrderInsert(self, data, error):
        """发单错误回报（交易所）"""
        event = Event(type=EVENT_ERRORDERINSERT + self.gatewayName)
        event.dict['data'] = data
        event.dict['error'] = error
        self.eventEngine.put(event)     
		
        err = VtErrorData()
        err.gatewayName = self.gatewayName
        err.errorID = error['ErrorID']
        err.errorMsg = error['ErrorMsg'].decode('gbk')
        self.gateway.onError(err)
    
    #----------------------------------------------------------------------
    def onErrRtnOrderAction(self, data, error):
        """撤单错误回报（交易所）"""
        event = Event(type=EVENT_ERRORDERCANCEL + self.gatewayName)
        event.dict['data'] = data
        event.dict['error'] = error
		event.dict['gateway'] = self.gatewayName
        self.eventEngine.put(event) 
		
        err = VtErrorData()
        err.gatewayName = self.gatewayName
        err.errorID = error['ErrorID']
        err.errorMsg = error['ErrorMsg'].decode('gbk')
        self.gateway.onError(err)
		
    #----------------------------------------------------------------------
    def onRspOrderAction(self, data, error, n, last):
        """撤单错误（柜台）"""
        err = VtErrorData()
        err.gatewayName = self.gatewayName
        err.errorID = error['ErrorID']
        err.errorMsg = error['ErrorMsg'].decode('gbk')
        self.gateway.onError(err)

        event2 = Event(type=EVENT_ERRORDERCANCEL + self.gatewayName)
        event2.dict['data'] = data
        event2.dict['error'] = error
		event2.dict['gateway'] = self.gatewayName
        self.eventEngine.put(event2) 
		
    #----------------------------------------------------------------------
    def onRspQueryMaxOrderVolume(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspSettlementInfoConfirm(self, data, error, n, last):
        """确认结算信息回报"""
		self.gateway.tdConnected = True
        event = Event(type=EVENT_TDLOGIN)
        self.eventEngine.put(event)         
		
        # 查询合约代码
        # self.reqID += 1
        # self.reqQryInstrument({}, self.reqID)
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = u'结算信息确认完成'
        self.gateway.onLog(log)
    
    #----------------------------------------------------------------------
    def onRspQryTradingAccount(self, data, error, n, last):
        """资金账户查询回报"""
        if error['ErrorID'] == 0:
            event = Event(type=EVENT_QRYACCOUNT + self.gatewayName )
            event.dict['data'] = data
            event.dict['last'] = last
            self.eventEngine.put(event)         
        else:
            event = Event(type=EVENT_LOG)
            log = u'资金账户查询回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)

    #----------------------------------------------------------------------
    def onRspParkedOrderInsert(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspParkedOrderAction(self, data, error, n, last):
        """"""
        pass
        
    #----------------------------------------------------------------------
    def onRspRemoveParkedOrder(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspRemoveParkedOrderAction(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspExecOrderInsert(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspExecOrderAction(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspForQuoteInsert(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQuoteInsert(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQuoteAction(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryOrder(self, data, error, n, last):
        """"""
        '''请求查询报单响应'''
        if error['ErrorID'] == 0:
            event = Event(type=EVENT_QRYORDER + self.gatewayName )
            event.dict['data'] = data
            event.dict['last'] = last
            self.eventEngine.put(event)         
        else:
            event = Event(type=EVENT_LOG)
            log = u'交易错误回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)
    
    #----------------------------------------------------------------------
    def onRspQryTrade(self, data, error, n, last):
        """"""
        if error['ErrorID'] == 0:
            event = Event(type=EVENT_QRYTRADE + self.gatewayName )
            event.dict['data'] = data
            event.dict['last'] = last
            self.eventEngine.put(event)         
        else:
            event = Event(type=EVENT_LOG)
            log = u'交易错误回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)
    
    #----------------------------------------------------------------------
    def onRspQryInvestorPosition(self, data, error, n, last):
        """持仓查询回报"""
        if error['ErrorID'] == 0:
            event = Event(type=EVENT_QRYPOSITION + self.gatewayName )
            event.dict['data'] = data
            event.dict['last'] = last
            self.eventEngine.put(event)         
        else:
            event = Event(type=EVENT_LOG)
            log = u'持仓查询回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)

    #----------------------------------------------------------------------
    def onRspQryInvestor(self, data, error, n, last):
        """投资者查询回报"""
        if error['ErrorID'] == 0:
            event = Event(type=EVENT_QRYINVESTOR + self.gatewayName )
            event.dict['data'] = data
            event.dict['last'] = last
            self.eventEngine.put(event)         
        else:
            event = Event(type=EVENT_LOG)
            log = u'合约投资者回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)
    
    #----------------------------------------------------------------------
    def onRspQryTradingCode(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInstrumentMarginRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInstrumentCommissionRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExchange(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryProduct(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInstrument(self, data, error, n, last):
        """合约查询回报"""
        if error['ErrorID'] == 0:
            event = Event(type=EVENT_QRYINSTRUMENT + self.gatewayName )
            event.dict['data'] = data
            event.dict['last'] = last
            self.eventEngine.put(event)         
        else:
            event = Event(type=EVENT_LOG)
            log = u'交易错误回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
            event.dict['log'] = log
            event.dict['level'] = logging.DEBUG
            self.eventEngine.put(event)
    
    #----------------------------------------------------------------------
    def onRspQryDepthMarketData(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQrySettlementInfo(self, data, error, n, last):
        """查询结算信息回报"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryTransferBank(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInvestorPositionDetail(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryNotice(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQrySettlementInfoConfirm(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInvestorPositionCombineDetail(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryCFMMCTradingAccountKey(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryEWarrantOffset(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInvestorProductGroupMargin(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExchangeMarginRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExchangeMarginRateAdjust(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExchangeRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQrySecAgentACIDMap(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryOptionInstrTradeCost(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryOptionInstrCommRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExecOrder(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryForQuote(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryQuote(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryTransferSerial(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryAccountregister(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspError(self, error, n, last):
        """错误回报"""
        err = VtErrorData()
        err.gatewayName = self.gatewayName
        err.errorID = error['ErrorID']
        err.errorMsg = error['ErrorMsg'].decode('gbk')
        self.gateway.onError(err)
    
    #----------------------------------------------------------------------
    def onRtnInstrumentStatus(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnTradingNotice(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnErrorConditionalOrder(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnExecOrder(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnExecOrderInsert(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnExecOrderAction(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnForQuoteInsert(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnQuote(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnQuoteInsert(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnQuoteAction(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnForQuoteRsp(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryContractBank(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryParkedOrder(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryParkedOrderAction(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryTradingNotice(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryBrokerTradingParams(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryBrokerTradingAlgos(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnFromBankToFutureByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnFromFutureToBankByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromBankToFutureByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromFutureToBankByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnFromBankToFutureByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnFromFutureToBankByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromBankToFutureByFutureManual(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromFutureToBankByFutureManual(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnQueryBankBalanceByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnBankToFutureByFuture(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnFutureToBankByFuture(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnRepealBankToFutureByFutureManual(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnRepealFutureToBankByFutureManual(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnQueryBankBalanceByFuture(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromBankToFutureByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromFutureToBankByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspFromBankToFutureByFuture(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspFromFutureToBankByFuture(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQueryBankAccountMoneyByFuture(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnOpenAccountByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnCancelAccountByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnChangeAccountByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def connect(self, userID, password, brokerID, address):
        """初始化连接"""
        self.userID = userID                # 账号
        self.password = password            # 密码
        self.brokerID = brokerID            # 经纪商代码
        self.address = address              # 服务器地址
        
        # 如果尚未建立服务器连接，则进行连接
        if not self.connectionStatus:
            # 创建C++环境中的API对象，这里传入的参数是需要用来保存.con文件的文件夹路径
            path = os.getcwd() + '\\temp\\' + self.gatewayName + '\\'
            if not os.path.exists(path):
                os.makedirs(path)
            self.createFtdcTraderApi(path)
            
            # 注册服务器地址
            self.registerFront(self.address)
            
            # 初始化连接，成功会调用onFrontConnected
            self.init()
            
        # 若已经连接但尚未登录，则进行登录
        else:
            if not self.loginStatus:
                self.login()    
    
    #----------------------------------------------------------------------
    def login(self):
        """连接服务器"""
        # 如果填入了用户名密码等，则登录
        if self.userID and self.password and self.brokerID:
            req = {}
            req['UserID'] = self.userID
            req['Password'] = self.password
            req['BrokerID'] = self.brokerID
            self.reqID += 1
            self.reqUserLogin(req, self.reqID)   
        
    #----------------------------------------------------------------------
    def qryAccount(self):
        """查询账户"""
        self.reqID += 1
        self.reqQryTradingAccount({}, self.reqID)
        
    #----------------------------------------------------------------------
    def qryPosition(self):
        """查询持仓"""
        self.reqID += 1
        req = {}
        req['BrokerID'] = self.brokerID
        req['InvestorID'] = self.userID
        self.reqQryInvestorPosition(req, self.reqID)
        
    #----------------------------------------------------------------------
    def sendOrder(self, orderReq):
        """发单"""
        self.reqID += 1
        self.orderRef += 1
        
        req = {}
        
        req['InstrumentID'] = orderReq.symbol
        req['LimitPrice'] = orderReq.price
        req['VolumeTotalOriginal'] = orderReq.volume
        
        # 下面如果由于传入的类型本接口不支持，则会返回空字符串
        try:
            req['OrderPriceType'] = priceTypeMap[orderReq.priceType]
            req['Direction'] = directionMap[orderReq.direction]
            req['CombOffsetFlag'] = offsetMap[orderReq.offset]
        except KeyError:
            return ''
            
        req['OrderRef'] = str(self.orderRef)
        req['InvestorID'] = self.userID
        req['UserID'] = self.userID
        req['BrokerID'] = self.brokerID
        
        req['CombHedgeFlag'] = defineDict['THOST_FTDC_HF_Speculation']       # 投机单
        req['ContingentCondition'] = defineDict['THOST_FTDC_CC_Immediately'] # 立即发单
        req['ForceCloseReason'] = defineDict['THOST_FTDC_FCC_NotForceClose'] # 非强平
        req['IsAutoSuspend'] = 0                                             # 非自动挂起
        req['TimeCondition'] = defineDict['THOST_FTDC_TC_GFD']               # 今日有效
        req['VolumeCondition'] = defineDict['THOST_FTDC_VC_AV']              # 任意成交量
        req['MinVolume'] = 1                                                 # 最小成交量为1
        
        self.reqOrderInsert(req, self.reqID)
        
        # 返回订单号（字符串），便于某些算法进行动态管理
        vtOrderID = '.'.join([self.gatewayName, str(self.orderRef)])
        return vtOrderID
    
    #----------------------------------------------------------------------
    def cancelOrder(self, cancelOrderReq):
        """撤单"""
        self.reqID += 1

        req = {}
        
        req['InstrumentID'] = cancelOrderReq.symbol
        req['ExchangeID'] = cancelOrderReq.exchange
        req['OrderRef'] = cancelOrderReq.orderID
        req['FrontID'] = cancelOrderReq.frontID
        req['SessionID'] = cancelOrderReq.sessionID
        
        req['ActionFlag'] = defineDict['THOST_FTDC_AF_Delete']
        req['BrokerID'] = self.brokerID
        req['InvestorID'] = self.userID
        
        self.reqOrderAction(req, self.reqID)
        
    #----------------------------------------------------------------------
    def close(self):
        """关闭"""
        self.exit()

if __name__ == '__main__':
    test()
    
