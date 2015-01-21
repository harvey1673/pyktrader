/*!
* \file LTSTraderAdapter.cpp
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

using namespace RELib_LTSNative;

namespace RELib_LTSNet
{

	/// <summary>
	///托管类,TraderAPI Adapter 创建LTSMDAdapter
	///存贮订阅信息文件的目录，默认为当前目录
	/// </summary>
	LTSTraderAdapter::LTSTraderAdapter(void)
	{
		m_pApi =CSecurityFtdcTraderApi::CreateFtdcTraderApi();
		m_pSpi = new CLTSTraderSpi(this);
#ifdef __LTS_MA__
		RegisterCallbacks();
#endif
		m_pApi->RegisterSpi(m_pSpi);
	}

	/// <summary>
	///创建LTSMDAdapter
	/// </summary>
	/// <param name="pszFlowPath">存贮订阅信息文件的目录，默认为当前目录</param>
	/// <param name="bIsUsingUdp">是否使用UDP协议</param>
	LTSTraderAdapter::LTSTraderAdapter(String^ pszFlowPath, String^ pszUserApiType)
	{
		CAutoStrPtr asp(pszFlowPath);
		CAutoStrPtr arg2(pszUserApiType);

		m_pApi = CSecurityFtdcTraderApi::CreateFtdcTraderApi(asp.m_pChar);
		m_pSpi = new CLTSTraderSpi(this);
#ifdef __LTS_MA__
		RegisterCallbacks();
#endif	
		m_pApi->RegisterSpi(m_pSpi);
	}

	LTSTraderAdapter::~LTSTraderAdapter(void)
	{
		Release();
	}
	void LTSTraderAdapter::Release(void)
	{
		if(m_pApi)
		{
			m_pApi->RegisterSpi(0);
			m_pApi->Release();
			m_pApi = nullptr;
			delete m_pSpi;
			m_pSpi = nullptr;
		}
	}
	///注册前置机网络地址
	void LTSTraderAdapter::RegisterFront(String^  pszFrontAddress)
	{
		CAutoStrPtr asp = CAutoStrPtr(pszFrontAddress);
		m_pApi->RegisterFront(asp.m_pChar);
	}
	

	///订阅私有流。
	void LTSTraderAdapter::SubscribePrivateTopic(EnumRESUMETYPE nResumeType)
	{
		m_pApi->SubscribePrivateTopic((SECURITY_TE_RESUME_TYPE)nResumeType);
	}
	///订阅公共流
	void LTSTraderAdapter::SubscribePublicTopic(EnumRESUMETYPE nResumeType)
	{
		m_pApi->SubscribePublicTopic((SECURITY_TE_RESUME_TYPE)nResumeType);
	}

	void LTSTraderAdapter::Init(void)
	{
		m_pApi->Init();
	}

	int LTSTraderAdapter::Join(void)
	{
		return m_pApi->Join();
	}

	String^ LTSTraderAdapter::GetTradingDay()
	{
		return gcnew String(m_pApi->GetTradingDay());
	}
	
	///用户登录请求
	int LTSTraderAdapter::ReqUserLogin(SecurityFtdcReqUserLoginField^ pReqUserLoginField, int nRequestID)
	{
		CSecurityFtdcReqUserLoginField native;
		MNConv<SecurityFtdcReqUserLoginField^, CSecurityFtdcReqUserLoginField>::M2N(pReqUserLoginField, &native);
		int result = m_pApi->ReqUserLogin(&native, nRequestID);
		return result;
	}


	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqUserLogout(SecurityFtdcUserLogoutField^ pUserLogout, int nRequestID)
	{
		CSecurityFtdcUserLogoutField native0;
		MNConv<SecurityFtdcUserLogoutField^, CSecurityFtdcUserLogoutField>::M2N(pUserLogout, &native0);

		return m_pApi->ReqUserLogout(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqOrderInsert(SecurityFtdcInputOrderField^ pInputOrder, int nRequestID)
	{
		CSecurityFtdcInputOrderField native0;
		MNConv<SecurityFtdcInputOrderField^, CSecurityFtdcInputOrderField>::M2N(pInputOrder, &native0);

		//return -1;
		return m_pApi->ReqOrderInsert(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqOrderAction(SecurityFtdcInputOrderActionField^ pInputOrderAction, int nRequestID)
	{
		CSecurityFtdcInputOrderActionField native0;
		MNConv<SecurityFtdcInputOrderActionField^, CSecurityFtdcInputOrderActionField>::M2N(pInputOrderAction, &native0);

		return m_pApi->ReqOrderAction(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqUserPasswordUpdate(SecurityFtdcUserPasswordUpdateField^ pUserPasswordUpdate, int nRequestID)
	{
		CSecurityFtdcUserPasswordUpdateField native0;
		MNConv<SecurityFtdcUserPasswordUpdateField^, CSecurityFtdcUserPasswordUpdateField>::M2N(pUserPasswordUpdate, &native0);

		return m_pApi->ReqUserPasswordUpdate(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqTradingAccountPasswordUpdate(SecurityFtdcTradingAccountPasswordUpdateField^ pTradingAccountPasswordUpdate, int nRequestID)
	{
		CSecurityFtdcTradingAccountPasswordUpdateField native0;
		MNConv<SecurityFtdcTradingAccountPasswordUpdateField^, CSecurityFtdcTradingAccountPasswordUpdateField>::M2N(pTradingAccountPasswordUpdate, &native0);

		return m_pApi->ReqTradingAccountPasswordUpdate(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryExchange(SecurityFtdcQryExchangeField^ pQryExchange, int nRequestID)
	{
		CSecurityFtdcQryExchangeField native0;
		MNConv<SecurityFtdcQryExchangeField^, CSecurityFtdcQryExchangeField>::M2N(pQryExchange, &native0);

		return m_pApi->ReqQryExchange(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryInstrument(SecurityFtdcQryInstrumentField^ pQryInstrument, int nRequestID)
	{
		CSecurityFtdcQryInstrumentField native0;
		MNConv<SecurityFtdcQryInstrumentField^, CSecurityFtdcQryInstrumentField>::M2N(pQryInstrument, &native0);

		return m_pApi->ReqQryInstrument(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryInvestor(SecurityFtdcQryInvestorField^ pQryInvestor, int nRequestID)
	{
		CSecurityFtdcQryInvestorField native0;
		MNConv<SecurityFtdcQryInvestorField^, CSecurityFtdcQryInvestorField>::M2N(pQryInvestor, &native0);

		return m_pApi->ReqQryInvestor(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryTradingCode(SecurityFtdcQryTradingCodeField^ pQryTradingCode, int nRequestID)
	{
		CSecurityFtdcQryTradingCodeField native0;
		MNConv<SecurityFtdcQryTradingCodeField^, CSecurityFtdcQryTradingCodeField>::M2N(pQryTradingCode, &native0);

		return m_pApi->ReqQryTradingCode(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryTradingAccount(SecurityFtdcQryTradingAccountField^ pQryTradingAccount, int nRequestID)
	{
		CSecurityFtdcQryTradingAccountField native0;
		MNConv<SecurityFtdcQryTradingAccountField^, CSecurityFtdcQryTradingAccountField>::M2N(pQryTradingAccount, &native0);

		return m_pApi->ReqQryTradingAccount(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryDepthMarketData(SecurityFtdcQryDepthMarketDataField^ pQryDepthMarketData, int nRequestID)
	{
		CSecurityFtdcQryDepthMarketDataField native0;
		MNConv<SecurityFtdcQryDepthMarketDataField^, CSecurityFtdcQryDepthMarketDataField>::M2N(pQryDepthMarketData, &native0);

		return m_pApi->ReqQryDepthMarketData(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	/*int LTSTraderAdapter::ReqQryInvestorPositionDetail(SecurityFtdcQryInvestorPositionDetailField^ pQryInvestorPositionDetail, int nRequestID)
	{
		CSecurityFtdcQryInvestorPositionDetailField native0;
		MNConv<SecurityFtdcQryInvestorPositionDetailField^, CSecurityFtdcQryInvestorPositionDetailField>::M2N(pQryInvestorPositionDetail, &native0);

		return m_pApi->ReqQryInvestorPositionDetail(&native0, nRequestID);
	}*/
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryBondInterest(SecurityFtdcQryBondInterestField^ pQryBondInterest, int nRequestID)
	{
		CSecurityFtdcQryBondInterestField native0;
		MNConv<SecurityFtdcQryBondInterestField^, CSecurityFtdcQryBondInterestField>::M2N(pQryBondInterest, &native0);

		return m_pApi->ReqQryBondInterest(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryOrder(SecurityFtdcQryOrderField^ pQryOrder, int nRequestID)
	{
		CSecurityFtdcQryOrderField native0;
		MNConv<SecurityFtdcQryOrderField^, CSecurityFtdcQryOrderField>::M2N(pQryOrder, &native0);

		return m_pApi->ReqQryOrder(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryTrade(SecurityFtdcQryTradeField^ pQryTrade, int nRequestID)
	{
		CSecurityFtdcQryTradeField native0;
		MNConv<SecurityFtdcQryTradeField^, CSecurityFtdcQryTradeField>::M2N(pQryTrade, &native0);

		return m_pApi->ReqQryTrade(&native0, nRequestID);
	}
	/// <summary>
	/// 
	/// </summary>
	int LTSTraderAdapter::ReqQryInvestorPosition(SecurityFtdcQryInvestorPositionField^ pQryInvestorPosition, int nRequestID)
	{
		CSecurityFtdcQryInvestorPositionField native0;
		MNConv<SecurityFtdcQryInvestorPositionField^, CSecurityFtdcQryInvestorPositionField>::M2N(pQryInvestorPosition, &native0);

		return m_pApi->ReqQryInvestorPosition(&native0, nRequestID);
	}

	///////////////////////////////////////////////////////////////融资融券新增部分
	///请求查询市值配售信息
	int LTSTraderAdapter:: ReqQryMarketRationInfo(SecurityFtdcQryMarketRationInfoField^ pQryMarketRationInfo, int nRequestID)
	{
		CSecurityFtdcQryMarketRationInfoField native0;
		MNConv<SecurityFtdcQryMarketRationInfoField^, CSecurityFtdcQryMarketRationInfoField>::M2N(pQryMarketRationInfo, &native0);

		return m_pApi->ReqQryMarketRationInfo(&native0, nRequestID);
	}

	///请求查询合约手续费率
	int LTSTraderAdapter:: ReqQryInstrumentCommissionRate(SecurityFtdcQryInstrumentCommissionRateField^ pQryInstrumentCommissionRate, int nRequestID)
	{
		CSecurityFtdcQryInstrumentCommissionRateField native0;
		MNConv<SecurityFtdcQryInstrumentCommissionRateField^, CSecurityFtdcQryInstrumentCommissionRateField>::M2N(pQryInstrumentCommissionRate, &native0);

		return m_pApi->ReqQryInstrumentCommissionRate(&native0, nRequestID);
	}

	///Liber发起出金请求
	int LTSTraderAdapter:: ReqFundOutByLiber(SecurityFtdcInputFundTransferField^ pInputFundTransfer, int nRequestID)
	{
		CSecurityFtdcInputFundTransferField native0;
		MNConv<SecurityFtdcInputFundTransferField^, CSecurityFtdcInputFundTransferField>::M2N(pInputFundTransfer, &native0);

		return m_pApi->ReqFundOutByLiber(&native0, nRequestID);
	}

	///资金转账查询请求
	int LTSTraderAdapter:: ReqQryFundTransferSerial(SecurityFtdcQryFundTransferSerialField^ pQryFundTransferSerial, int nRequestID)
	{
		CSecurityFtdcQryFundTransferSerialField native0;
		MNConv<SecurityFtdcQryFundTransferSerialField^, CSecurityFtdcQryFundTransferSerialField>::M2N(pQryFundTransferSerial, &native0);

		return m_pApi->ReqQryFundTransferSerial(&native0, nRequestID);
	}


#ifdef __LTS_MA__

	//------------------------------------ Callbacks ------------------------------------
	void LTSTraderAdapter::cbk_OnFrontConnected(){
		this->OnFrontConnected();
	}
	void LTSTraderAdapter::cbk_OnFrontDisconnected(int nReason){
		this->OnFrontDisconnected(nReason);
	}
	void LTSTraderAdapter::cbk_OnHeartBeatWarning(int nTimeLapse){
		this->OnHeartBeatWarning(nTimeLapse);
	}


	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspError(CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspError(RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspUserLogin(CSecurityFtdcRspUserLoginField *pRspUserLogin,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspUserLogin(MNConv<SecurityFtdcRspUserLoginField^, CSecurityFtdcRspUserLoginField>::N2M(pRspUserLogin),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspUserLogout(CSecurityFtdcUserLogoutField *pUserLogout,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspUserLogout(MNConv<SecurityFtdcUserLogoutField^, CSecurityFtdcUserLogoutField>::N2M(pUserLogout),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspOrderInsert(MNConv<SecurityFtdcInputOrderField^, CSecurityFtdcInputOrderField>::N2M(pInputOrder),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspOrderAction(CSecurityFtdcInputOrderActionField *pInputOrderAction,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspOrderAction(MNConv<SecurityFtdcInputOrderActionField^, CSecurityFtdcInputOrderActionField>::N2M(pInputOrderAction),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspUserPasswordUpdate(CSecurityFtdcUserPasswordUpdateField *pUserPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspUserPasswordUpdate(MNConv<SecurityFtdcUserPasswordUpdateField^, CSecurityFtdcUserPasswordUpdateField>::N2M(pUserPasswordUpdate),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspTradingAccountPasswordUpdate(CSecurityFtdcTradingAccountPasswordUpdateField *pTradingAccountPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspTradingAccountPasswordUpdate(MNConv<SecurityFtdcTradingAccountPasswordUpdateField^, CSecurityFtdcTradingAccountPasswordUpdateField>::N2M(pTradingAccountPasswordUpdate),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryExchange(CSecurityFtdcExchangeField *pExchange,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryExchange(MNConv<SecurityFtdcExchangeField^, CSecurityFtdcExchangeField>::N2M(pExchange),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryInstrument(CSecurityFtdcInstrumentField *pInstrument,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryInstrument(MNConv<SecurityFtdcInstrumentField^, CSecurityFtdcInstrumentField>::N2M(pInstrument),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryInvestor(CSecurityFtdcInvestorField *pInvestor,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryInvestor(MNConv<SecurityFtdcInvestorField^, CSecurityFtdcInvestorField>::N2M(pInvestor),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryTradingCode(CSecurityFtdcTradingCodeField *pTradingCode,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryTradingCode(MNConv<SecurityFtdcTradingCodeField^, CSecurityFtdcTradingCodeField>::N2M(pTradingCode),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryTradingAccount(CSecurityFtdcTradingAccountField *pTradingAccount,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryTradingAccount(MNConv<SecurityFtdcTradingAccountField^, CSecurityFtdcTradingAccountField>::N2M(pTradingAccount),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryDepthMarketData(CSecurityFtdcDepthMarketDataField *pDepthMarketData,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryDepthMarketData(MNConv<SecurityFtdcDepthMarketDataField^, CSecurityFtdcDepthMarketDataField>::N2M(pDepthMarketData),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryInvestorPositionDetail(CSecurityFtdcInvestorPositionDetailField *pInvestorPositionDetail,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryInvestorPositionDetail(MNConv<SecurityFtdcInvestorPositionDetailField^, CSecurityFtdcInvestorPositionDetailField>::N2M(pInvestorPositionDetail),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryBondInterest(CSecurityFtdcBondInterestField *pBondInterest,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryBondInterest(MNConv<SecurityFtdcBondInterestField^, CSecurityFtdcBondInterestField>::N2M(pBondInterest),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryOrder(CSecurityFtdcOrderField *pOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryOrder(MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryTrade(CSecurityFtdcTradeField *pTrade,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryTrade(MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRspQryInvestorPosition(CSecurityFtdcInvestorPositionField *pInvestorPosition,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast){
		this->OnRspQryInvestorPosition(MNConv<SecurityFtdcInvestorPositionField^, CSecurityFtdcInvestorPositionField>::N2M(pInvestorPosition),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRtnOrder(CSecurityFtdcOrderField *pOrder){
		this->OnRtnOrder(MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder));
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnRtnTrade(CSecurityFtdcTradeField *pTrade){
		this->OnRtnTrade(MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade));
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnErrRtnOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo){
		this->OnErrRtnOrderInsert(MNConv<SecurityFtdcInputOrderField^, CSecurityFtdcInputOrderField>::N2M(pInputOrder),RspInfoField(pRspInfo));
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSTraderAdapter::cbk_OnErrRtnOrderAction(CSecurityFtdcOrderActionField *pOrderAction,CSecurityFtdcRspInfoField *pRspInfo){
		this->OnErrRtnOrderAction(MNConv<SecurityFtdcOrderActionField^, CSecurityFtdcOrderActionField>::N2M(pOrderAction),RspInfoField(pRspInfo));
	}

	// 将所有回调函数地址传递给SPI，并保存对delegate的引用
	void LTSTraderAdapter::RegisterCallbacks()
	{
		m_pSpi->d_FrontConnected = gcnew Internal_FrontConnected(this, &LTSTraderAdapter::cbk_OnFrontConnected);
		m_pSpi->p_OnFrontConnected = (Callback_OnFrontConnected)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_FrontConnected).ToPointer();

		m_pSpi->d_FrontDisconnected = gcnew Internal_FrontDisconnected(this, &LTSTraderAdapter::cbk_OnFrontDisconnected);
		m_pSpi->p_OnFrontDisconnected = (Callback_OnFrontDisconnected)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_FrontDisconnected).ToPointer();

		m_pSpi->d_HeartBeatWarning = gcnew Internal_HeartBeatWarning(this, &LTSTraderAdapter::cbk_OnHeartBeatWarning);
		m_pSpi->p_OnHeartBeatWarning = (Callback_OnHeartBeatWarning)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_HeartBeatWarning).ToPointer();

		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspError = gcnew Internal_RspError(this, &LTSTraderAdapter::cbk_OnRspError);
		m_pSpi->p_OnRspError = (Callback_OnRspError)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspError).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspUserLogin = gcnew Internal_RspUserLogin(this, &LTSTraderAdapter::cbk_OnRspUserLogin);
		m_pSpi->p_OnRspUserLogin = (Callback_OnRspUserLogin)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspUserLogin).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspUserLogout = gcnew Internal_RspUserLogout(this, &LTSTraderAdapter::cbk_OnRspUserLogout);
		m_pSpi->p_OnRspUserLogout = (Callback_OnRspUserLogout)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspUserLogout).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspOrderInsert = gcnew Internal_RspOrderInsert(this, &LTSTraderAdapter::cbk_OnRspOrderInsert);
		m_pSpi->p_OnRspOrderInsert = (Callback_OnRspOrderInsert)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspOrderInsert).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspOrderAction = gcnew Internal_RspOrderAction(this, &LTSTraderAdapter::cbk_OnRspOrderAction);
		m_pSpi->p_OnRspOrderAction = (Callback_OnRspOrderAction)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspOrderAction).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspUserPasswordUpdate = gcnew Internal_RspUserPasswordUpdate(this, &LTSTraderAdapter::cbk_OnRspUserPasswordUpdate);
		m_pSpi->p_OnRspUserPasswordUpdate = (Callback_OnRspUserPasswordUpdate)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspUserPasswordUpdate).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspTradingAccountPasswordUpdate = gcnew Internal_RspTradingAccountPasswordUpdate(this, &LTSTraderAdapter::cbk_OnRspTradingAccountPasswordUpdate);
		m_pSpi->p_OnRspTradingAccountPasswordUpdate = (Callback_OnRspTradingAccountPasswordUpdate)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspTradingAccountPasswordUpdate).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryExchange = gcnew Internal_RspQryExchange(this, &LTSTraderAdapter::cbk_OnRspQryExchange);
		m_pSpi->p_OnRspQryExchange = (Callback_OnRspQryExchange)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryExchange).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryInstrument = gcnew Internal_RspQryInstrument(this, &LTSTraderAdapter::cbk_OnRspQryInstrument);
		m_pSpi->p_OnRspQryInstrument = (Callback_OnRspQryInstrument)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryInstrument).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryInvestor = gcnew Internal_RspQryInvestor(this, &LTSTraderAdapter::cbk_OnRspQryInvestor);
		m_pSpi->p_OnRspQryInvestor = (Callback_OnRspQryInvestor)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryInvestor).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryTradingCode = gcnew Internal_RspQryTradingCode(this, &LTSTraderAdapter::cbk_OnRspQryTradingCode);
		m_pSpi->p_OnRspQryTradingCode = (Callback_OnRspQryTradingCode)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryTradingCode).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryTradingAccount = gcnew Internal_RspQryTradingAccount(this, &LTSTraderAdapter::cbk_OnRspQryTradingAccount);
		m_pSpi->p_OnRspQryTradingAccount = (Callback_OnRspQryTradingAccount)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryTradingAccount).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryDepthMarketData = gcnew Internal_RspQryDepthMarketData(this, &LTSTraderAdapter::cbk_OnRspQryDepthMarketData);
		m_pSpi->p_OnRspQryDepthMarketData = (Callback_OnRspQryDepthMarketData)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryDepthMarketData).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryInvestorPositionDetail = gcnew Internal_RspQryInvestorPositionDetail(this, &LTSTraderAdapter::cbk_OnRspQryInvestorPositionDetail);
		m_pSpi->p_OnRspQryInvestorPositionDetail = (Callback_OnRspQryInvestorPositionDetail)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryInvestorPositionDetail).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryBondInterest = gcnew Internal_RspQryBondInterest(this, &LTSTraderAdapter::cbk_OnRspQryBondInterest);
		m_pSpi->p_OnRspQryBondInterest = (Callback_OnRspQryBondInterest)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryBondInterest).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryOrder = gcnew Internal_RspQryOrder(this, &LTSTraderAdapter::cbk_OnRspQryOrder);
		m_pSpi->p_OnRspQryOrder = (Callback_OnRspQryOrder)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryOrder).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryTrade = gcnew Internal_RspQryTrade(this, &LTSTraderAdapter::cbk_OnRspQryTrade);
		m_pSpi->p_OnRspQryTrade = (Callback_OnRspQryTrade)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryTrade).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryInvestorPosition = gcnew Internal_RspQryInvestorPosition(this, &LTSTraderAdapter::cbk_OnRspQryInvestorPosition);
		m_pSpi->p_OnRspQryInvestorPosition = (Callback_OnRspQryInvestorPosition)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryInvestorPosition).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RtnOrder = gcnew Internal_RtnOrder(this, &LTSTraderAdapter::cbk_OnRtnOrder);
		m_pSpi->p_OnRtnOrder = (Callback_OnRtnOrder)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RtnOrder).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RtnTrade = gcnew Internal_RtnTrade(this, &LTSTraderAdapter::cbk_OnRtnTrade);
		m_pSpi->p_OnRtnTrade = (Callback_OnRtnTrade)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RtnTrade).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_ErrRtnOrderInsert = gcnew Internal_ErrRtnOrderInsert(this, &LTSTraderAdapter::cbk_OnErrRtnOrderInsert);
		m_pSpi->p_OnErrRtnOrderInsert = (Callback_OnErrRtnOrderInsert)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_ErrRtnOrderInsert).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_ErrRtnOrderAction = gcnew Internal_ErrRtnOrderAction(this, &LTSTraderAdapter::cbk_OnErrRtnOrderAction);
		m_pSpi->p_OnErrRtnOrderAction = (Callback_OnErrRtnOrderAction)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_ErrRtnOrderAction).ToPointer();
	}
#endif

} // end of namespace
