/*!
* \file LTSStruct.h
* \brief 示例代码主程序接口
*
* 本项目是基于华宝技术LTS证券接口C#开发的示例程序，用于展示LTS如何在DoNet环境下用C#进行开发。示例代码演示了LTS各类接口C#的调用，在编写相关项目时可以参考。
* 由尔易信息提供开源，最新代码可从http://github.com/REInfo获取。
* 上海尔易信息科技有限公司提供证券、期货、期权、现货等市场交易、结算、 风控业务的客户化定制服务。
*
* \author wywty
* \version 1.0
* \date 2014-6-30
* 
*/
#pragma once

using namespace System;
using namespace System::Runtime::InteropServices;

namespace RELib_LTSNet
{

	public enum struct EnumRESUMETYPE: Byte
	{
		TERT_RESTART = 0,
		TERT_RESUME,
		TERT_QUICK
	};
	/// <summary>
	/// 交易所属性 CExchangePropertyType
	/// </summary>
	public enum struct EnumExchangePropertyType : Byte
	{
		/// <summary>
		/// 正常
		/// </summary>
		Normal=(Byte)'0',
		/// <summary>
		/// 根据成交生成报单
		/// </summary>
		GenOrderByTrade=(Byte)'1',
	};
	/// <summary>
	/// 交易所连接状态 CExchangeConnectStatusType
	/// </summary>
	public enum struct EnumExchangeConnectStatusType : Byte
	{
		/// <summary>
		/// 没有任何连接
		/// </summary>
		NoConnection=(Byte)'1',
		/// <summary>
		/// 已经发出合约查询请求
		/// </summary>
		QryInstrumentSent=(Byte)'2',
		/// <summary>
		/// 已经获取信息
		/// </summary>
		GotInformation=(Byte)'9',
	};
	/// <summary>
	/// 产品类型 CProductClassType
	/// </summary>
	public enum struct EnumProductClassType : Byte
	{
		/// <summary>
		/// 期货
		/// </summary>
		Futures=(Byte)'1',
		/// <summary>
		/// 期权
		/// </summary>
		Options=(Byte)'2',
		/// <summary>
		/// 组合
		/// </summary>
		Combination=(Byte)'3',
		/// <summary>
		/// 即期
		/// </summary>
		Spot=(Byte)'4',
		/// <summary>
		/// 期转现
		/// </summary>
		EFP=(Byte)'5',
		/// <summary>
		/// 证券A股
		/// </summary>
		StockA=(Byte)'6',
		/// <summary>
		/// 证券B股
		/// </summary>
		StockB=(Byte)'7',
		/// <summary>
		/// ETF
		/// </summary>
		ETF=(Byte)'8',
		/// <summary>
		/// ETF申赎
		/// </summary>
		ETFPurRed=(Byte)'9',
	};
	/// <summary>
	/// 持仓类型 CPositionTypeType
	/// </summary>
	public enum struct EnumPositionTypeType : Byte
	{
		/// <summary>
		/// 净持仓
		/// </summary>
		Net=(Byte)'1',
		/// <summary>
		/// 综合持仓
		/// </summary>
		Gross=(Byte)'2',
	};
	/// <summary>
	/// 持仓日期类型 CPositionDateTypeType
	/// </summary>
	public enum struct EnumPositionDateTypeType : Byte
	{
		/// <summary>
		/// 使用历史持仓
		/// </summary>
		UseHistory=(Byte)'1',
		/// <summary>
		/// 不使用历史持仓
		/// </summary>
		NoUseHistory=(Byte)'2',
	};
	/// <summary>
	/// 合约生命周期状态 CInstLifePhaseType
	/// </summary>
	public enum struct EnumInstLifePhaseType : Byte
	{
		/// <summary>
		/// 未上市
		/// </summary>
		NotStart=(Byte)'0',
		/// <summary>
		/// 上市
		/// </summary>
		Started=(Byte)'1',
		/// <summary>
		/// 停牌
		/// </summary>
		Pause=(Byte)'2',
		/// <summary>
		/// 到期
		/// </summary>
		Expired=(Byte)'3',
	};
	/// <summary>
	/// 持仓交易类型 CPosTradeTypeType
	/// </summary>
	public enum struct EnumPosTradeTypeType : Byte
	{
		/// <summary>
		/// 今日新增持仓能卖出
		/// </summary>
		CanSelTodayPos=(Byte)'1',
		/// <summary>
		/// 今日新增持仓不能卖出
		/// </summary>
		CannotSellTodayPos=(Byte)'2',
	};
	/// <summary>
	/// 证件类型 CIdCardTypeType
	/// </summary>
	public enum struct EnumIdCardTypeType : Byte
	{
		/// <summary>
		/// 组织机构代码
		/// </summary>
		EID=(Byte)'0',
		/// <summary>
		/// 身份证
		/// </summary>
		IDCard=(Byte)'1',
		/// <summary>
		/// 军官证
		/// </summary>
		OfficerIDCard=(Byte)'2',
		/// <summary>
		/// 警官证
		/// </summary>
		PoliceIDCard=(Byte)'3',
		/// <summary>
		/// 士兵证
		/// </summary>
		SoldierIDCard=(Byte)'4',
		/// <summary>
		/// 户口簿
		/// </summary>
		HouseholdRegister =(Byte)'5',
		/// <summary>
		/// 护照
		/// </summary>
		Passport=(Byte)'6',
		/// <summary>
		/// 台胞证
		/// </summary>
		TaiwanCompatriotIDCard =(Byte)'7',
		/// <summary>
		/// 回乡证
		/// </summary>
		HomeComingCard=(Byte)'8',
		/// <summary>
		/// 营业执照号
		/// </summary>
		LicenseNo=(Byte)'9',
		/// <summary>
		/// 税务登记号
		/// </summary>
		TaxNo=(Byte)'A',
		/// <summary>
		/// 其他证件
		/// </summary>
		OtherCard=(Byte)'x',
	};
	/// <summary>
	/// 交易编码类型 CClientTypeType
	/// </summary>
	public enum struct EnumClientTypeType : Byte
	{
		/// <summary>
		/// 普通
		/// </summary>
		Normal=(Byte)'1',
		/// <summary>
		/// 信用交易
		/// </summary>
		Credit=(Byte)'2',
		/// <summary>
		/// 衍生品账户
		/// </summary>
		Derive=(Byte)'3',
		/// <summary>
		/// 其他类型
		/// </summary>
		Other=(Byte)'4',
	};
	/// <summary>
	/// 功能代码 CFunctionCodeType
	/// </summary>
	public enum struct EnumFunctionCodeType : Byte
	{
		/// <summary>
		/// 数据异步化
		/// </summary>
		DataAsync=(Byte)'1',
		/// <summary>
		/// 强制用户登出
		/// </summary>
		ForceUserLogout=(Byte)'2',
		/// <summary>
		/// 变更管理用户口令
		/// </summary>
		UserPasswordUpdate=(Byte)'3',
		/// <summary>
		/// 变更经纪公司口令
		/// </summary>
		BrokerPasswordUpdate=(Byte)'4',
		/// <summary>
		/// 变更投资者口令
		/// </summary>
		InvestorPasswordUpdate=(Byte)'5',
		/// <summary>
		/// 报单插入
		/// </summary>
		OrderInsert=(Byte)'6',
		/// <summary>
		/// 报单操作
		/// </summary>
		OrderAction=(Byte)'7',
		/// <summary>
		/// 同步系统数据
		/// </summary>
		SyncSystemData=(Byte)'8',
		/// <summary>
		/// 同步经纪公司数据
		/// </summary>
		SyncBrokerData=(Byte)'9',
		/// <summary>
		/// 批量同步经纪公司数据
		/// </summary>
		BachSyncBrokerData=(Byte)'A',
		/// <summary>
		/// 超级查询
		/// </summary>
		SuperQuery=(Byte)'B',
		/// <summary>
		/// 报单插入
		/// </summary>
		ParkedOrderInsert=(Byte)'C',
		/// <summary>
		/// 报单操作
		/// </summary>
		ParkedOrderAction=(Byte)'D',
		/// <summary>
		/// 同步动态令牌
		/// </summary>
		SyncOTP=(Byte)'E',
		/// <summary>
		/// 未知单操作
		/// </summary>
		UnkownOrderAction=(Byte)'F',

		///转托管
		DepositoryTransfer=(Byte)'G',
		///余券划转
		ExcessStockTransfer=(Byte)'H',
	};
	/// <summary>
	/// 用户类型 CUserTypeType
	/// </summary>
	public enum struct EnumUserTypeType : Byte
	{
		/// <summary>
		/// 投资者
		/// </summary>
		Investor=(Byte)'0',
		/// <summary>
		/// 操作员
		/// </summary>
		Operator=(Byte)'1',
		/// <summary>
		/// 管理员
		/// </summary>
		SuperUser=(Byte)'2',
	};
	/// <summary>
	/// 经纪公司功能代码 CBrokerFunctionCodeType
	/// </summary>
	public enum struct EnumBrokerFunctionCodeType : Byte
	{
		/// <summary>
		/// 强制用户登出
		/// </summary>
		ForceUserLogout=(Byte)'1',
		/// <summary>
		/// 变更用户口令
		/// </summary>
		UserPasswordUpdate=(Byte)'2',
		/// <summary>
		/// 同步经纪公司数据
		/// </summary>
		SyncBrokerData=(Byte)'3',
		/// <summary>
		/// 批量同步经纪公司数据
		/// </summary>
		BachSyncBrokerData=(Byte)'4',
		/// <summary>
		/// 报单插入
		/// </summary>
		OrderInsert=(Byte)'5',
		/// <summary>
		/// 报单操作
		/// </summary>
		OrderAction=(Byte)'6',
		/// <summary>
		/// 全部查询
		/// </summary>
		AllQuery=(Byte)'7',
		/// <summary>
		/// 未知单操作
		/// </summary>
		UnkownOrderAction=(Byte)'8',
		///转托管
		DepositoryTransfer=(Byte)'9',
		///余券划转
		ExcessStockTransfer=(Byte)'A',
		/// <summary>
		/// 系统功能：登入/登出/修改密码等
		/// </summary>
		log=(Byte)'a',
		/// <summary>
		/// 基本查询：查询基础数据，如合约，交易所等常量
		/// </summary>
		BaseQry=(Byte)'b',
		/// <summary>
		/// 交易查询：如查成交，委托
		/// </summary>
		TradeQry=(Byte)'c',
		/// <summary>
		/// 交易功能：报单，撤单
		/// </summary>
		Trade=(Byte)'d',
		/// <summary>
		/// 银期转账
		/// </summary>
		Virement=(Byte)'e',
		/// <summary>
		/// 风险监控
		/// </summary>
		Risk=(Byte)'f',
		/// <summary>
		/// 查询/管理：查询会话，踢人等
		/// </summary>
		Session=(Byte)'g',
		/// <summary>
		/// 风控通知控制
		/// </summary>
		RiskNoticeCtl=(Byte)'h',
		/// <summary>
		/// 风控通知发送
		/// </summary>
		RiskNotice=(Byte)'i',
		/// <summary>
		/// 察看经纪公司资金权限
		/// </summary>
		BrokerDeposit=(Byte)'j',
		/// <summary>
		/// 资金查询
		/// </summary>
		QueryFund=(Byte)'k',
		/// <summary>
		/// 报单查询
		/// </summary>
		QueryOrder=(Byte)'l',
		/// <summary>
		/// 成交查询
		/// </summary>
		QueryTrade=(Byte)'m',
		/// <summary>
		/// 持仓查询
		/// </summary>
		QueryPosition=(Byte)'n',
		/// <summary>
		/// 行情查询
		/// </summary>
		QueryMarketData=(Byte)'o',
		/// <summary>
		/// 用户事件查询
		/// </summary>
		QueryUserEvent=(Byte)'p',
		/// <summary>
		/// 风险通知查询
		/// </summary>
		QueryRiskNotify=(Byte)'q',
		/// <summary>
		/// 出入金查询
		/// </summary>
		QueryFundChange=(Byte)'r',
		/// <summary>
		/// 投资者信息查询
		/// </summary>
		QueryInvestor=(Byte)'s',
		/// <summary>
		/// 交易编码查询
		/// </summary>
		QueryTradingCode=(Byte)'t',
		/// <summary>
		/// 强平
		/// </summary>
		ForceClose=(Byte)'u',
		/// <summary>
		/// 压力测试
		/// </summary>
		PressTest=(Byte)'v',
		/// <summary>
		/// 权益反算
		/// </summary>
		RemainCalc=(Byte)'w',
		/// <summary>
		/// 净持仓保证金指标
		/// </summary>
		NetPositionInd=(Byte)'x',
		/// <summary>
		/// 风险预算
		/// </summary>
		RiskPredict=(Byte)'y',
		/// <summary>
		/// 数据导出
		/// </summary>
		DataExport=(Byte)'z',
		/// <summary>
		/// 风控指标设置
		/// </summary>
		/*RiskTargetSetup=(Byte)'A',*/
		/// <summary>
		/// 行情预警
		/// </summary>
		MarketDataWarn=(Byte)'B',
		/// <summary>
		/// 业务通知查询
		/// </summary>
		QryBizNotice=(Byte)'C',
		/// <summary>
		/// 业务通知模板设置
		/// </summary>
		CfgBizNotice=(Byte)'D',
		/// <summary>
		/// 同步动态令牌
		/// </summary>
		SyncOTP=(Byte)'E',
		/// <summary>
		/// 发送业务通知
		/// </summary>
		SendBizNotice=(Byte)'F',
		/// <summary>
		/// 风险级别标准设置
		/// </summary>
		CfgRiskLevelStd=(Byte)'G',
		/// <summary>
		/// 交易终端应急功能
		/// </summary>
		TbCommand=(Byte)'H',
	};
	/// <summary>
	/// 账户类型 CAccountTypeType
	/// </summary>
	public enum struct EnumAccountTypeType : Byte
	{
		/// <summary>
		/// 普通账户
		/// </summary>
		Normal=(Byte)'1',
		/// <summary>
		/// 信用账户
		/// </summary>
		Credit=(Byte)'2',
		/// <summary>
		/// 衍生品账户
		/// </summary>
		Derive=(Byte)'3',
		/// <summary>
		/// 其他类型
		/// </summary>
		Other=(Byte)'4',
	};
	/// <summary>
	/// 投资者范围 CDepartmentRangeType
	/// </summary>
	public enum struct EnumDepartmentRangeType : Byte
	{
		/// <summary>
		/// 所有
		/// </summary>
		All=(Byte)'1',
		/// <summary>
		/// 组织架构
		/// </summary>
		Group=(Byte)'2',
		/// <summary>
		/// 单一投资者
		/// </summary>
		Single=(Byte)'3',
	};
	/// <summary>
	/// 客户权限类型 CUserRightTypeType
	/// </summary>
	public enum struct EnumUserRightTypeType : Byte
	{
		/// <summary>
		/// 登录
		/// </summary>
		Logon=(Byte)'1',
		/// <summary>
		/// 银期转帐
		/// </summary>
		Transfer=(Byte)'2',
		/// <summary>
		/// 邮寄结算单
		/// </summary>
		EMail=(Byte)'3',
		/// <summary>
		/// 传真结算单
		/// </summary>
		Fax=(Byte)'4',
		/// <summary>
		/// 条件单
		/// </summary>
		ConditionOrder=(Byte)'5',
	};
	/// <summary>
	/// 投机套保标志 CHedgeFlagType
	/// </summary>
	public enum struct EnumHedgeFlagType : Byte
	{
		/// <summary>
		/// 投机
		/// </summary>
		Speculation=(Byte)'1',
		/// <summary>
		/// 套保
		/// </summary>
		Hedge=(Byte)'3',
	};
	/// <summary>
	/// 买卖方向 CDirectionType
	/// </summary>
	public enum struct EnumDirectionType : Byte
	{
		/// <summary>
		/// 买
		/// </summary>
		Buy=(Byte)'0',
		/// <summary>
		/// 卖
		/// </summary>
		Sell=(Byte)'1',
		/// <summary>
		/// ETF申购
		/// </summary>
		ETFPur=(Byte)'2',
		/// <summary>
		/// ETF赎回
		/// </summary>
		ETFRed=(Byte)'3',
		/// <summary>
		/// 现金替代，只用作回报
		/// </summary>
		CashIn=(Byte)'4',
		/// <summary>
		/// 债券入库
		/// </summary>
		PledgeBondIn=(Byte)'5',
		/// <summary>
		/// 债券出库
		/// </summary>
		PledgeBondOut=(Byte)'6',
		///配股
		Rationed=(Byte) '7',
		///转托管
		DepositoryTransfer =(Byte)'8',
		///信用账户配股
		CreditRationed =(Byte)'9',
		///担保品买入
		BuyCollateral=(Byte) 'A',
		///担保品卖出
		SellCollateral =(Byte)'B',
		///担保品转入
		CollateralTransferIn=(Byte) 'C',
		///担保品转出
		CollateralTransferOut=(Byte) 'D',
		///融资买入
		MarginTrade =(Byte)'E',
		///融券卖出
		ShortSell =(Byte)'F',
		///卖券还款
		RepayMargin=(Byte) 'G',
		///买券还券
		RepayStock =(Byte)'H',
		///直接还款
		DirectRepayMargin =(Byte)'I',
		///直接还券
		DirectRepayStock =(Byte)'J',
		///余券划转
		ExcessStockTransfer=(Byte) 'K',
	};
	/// <summary>
	/// 成交类型 CTradeTypeType
	/// </summary>
	public enum struct EnumTradeTypeType : Byte
	{
		/// <summary>
		/// 普通成交
		/// </summary>
		Common=(Byte)'0',
		/// <summary>
		/// 期权执行
		/// </summary>
		OptionsExecution=(Byte)'1',
		/// <summary>
		/// OTC成交
		/// </summary>
		OTC=(Byte)'2',
		/// <summary>
		/// 期转现衍生成交
		/// </summary>
		EFPDerived=(Byte)'3',
		/// <summary>
		/// 组合衍生成交
		/// </summary>
		CombinationDerived=(Byte)'4',
		/// <summary>
		/// ETF申购
		/// </summary>
		EFTPurchase=(Byte)'5',
		/// <summary>
		/// ETF赎回
		/// </summary>
		EFTRedem=(Byte)'6',
	};
	/// <summary>
	/// 基金当天申购赎回状态 CCreationredemptionStatusType
	/// </summary>
	public enum struct EnumCreationredemptionStatusType : Byte
	{
		/// <summary>
		/// 不允许申购赎回
		/// </summary>
		Forbidden=(Byte)'0',
		/// <summary>
		/// 表示允许申购和赎回
		/// </summary>
		Allow=(Byte)'1',
		/// <summary>
		/// 允许申购、不允许赎回
		/// </summary>
		OnlyPurchase=(Byte)'2',
		/// <summary>
		/// 不允许申购、允许赎回
		/// </summary>
		OnlyRedeem=(Byte)'3',
	};
	/// <summary>
	/// ETF现金替代标志 CETFCurrenceReplaceStatusType
	/// </summary>
	public enum struct EnumETFCurrenceReplaceStatusType : Byte
	{
		/// <summary>
		/// 禁止现金替代
		/// </summary>
		Forbidden=(Byte)'0',
		/// <summary>
		/// 可以现金替代
		/// </summary>
		Allow=(Byte)'1',
		/// <summary>
		/// 必须现金替代
		/// </summary>
		Force=(Byte)'2',
	};
	/// <summary>
	/// 股本类型 CCapitalStockTypeType
	/// </summary>
	public enum struct EnumCapitalStockTypeType : Byte
	{
		/// <summary>
		/// 总通股本
		/// </summary>
		TOTALSTOCK=(Byte)'1',
		/// <summary>
		/// 流通股本
		/// </summary>
		CIRCULATION=(Byte)'2',
	};
	/// <summary>
	/// 保证金价格类型 CMarginPriceTypeType
	/// </summary>
	public enum struct EnumMarginPriceTypeType : Byte
	{
		/// <summary>
		/// 昨结算价
		/// </summary>
		PreSettlementPrice=(Byte)'1',
		/// <summary>
		/// 最新价
		/// </summary>
		SettlementPrice=(Byte)'2',
		/// <summary>
		/// 成交均价
		/// </summary>
		AveragePrice=(Byte)'3',
		/// <summary>
		/// 开仓价
		/// </summary>
		OpenPrice=(Byte)'4',
	};
	/// <summary>
	/// 盈亏算法 CAlgorithmType
	/// </summary>
	public enum struct EnumAlgorithmType : Byte
	{
		/// <summary>
		/// 浮盈浮亏都计算
		/// </summary>
		All=(Byte)'1',
		/// <summary>
		/// 浮盈不计，浮亏计
		/// </summary>
		OnlyLost=(Byte)'2',
		/// <summary>
		/// 浮盈计，浮亏不计
		/// </summary>
		OnlyGain=(Byte)'3',
		/// <summary>
		/// 浮盈浮亏都不计算
		/// </summary>
		None=(Byte)'4',
	};


	/// <summary>
	/// 是否包含平仓盈利 CIncludeCloseProfitType
	/// </summary>
	public enum struct EnumIncludeCloseProfitType : Byte
	{
		/// <summary>
		/// 包含平仓盈利
		/// </summary>
		Include=(Byte)'0',
		/// <summary>
		/// 不包含平仓盈利
		/// </summary>
		NotInclude=(Byte)'2',
	};
	/// <summary>
	/// 是否受可提比例限制 CAllWithoutTradeType
	/// </summary>
	public enum struct EnumAllWithoutTradeType : Byte
	{
		/// <summary>
		/// 不受可提比例限制
		/// </summary>
		Enable=(Byte)'0',
		/// <summary>
		/// 受可提比例限制
		/// </summary>
		Disable=(Byte)'2',
		/// <summary>
		/// 无仓不受可提比例限制
		/// </summary>
		NoHoldEnable=(Byte)'3',
	};
	/// <summary>
	/// 持仓处理算法编号 CHandlePositionAlgoIDType
	/// </summary>
	public enum struct EnumHandlePositionAlgoIDType : Byte
	{
		/// <summary>
		/// 基本
		/// </summary>
		Base=(Byte)'1',
		/// <summary>
		/// 非交易
		/// </summary>
		NoneTrade=(Byte)'4',
		/// <summary>
		/// 证券
		/// </summary>
		Stock=(Byte)'5',
	};
	/// <summary>
	/// 交易系统参数代码 CTradeParamIDType
	/// </summary>
	public enum struct EnumTradeParamIDType : Byte
	{
		/// <summary>
		/// 系统加密算法
		/// </summary>
		EncryptionStandard=(Byte)'E',
		/// <summary>
		/// 用户最大会话数
		/// </summary>
		SingleUserSessionMaxNum=(Byte)'S',
		/// <summary>
		/// 最大连续登录失败数
		/// </summary>
		LoginFailMaxNum=(Byte)'L',
		/// <summary>
		/// 是否强制认证
		/// </summary>
		IsAuthForce=(Byte)'A',

		///是否生成用户事件
		GenUserEvent =(Byte)'G',
		///起始报单本地编号
		StartOrderLocalID =(Byte)'O',
		///融资融券买券还券算法
		RepayStockAlgo =(Byte)'R',
	};
	/// <summary>
	/// 投资者范围 CInvestorRangeType
	/// </summary>
	public enum struct EnumInvestorRangeType : Byte
	{
		/// <summary>
		/// 所有
		/// </summary>
		All=(Byte)'1',
		/// <summary>
		/// 投资者组
		/// </summary>
		Group=(Byte)'2',
		/// <summary>
		/// 单一投资者
		/// </summary>
		Single=(Byte)'3',
	};
	/// <summary>
	/// 数据同步状态 CDataSyncStatusType
	/// </summary>
	public enum struct EnumDataSyncStatusType : Byte
	{
		/// <summary>
		/// 未同步
		/// </summary>
		Asynchronous=(Byte)'1',
		/// <summary>
		/// 同步中
		/// </summary>
		Synchronizing=(Byte)'2',
		/// <summary>
		/// 已同步
		/// </summary>
		Synchronized=(Byte)'3',
	};
	/// <summary>
	/// 交易所交易员连接状态 CTraderConnectStatusType
	/// </summary>
	public enum struct EnumTraderConnectStatusType : Byte
	{
		/// <summary>
		/// 没有任何连接
		/// </summary>
		NotConnected=(Byte)'1',
		/// <summary>
		/// 已经连接
		/// </summary>
		Connected=(Byte)'2',
		/// <summary>
		/// 已经发出合约查询请求
		/// </summary>
		QryInstrumentSent=(Byte)'3',
		/// <summary>
		/// 订阅私有流
		/// </summary>
		SubPrivateFlow=(Byte)'4',
	};
	/// <summary>
	/// 报单操作状态 COrderActionStatusType
	/// </summary>
	public enum struct EnumOrderActionStatusType : Byte
	{
		/// <summary>
		/// 已经提交
		/// </summary>
		Submitted=(Byte)'a',
		/// <summary>
		/// 已经接受
		/// </summary>
		Accepted=(Byte)'b',
		/// <summary>
		/// 已经被拒绝
		/// </summary>
		Rejected=(Byte)'c',
	};
	/// <summary>
	/// 报单状态 COrderStatusType
	/// </summary>
	public enum struct EnumOrderStatusType : Byte
	{
		/// <summary>
		/// 全部成交
		/// </summary>
		AllTraded=(Byte)'0',
		/// <summary>
		/// 部分成交还在队列中
		/// </summary>
		PartTradedQueueing=(Byte)'1',
		/// <summary>
		/// 部分成交不在队列中
		/// </summary>
		PartTradedNotQueueing=(Byte)'2',
		/// <summary>
		/// 未成交还在队列中
		/// </summary>
		NoTradeQueueing=(Byte)'3',
		/// <summary>
		/// 未成交不在队列中
		/// </summary>
		NoTradeNotQueueing=(Byte)'4',
		/// <summary>
		/// 撤单
		/// </summary>
		Canceled=(Byte)'5',
		/// <summary>
		/// 未知
		/// </summary>
		Unknown=(Byte)'a',
		/// <summary>
		/// 尚未触发
		/// </summary>
		NotTouched=(Byte)'b',
		/// <summary>
		/// 已触发
		/// </summary>
		Touched=(Byte)'c',
	};
	/// <summary>
	/// 报单提交状态 COrderSubmitStatusType
	/// </summary>
	public enum struct EnumOrderSubmitStatusType : Byte
	{
		/// <summary>
		/// 已经提交
		/// </summary>
		InsertSubmitted=(Byte)'0',
		/// <summary>
		/// 撤单已经提交
		/// </summary>
		CancelSubmitted=(Byte)'1',
		/// <summary>
		/// 修改已经提交
		/// </summary>
		ModifySubmitted=(Byte)'2',
		/// <summary>
		/// 已经接受
		/// </summary>
		Accepted=(Byte)'3',
		/// <summary>
		/// 报单已经被拒绝
		/// </summary>
		InsertRejected=(Byte)'4',
		/// <summary>
		/// 撤单已经被拒绝
		/// </summary>
		CancelRejected=(Byte)'5',
		/// <summary>
		/// 改单已经被拒绝
		/// </summary>
		ModifyRejected=(Byte)'6',
	};
	/// <summary>
	/// 持仓日期 CPositionDateType
	/// </summary>
	public enum struct EnumPositionDateType : Byte
	{
		/// <summary>
		/// 今日持仓
		/// </summary>
		Today=(Byte)'1',
		/// <summary>
		/// 历史持仓
		/// </summary>
		History=(Byte)'2',
	};
	/// <summary>
	/// 交易角色 CTradingRoleType
	/// </summary>
	public enum struct EnumTradingRoleType : Byte
	{
		/// <summary>
		/// 代理
		/// </summary>
		Broker=(Byte)'1',
		/// <summary>
		/// 自营
		/// </summary>
		Host=(Byte)'2',
		/// <summary>
		/// 做市商
		/// </summary>
		Maker=(Byte)'3',
	};
	/// <summary>
	/// 持仓多空方向 CPosiDirectionType
	/// </summary>
	public enum struct EnumPosiDirectionType : Byte
	{
		/// <summary>
		/// 净
		/// </summary>
		Net=(Byte)'1',
		/// <summary>
		/// 多头
		/// </summary>
		Long=(Byte)'2',
		/// <summary>
		/// 空头
		/// </summary>
		Short=(Byte)'3',
		/// <summary>
		/// 备兑
		/// </summary>
		Covered=(Byte)'4',
	};
	/// <summary>
	/// 报单价格条件 COrderPriceTypeType
	/// </summary>
	public enum struct EnumOrderPriceTypeType : Byte
	{
		/// <summary>
		///即时成交剩余撤销市价单
		/// </summary>
		AnyPrice=(Byte)'1',
		/// <summary>
		/// 限价
		/// </summary>
		LimitPrice=(Byte)'2',
		///最优五档即时成交剩余撤销市价单
		BestPrice=(Byte)'3',
		///最优五档即时成交剩余转限价市价单
		BestLimitPrice=(Byte)'4',
		///全部成交或撤销市价单
		AllPrice=(Byte)'5',
		///本方最优价格市价单
		ForwardBestPrice=(Byte)'6',
		///对方最优价格市价单
		ReverseBestPrice=(Byte)'7',
		/// <summary>
		/// 激活A股网络密码服务代码
		/// </summary>
		ActiveANetPassSvrCode=(Byte)'G',
		/// <summary>
		/// 注销A股网络密码服务代码
		/// </summary>
		InactiveANetPassSvrCode=(Byte)'H',
		/// <summary>
		/// 激活B股网络密码服务代码
		/// </summary>
		ActiveBNetPassSvrCode=(Byte)'I',
		/// <summary>
		/// 注销B股网络密码服务代码
		/// </summary>
		InactiveBNetPassSvrCode=(Byte)'J',
		/// <summary>
		/// 回购注销
		/// </summary>
		Repurchase=(Byte)'K',
		/// <summary>
		/// 指定撤销
		/// </summary>
		DesignatedCancel=(Byte)'L',
		/// <summary>
		/// 指定登记
		/// </summary>
		Designated=(Byte)'M',
		/// <summary>
		/// 证券参与申购
		/// </summary>
		SubscribingShares=(Byte)'N',
		/// <summary>
		/// 证券参与配股
		/// </summary>
		Split=(Byte)'O',
		/// <summary>
		/// 要约收购登记
		/// </summary>
		TenderOffer=(Byte)'P',
		/// <summary>
		/// 要约收购撤销
		/// </summary>
		TenderOfferCancel=(Byte)'Q',
		/// <summary>
		/// 证券投票
		/// </summary>
		Ballot=(Byte)'R',
		/// <summary>
		/// 可转债转换登记
		/// </summary>
		ConvertibleBondsConvet=(Byte)'S',
		/// <summary>
		/// 可转债回售登记
		/// </summary>
		ConvertibleBondsRepurchase=(Byte)'T',
		/// <summary>
		/// 权证行权
		/// </summary>
		Exercise=(Byte)'U',
		/// <summary>
		/// 开放式基金申购
		/// </summary>
		PurchasingFunds=(Byte)'V',
		/// <summary>
		/// 开放式基金赎回
		/// </summary>
		RedemingFunds=(Byte)'W',
		/// <summary>
		/// 开放式基金认购
		/// </summary>
		SubscribingFunds=(Byte)'X',
		/// <summary>
		/// 开放式基金转托管转出
		/// </summary>
		LOFIssue=(Byte)'Y',
		/// <summary>
		/// 开放式基金设置分红方式
		/// </summary>
		LOFSetBonusType=(Byte)'Z',
		/// <summary>
		/// 开放式基金转换为其他基金
		/// </summary>
		LOFConvert=(Byte)'a',
		/// <summary>
		/// 债券入库
		/// </summary>
		DebentureStockIn=(Byte)'b',
		/// <summary>
		/// 债券出库
		/// </summary>
		DebentureStockOut=(Byte)'c',
		/// <summary>
		/// ETF申购
		/// </summary>
		PurchasesETF =(Byte)'d',
		/// <summary>
		/// ETF赎回
		/// </summary>
		RedeemETF=(Byte)'e',
	};
	/// <summary>
	/// 开平标志 COffsetFlagType
	/// </summary>
	public enum struct EnumOffsetFlagType : Byte
	{
		/// <summary>
		/// 开仓
		/// </summary>
		Open=(Byte)'0',
		/// <summary>
		/// 平仓
		/// </summary>
		Close=(Byte)'1',
		/// <summary>
		/// 强平
		/// </summary>
		ForceClose=(Byte)'2',
		/// <summary>
		/// 平今
		/// </summary>
		CloseToday=(Byte)'3',
		/// <summary>
		/// 平昨
		/// </summary>
		CloseYesterday=(Byte)'4',
		/// <summary>
		/// 强减
		/// </summary>
		ForceOff=(Byte)'5',
		/// <summary>
		/// 本地强平
		/// </summary>
		LocalForceClose=(Byte)'6',
		/// <summary>
		/// 行权
		/// </summary>
		Execute=(Byte)'7',
	};
	/// <summary>
	/// 强平原因 CForceCloseReasonType
	/// </summary>
	public enum struct EnumForceCloseReasonType : Byte
	{
		/// <summary>
		/// 非强平
		/// </summary>
		NotForceClose=(Byte)'0',
		/// <summary>
		/// 资金不足
		/// </summary>
		LackDeposit=(Byte)'1',
		/// <summary>
		/// 客户超仓
		/// </summary>
		ClientOverPositionLimit=(Byte)'2',
		/// <summary>
		/// 会员超仓
		/// </summary>
		MemberOverPositionLimit=(Byte)'3',
		/// <summary>
		/// 持仓非整数倍
		/// </summary>
		NotMultiple=(Byte)'4',
		/// <summary>
		/// 违规
		/// </summary>
		Violation=(Byte)'5',
		/// <summary>
		/// 其它
		/// </summary>
		Other=(Byte)'6',
		/// <summary>
		/// 自然人临近交割
		/// </summary>
		PersonDeliv=(Byte)'7',
	};
	/// <summary>
	/// 报单类型 COrderTypeType
	/// </summary>
	public enum struct EnumOrderTypeType : Byte
	{
		/// <summary>
		/// 正常
		/// </summary>
		Normal=(Byte)'0',
		/// <summary>
		/// 报价衍生
		/// </summary>
		DeriveFromQuote=(Byte)'1',
		/// <summary>
		/// 组合衍生
		/// </summary>
		DeriveFromCombination=(Byte)'2',
		/// <summary>
		/// 组合报单
		/// </summary>
		Combination=(Byte)'3',
		/// <summary>
		/// 条件单
		/// </summary>
		ConditionalOrder=(Byte)'4',
		/// <summary>
		/// 互换单
		/// </summary>
		Swap=(Byte)'5',
	};
	/// <summary>
	/// 有效期类型 CTimeConditionType
	/// </summary>
	public enum struct EnumTimeConditionType : Byte
	{
		/// <summary>
		/// 立即完成，否则撤销
		/// </summary>
		IOC=(Byte)'1',
		/// <summary>
		/// 本节有效
		/// </summary>
		GFS=(Byte)'2',
		/// <summary>
		/// 当日有效
		/// </summary>
		GFD=(Byte)'3',
		/// <summary>
		/// 指定日期前有效
		/// </summary>
		GTD=(Byte)'4',
		/// <summary>
		/// 撤销前有效
		/// </summary>
		GTC=(Byte)'5',
		/// <summary>
		/// 集合竞价有效
		/// </summary>
		GFA=(Byte)'6',
	};
	/// <summary>
	/// 成交量类型 CVolumeConditionType
	/// </summary>
	public enum struct EnumVolumeConditionType : Byte
	{
		/// <summary>
		/// 任何数量
		/// </summary>
		AV=(Byte)'1',
		/// <summary>
		/// 最小数量
		/// </summary>
		MV=(Byte)'2',
		/// <summary>
		/// 全部数量
		/// </summary>
		CV=(Byte)'3',
	};
	/// <summary>
	/// 触发条件 CContingentConditionType
	/// </summary>
	public enum struct EnumContingentConditionType : Byte
	{
		/// <summary>
		/// 立即
		/// </summary>
		Immediately=(Byte)'1',
		/// <summary>
		/// 止损
		/// </summary>
		Touch=(Byte)'2',
		/// <summary>
		/// 止赢
		/// </summary>
		TouchProfit=(Byte)'3',
		/// <summary>
		/// 预埋单
		/// </summary>
		ParkedOrder=(Byte)'4',
		/// <summary>
		/// 最新价大于条件价
		/// </summary>
		LastPriceGreaterThanStopPrice=(Byte)'5',
		/// <summary>
		/// 最新价大于等于条件价
		/// </summary>
		LastPriceGreaterEqualStopPrice=(Byte)'6',
		/// <summary>
		/// 最新价小于条件价
		/// </summary>
		LastPriceLesserThanStopPrice=(Byte)'7',
		/// <summary>
		/// 最新价小于等于条件价
		/// </summary>
		LastPriceLesserEqualStopPrice=(Byte)'8',
		/// <summary>
		/// 卖一价大于条件价
		/// </summary>
		AskPriceGreaterThanStopPrice=(Byte)'9',
		/// <summary>
		/// 卖一价大于等于条件价
		/// </summary>
		AskPriceGreaterEqualStopPrice=(Byte)'A',
		/// <summary>
		/// 卖一价小于条件价
		/// </summary>
		AskPriceLesserThanStopPrice=(Byte)'B',
		/// <summary>
		/// 卖一价小于等于条件价
		/// </summary>
		AskPriceLesserEqualStopPrice=(Byte)'C',
		/// <summary>
		/// 买一价大于条件价
		/// </summary>
		BidPriceGreaterThanStopPrice=(Byte)'D',
		/// <summary>
		/// 买一价大于等于条件价
		/// </summary>
		BidPriceGreaterEqualStopPrice=(Byte)'E',
		/// <summary>
		/// 买一价小于条件价
		/// </summary>
		BidPriceLesserThanStopPrice=(Byte)'F',
		/// <summary>
		/// 买一价小于等于条件价
		/// </summary>
		BidPriceLesserEqualStopPrice=(Byte)'H',
	};
	/// <summary>
	/// 操作标志 CActionFlagType
	/// </summary>
	public enum struct EnumActionFlagType : Byte
	{
		/// <summary>
		/// 删除
		/// </summary>
		Delete=(Byte)'0',
		/// <summary>
		/// 修改
		/// </summary>
		Modify=(Byte)'3',
	};
	/// <summary>
	/// 交易权限 CTradingRightType
	/// </summary>
	public enum struct EnumTradingRightType : Byte
	{
		/// <summary>
		/// 可以交易
		/// </summary>
		Allow=(Byte)'0',
		/// <summary>
		/// 不能交易
		/// </summary>
		Forbidden=(Byte)'2',
	};
	/// <summary>
	/// 报单来源 COrderSourceType
	/// </summary>
	public enum struct EnumOrderSourceType : Byte
	{
		/// <summary>
		/// 来自参与者
		/// </summary>
		Participant=(Byte)'0',
		/// <summary>
		/// 来自管理员
		/// </summary>
		Administrator=(Byte)'1',
	};
	/// <summary>
	/// 成交价来源 CPriceSourceType
	/// </summary>
	public enum struct EnumPriceSourceType : Byte
	{
		/// <summary>
		/// 前成交价
		/// </summary>
		LastPrice=(Byte)'0',
		/// <summary>
		/// 买委托价
		/// </summary>
		Buy=(Byte)'1',
		/// <summary>
		/// 卖委托价
		/// </summary>
		Sell=(Byte)'2',
	};
	/// <summary>
	/// 用户事件类型 CUserEventTypeType
	/// </summary>
	public enum struct EnumUserEventTypeType : Byte
	{
		/// <summary>
		/// 登录
		/// </summary>
		Login=(Byte)'1',
		/// <summary>
		/// 登出
		/// </summary>
		Logout=(Byte)'2',
		/// <summary>
		/// 交易成功
		/// </summary>
		Trading=(Byte)'3',
		/// <summary>
		/// 交易失败
		/// </summary>
		TradingError=(Byte)'4',
		/// <summary>
		/// 修改密码
		/// </summary>
		UpdatePassword=(Byte)'5',
		/// <summary>
		/// 客户端认证
		/// </summary>
		Authenticate=(Byte)'6',
		/// <summary>
		/// 其他
		/// </summary>
		Other=(Byte)'9',
	};
	/// <summary>
	/// 动态令牌类型 COTPTypeType
	/// </summary>
	public enum struct EnumOTPTypeType : Byte
	{
		/// <summary>
		/// 无动态令牌
		/// </summary>
		NONE=(Byte)'0',
		/// <summary>
		/// 时间令牌
		/// </summary>
		TOTP=(Byte)'1',
	};
	/// <summary>
	/// 成交来源 CTradeSourceType
	/// </summary>
	public enum struct EnumTradeSourceType : Byte
	{
		/// <summary>
		/// 来自交易所普通回报
		/// </summary>
		NORMAL=(Byte)'0',
		/// <summary>
		/// 来自查询
		/// </summary>
		QUERY=(Byte)'1',
	};
	/// <summary>
	/// 股票权限分类 CInstrumentRangeType
	/// </summary>
	public enum struct EnumInstrumentRangeType : Byte
	{
		/// <summary>
		/// 所有
		/// </summary>
		All=(Byte)'1',
		/// <summary>
		/// 产品
		/// </summary>
		Product=(Byte)'2',
		/// <summary>
		/// 股票权限模版
		/// </summary>
		Model=(Byte)'3',
		/// <summary>
		/// 股票
		/// </summary>
		Stock=(Byte)'4',
		/// <summary>
		/// 市场
		/// </summary>
		Market=(Byte)'5',
	};
	/// <summary>
	/// 证券交易类型 CStockTradeTypeType
	/// </summary>
	public enum struct EnumStockTradeTypeType : Byte
	{
		/// <summary>
		/// 可交易证券
		/// </summary>
		Stock=(Byte)'0',
		/// <summary>
		/// 买入网络密码服务
		/// </summary>
		BuyNetService=(Byte)'1',
		/// <summary>
		/// 回购注销
		/// </summary>
		CancelRepurchase=(Byte)'2',
		/// <summary>
		/// 指定撤销
		/// </summary>
		CancelRegister=(Byte)'3',
		/// <summary>
		/// 指定登记
		/// </summary>
		Register=(Byte)'4',
		/// <summary>
		/// 买入发行申购
		/// </summary>
		PurchaseIssue=(Byte)'5',
		/// <summary>
		/// 卖出配股
		/// </summary>
		Allotment=(Byte)'6',
		/// <summary>
		/// 卖出要约收购
		/// </summary>
		SellTender=(Byte)'7',
		/// <summary>
		/// 买入要约收购
		/// </summary>
		BuyTender=(Byte)'8',
		/// <summary>
		/// 网上投票
		/// </summary>
		NetVote=(Byte)'9',
		/// <summary>
		/// 卖出可转债回售
		/// </summary>
		SellConvertibleBonds=(Byte)'a',
		/// <summary>
		/// 权证行权代码
		/// </summary>
		OptionExecute=(Byte)'b',
		/// <summary>
		/// 开放式基金申购
		/// </summary>
		PurchaseOF=(Byte)'c',
		/// <summary>
		/// 开放式基金赎回
		/// </summary>
		RedeemOF=(Byte)'d',
		/// <summary>
		/// 开放式基金认购
		/// </summary>
		SubscribeOF=(Byte)'e',
		/// <summary>
		/// 开放式基金转托管转出
		/// </summary>
		OFCustodianTranfer=(Byte)'f',
		/// <summary>
		/// 开放式基金分红设置
		/// </summary>
		OFDividendConfig =(Byte)'g',
		/// <summary>
		/// 开放式基金转成其他基金
		/// </summary>
		OFTransfer=(Byte)'h',
		/// <summary>
		/// 债券入库
		/// </summary>
		BondsIn=(Byte)'i',
		/// <summary>
		/// 债券出库
		/// </summary>
		BondsOut=(Byte)'j',
		/// <summary>
		/// EFT申购
		/// </summary>
		PurchaseETF=(Byte)'k',
		/// <summary>
		/// EFT赎回
		/// </summary>
		RedeemETF=(Byte)'l',
		/// <summary>
		/// 可转债回售登记
		/// </summary>
		ConvertibleRegister=(Byte)'m',
	};
	/// <summary>
	/// 资金处理算法编号 CHandleTradingAccountAlgoIDType
	/// </summary>
	public enum struct EnumHandleTradingAccountAlgoIDType : Byte
	{
		/// <summary>
		/// 基本
		/// </summary>
		Base=(Byte)'1',
	};
	/// <summary>
	/// 响应信息
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcRspInfoField
	{
		/// <summary>
		/// 错误代码
		/// </summary>
		int ErrorID;
		/// <summary>
		/// 错误信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ ErrorMsg;
	};
	/// <summary>
	/// 交易所
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcExchangeField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 交易所名称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ExchangeName;
		/// <summary>
		/// 交易所属性
		/// </summary>
		EnumExchangePropertyType ExchangeProperty;
	};
	/// <summary>
	/// 产品
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcProductField
	{
		/// <summary>
		/// 产品代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ProductID;
		/// <summary>
		/// 产品名称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ ProductName;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 产品类型
		/// </summary>
		EnumProductClassType ProductClass;
		/// <summary>
		/// 合约数量乘数
		/// </summary>
		int VolumeMultiple;
		/// <summary>
		/// 最小变动价位
		/// </summary>
		double PriceTick;
		/// <summary>
		/// 市价单最大下单量
		/// </summary>
		int MaxMarketOrderVolume;
		/// <summary>
		/// 市价单最小下单量
		/// </summary>
		int MinMarketOrderVolume;
		/// <summary>
		/// 限价单最大下单量
		/// </summary>
		int MaxLimitOrderVolume;
		/// <summary>
		/// 限价单最小下单量
		/// </summary>
		int MinLimitOrderVolume;
		/// <summary>
		/// 持仓类型
		/// </summary>
		EnumPositionTypeType PositionType;
		/// <summary>
		/// 持仓日期类型
		/// </summary>
		EnumPositionDateTypeType PositionDateType;
		/// <summary>
		/// ETF最小交易单位
		/// </summary>
		int EFTMinTradeVolume;
	};
	/// <summary>
	/// 合约
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInstrumentField
	{
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 合约名称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ InstrumentName;
		/// <summary>
		/// 合约在交易所的代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ExchangeInstID;
		/// <summary>
		/// 产品代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ProductID;
		/// <summary>
		/// 产品类型
		/// </summary>
		EnumProductClassType ProductClass;
		/// <summary>
		/// 交割年份
		/// </summary>
		int DeliveryYear;
		/// <summary>
		/// 交割月
		/// </summary>
		int DeliveryMonth;
		/// <summary>
		/// 市价单最大下单量
		/// </summary>
		int MaxMarketOrderVolume;
		/// <summary>
		/// 市价单最小下单量
		/// </summary>
		int MinMarketOrderVolume;
		/// <summary>
		/// 限价单最大下单量
		/// </summary>
		int MaxLimitOrderVolume;
		/// <summary>
		/// 限价单最小下单量
		/// </summary>
		int MinLimitOrderVolume;
		/// <summary>
		/// 合约数量乘数
		/// </summary>
		int VolumeMultiple;
		/// <summary>
		/// 最小变动价位
		/// </summary>
		double PriceTick;
		/// <summary>
		/// 创建日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ CreateDate;
		/// <summary>
		/// 上市日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ OpenDate;
		/// <summary>
		/// 到期日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExpireDate;
		/// <summary>
		/// 开始交割日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ StartDelivDate;
		/// <summary>
		/// 结束交割日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ EndDelivDate;
		/// <summary>
		/// 合约生命周期状态
		/// </summary>
		EnumInstLifePhaseType InstLifePhase;
		/// <summary>
		/// 当前是否交易
		/// </summary>
		int IsTrading;
		/// <summary>
		/// 持仓类型
		/// </summary>
		EnumPositionTypeType PositionType;
		/// <summary>
		/// 报单能否撤单
		/// </summary>
		int OrderCanBeWithdraw;
		/// <summary>
		/// 最小买下单单位
		/// </summary>
		int MinBuyVolume;
		/// <summary>
		/// 最小卖下单单位
		/// </summary>
		int MinSellVolume;
		/// <summary>
		/// 股票权限模版代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ RightModelID;
		/// <summary>
		/// 持仓交易类型
		/// </summary>
		EnumPosTradeTypeType PosTradeType;
		/// <summary>
		/// 市场代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ MarketID;
		/// <summary>
		/// 期权执行价格
		/// </summary>
		double ExecPrice;
		/// <summary>
		/// 标的物前收盘
		/// </summary>
		double UnderlyingPreclosPrice;
		/// <summary>
		/// Param1
		/// </summary>
		double OptionParam1;
		/// <summary>
		/// Param2
		/// </summary>
		double OptionParam2;
		/// <summary>
		/// UnitMargin
		/// </summary>
		double UnitMargin;
	};
	/// <summary>
	/// 交易所交易员
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcTraderField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ Password;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 初始本地报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ StartOrderLocalID;
	};
	/// <summary>
	/// 经纪公司
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcBrokerField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 经纪公司简称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ BrokerAbbr;
		/// <summary>
		/// 经纪公司名称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ BrokerName;
		/// <summary>
		/// 是否活跃
		/// </summary>
		int IsActive;
	};
	/// <summary>
	/// 会员编码和经纪公司编码对照表
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcPartBrokerField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 是否活跃
		/// </summary>
		int IsActive;
	};
	/// <summary>
	/// 投资者
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInvestorField
	{
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者分组代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorGroupID;
		/// <summary>
		/// 投资者名称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ InvestorName;
		/// <summary>
		/// 证件类型
		/// </summary>
		EnumIdCardTypeType IdentifiedCardType;
		/// <summary>
		/// 证件号码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 51)]
		String^ IdentifiedCardNo;
		/// <summary>
		/// 是否活跃
		/// </summary>
		int IsActive;
		/// <summary>
		/// 上海营业部编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ SHBranchID;
		/// <summary>
		/// 深圳营业部编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ SZBranchID;
		/// <summary>
		/// 投资者所有资产
		/// </summary>
		double TotalBalance;
	};
	/// <summary>
	/// 交易编码
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcTradingCodeField
	{
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 客户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ ClientID;
		/// <summary>
		/// 是否活跃
		/// </summary>
		int IsActive;
		/// <summary>
		/// AccountID
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
		/// <summary>
		/// 交易单元号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ PBU;
		/// <summary>
		/// ClientType
		/// </summary>
		EnumClientTypeType ClientType;
	};
	/// <summary>
	/// 管理用户
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcSuperUserField
	{
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 用户名称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ UserName;
		/// <summary>
		/// 密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ Password;
		/// <summary>
		/// 是否活跃
		/// </summary>
		int IsActive;
	};
	/// <summary>
	/// 管理用户功能权限
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcSuperUserFunctionField
	{
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 功能代码
		/// </summary>
		EnumFunctionCodeType FunctionCode;
	};
	/// <summary>
	/// 经纪公司用户
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcBrokerUserField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 用户名称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ UserName;
		/// <summary>
		/// 用户类型
		/// </summary>
		EnumUserTypeType UserType;
		/// <summary>
		/// 是否活跃
		/// </summary>
		int IsActive;
		/// <summary>
		/// 是否使用令牌
		/// </summary>
		int IsUsingOTP;
	};
	/// <summary>
	/// 经纪公司用户功能权限
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcBrokerUserFunctionField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 经纪公司功能代码
		/// </summary>
		EnumBrokerFunctionCodeType BrokerFunctionCode;
	};
	/// <summary>
	/// 资金账户
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcTradingAccountField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者帐号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
		/// <summary>
		/// 上次质押金额
		/// </summary>
		double PreMortgage;
		/// <summary>
		/// 上次信用额度
		/// </summary>
		double PreCredit;
		/// <summary>
		/// 上次存款额
		/// </summary>
		double PreDeposit;
		/// <summary>
		/// 上次结算准备金
		/// </summary>
		double PreBalance;
		/// <summary>
		/// 上次占用的保证金
		/// </summary>
		double PreMargin;
		/// <summary>
		/// 利息基数
		/// </summary>
		double InterestBase;
		/// <summary>
		/// 利息收入
		/// </summary>
		double Interest;
		/// <summary>
		/// 入金金额
		/// </summary>
		double Deposit;
		/// <summary>
		/// 出金金额
		/// </summary>
		double Withdraw;
		/// <summary>
		/// 冻结的保证金
		/// </summary>
		double FrozenMargin;
		/// <summary>
		/// 冻结的资金
		/// </summary>
		double FrozenCash;
		/// <summary>
		/// 冻结的手续费
		/// </summary>
		double FrozenCommission;
		/// <summary>
		/// 当前保证金总额
		/// </summary>
		double CurrMargin;
		/// <summary>
		/// 维持保证金
		/// </summary>
		double MaintainMargin;
		/// <summary>
		/// 资金差额
		/// </summary>
		double CashIn;
		/// <summary>
		/// 手续费
		/// </summary>
		double Commission;
		/// <summary>
		/// 期货结算准备金
		/// </summary>
		double Balance;
		/// <summary>
		/// 现金
		/// </summary>
		double Available;
		/// <summary>
		/// 可取资金
		/// </summary>
		double WithdrawQuota;
		/// <summary>
		/// 基本准备金
		/// </summary>
		double Reserve;
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 结算编号
		/// </summary>
		int SettlementID;
		/// <summary>
		/// 信用额度
		/// </summary>
		double Credit;
		/// <summary>
		/// 质押金额
		/// </summary>
		double Mortgage;
		/// <summary>
		/// 交易所保证金
		/// </summary>
		double ExchangeMargin;
		/// <summary>
		/// 投资者交割保证金
		/// </summary>
		double DeliveryMargin;
		/// <summary>
		/// 交易所交割保证金
		/// </summary>
		double ExchangeDeliveryMargin;
		/// <summary>
		/// 冻结的过户费
		/// </summary>
		double FrozenTransferFee;
		/// <summary>
		/// 冻结的印花税
		/// </summary>
		double FrozenStampTax;
		/// <summary>
		/// 过户费
		/// </summary>
		double TransferFee;
		/// <summary>
		/// 印花税
		/// </summary>
		double StampTax;
		/// <summary>
		/// 折算金额
		/// </summary>
		double ConversionAmount;
		/// <summary>
		/// 授信额度
		/// </summary>
		double CreditAmount;
		/// <summary>
		/// 证券总价值
		/// </summary>
		double StockValue;
		/// <summary>
		/// 国债回购占用资金
		/// </summary>
		double BondRepurchaseAmount;
		/// <summary>
		/// 国债逆回购占用资金
		/// </summary>
		double ReverseRepurchaseAmount;
		/// <summary>
		/// 币种
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 4)]
		String^ CurrencyCode;
		/// <summary>
		/// 账户类型
		/// </summary>
		EnumAccountTypeType AccountType;
		/// <summary>
		/// 买入期权占用资金
		/// </summary>
		double OptionBuyAmount;
		/// <summary>
		/// 买入期权冻结占用资金
		/// </summary>
		double OptionBuyFrozenAmount;
	};
	/// <summary>
	/// 禁止登录用户
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcLoginForbiddenUserField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
	};
	/// <summary>
	/// 深度行情
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcDepthMarketDataField
	{
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 合约在交易所的代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ExchangeInstID;
		/// <summary>
		/// 最新价
		/// </summary>
		double LastPrice;
		/// <summary>
		/// 上次结算价
		/// </summary>
		double PreSettlementPrice;
		/// <summary>
		/// 昨收盘
		/// </summary>
		double PreClosePrice;
		/// <summary>
		/// 昨持仓量
		/// </summary>
		double PreOpenInterest;
		/// <summary>
		/// 今开盘
		/// </summary>
		double OpenPrice;
		/// <summary>
		/// 最高价
		/// </summary>
		double HighestPrice;
		/// <summary>
		/// 最低价
		/// </summary>
		double LowestPrice;
		/// <summary>
		/// 数量
		/// </summary>
		int Volume;
		/// <summary>
		/// 成交金额
		/// </summary>
		double Turnover;
		/// <summary>
		/// 持仓量
		/// </summary>
		double OpenInterest;
		/// <summary>
		/// 今收盘
		/// </summary>
		double ClosePrice;
		/// <summary>
		/// 本次结算价
		/// </summary>
		double SettlementPrice;
		/// <summary>
		/// 涨停板价
		/// </summary>
		double UpperLimitPrice;
		/// <summary>
		/// 跌停板价
		/// </summary>
		double LowerLimitPrice;
		/// <summary>
		/// 昨虚实度
		/// </summary>
		double PreDelta;
		/// <summary>
		/// 今虚实度
		/// </summary>
		double CurrDelta;
		/// <summary>
		/// 最后修改时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ UpdateTime;
		/// <summary>
		/// 最后修改毫秒
		/// </summary>
		int UpdateMillisec;
		/// <summary>
		/// 申买价一
		/// </summary>
		double BidPrice1;
		/// <summary>
		/// 申买量一
		/// </summary>
		int BidVolume1;
		/// <summary>
		/// 申卖价一
		/// </summary>
		double AskPrice1;
		/// <summary>
		/// 申卖量一
		/// </summary>
		int AskVolume1;
		/// <summary>
		/// 申买价二
		/// </summary>
		double BidPrice2;
		/// <summary>
		/// 申买量二
		/// </summary>
		int BidVolume2;
		/// <summary>
		/// 申卖价二
		/// </summary>
		double AskPrice2;
		/// <summary>
		/// 申卖量二
		/// </summary>
		int AskVolume2;
		/// <summary>
		/// 申买价三
		/// </summary>
		double BidPrice3;
		/// <summary>
		/// 申买量三
		/// </summary>
		int BidVolume3;
		/// <summary>
		/// 申卖价三
		/// </summary>
		double AskPrice3;
		/// <summary>
		/// 申卖量三
		/// </summary>
		int AskVolume3;
		/// <summary>
		/// 申买价四
		/// </summary>
		double BidPrice4;
		/// <summary>
		/// 申买量四
		/// </summary>
		int BidVolume4;
		/// <summary>
		/// 申卖价四
		/// </summary>
		double AskPrice4;
		/// <summary>
		/// 申卖量四
		/// </summary>
		int AskVolume4;
		/// <summary>
		/// 申买价五
		/// </summary>
		double BidPrice5;
		/// <summary>
		/// 申买量五
		/// </summary>
		int BidVolume5;
		/// <summary>
		/// 申卖价五
		/// </summary>
		double AskPrice5;
		/// <summary>
		/// 申卖量五
		/// </summary>
		int AskVolume5;
		/// <summary>
		/// 当日均价
		/// </summary>
		double AveragePrice;
		/// <summary>
		/// 业务日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ActionDay;
	};
	/// <summary>
	/// 投资者合约交易权限
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInstrumentTradingRightField
	{
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 投资者范围
		/// </summary>
		EnumInvestorRangeType InvestorRange;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 买卖
		/// </summary>
		EnumDirectionType Direction;
		/// <summary>
		/// 交易权限
		/// </summary>
		EnumTradingRightType TradingRight;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 股票权限分类
		/// </summary>
		EnumInstrumentRangeType InstrumentRange;
	};
	/// <summary>
	/// 投资者持仓明细
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInvestorPositionDetailField
	{
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 投机套保标志
		/// </summary>
		EnumHedgeFlagType HedgeFlag;
		/// <summary>
		/// 买卖
		/// </summary>
		EnumDirectionType Direction;
		/// <summary>
		/// 开仓日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ OpenDate;
		/// <summary>
		/// 成交编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ TradeID;
		/// <summary>
		/// 数量
		/// </summary>
		int Volume;
		/// <summary>
		/// 开仓价
		/// </summary>
		double OpenPrice;
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 结算编号
		/// </summary>
		int SettlementID;
		/// <summary>
		/// 成交类型
		/// </summary>
		EnumTradeTypeType TradeType;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 投资者保证金
		/// </summary>
		double Margin;
		/// <summary>
		/// 交易所保证金
		/// </summary>
		double ExchMargin;
		/// <summary>
		/// 昨结算价
		/// </summary>
		double LastSettlementPrice;
		/// <summary>
		/// 结算价
		/// </summary>
		double SettlementPrice;
		/// <summary>
		/// 平仓量
		/// </summary>
		int CloseVolume;
		/// <summary>
		/// 平仓金额
		/// </summary>
		double CloseAmount;
		/// <summary>
		/// 过户费
		/// </summary>
		double TransferFee;
		/// <summary>
		/// 印花税
		/// </summary>
		double StampTax;
		/// <summary>
		/// 手续费
		/// </summary>
		double Commission;
		/// <summary>
		/// AccountID
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
		/// <summary>
		/// 期权是否看涨期权
		/// </summary>
		int IsCall;
		/// <summary>
		/// 标的物合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ UnderLyingInstrumentID;
	};
	/// <summary>
	/// 债券利息
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcBondInterestField
	{
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 利息
		/// </summary>
		double Interest;
	};
	/// <summary>
	/// 交易所交易员报盘机
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcTraderOfferField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ Password;
		/// <summary>
		/// 本地报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderLocalID;
		/// <summary>
		/// 交易所交易员连接状态
		/// </summary>
		EnumTraderConnectStatusType TraderConnectStatus;
		/// <summary>
		/// 发出连接请求的日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ConnectRequestDate;
		/// <summary>
		/// 发出连接请求的时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ConnectRequestTime;
		/// <summary>
		/// 上次报告日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ LastReportDate;
		/// <summary>
		/// 上次报告时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ LastReportTime;
		/// <summary>
		/// 完成连接日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ConnectDate;
		/// <summary>
		/// 完成连接时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ConnectTime;
		/// <summary>
		/// 启动日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ StartDate;
		/// <summary>
		/// 启动时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ StartTime;
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
	};
	/// <summary>
	/// 交易所行情报盘机
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMDTraderOfferField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ Password;
		/// <summary>
		/// 本地报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderLocalID;
		/// <summary>
		/// 交易所交易员连接状态
		/// </summary>
		EnumTraderConnectStatusType TraderConnectStatus;
		/// <summary>
		/// 发出连接请求的日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ConnectRequestDate;
		/// <summary>
		/// 发出连接请求的时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ConnectRequestTime;
		/// <summary>
		/// 上次报告日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ LastReportDate;
		/// <summary>
		/// 上次报告时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ LastReportTime;
		/// <summary>
		/// 完成连接日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ConnectDate;
		/// <summary>
		/// 完成连接时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ConnectTime;
		/// <summary>
		/// 启动日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ StartDate;
		/// <summary>
		/// 启动时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ StartTime;
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
	};
	/// <summary>
	/// 前置状态
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcFrontStatusField
	{
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
		/// <summary>
		/// 上次报告日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ LastReportDate;
		/// <summary>
		/// 上次报告时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ LastReportTime;
		/// <summary>
		/// 是否活跃
		/// </summary>
		int IsActive;
	};
	/// <summary>
	/// 用户会话
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcUserSessionField
	{
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
		/// <summary>
		/// 会话编号
		/// </summary>
		int SessionID;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 登录日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ LoginDate;
		/// <summary>
		/// 登录时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ LoginTime;
		/// <summary>
		/// IP地址
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ IPAddress;
		/// <summary>
		/// 用户端产品信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ UserProductInfo;
		/// <summary>
		/// 接口端产品信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ InterfaceProductInfo;
		/// <summary>
		/// 协议信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ProtocolInfo;
		/// <summary>
		/// Mac地址
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ MacAddress;
	};
	/// <summary>
	/// 报单
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcOrderField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 报单引用
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderRef;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 报单价格条件
		/// </summary>
		EnumOrderPriceTypeType OrderPriceType;
		/// <summary>
		/// 买卖方向
		/// </summary>
		EnumDirectionType Direction;
		/// <summary>
		/// 组合开平标志
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 5)]
		String^ CombOffsetFlag;
		/// <summary>
		/// 组合投机套保标志
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 5)]
		String^ CombHedgeFlag;
		/// <summary>
		/// 价格
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ LimitPrice;
		/// <summary>
		/// 数量
		/// </summary>
		int VolumeTotalOriginal;
		/// <summary>
		/// 有效期类型
		/// </summary>
		EnumTimeConditionType TimeCondition;
		/// <summary>
		/// GTD日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ GTDDate;
		/// <summary>
		/// 成交量类型
		/// </summary>
		EnumVolumeConditionType VolumeCondition;
		/// <summary>
		/// 最小成交量
		/// </summary>
		int MinVolume;
		/// <summary>
		/// 触发条件
		/// </summary>
		EnumContingentConditionType ContingentCondition;
		/// <summary>
		/// 止损价
		/// </summary>
		double StopPrice;
		/// <summary>
		/// 强平原因
		/// </summary>
		EnumForceCloseReasonType ForceCloseReason;
		/// <summary>
		/// 自动挂起标志
		/// </summary>
		int IsAutoSuspend;
		/// <summary>
		/// 业务单元
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BusinessUnit;
		/// <summary>
		/// 请求编号
		/// </summary>
		int RequestID;
		/// <summary>
		/// 本地报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderLocalID;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 客户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ ClientID;
		/// <summary>
		/// 合约在交易所的代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ExchangeInstID;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
		/// <summary>
		/// 安装编号
		/// </summary>
		int InstallID;
		/// <summary>
		/// 报单提交状态
		/// </summary>
		EnumOrderSubmitStatusType OrderSubmitStatus;
		/// <summary>
		/// 账户代
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
		/// <summary>
		/// 报单提示序号
		/// </summary>
		int NotifySequence;
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 结算编号
		/// </summary>
		int SettlementID;
		/// <summary>
		/// 报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ OrderSysID;
		/// <summary>
		/// 报单来源
		/// </summary>
		EnumOrderSourceType OrderSource;
		/// <summary>
		/// 报单状态
		/// </summary>
		EnumOrderStatusType OrderStatus;
		/// <summary>
		/// 报单类型
		/// </summary>
		EnumOrderTypeType OrderType;
		/// <summary>
		/// 今成交数量
		/// </summary>
		int VolumeTraded;
		/// <summary>
		/// 剩余数量
		/// </summary>
		int VolumeTotal;
		/// <summary>
		/// 报单日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ InsertDate;
		/// <summary>
		/// 委托时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ InsertTime;
		/// <summary>
		/// 激活时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ActiveTime;
		/// <summary>
		/// 挂起时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ SuspendTime;
		/// <summary>
		/// 最后修改时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ UpdateTime;
		/// <summary>
		/// 撤销时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ CancelTime;
		/// <summary>
		/// 最后修改交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ ActiveTraderID;
		/// <summary>
		/// 结算会员编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ClearingPartID;
		/// <summary>
		/// 序号
		/// </summary>
		int SequenceNo;
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
		/// <summary>
		/// 会话编号
		/// </summary>
		int SessionID;
		/// <summary>
		/// 用户端产品信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ UserProductInfo;
		/// <summary>
		/// 状态信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ StatusMsg;
		/// <summary>
		/// 用户强评标志
		/// </summary>
		int UserForceClose;
		/// <summary>
		/// 操作用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ ActiveUserID;
		/// <summary>
		/// 经纪公司报单编号
		/// </summary>
		int BrokerOrderSeq;
		/// <summary>
		/// 相关报单
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ RelativeOrderSysID;
		/// <summary>
		/// 营业部编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ BranchID;
		/// <summary>
		/// 成交数量
		/// </summary>
		double TradeAmount;
		/// <summary>
		/// 是否ETF
		/// </summary>
		int IsETF;
		/// <summary>
		/// 账户类型
		/// </summary>
		EnumAccountTypeType AccountType;
	};
	/// <summary>
	/// 报单操作
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcOrderActionField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 报单操作引用
		/// </summary>
		int OrderActionRef;
		/// <summary>
		/// 报单引用
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderRef;
		/// <summary>
		/// 请求编号
		/// </summary>
		int RequestID;
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
		/// <summary>
		/// 会话编号
		/// </summary>
		int SessionID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 操作标志
		/// </summary>
		EnumActionFlagType ActionFlag;
		/// <summary>
		/// 价格
		/// </summary>
		double LimitPrice;
		/// <summary>
		/// 数量变化
		/// </summary>
		int VolumeChange;
		/// <summary>
		/// 操作日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ActionDate;
		/// <summary>
		/// 操作时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ActionTime;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
		/// <summary>
		/// 安装编号
		/// </summary>
		int InstallID;
		/// <summary>
		/// 本地报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderLocalID;
		/// <summary>
		/// 操作本地编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ ActionLocalID;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 客户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ ClientID;
		/// <summary>
		/// 业务单元
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BusinessUnit;
		/// <summary>
		/// 报单操作状态
		/// </summary>
		EnumOrderActionStatusType OrderActionStatus;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 营业部编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ BranchID;
		/// <summary>
		/// 状态信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ StatusMsg;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 账户类型
		/// </summary>
		EnumAccountTypeType AccountType;
	};
	/// <summary>
	/// 错误报单
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcErrOrderField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 报单引用
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderRef;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 报单价格条件
		/// </summary>
		EnumOrderPriceTypeType OrderPriceType;
		/// <summary>
		/// 买卖方向
		/// </summary>
		EnumDirectionType Direction;
		/// <summary>
		/// 组合开平标志
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 5)]
		String^ CombOffsetFlag;
		/// <summary>
		/// 组合投机套保标志
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 5)]
		String^ CombHedgeFlag;
		/// <summary>
		/// 价格
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ LimitPrice;
		/// <summary>
		/// 数量
		/// </summary>
		int VolumeTotalOriginal;
		/// <summary>
		/// 有效期类型
		/// </summary>
		EnumTimeConditionType TimeCondition;
		/// <summary>
		/// GTD日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ GTDDate;
		/// <summary>
		/// 成交量类型
		/// </summary>
		EnumVolumeConditionType VolumeCondition;
		/// <summary>
		/// 最小成交量
		/// </summary>
		int MinVolume;
		/// <summary>
		/// 触发条件
		/// </summary>
		EnumContingentConditionType ContingentCondition;
		/// <summary>
		/// 止损价
		/// </summary>
		double StopPrice;
		/// <summary>
		/// 强平原因
		/// </summary>
		EnumForceCloseReasonType ForceCloseReason;
		/// <summary>
		/// 自动挂起标志
		/// </summary>
		int IsAutoSuspend;
		/// <summary>
		/// 业务单元
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BusinessUnit;
		/// <summary>
		/// 请求编号
		/// </summary>
		int RequestID;
		/// <summary>
		/// 用户强评标志
		/// </summary>
		int UserForceClose;
		/// <summary>
		/// 错误代码
		/// </summary>
		int ErrorID;
		/// <summary>
		/// 错误信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ ErrorMsg;
	};
	/// <summary>
	/// 错误报单操作
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcErrOrderActionField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 报单操作引用
		/// </summary>
		int OrderActionRef;
		/// <summary>
		/// 报单引用
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderRef;
		/// <summary>
		/// 请求编号
		/// </summary>
		int RequestID;
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
		/// <summary>
		/// 会话编号
		/// </summary>
		int SessionID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 操作标志
		/// </summary>
		EnumActionFlagType ActionFlag;
		/// <summary>
		/// 价格
		/// </summary>
		double LimitPrice;
		/// <summary>
		/// 数量变化
		/// </summary>
		int VolumeChange;
		/// <summary>
		/// 操作日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ActionDate;
		/// <summary>
		/// 操作时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ActionTime;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
		/// <summary>
		/// 安装编号
		/// </summary>
		int InstallID;
		/// <summary>
		/// 本地报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderLocalID;
		/// <summary>
		/// 操作本地编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ ActionLocalID;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 客户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ ClientID;
		/// <summary>
		/// 业务单元
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BusinessUnit;
		/// <summary>
		/// 报单操作状态
		/// </summary>
		EnumOrderActionStatusType OrderActionStatus;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 营业部编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ BranchID;
		/// <summary>
		/// 状态信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ StatusMsg;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 账户类型
		/// </summary>
		EnumAccountTypeType AccountType;
		/// <summary>
		/// 错误代码
		/// </summary>
		int ErrorID;
		/// <summary>
		/// 错误信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ ErrorMsg;
	};
	/// <summary>
	/// 成交
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcTradeField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 报单引用
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderRef;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 成交编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ TradeID;
		/// <summary>
		/// 买卖方向
		/// </summary>
		EnumDirectionType Direction;
		/// <summary>
		/// 报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ OrderSysID;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 客户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ ClientID;
		/// <summary>
		/// 交易角色
		/// </summary>
		EnumTradingRoleType TradingRole;
		/// <summary>
		/// 合约在交易所的代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ExchangeInstID;
		/// <summary>
		/// 开平标志
		/// </summary>
		EnumOffsetFlagType OffsetFlag;
		/// <summary>
		/// 投机套保标志
		/// </summary>
		EnumHedgeFlagType HedgeFlag;
		/// <summary>
		/// 价格
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ Price;
		/// <summary>
		/// 数量
		/// </summary>
		int Volume;
		/// <summary>
		/// 成交时期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradeDate;
		/// <summary>
		/// 成交时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradeTime;
		/// <summary>
		/// 成交类型
		/// </summary>
		EnumTradeTypeType TradeType;
		/// <summary>
		/// 成交价来源
		/// </summary>
		EnumPriceSourceType PriceSource;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
		/// <summary>
		/// 本地报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderLocalID;
		/// <summary>
		/// 结算会员编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ClearingPartID;
		/// <summary>
		/// 业务单元
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BusinessUnit;
		/// <summary>
		/// 序号
		/// </summary>
		int SequenceNo;
		/// <summary>
		/// 成交来源
		/// </summary>
		EnumTradeSourceType TradeSource;
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 结算编号
		/// </summary>
		int SettlementID;
		/// <summary>
		/// 经纪公司报单编号
		/// </summary>
		int BrokerOrderSeq;
	};
	/// <summary>
	/// 投资者持仓
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInvestorPositionField
	{
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 持仓多空方向
		/// </summary>
		EnumPosiDirectionType PosiDirection;
		/// <summary>
		/// 投机套保标志
		/// </summary>
		EnumHedgeFlagType HedgeFlag;
		/// <summary>
		/// 持仓日期
		/// </summary>
		EnumPositionDateType PositionDate;
		/// <summary>
		/// 上日持仓
		/// </summary>
		int YdPosition;
		/// <summary>
		/// 今日持仓
		/// </summary>
		int Position;
		/// <summary>
		/// 多头冻结
		/// </summary>
		int LongFrozen;
		/// <summary>
		/// 空头冻结
		/// </summary>
		int ShortFrozen;
		/// <summary>
		/// 开仓冻结金额
		/// </summary>
		double LongFrozenAmount;
		/// <summary>
		/// 开仓冻结金额
		/// </summary>
		double ShortFrozenAmount;
		/// <summary>
		/// 开仓量
		/// </summary>
		int OpenVolume;
		/// <summary>
		/// 平仓量
		/// </summary>
		int CloseVolume;
		/// <summary>
		/// 开仓金额
		/// </summary>
		double OpenAmount;
		/// <summary>
		/// 平仓金额
		/// </summary>
		double CloseAmount;
		/// <summary>
		/// 持仓成本
		/// </summary>
		double PositionCost;
		/// <summary>
		/// 冻结的资金
		/// </summary>
		double FrozenCash;
		/// <summary>
		/// 资金差额
		/// </summary>
		double CashIn;
		/// <summary>
		/// 手续费
		/// </summary>
		double Commission;
		/// <summary>
		/// 上次结算价
		/// </summary>
		double PreSettlementPrice;
		/// <summary>
		/// 本次结算价
		/// </summary>
		double SettlementPrice;
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 结算编号
		/// </summary>
		int SettlementID;
		/// <summary>
		/// 开仓成本
		/// </summary>
		double OpenCost;
		/// <summary>
		/// 交易所保证金
		/// </summary>
		double ExchangeMargin;
		/// <summary>
		/// 维持保证金
		/// </summary>
		double MaintainMargin;
		/// <summary>
		/// 今日持仓
		/// </summary>
		int TodayPosition;
		/// <summary>
		/// 过户费
		/// </summary>
		double TransferFee;
		/// <summary>
		/// 印花税
		/// </summary>
		double StampTax;
		/// <summary>
		/// 今日申购赎回数量
		/// </summary>
		int TodayPurRedVolume;
		/// <summary>
		/// 折算率
		/// </summary>
		double ConversionRate;
		/// <summary>
		/// 折算金额
		/// </summary>
		double ConversionAmount;
		/// <summary>
		/// 证券价值
		/// </summary>
		double StockValue;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// AccountID
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
		/// <summary>
		/// 锁定的仓位
		/// </summary>
		int LockPosition;
		/// <summary>
		/// 备兑仓位
		/// </summary>
		int CoverPosition;
		/// <summary>
		/// 锁定冻结仓位
		/// </summary>
		int LongLockFrozen;
		/// <summary>
		/// 解锁冻结仓位
		/// </summary>
		int ShortLockFrozen;
		/// <summary>
		/// 备兑冻结仓位
		/// </summary>
		int CoverFrozen;
	};
	/// <summary>
	/// 出入金同步
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcSyncDepositField
	{
		/// <summary>
		/// 出入金流水号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ DepositSeqNo;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 入金金额
		/// </summary>
		double Deposit;
		/// <summary>
		/// 是否强制进行
		/// </summary>
		int IsForce;
		/// <summary>
		/// 账户代
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
	};
	/// <summary>
	/// 查询经纪公司用户事件
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcBrokerUserEventField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 用户事件类型
		/// </summary>
		EnumUserEventTypeType UserEventType;
		/// <summary>
		/// 用户事件序号
		/// </summary>
		int EventSequenceNo;
		/// <summary>
		/// 事件发生日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ EventDate;
		/// <summary>
		/// 事件发生时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ EventTime;
		/// <summary>
		/// 用户事件信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 1025)]
		String^ UserEventInfo;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
	};
	/// <summary>
	/// 合约手续费率
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInstrumentCommissionRateField
	{
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 投资者范围
		/// </summary>
		EnumInvestorRangeType InvestorRange;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 买卖方向
		/// </summary>
		EnumDirectionType Direction;
		/// <summary>
		/// 印花税率
		/// </summary>
		double StampTaxRateByMoney;
		/// <summary>
		/// 印花税率(按手数)
		/// </summary>
		double StampTaxRateByVolume;
		/// <summary>
		/// 过户费率
		/// </summary>
		double TransferFeeRateByMoney;
		/// <summary>
		/// 过户费率(按手数)
		/// </summary>
		double TransferFeeRateByVolume;
		/// <summary>
		/// 交易费
		/// </summary>
		double TradeFeeByMoney;
		/// <summary>
		/// 交易费(按手数)
		/// </summary>
		double TradeFeeByVolume;
		/// <summary>
		/// 交易附加费率
		/// </summary>
		double MarginByMoney;
		/// <summary>
		/// 最小过户费
		/// </summary>
		double MinTradeFee;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
	};
	/// <summary>
	/// 查询交易所
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryExchangeField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
	};
	/// <summary>
	/// 查询产品
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryProductField
	{
		/// <summary>
		/// 产品代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ProductID;
	};
	/// <summary>
	/// 查询合约
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryInstrumentField
	{
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 合约在交易所的代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ExchangeInstID;
		/// <summary>
		/// 产品代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ ProductID;
	};
	/// <summary>
	/// 查询交易员
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryTraderField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
	};
	/// <summary>
	/// 查询经纪公司
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryBrokerField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
	};
	/// <summary>
	/// 查询经纪公司会员代码
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryPartBrokerField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
	};
	/// <summary>
	/// 查询投资者
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryInvestorField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
	};
	/// <summary>
	/// 查询交易编码
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryTradingCodeField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 客户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ ClientID;
	};
	/// <summary>
	/// 查询管理用户
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQrySuperUserField
	{
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
	};
	/// <summary>
	/// 查询管理用户功能权限
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQrySuperUserFunctionField
	{
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
	};
	/// <summary>
	/// 查询经纪公司用户
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryBrokerUserField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
	};
	/// <summary>
	/// 查询经纪公司用户权限
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryBrokerUserFunctionField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
	};
	/// <summary>
	/// 查询资金账户
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryTradingAccountField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
	};
	/// <summary>
	/// 查询禁止登录用户
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryLoginForbiddenUserField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
	};
	/// <summary>
	/// 查询行情
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryDepthMarketDataField
	{
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
	};
	/// <summary>
	/// 查询合约交易权限
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryInstrumentTradingRightField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
	};
	/// <summary>
	/// 查询投资者持仓明细
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryInvestorPositionDetailField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
	};
	/// <summary>
	/// 查询债券利息
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryBondInterestField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
	};
	/// <summary>
	/// 查询交易员报盘机
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryTraderOfferField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
	};
	/// <summary>
	/// 查询行情报盘机
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryMDTraderOfferField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 会员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ParticipantID;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
	};
	/// <summary>
	/// 查询前置状态
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryFrontStatusField
	{
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
	};
	/// <summary>
	/// 查询用户会话
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryUserSessionField
	{
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
		/// <summary>
		/// 会话编号
		/// </summary>
		int SessionID;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
	};
	/// <summary>
	/// 查询报单
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryOrderField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ OrderSysID;
		/// <summary>
		/// 开始时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ InsertTimeStart;
		/// <summary>
		/// 结束时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ InsertTimeEnd;
	};
	/// <summary>
	/// 查询报单操作
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryOrderActionField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
	};
	/// <summary>
	/// 查询错误报单
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryErrOrderField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
	};
	/// <summary>
	/// 查询错误报单操作
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryErrOrderActionField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
	};
	/// <summary>
	/// 查询成交
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryTradeField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 成交编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ TradeID;
		/// <summary>
		/// 开始时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradeTimeStart;
		/// <summary>
		/// 结束时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradeTimeEnd;
	};
	/// <summary>
	/// 查询投资者持仓
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryInvestorPositionField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
	};
	/// <summary>
	/// 查询出入金流水
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQrySyncDepositField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 出入金流水号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ DepositSeqNo;
	};
	/// <summary>
	/// 查询经纪公司用户事件
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryBrokerUserEventField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 用户事件类型
		/// </summary>
		EnumUserEventTypeType UserEventType;
	};
	/// <summary>
	/// 查询合约手续费率
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryInstrumentCommissionRateField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 买卖方向
		/// </summary>
		EnumDirectionType Direction;
	};
	/// <summary>
	/// 用户口令变更
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcUserPasswordUpdateField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 原来的口令
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ OldPassword;
		/// <summary>
		/// 新的口令
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ NewPassword;
	};
	/// <summary>
	/// 资金账户口令变更域
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcTradingAccountPasswordUpdateField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者帐号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
		/// <summary>
		/// 原来的口令
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ OldPassword;
		/// <summary>
		/// 新的口令
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ NewPassword;
	};
	/// <summary>
	/// 手工同步用户动态令牌
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcManualSyncBrokerUserOTPField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 动态令牌类型
		/// </summary>
		EnumOTPTypeType OTPType;
		/// <summary>
		/// 第一个动态密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ FirstOTP;
		/// <summary>
		/// 第二个动态密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ SecondOTP;
	};
	/// <summary>
	/// 经纪公司用户口令
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcBrokerUserPasswordField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ Password;
	};
	/// <summary>
	/// 资金账户口令域
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcTradingAccountPasswordField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者帐号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
		/// <summary>
		/// 密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ Password;
	};
	/// <summary>
	/// 用户权限
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcUserRightField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 客户权限类型
		/// </summary>
		EnumUserRightTypeType UserRightType;
		/// <summary>
		/// 是否禁止
		/// </summary>
		int IsForbidden;
	};
	/// <summary>
	/// 投资者账户
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInvestorAccountField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 投资者帐号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
		/// <summary>
		/// 账户类型
		/// </summary>
		EnumAccountTypeType AccountType;
		/// <summary>
		/// 是否主账户
		/// </summary>
		int IsDefault;
	};
	/// <summary>
	/// 用户IP
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcUserIPField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// IP地址
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ IPAddress;
		/// <summary>
		/// IP地址掩码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ IPMask;
		/// <summary>
		/// Mac地址
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ MacAddress;
	};
	/// <summary>
	/// 用户动态令牌参数
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcBrokerUserOTPParamField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 动态令牌提供商
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 2)]
		String^ OTPVendorsID;
		/// <summary>
		/// 动态令牌序列号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 17)]
		String^ SerialNumber;
		/// <summary>
		/// 令牌密钥
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ AuthKey;
		/// <summary>
		/// 漂移值
		/// </summary>
		int LastDrift;
		/// <summary>
		/// 成功值
		/// </summary>
		int LastSuccess;
		/// <summary>
		/// 动态令牌类型
		/// </summary>
		EnumOTPTypeType OTPType;
	};
	/// <summary>
	/// 用户登录请求
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcReqUserLoginField
	{
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ Password;
		/// <summary>
		/// 用户端产品信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ UserProductInfo;
		/// <summary>
		/// 接口端产品信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ InterfaceProductInfo;
		/// <summary>
		/// 协议信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ ProtocolInfo;
		/// <summary>
		/// Mac地址
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ MacAddress;
		/// <summary>
		/// 动态密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ OneTimePassword;
		/// <summary>
		/// 终端IP地址
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ ClientIPAddress;
		/// <summary>
		/// 客户端认证码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 17)]
		String^ AuthCode;
	};
	/// <summary>
	/// 用户登录应答
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcRspUserLoginField
	{
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 登录成功时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ LoginTime;
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 交易系统名称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ SystemName;
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
		/// <summary>
		/// 会话编号
		/// </summary>
		int SessionID;
		/// <summary>
		/// 最大报单引用
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ MaxOrderRef;
	};
	/// <summary>
	/// 用户登出请求
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcUserLogoutField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
	};
	/// <summary>
	/// 全部登出信息
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcLogoutAllField
	{
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
		/// <summary>
		/// 会话编号
		/// </summary>
		int SessionID;
		/// <summary>
		/// 系统名称
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ SystemName;
	};
	/// <summary>
	/// 强制交易员退出
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcForceUserLogoutField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
	};
	/// <summary>
	/// 输入报单
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInputOrderField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 报单引用
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderRef;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 报单价格条件
		/// </summary>
		EnumOrderPriceTypeType OrderPriceType;
		/// <summary>
		/// 买卖方向
		/// </summary>
		EnumDirectionType Direction;
		/// <summary>
		/// 组合开平标志
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 5)]
		String^ CombOffsetFlag;
		/// <summary>
		/// 组合投机套保标志
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 5)]
		String^ CombHedgeFlag;
		/// <summary>
		/// 价格
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ LimitPrice;
		/// <summary>
		/// 数量
		/// </summary>
		int VolumeTotalOriginal;
		/// <summary>
		/// 有效期类型
		/// </summary>
		EnumTimeConditionType TimeCondition;
		/// <summary>
		/// GTD日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ GTDDate;
		/// <summary>
		/// 成交量类型
		/// </summary>
		EnumVolumeConditionType VolumeCondition;
		/// <summary>
		/// 最小成交量
		/// </summary>
		int MinVolume;
		/// <summary>
		/// 触发条件
		/// </summary>
		EnumContingentConditionType ContingentCondition;
		/// <summary>
		/// 止损价
		/// </summary>
		double StopPrice;
		/// <summary>
		/// 强平原因
		/// </summary>
		EnumForceCloseReasonType ForceCloseReason;
		/// <summary>
		/// 自动挂起标志
		/// </summary>
		int IsAutoSuspend;
		/// <summary>
		/// 业务单元
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BusinessUnit;
		/// <summary>
		/// 请求编号
		/// </summary>
		int RequestID;
		/// <summary>
		/// 用户强评标志
		/// </summary>
		int UserForceClose;
	};
	/// <summary>
	/// 输入报单操作
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInputOrderActionField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 报单操作引用
		/// </summary>
		int OrderActionRef;
		/// <summary>
		/// 报单引用
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderRef;
		/// <summary>
		/// 请求编号
		/// </summary>
		int RequestID;
		/// <summary>
		/// 前置编号
		/// </summary>
		int FrontID;
		/// <summary>
		/// 会话编号
		/// </summary>
		int SessionID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
		/// <summary>
		/// 操作标志
		/// </summary>
		EnumActionFlagType ActionFlag;
		/// <summary>
		/// 价格
		/// </summary>
		double LimitPrice;
		/// <summary>
		/// 数量变化
		/// </summary>
		int VolumeChange;
		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 交易所交易员代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 21)]
		String^ BranchPBU;
		/// <summary>
		/// 本地报单编号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^ OrderLocalID;
	};
	/// <summary>
	/// 指定的合约
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcSpecificInstrumentField
	{
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
	};
	/// <summary>
	/// 指定的交易所
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcSpecificExchangeField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
	};
	/// <summary>
	/// 行情基础属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataBaseField
	{
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		/// <summary>
		/// 上次结算价
		/// </summary>
		double PreSettlementPrice;
		/// <summary>
		/// 昨收盘
		/// </summary>
		double PreClosePrice;
		/// <summary>
		/// 昨持仓量
		/// </summary>
		double PreOpenInterest;
		/// <summary>
		/// 昨虚实度
		/// </summary>
		double PreDelta;
	};
	/// <summary>
	/// 行情静态属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataStaticField
	{
		/// <summary>
		/// 今开盘
		/// </summary>
		double OpenPrice;
		/// <summary>
		/// 最高价
		/// </summary>
		double HighestPrice;
		/// <summary>
		/// 最低价
		/// </summary>
		double LowestPrice;
		/// <summary>
		/// 今收盘
		/// </summary>
		double ClosePrice;
		/// <summary>
		/// 涨停板价
		/// </summary>
		double UpperLimitPrice;
		/// <summary>
		/// 跌停板价
		/// </summary>
		double LowerLimitPrice;
		/// <summary>
		/// 本次结算价
		/// </summary>
		double SettlementPrice;
		/// <summary>
		/// 今虚实度
		/// </summary>
		double CurrDelta;
	};
	/// <summary>
	/// 行情最新成交属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataLastMatchField
	{
		/// <summary>
		/// 最新价
		/// </summary>
		double LastPrice;
		/// <summary>
		/// 数量
		/// </summary>
		int Volume;
		/// <summary>
		/// 成交金额
		/// </summary>
		double Turnover;
		/// <summary>
		/// 持仓量
		/// </summary>
		double OpenInterest;
	};
	/// <summary>
	/// 行情最优价属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataBestPriceField
	{
		/// <summary>
		/// 申买价一
		/// </summary>
		double BidPrice1;
		/// <summary>
		/// 申买量一
		/// </summary>
		int BidVolume1;
		/// <summary>
		/// 申卖价一
		/// </summary>
		double AskPrice1;
		/// <summary>
		/// 申卖量一
		/// </summary>
		int AskVolume1;
	};
	/// <summary>
	/// 行情申买二、三属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataBid23Field
	{
		/// <summary>
		/// 申买价二
		/// </summary>
		double BidPrice2;
		/// <summary>
		/// 申买量二
		/// </summary>
		int BidVolume2;
		/// <summary>
		/// 申买价三
		/// </summary>
		double BidPrice3;
		/// <summary>
		/// 申买量三
		/// </summary>
		int BidVolume3;
	};
	/// <summary>
	/// 行情申卖二、三属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataAsk23Field
	{
		/// <summary>
		/// 申卖价二
		/// </summary>
		double AskPrice2;
		/// <summary>
		/// 申卖量二
		/// </summary>
		int AskVolume2;
		/// <summary>
		/// 申卖价三
		/// </summary>
		double AskPrice3;
		/// <summary>
		/// 申卖量三
		/// </summary>
		int AskVolume3;
	};
	/// <summary>
	/// 行情申买四、五属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataBid45Field
	{
		/// <summary>
		/// 申买价四
		/// </summary>
		double BidPrice4;
		/// <summary>
		/// 申买量四
		/// </summary>
		int BidVolume4;
		/// <summary>
		/// 申买价五
		/// </summary>
		double BidPrice5;
		/// <summary>
		/// 申买量五
		/// </summary>
		int BidVolume5;
	};
	/// <summary>
	/// 行情申卖四、五属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataAsk45Field
	{
		/// <summary>
		/// 申卖价四
		/// </summary>
		double AskPrice4;
		/// <summary>
		/// 申卖量四
		/// </summary>
		int AskVolume4;
		/// <summary>
		/// 申卖价五
		/// </summary>
		double AskPrice5;
		/// <summary>
		/// 申卖量五
		/// </summary>
		int AskVolume5;
	};
	/// <summary>
	/// 行情更新时间属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataUpdateTimeField
	{
		/// <summary>
		/// 合约代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 31)]
		String^ InstrumentID;
		/// <summary>
		/// 最后修改时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ UpdateTime;
		/// <summary>
		/// 最后修改毫秒
		/// </summary>
		int UpdateMillisec;
		/// <summary>
		/// 业务日期
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ActionDay;
	};
	/// <summary>
	/// 成交均价
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataAveragePriceField
	{
		/// <summary>
		/// 当日均价
		/// </summary>
		double AveragePrice;
	};
	/// <summary>
	/// 行情交易所代码属性
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcMarketDataExchangeField
	{
		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
	};
	/// <summary>
	/// 信息分发
	///顺序布局
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcDisseminationField
	{
		/// <summary>
		/// 序列系列号
		/// </summary>
		short SequenceSeries;
		/// <summary>
		/// 序列号
		/// </summary>
		int SequenceNo;
	};

	///////////////////////////////////////////////////////////////////////融资融券新增部分
	/// <summary>
	/// 查询市值配售信息
	/// </summary>
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryMarketRationInfoField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;

		/// <summary>
		/// 交易所代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ ExchangeID;
	};

	///资金转账输入
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcInputFundTransferField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;

		/// <summary>
		/// 投资者资金帐号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;

		/// <summary>
		/// 资金帐户密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ Password;

		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;

		///交易金额
		double	TradeAmount;

		/// <summary>
		/// 摘要
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 36)]
		String^	Digest;
		///账户类型
		EnumAccountTypeType	AccountType;
	};

	/// <summary>
	/// 账户类型 CAccountTypeType
	/// </summary>
	public enum struct EnumFundTransfer : Byte
	{
		/// <summary>
		/// 普通账户
		/// </summary>
		FDIn=(Byte)'1',
		/// <summary>
		/// 信用账户
		/// </summary>
		FDOut=(Byte)'2',
	};

	///资金转账
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcFundTransferField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;
		/// <summary>
		/// 投资者代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ InvestorID;
		/// <summary>
		/// 投资者资金帐号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;

		/// <summary>
		/// 资金帐户密码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 41)]
		String^ Password;

		/// <summary>
		/// 用户代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 16)]
		String^ UserID;

		///交易金额
		double	TradeAmount;
		/// <summary>
		/// 摘要
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 36)]
		String^	Digest;

		///会话编号
		int	SessionID;
		///Liber核心流水号
		int	LiberSerial;
		///转账平台流水号
		int	PlateSerial;

		/// <summary>
		/// 第三方流水号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 13)]
		String^	TransferSerial;
		/// <summary>
		/// 交易日
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradingDay;
		
		/// <summary>
		/// 转账时间
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 9)]
		String^ TradeTime;

		///出入金方向
		EnumFundTransfer	FundDirection;
		/// <summary>
		/// 错误代码
		/// </summary>
		int ErrorID;
		/// <summary>
		/// 错误信息
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 81)]
		String^ ErrorMsg;
	};

	///资金转账查询请求
	[StructLayout(LayoutKind::Sequential)]
	public ref struct SecurityFtdcQryFundTransferSerialField
	{
		/// <summary>
		/// 经纪公司代码
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 11)]
		String^ BrokerID;

		/// <summary>
		/// 投资者资金帐号
		/// </summary>
		[MarshalAs(UnmanagedType::ByValTStr, SizeConst = 15)]
		String^ AccountID;
		///账户类型
		EnumAccountTypeType	AccountType;
	};
	/////////////////////////////////////////////////////////////////////////
	///TFtdcFundIOTypeType是一个出入金类型类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumFundIOTypeType: Byte
	{
		///出入金
		FundIO=(Byte)'1',
		///银期转帐
		Transfer=(Byte)'2',
	};
	/////////////////////////////////////////////////////////////////////////
	///TFtdcFundTypeType是一个资金类型类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumFundTypeType : Byte
	{
		///银行存款
		Deposite=(Byte)'1',
		///分项资金
		ItemFund=(Byte) '2',
		///公司调整
		Company =(Byte)'3',
	};

	/////////////////////////////////////////////////////////////////////////
	///TFtdcFundDirectionType是一个出入金方向类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumFundDirectionType : Byte
	{
		///入金
		In =(Byte)'1',
		///出金
		Out =(Byte)'2',
	};

	/////////////////////////////////////////////////////////////////////////
	///TFtdcBankFlagType是一个银行统一标识类型类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumBankFlagType : Byte
	{
		///工商银行
		ICBC  =(Byte)'1',
		///农业银行
		ABC  =(Byte)'2',
		///中国银行
		BC  =(Byte)'3',
		///建设银行
		CBC  =(Byte)'4',
		///交通银行
		BOC  =(Byte)'5',
		///其他银行
		Other  =(Byte)'Z',
	};

	/////////////////////////////////////////////////////////////////////////
	///TFtdcFundStatusType是一个资金状态类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumFundStatusType : Byte
	{
		///已录入
		Record  =(Byte)'1',
		///已复核
		Check  =(Byte)'2',
		///已冲销
		Charge =(Byte) '3',
	};

	/////////////////////////////////////////////////////////////////////////
	///TFtdcLastFragmentType是一个最后分片标志类型
	///TFtdcYesNoIndicatorType是一个是或否标识类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumYesNo : Byte
	{
		///是
		 Yes  =(Byte) '0',
		///不是
		 No  =(Byte) '1',
	};

	/////////////////////////////////////////////////////////////////////////
	///TFtdcCustTypeType是一个客户类型类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumCustTypeType : Byte
	{
		///自然人
		Person =(Byte)'0',
		///机构户
		Institution =(Byte)'1',
	};

	/////////////////////////////////////////////////////////////////////////
	///TFtdcFeePayFlagType是一个费用支付标志类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumFeePayFlagType : Byte
	{
		///由受益方支付费用
		 BEN =(Byte)'0',
			///由发送方支付费用
		 OUR =(Byte)'1',
			///由发送方支付发起的费用，受益方支付接受的费用
		 SHA =(Byte)'2',
	};
	/////////////////////////////////////////////////////////////////////////
	///TFtdcBankAccTypeType是一个银行帐号类型类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumBankAccTypeType : Byte
	{
		///银行存折
		BankBook =(Byte)'1',
			///储蓄卡
		SavingCard =(Byte)'2',
			///信用卡
		CreditCard =(Byte)'3',
	};

	/////////////////////////////////////////////////////////////////////////
	///TFtdcPwdFlagType是一个密码核对标志类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumPwdFlagType : Byte
	{
		///不核对
		 NoCheck  =(Byte)'0',
			///明文核对
		 BlankCheck  =(Byte)'1',
			///密文核对
		 EncryptCheck  =(Byte)'2',
	};

	/////////////////////////////////////////////////////////////////////////
	///TFtdcTransferStatusType是一个转账交易状态类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumTransferStatusType: Byte
	{
		///正常
		 Normal=(Byte)'0',
			///被冲正
		 Repealed=(Byte)'1',
	};


	/////////////////////////////////////////////////////////////////////////
	///TFtdcAvailabilityFlagType是一个有效标志类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumAvailabilityFlagType: Byte
	{
		///未确认
		 Invalid =(Byte)'0',
			///有效
		 Valid=(Byte) '1',
			///冲正
		 Repeal=(Byte) '2',
	 };

	/////////////////////////////////////////////////////////////////////////
	///TFtdcRepayStockAlgoType是一个买券还券算法类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumRepayStockAlgoType: Byte
	{
		///默认算法
		 Original=(Byte) '0',
			///按还券比例计算
		 Ratio=(Byte) '1',
			///Min[1,2]
		 Min =(Byte)'2',
	};

	/////////////////////////////////////////////////////////////////////////
	///TFtdcTradeSpanType是一个交易时间段类型类型
	/////////////////////////////////////////////////////////////////////////
	public enum struct EnumTradeSpanType: Byte
	{
		///普通业务
		Common =(Byte)'1',
		///个股期权
		Options =(Byte)'2',
	 };
};
