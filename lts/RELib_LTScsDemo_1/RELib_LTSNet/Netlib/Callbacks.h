/*!
* \file CallBacks.h
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
// LTS MA only
#ifdef __LTS_MA__

namespace RELib_LTSNative
{

	// common 
	typedef void (__stdcall *Callback_OnFrontConnected)();
	typedef void (__stdcall *Callback_OnFrontDisconnected)(int nReason);
	typedef void (__stdcall *Callback_OnHeartBeatWarning)(int nTimeLapse);

	// marketdata
	typedef void (__stdcall *Callback_OnRspSubMarketData)(CSecurityFtdcSpecificInstrumentField *pSpecificInstrument, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	typedef void (__stdcall *Callback_OnRspUnSubMarketData)(CSecurityFtdcSpecificInstrumentField *pSpecificInstrument, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	typedef void (__stdcall *Callback_OnRtnDepthMarketData)(CSecurityFtdcDepthMarketDataField *pDepthMarketData);

	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspError)(CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspUserLogin)(CSecurityFtdcRspUserLoginField *pRspUserLogin,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspUserLogout)(CSecurityFtdcUserLogoutField *pUserLogout,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspOrderInsert)(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspOrderAction)(CSecurityFtdcInputOrderActionField *pInputOrderAction,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspUserPasswordUpdate)(CSecurityFtdcUserPasswordUpdateField *pUserPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspTradingAccountPasswordUpdate)(CSecurityFtdcTradingAccountPasswordUpdateField *pTradingAccountPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryExchange)(CSecurityFtdcExchangeField *pExchange,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryInstrument)(CSecurityFtdcInstrumentField *pInstrument,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryInvestor)(CSecurityFtdcInvestorField *pInvestor,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryTradingCode)(CSecurityFtdcTradingCodeField *pTradingCode,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryTradingAccount)(CSecurityFtdcTradingAccountField *pTradingAccount,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryDepthMarketData)(CSecurityFtdcDepthMarketDataField *pDepthMarketData,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryInvestorPositionDetail)(CSecurityFtdcInvestorPositionDetailField *pInvestorPositionDetail,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryBondInterest)(CSecurityFtdcBondInterestField *pBondInterest,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryOrder)(CSecurityFtdcOrderField *pOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryTrade)(CSecurityFtdcTradeField *pTrade,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRspQryInvestorPosition)(CSecurityFtdcInvestorPositionField *pInvestorPosition,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRtnOrder)(CSecurityFtdcOrderField *pOrder,CSecurityFtdcOrderField *pOrder);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnRtnTrade)(CSecurityFtdcTradeField *pTrade,CSecurityFtdcTradeField *pTrade);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnErrRtnOrderInsert)(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo);
	/// <summary>
	/// 
	/// </summary>
	typedef void (__stdcall *Callback_OnErrRtnOrderAction)(CSecurityFtdcOrderActionField *pOrderAction,CSecurityFtdcRspInfoField *pRspInfo);

	///////////////////////////////////////////////////////////////融资融券新增部分
	///Liber发起出金应答
	typedef void (__stdcall *Callback_OnRspFundOutByLiber)(CSecurityFtdcInputFundTransferField *pInputFundTransfer, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///Liber发起出金通知
	typedef void (__stdcall *Callback_OnRtnFundOutByLiber)(CSecurityFtdcFundTransferField *pFundTransfer);

	///iber发起出金错误回报
	typedef void (__stdcall *Callback_OnErrRtnFundOutByLiber)(CSecurityFtdcInputFundTransferField *pInputFundTransfer, CSecurityFtdcRspInfoField *pRspInfo);

	///银行发起入金通知
	typedef void (__stdcall *Callback_OnRtnFundInByBank)(CSecurityFtdcFundTransferField *pFundTransfer);

	///资金转账查询应答
	typedef void (__stdcall *Callback_OnRspQryFundTransferSerial)(CSecurityFtdcFundTransferField *pFundTransfer, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
};

#endif
