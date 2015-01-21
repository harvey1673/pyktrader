/*!
* \file LTSTraderSpi.cpp
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

#include "StdAfx.h"
#include "LTSTraderSpi.h"
#include "LTSTraderAdapter.h"
#include "Callbacks.h"


namespace RELib_LTSNative
{
	CLTSTraderSpi::CLTSTraderSpi(LTSTraderAdapter^ pAdapter) {
#ifndef __LTS_MA__
		m_pAdapter = pAdapter;
#endif
	};
#ifdef __LTS_MA__

	///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
	void CLTSTraderSpi::OnFrontConnected(){
		p_OnFrontConnected();
	};
	
	///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
	///@param nReason 错误原因
	///        0x1001 网络读失败
	///        0x1002 网络写失败
	///        0x2001 接收心跳超时
	///        0x2002 发送心跳失败
	///        0x2003 收到错误报文
	void CLTSTraderSpi::OnFrontDisconnected(int nReason){
		p_OnFrontDisconnected(nReason);
	};

	///心跳超时警告。当长时间未收到报文时，该方法被调用。
	///@param nTimeLapse 距离上次接收报文的时间
	void CLTSTraderSpi::OnHeartBeatWarning(int nTimeLapse){
		p_OnHeartBeatWarning(nTimeLapse);
	};

	///客户端认证响应
	/*void CLTSTraderSpi::OnRspAuthenticate(CIndexFtdcRspAuthenticateField *pRspAuthenticateField, CIndexFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
	p_OnRspAuthenticate(MNConv<ThostFtdcRspAuthenticateField^,CIndexFtdcRspAuthenticateField>::N2M(pRspAuthenticateField), RspInfoField(pRspInfo), nRequestID, bIsLast);
	};*/


	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspError(CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspError(RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspUserLogin(CSecurityFtdcRspUserLoginField *pRspUserLogin,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspUserLogin(MNConv<SecurityFtdcRspUserLoginField^, CSecurityFtdcRspUserLoginField>::N2M(pRspUserLogin),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspUserLogout(CSecurityFtdcUserLogoutField *pUserLogout,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspUserLogout(MNConv<SecurityFtdcUserLogoutField^, CSecurityFtdcUserLogoutField>::N2M(pUserLogout),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspOrderInsert(MNConv<SecurityFtdcInputOrderField^, CSecurityFtdcInputOrderField>::N2M(pInputOrder),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspOrderAction(CSecurityFtdcInputOrderActionField *pInputOrderAction,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspOrderAction(MNConv<SecurityFtdcInputOrderActionField^, CSecurityFtdcInputOrderActionField>::N2M(pInputOrderAction),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspUserPasswordUpdate(CSecurityFtdcUserPasswordUpdateField *pUserPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspUserPasswordUpdate(MNConv<SecurityFtdcUserPasswordUpdateField^, CSecurityFtdcUserPasswordUpdateField>::N2M(pUserPasswordUpdate),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspTradingAccountPasswordUpdate(CSecurityFtdcTradingAccountPasswordUpdateField *pTradingAccountPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspTradingAccountPasswordUpdate(MNConv<SecurityFtdcTradingAccountPasswordUpdateField^, CSecurityFtdcTradingAccountPasswordUpdateField>::N2M(pTradingAccountPasswordUpdate),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryExchange(CSecurityFtdcExchangeField *pExchange,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryExchange(MNConv<SecurityFtdcExchangeField^, CSecurityFtdcExchangeField>::N2M(pExchange),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryInstrument(CSecurityFtdcInstrumentField *pInstrument,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryInstrument(MNConv<SecurityFtdcInstrumentField^, CSecurityFtdcInstrumentField>::N2M(pInstrument),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryInvestor(CSecurityFtdcInvestorField *pInvestor,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryInvestor(MNConv<SecurityFtdcInvestorField^, CSecurityFtdcInvestorField>::N2M(pInvestor),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryTradingCode(CSecurityFtdcTradingCodeField *pTradingCode,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryTradingCode(MNConv<SecurityFtdcTradingCodeField^, CSecurityFtdcTradingCodeField>::N2M(pTradingCode),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryTradingAccount(CSecurityFtdcTradingAccountField *pTradingAccount,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryTradingAccount(MNConv<SecurityFtdcTradingAccountField^, CSecurityFtdcTradingAccountField>::N2M(pTradingAccount),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryDepthMarketData(CSecurityFtdcDepthMarketDataField *pDepthMarketData,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryDepthMarketData(MNConv<SecurityFtdcDepthMarketDataField^, CSecurityFtdcDepthMarketDataField>::N2M(pDepthMarketData),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryInvestorPositionDetail(CSecurityFtdcInvestorPositionDetailField *pInvestorPositionDetail,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryInvestorPositionDetail(MNConv<SecurityFtdcInvestorPositionDetailField^, CSecurityFtdcInvestorPositionDetailField>::N2M(pInvestorPositionDetail),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryBondInterest(CSecurityFtdcBondInterestField *pBondInterest,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryBondInterest(MNConv<SecurityFtdcBondInterestField^, CSecurityFtdcBondInterestField>::N2M(pBondInterest),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryOrder(CSecurityFtdcOrderField *pOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryOrder(MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryTrade(CSecurityFtdcTradeField *pTrade,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryTrade(MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryInvestorPosition(CSecurityFtdcInvestorPositionField *pInvestorPosition,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		p_OnRspQryInvestorPosition(MNConv<SecurityFtdcInvestorPositionField^, CSecurityFtdcInvestorPositionField>::N2M(pInvestorPosition),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRtnOrder(CSecurityFtdcOrderField *pOrder,CSecurityFtdcOrderField *pOrder){
		p_OnRtnOrder(MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder),MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder));
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRtnTrade(CSecurityFtdcTradeField *pTrade,CSecurityFtdcTradeField *pTrade){
		p_OnRtnTrade(MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade),MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade));
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnErrRtnOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo){
		p_OnErrRtnOrderInsert(MNConv<SecurityFtdcInputOrderField^, CSecurityFtdcInputOrderField>::N2M(pInputOrder),RspInfoField(pRspInfo));
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnErrRtnOrderAction(CSecurityFtdcOrderActionField *pOrderAction,CSecurityFtdcRspInfoField *pRspInfo){
		p_OnErrRtnOrderAction(MNConv<SecurityFtdcOrderActionField^, CSecurityFtdcOrderActionField>::N2M(pOrderAction),RspInfoField(pRspInfo));
	};

	///////////////////////////////////////////////////////////////融资融券新增部分
	///Liber发起出金应答
	void CLTSTraderSpi::OnRspFundOutByLiber(CSecurityFtdcInputFundTransferField *pInputFundTransfer, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
	{
		p_OnRspFundOutByLiber(MNConv<SecurityFtdcInputFundTransferField^, CSecurityFtdcInputFundTransferField>::N2M(pInputFundTransfer),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};

	///Liber发起出金通知
	void CLTSTraderSpi::OnRtnFundOutByLiber(CSecurityFtdcFundTransferField *pFundTransfer)
	{
		p_OnRtnFundOutByLiber(MNConv<SecurityFtdcFundTransferField^, CSecurityFtdcFundTransferField>::N2M(pFundTransfer));
	};

	///iber发起出金错误回报
	void CLTSTraderSpi::OnErrRtnFundOutByLiber(CSecurityFtdcInputFundTransferField *pInputFundTransfer, CSecurityFtdcRspInfoField *pRspInfo)
	{
		p_OnErrRtnFundOutByLiber(MNConv<SecurityFtdcInputFundTransferField^, CSecurityFtdcInputFundTransferField>::N2M(pInputFundTransfer),RspInfoField(pRspInfo));
	};

	///银行发起入金通知
	void CLTSTraderSpi::OnRtnFundInByBank(CSecurityFtdcFundTransferField *pFundTransfer)
	{
		p_OnRtnFundInByBank(MNConv<SecurityFtdcFundTransferField^, CSecurityFtdcFundTransferField>::N2M(pFundTransfer));
	};

	///资金转账查询应答
	void CLTSTraderSpi::OnRspQryFundTransferSerial(CSecurityFtdcFundTransferField *pFundTransfer, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
	{
		p_OnRspQryFundTransferSerial(MNConv<SecurityFtdcFundTransferField^, CSecurityFtdcFundTransferField>::N2M(pFundTransfer),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};

#else
	///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
	void CLTSTraderSpi::OnFrontConnected(){
		m_pAdapter->OnFrontConnected();
	};
	
	///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
	///@param nReason 错误原因
	///        0x1001 网络读失败
	///        0x1002 网络写失败
	///        0x2001 接收心跳超时
	///        0x2002 发送心跳失败
	///        0x2003 收到错误报文
	void CLTSTraderSpi::OnFrontDisconnected(int nReason){
		m_pAdapter->OnFrontDisconnected(nReason);
	};

	///心跳超时警告。当长时间未收到报文时，该方法被调用。
	///@param nTimeLapse 距离上次接收报文的时间
	void CLTSTraderSpi::OnHeartBeatWarning(int nTimeLapse){
		m_pAdapter->OnHeartBeatWarning(nTimeLapse);
	};

	///客户端认证响应
	/*void CLTSTraderSpi::OnRspAuthenticate(CIndexFtdcRspAuthenticateField *pRspAuthenticateField, CIndexFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
	m_pAdapter->OnRspAuthenticate(MNConv<ThostFtdcRspAuthenticateField^,CIndexFtdcRspAuthenticateField>::N2M(pRspAuthenticateField), RspInfoField(pRspInfo), nRequestID, bIsLast);
	};*/


	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspError(CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspError(RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspUserLogin(CSecurityFtdcRspUserLoginField *pRspUserLogin,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspUserLogin(MNConv<SecurityFtdcRspUserLoginField^, CSecurityFtdcRspUserLoginField>::N2M(pRspUserLogin),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspUserLogout(CSecurityFtdcUserLogoutField *pUserLogout,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspUserLogout(MNConv<SecurityFtdcUserLogoutField^, CSecurityFtdcUserLogoutField>::N2M(pUserLogout),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspOrderInsert(MNConv<SecurityFtdcInputOrderField^, CSecurityFtdcInputOrderField>::N2M(pInputOrder),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspOrderAction(CSecurityFtdcInputOrderActionField *pInputOrderAction,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspOrderAction(MNConv<SecurityFtdcInputOrderActionField^, CSecurityFtdcInputOrderActionField>::N2M(pInputOrderAction),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspUserPasswordUpdate(CSecurityFtdcUserPasswordUpdateField *pUserPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspUserPasswordUpdate(MNConv<SecurityFtdcUserPasswordUpdateField^, CSecurityFtdcUserPasswordUpdateField>::N2M(pUserPasswordUpdate),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspTradingAccountPasswordUpdate(CSecurityFtdcTradingAccountPasswordUpdateField *pTradingAccountPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspTradingAccountPasswordUpdate(MNConv<SecurityFtdcTradingAccountPasswordUpdateField^, CSecurityFtdcTradingAccountPasswordUpdateField>::N2M(pTradingAccountPasswordUpdate),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryExchange(CSecurityFtdcExchangeField *pExchange,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryExchange(MNConv<SecurityFtdcExchangeField^, CSecurityFtdcExchangeField>::N2M(pExchange),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryInstrument(CSecurityFtdcInstrumentField *pInstrument,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryInstrument(MNConv<SecurityFtdcInstrumentField^, CSecurityFtdcInstrumentField>::N2M(pInstrument),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryInvestor(CSecurityFtdcInvestorField *pInvestor,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryInvestor(MNConv<SecurityFtdcInvestorField^, CSecurityFtdcInvestorField>::N2M(pInvestor),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryTradingCode(CSecurityFtdcTradingCodeField *pTradingCode,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryTradingCode(MNConv<SecurityFtdcTradingCodeField^, CSecurityFtdcTradingCodeField>::N2M(pTradingCode),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryTradingAccount(CSecurityFtdcTradingAccountField *pTradingAccount,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryTradingAccount(MNConv<SecurityFtdcTradingAccountField^, CSecurityFtdcTradingAccountField>::N2M(pTradingAccount),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryDepthMarketData(CSecurityFtdcDepthMarketDataField *pDepthMarketData,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryDepthMarketData(MNConv<SecurityFtdcDepthMarketDataField^, CSecurityFtdcDepthMarketDataField>::N2M(pDepthMarketData),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryInvestorPositionDetail(CSecurityFtdcInvestorPositionDetailField *pInvestorPositionDetail,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryInvestorPositionDetail(MNConv<SecurityFtdcInvestorPositionDetailField^, CSecurityFtdcInvestorPositionDetailField>::N2M(pInvestorPositionDetail),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryBondInterest(CSecurityFtdcBondInterestField *pBondInterest,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryBondInterest(MNConv<SecurityFtdcBondInterestField^, CSecurityFtdcBondInterestField>::N2M(pBondInterest),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryOrder(CSecurityFtdcOrderField *pOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryOrder(MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryTrade(CSecurityFtdcTradeField *pTrade,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryTrade(MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRspQryInvestorPosition(CSecurityFtdcInvestorPositionField *pInvestorPosition,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		m_pAdapter->OnRspQryInvestorPosition(MNConv<SecurityFtdcInvestorPositionField^, CSecurityFtdcInvestorPositionField>::N2M(pInvestorPosition),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRtnOrder(CSecurityFtdcOrderField *pOrder){
		m_pAdapter->OnRtnOrder(MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder));
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnRtnTrade(CSecurityFtdcTradeField *pTrade){
		m_pAdapter->OnRtnTrade(MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade));
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnErrRtnOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo){
		m_pAdapter->OnErrRtnOrderInsert(MNConv<SecurityFtdcInputOrderField^, CSecurityFtdcInputOrderField>::N2M(pInputOrder),RspInfoField(pRspInfo));
	};
	/// <summary>
	/// 
	/// </summary>
	void CLTSTraderSpi::OnErrRtnOrderAction(CSecurityFtdcOrderActionField *pOrderAction,CSecurityFtdcRspInfoField *pRspInfo){
		m_pAdapter->OnErrRtnOrderAction(MNConv<SecurityFtdcOrderActionField^, CSecurityFtdcOrderActionField>::N2M(pOrderAction),RspInfoField(pRspInfo));
	};

	///////////////////////////////////////////////////////////////融资融券新增部分
	///Liber发起出金应答
	void CLTSTraderSpi::OnRspFundOutByLiber(CSecurityFtdcInputFundTransferField *pInputFundTransfer, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
	{
		m_pAdapter->OnRspFundOutByLiber(MNConv<SecurityFtdcInputFundTransferField^, CSecurityFtdcInputFundTransferField>::N2M(pInputFundTransfer),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};

	///Liber发起出金通知
	void CLTSTraderSpi::OnRtnFundOutByLiber(CSecurityFtdcFundTransferField *pFundTransfer)
	{
		m_pAdapter->OnRtnFundOutByLiber(MNConv<SecurityFtdcFundTransferField^, CSecurityFtdcFundTransferField>::N2M(pFundTransfer));
	};

	///iber发起出金错误回报
	void CLTSTraderSpi::OnErrRtnFundOutByLiber(CSecurityFtdcInputFundTransferField *pInputFundTransfer, CSecurityFtdcRspInfoField *pRspInfo)
	{
		m_pAdapter->OnErrRtnFundOutByLiber(MNConv<SecurityFtdcInputFundTransferField^, CSecurityFtdcInputFundTransferField>::N2M(pInputFundTransfer),RspInfoField(pRspInfo));
	};

	///银行发起入金通知
	void CLTSTraderSpi::OnRtnFundInByBank(CSecurityFtdcFundTransferField *pFundTransfer)
	{
		m_pAdapter->OnRtnFundInByBank(MNConv<SecurityFtdcFundTransferField^, CSecurityFtdcFundTransferField>::N2M(pFundTransfer));
	};

	///资金转账查询应答
	void CLTSTraderSpi::OnRspQryFundTransferSerial(CSecurityFtdcFundTransferField *pFundTransfer, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
	{
		m_pAdapter->OnRspQryFundTransferSerial(MNConv<SecurityFtdcFundTransferField^, CSecurityFtdcFundTransferField>::N2M(pFundTransfer),RspInfoField(pRspInfo),nRequestID,bIsLast);
	};

#endif
};