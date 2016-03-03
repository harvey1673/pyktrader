# encoding: UTF-8
from ctp_gateway import *

class SimCtpTdApi(object):
    def __init__(self, gateway):
        """API对象的初始化函数"""
        self.gateway = gateway                  # gateway对象
        self.gatewayName = gateway.gatewayName  # gateway对象名称

        self.reqID = EMPTY_INT              # 操作请求编号
        self.orderRef = EMPTY_INT           # 订单编号

        self.connectionStatus = True      # 连接状态
        self.loginStatus = True            # 登录状态

        self.userID = EMPTY_STRING          # 账号
        self.password = EMPTY_STRING        # 密码
        self.brokerID = EMPTY_STRING        # 经纪商代码
        self.address = EMPTY_STRING         # 服务器地址

        self.frontID = EMPTY_INT            # 前置机编号
        self.sessionID = EMPTY_INT          # 会话编号

    def sendOrder(self, iorder):
        """发单"""
        iorder.local_id = iorder.order_ref
        self.reqID += 1
        self.orderRef = max(self.orderRef, iorder.local_id)
        req = {}
        req['InstrumentID'] = iorder.instrument.name
        req['LimitPrice'] = iorder.limit_price
        req['VolumeTotalOriginal'] = iorder.volume
        try:
            req['OrderPriceType'] = iorder.price_type
            req['Direction'] = iorder.direction
            req['CombOffsetFlag'] = iorder.action_type
        except KeyError:
            return ''
        req['OrderRef'] = str(iorder.local_id)
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

    def reqOrderInsert(self, order, request_id):
        oid = order['OrderRef']
        trade= {'InstrumentID' : order['InstrumentID'],
                'Direction': order['Direction'],
                'Price': order['LimitPrice'],
                'Volume': order['VolumeTotalOriginal'],
                'OrderRef': oid,
                'TradeID': oid,
                'OrderSysID': oid,
                'BrokerOrderSeq': int(oid),
                'OrderLocalID': oid,
                'TradeTime': time.strftime('%H%M%S')}
        event1 = Event(type=EVENT_RTNTRADE+self.gatewayName)
        event1.dict['data'] = trade
        self.gateway.eventEngine.put(event1)

    def cancelOrder(self, iorder):
        """撤单"""
        inst = iorder.instrument
        self.reqID += 1
        req = {}
        req['InstrumentID'] = inst.name
        req['ExchangeID'] = inst.exchange
        req['ActionFlag'] = defineDict['THOST_FTDC_AF_Delete']
        req['BrokerID'] = self.brokerID
        req['InvestorID'] = self.userID
        req['OrderSysID'] = str(iorder.order_ref)
        req['OrderRef'] = str(iorder.order_ref)
        req['FrontID'] = self.frontID
        req['SessionID'] = self.sessionID
        self.reqOrderAction(req, self.reqID)

    def reqOrderAction(self, corder, request_id):
        local_id = int(corder['OrderRef'])
        if (local_id in self.gateway.id2order):
            myorder = self.gateway.id2order[local_id]
            myorder.on_cancel()
            event = Event(type=EVENT_ETRADEUPDATE)
            event.dict['trade_ref'] = myorder.trade_ref
            self.gateway.eventEngine.put(event)

    def reqQryTradingAccount(self,req,req_id=0):
        pass

    def reqQryInstrument(self,req,req_id=0):
        pass

    def reqQryInstrumentMarginRate(self,req,req_id=0):
        pass

    def reqQryInvestorPosition(self,req,req_id=0):
        pass

    def qryPosition(self):
        pass

    def qryAccount(self):
        pass

    def qryInstrument(self):
        pass

    def close(self):
        pass

    def connect(self, userID, password, brokerID, address):
        """初始化连接"""
        self.userID = userID                # 账号
        self.password = password            # 密码
        self.brokerID = brokerID            # 经纪商代码
        self.address = address              # 服务器地址

class CtpSimGateway(CtpGateway):
    def __init__(self, agent, gatewayName='CTP'):
        """Constructor"""
        super(CtpSimGateway, self).__init__(agent, gatewayName)
        self.tdApi = SimCtpTdApi(self)     # 交易API
        self.qryEnabled = False         # 是否要启动循环查询
        self.md_data_buffer = 0

    def connect(self):
        fileName = self.file_prefix + 'connect.json'
        try:
            f = file(fileName)
        except IOError:
            logContent = u'读取连接配置出错，请检查'
            self.onLog(logContent, level = logging.WARNING)
            return
        # 解析json文件
        setting = json.load(f)
        try:
            userID = str(setting['userID'])
            password = str(setting['password'])
            brokerID = str(setting['brokerID'])
            mdAddress = str(setting['mdAddress'])
        except KeyError:
            logContent = u'连接配置缺少字段，请检查'
            self.onLog(logContent, level = logging.WARNING)
            return

        # 创建行情和交易接口对象
        self.mdApi.connect(userID, password, brokerID, mdAddress)
        self.mdConnected = False
        self.tdApi.connect(userID, password, brokerID, mdAddress)
        self.tdConnected = True

    def register_event_handler(self):
        self.eventEngine.register(EVENT_MARKETDATA+self.gatewayName, self.rsp_market_data)
        self.eventEngine.register(EVENT_ERRORDERCANCEL+self.gatewayName, self.err_order_insert)
        self.eventEngine.register(EVENT_ERRORDERINSERT+self.gatewayName, self.err_order_action)
        self.eventEngine.register(EVENT_RTNTRADE+self.gatewayName, self.rtn_trade)
        #self.eventEngine.register(EVENT_RTNORDER+self.gatewayName, self.rtn_order)

    def rsp_td_login(self, event):
        pass

