/*!
* \file Delegates.h
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

namespace RELib_LTSNet
{

	// common deleagats
	///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
	public delegate  void FrontConnected();

	///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
	///@param nReason 错误原因
	///        0x1001 网络读失败
	///        0x1002 网络写失败
	///        0x2001 接收心跳超时
	///        0x2002 发送心跳失败
	///        0x2003 收到错误报文
	public delegate  void FrontDisconnected(int nReason);

	///心跳超时警告。当长时间未收到报文时，该方法被调用。
	///@param nTimeLapse 距离上次接收报文的时间
	public delegate  void HeartBeatWarning(int nTimeLapse);



	

	///错误应答
	public delegate void RspError(SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///登录请求响应
	public delegate void RspUserLogin(SecurityFtdcRspUserLoginField^ pRspUserLogin, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///登出请求响应
	public delegate void RspUserLogout(SecurityFtdcUserLogoutField^ pUserLogout, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///订阅行情应答
	public delegate void RspSubMarketData(SecurityFtdcSpecificInstrumentField^ pSpecificInstrument, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///取消订阅行情应答
	public delegate void RspUnSubMarketData(SecurityFtdcSpecificInstrumentField^ pSpecificInstrument, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///深度行情通知
	public delegate void RtnDepthMarketData(SecurityFtdcDepthMarketDataField^ pDepthMarketData);

	///报单录入请求响应
	public delegate void RspOrderInsert(SecurityFtdcInputOrderField^ pInputOrder, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///报单操作请求响应
	public delegate void RspOrderAction(SecurityFtdcInputOrderActionField^ pInputOrderAction, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///用户口令更新请求响应
	public delegate void RspUserPasswordUpdate(SecurityFtdcUserPasswordUpdateField^ pUserPasswordUpdate, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///资金账户口令更新请求响应
	public delegate void RspTradingAccountPasswordUpdate(SecurityFtdcTradingAccountPasswordUpdateField^ pTradingAccountPasswordUpdate, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询交易所响应
	public delegate void RspQryExchange(SecurityFtdcExchangeField^ pExchange, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询合约响应
	public delegate void RspQryInstrument(SecurityFtdcInstrumentField^ pInstrument, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询投资者响应
	public delegate void RspQryInvestor(SecurityFtdcInvestorField^ pInvestor, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询交易编码响应
	public delegate void RspQryTradingCode(SecurityFtdcTradingCodeField^ pTradingCode, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询资金账户响应
	public delegate void RspQryTradingAccount(SecurityFtdcTradingAccountField^ pTradingAccount, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询行情响应
	public delegate void RspQryDepthMarketData(SecurityFtdcDepthMarketDataField^ pDepthMarketData, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询投资者持仓明细响应
	public delegate void RspQryInvestorPositionDetail(SecurityFtdcInvestorPositionDetailField^ pInvestorPositionDetail, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询债券利息响应
	public delegate void RspQryBondInterest(SecurityFtdcBondInterestField^ pBondInterest, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询报单响应
	public delegate void RspQryOrder(SecurityFtdcOrderField^ pOrder, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询成交响应
	public delegate void RspQryTrade(SecurityFtdcTradeField^ pTrade, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///请求查询投资者持仓响应
	public delegate void RspQryInvestorPosition(SecurityFtdcInvestorPositionField^ pInvestorPosition, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///报单通知
	public delegate void RtnOrder(SecurityFtdcOrderField^ pOrder);

	///成交通知
	public delegate void RtnTrade(SecurityFtdcTradeField^ pTrade);

	///报单录入错误回报
	public delegate void ErrRtnOrderInsert(SecurityFtdcInputOrderField^ pInputOrder, SecurityFtdcRspInfoField^ pRspInfo);

	///报单操作错误回报
	public delegate void ErrRtnOrderAction(SecurityFtdcOrderActionField^ pOrderAction, SecurityFtdcRspInfoField^ pRspInfo);



	///////////////////////////////////////////////////////////////融资融券新增部分
	///Liber发起出金应答
	public delegate void RspFundOutByLiber(SecurityFtdcInputFundTransferField^ pInputFundTransfer, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);

	///Liber发起出金通知
	public delegate void RtnFundOutByLiber(SecurityFtdcFundTransferField^ pFundTransfer);

	///iber发起出金错误回报
	public delegate void ErrRtnFundOutByLiber(SecurityFtdcInputFundTransferField^ pInputFundTransfer, SecurityFtdcRspInfoField^ pRspInfo);

	///银行发起入金通知
	public delegate void RtnFundInByBank(SecurityFtdcFundTransferField^ pFundTransfer);

	///资金转账查询应答
	public delegate void RspQryFundTransferSerial(SecurityFtdcFundTransferField^ pFundTransfer, SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast);
};

#ifdef __LTS_MA__

namespace RELib_LTSNative
{

	///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
	delegate void Internal_FrontConnected();

	///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
	///@param nReason 错误原因
	///        0x1001 网络读失败
	///        0x1002 网络写失败
	///        0x2001 接收心跳超时
	///        0x2002 发送心跳失败
	///        0x2003 收到错误报文
	delegate void Internal_FrontDisconnected(int nReason);

	///心跳超时警告。当长时间未收到报文时，该方法被调用。
	///@param nTimeLapse 距离上次接收报文的时间
	delegate void Internal_HeartBeatWarning(int nTimeLapse);

	///报文回调开始通知。当API收到一个报文后，首先调用本方法，然后是各数据域的回调，最后是报文回调结束通知。
	///@param nTopicID 主题代码（如私有流、公共流、行情流等）
	///@param nSequenceNo 报文序号
	delegate void Internal_PackageStart(int nTopicID, int nSequenceNo);

	///报文回调结束通知。当API收到一个报文后，首先调用报文回调开始通知，然后是各数据域的回调，最后调用本方法。
	///@param nTopicID 主题代码（如私有流、公共流、行情流等）
	///@param nSequenceNo 报文序号
	delegate void Internal_PackageEnd(int nTopicID, int nSequenceNo);

	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspError(CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspUserLogin(CSecurityFtdcRspUserLoginField *pRspUserLogin,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspUserLogout(CSecurityFtdcUserLogoutField *pUserLogout,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspOrderAction(CSecurityFtdcInputOrderActionField *pInputOrderAction,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspUserPasswordUpdate(CSecurityFtdcUserPasswordUpdateField *pUserPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspTradingAccountPasswordUpdate(CSecurityFtdcTradingAccountPasswordUpdateField *pTradingAccountPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryExchange(CSecurityFtdcExchangeField *pExchange,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryInstrument(CSecurityFtdcInstrumentField *pInstrument,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryInvestor(CSecurityFtdcInvestorField *pInvestor,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryTradingCode(CSecurityFtdcTradingCodeField *pTradingCode,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryTradingAccount(CSecurityFtdcTradingAccountField *pTradingAccount,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryDepthMarketData(CSecurityFtdcDepthMarketDataField *pDepthMarketData,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryInvestorPositionDetail(CSecurityFtdcInvestorPositionDetailField *pInvestorPositionDetail,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryBondInterest(CSecurityFtdcBondInterestField *pBondInterest,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryOrder(CSecurityFtdcOrderField *pOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryTrade(CSecurityFtdcTradeField *pTrade,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RspQryInvestorPosition(CSecurityFtdcInvestorPositionField *pInvestorPosition,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RtnOrder(CSecurityFtdcOrderField *pOrder);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_RtnTrade(CSecurityFtdcTradeField *pTrade);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_ErrRtnOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo);
	/// <summary>
	/// 
	/// </summary>
	delegate void Internal_ErrRtnOrderAction(CSecurityFtdcOrderActionField *pOrderAction,CSecurityFtdcRspInfoField *pRspInfo);


	///////////////////////////////////////////////////////////////融资融券新增部分
	///Liber发起出金应答
	delegate void Internal_OnRspFundOutByLiber(CSecurityFtdcInputFundTransferField *pInputFundTransfer, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///Liber发起出金通知
	delegate void Internal_OnRtnFundOutByLiber(CSecurityFtdcFundTransferField *pFundTransfer);

	///iber发起出金错误回报
	delegate void Internal_OnErrRtnFundOutByLiber(CSecurityFtdcInputFundTransferField *pInputFundTransfer, CSecurityFtdcRspInfoField *pRspInfo);

	///银行发起入金通知
	delegate void Internal_OnRtnFundInByBank(CSecurityFtdcFundTransferField *pFundTransfer);

	///资金转账查询应答
	delegate void Internal_OnRspQryFundTransferSerial(CSecurityFtdcFundTransferField *pFundTransfer, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
};

#endif
