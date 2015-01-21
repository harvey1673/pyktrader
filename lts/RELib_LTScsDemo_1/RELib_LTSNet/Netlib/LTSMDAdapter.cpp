/*!
* \file LTSMDAdapter.cpp
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
#include "LTSMdSpi.h"
#include "LTSMDAdapter.h"
#include <memory.h>

using namespace RELib_LTSNative;

namespace RELib_LTSNet
{

	/// <summary>
	///创建LTSMDAdapter
	///存贮订阅信息文件的目录，默认为当前目录
	/// </summary>
	LTSMDAdapter::LTSMDAdapter(void)
	{
		m_pApi =CSecurityFtdcMdApi::CreateFtdcMdApi();
		m_pSpi = new CLTSMdSpi(this);
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
	LTSMDAdapter::LTSMDAdapter(String^ pszFlowPath)
	{
		CAutoStrPtr asp(pszFlowPath);
		//CAutoStrPtr arg2(pszUserApiType);

		m_pApi = CSecurityFtdcMdApi::CreateFtdcMdApi(asp.m_pChar);
		m_pSpi = new CLTSMdSpi(this);
#ifdef __LTS_MA__
		RegisterCallbacks();
#endif	
		m_pApi->RegisterSpi(m_pSpi);
	}

	LTSMDAdapter::~LTSMDAdapter(void)
	{
		Release();
	}
	///删除接口对象本身
	///@remark 不再使用本接口对象时,调用该函数删除接口对象
	void LTSMDAdapter::Release(void)
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
	///初始化
	///@remark 初始化运行环境,只有调用后,接口才开始工作
	void LTSMDAdapter::Init(void)
	{
		m_pApi->Init();
	}

	///等待接口线程结束运行
	///@return 线程退出代码
	int LTSMDAdapter::Join(void)
	{
		return m_pApi->Join();
	}

	///获取当前交易日
	///@retrun 获取到的交易日
	///@remark 只有登录成功后,才能得到正确的交易日
	String^ LTSMDAdapter::GetTradingDay()
	{
		return gcnew String(m_pApi->GetTradingDay());
	}

	///注册前置机网络地址
	///@param pszFrontAddress：前置机网络地址。
	///@remark 网络地址的格式为：“protocol://ipaddress:port”，如：”tcp://127.0.0.1:12001”。 
	///@remark “tcp”代表传输协议，“127.0.0.1”代表服务器地址。”12001”代表服务器端口号。
	///@remark RegisterFront优先于RegisterNameServer
	void LTSMDAdapter::RegisterFront(String^  pszFrontAddress)
	{
		CAutoStrPtr asp = CAutoStrPtr(pszFrontAddress);
		m_pApi->RegisterFront(asp.m_pChar);
	}		

	///注册回调接口
	///@param pSpi 派生自回调接口类的实例
	/*void LTSMDAdapter::RegisterSpi(CSecurityFtdcMdSpi *pSpi){
		CSecurityFtdcMdApi native;
		MNConv<SecurityFtdcMdApi^, CSecurityFtdcMdApi>::M2N(pSpi, &native);
		return m_pApi->RegisterSpi(&native);
	}	*/		

	///加载证书
	///@param pszCertFileName 用户证书文件名
	///@param pszKeyFileName 用户私钥文件名
	///@param pszCaFileName 可信任CA证书文件名
	///@param pszKeyFilePassword 用户私钥文件密码
	///@return 0 操作成功
	///@return -1 可信任CA证书载入失败
	///@return -2 用户证书载入失败
	///@return -3 用户私钥载入失败	
	///@return -4 用户证书校验失败
	// int RegisterCertificateFile(const char *pszCertFileName, const char *pszKeyFileName, 
	//	const char *pszCaFileName, const char *pszKeyFilePassword) = 0;

	///订阅市场行情。
	///@param nTopicID 市场行情主题  
	///@param nResumeType 市场行情重传方式  
	///        TERT_RESTART:从本交易日开始重传
	///        TERT_RESUME:从上次收到的续传
	///        TERT_QUICK:先传送当前行情快照,再传送登录后市场行情的内容
	///@remark 该方法要在Init方法前调用。若不调用则不会收到私有流的数据。
	int LTSMDAdapter::SubscribeMarketData(array<String^>^ ppInstrumentID, int nCount, String^ pExchageID){
		if(ppInstrumentID == nullptr || ppInstrumentID->Length <= 0)
			return -1;

		

		int count = ppInstrumentID->Length;
		char** pp = new char*[count];
		CAutoStrPtr** asp = new CAutoStrPtr*[count];
		for(int i=0; i<count; i++)
		{
			//智能指针，可以自动释放 string指针
			CAutoStrPtr* ptr = new CAutoStrPtr(ppInstrumentID[i]);
			asp[i] = ptr;
			pp[i] = ptr->m_pChar;
		}
		CAutoStrPtr asp2 = CAutoStrPtr(pExchageID);
		int result = m_pApi->SubscribeMarketData(pp,nCount,asp2.m_pChar);

		// 释放所有分配的字符串内存
		for(int i=0; i<count; i++)
			delete asp[i];
		delete asp;
		delete pp;

		return result;
	}

	int LTSMDAdapter::UnSubscribeMarketData(array<String^>^ ppInstrumentID, int nCount, String^ pExchageID)
	{
		if(ppInstrumentID == nullptr || ppInstrumentID->Length <= 0)
			return -1;

		nCount = ppInstrumentID->Length;
		char** pp = new char*[nCount];
		CAutoStrPtr** asp = new CAutoStrPtr*[nCount];
		for(int i=0; i<nCount; i++)
		{
			CAutoStrPtr* ptr = new CAutoStrPtr(ppInstrumentID[i]);
			asp[i] = ptr;
			pp[i] = ptr->m_pChar;
		}
		CAutoStrPtr asp2 = CAutoStrPtr(pExchageID);
		int result = m_pApi->UnSubscribeMarketData(pp, nCount,asp2.m_pChar);

		// 释放所分配的字符串内存
		for(int i=0; i<nCount; i++)
			delete asp[i];
		delete asp;
		delete pp;

		return result;
	}
	

	/// <summary>
	/// 用户登录请求
	/// </summary>
	int LTSMDAdapter::ReqUserLogin(SecurityFtdcReqUserLoginField^ pReqUserLoginField, int nRequestID)
	{
		CSecurityFtdcReqUserLoginField native;
		MNConv<SecurityFtdcReqUserLoginField^, CSecurityFtdcReqUserLoginField>::M2N(pReqUserLoginField, &native);
		return m_pApi->ReqUserLogin(&native, nRequestID);
	}

	/// <summary>
	/// 
	/// </summary>
	int LTSMDAdapter::ReqUserLogout(SecurityFtdcUserLogoutField^ pUserLogout, int nRequestID)
	{
		CSecurityFtdcUserLogoutField native0;
		MNConv<SecurityFtdcUserLogoutField^, CSecurityFtdcUserLogoutField>::M2N(pUserLogout, &native0);

		return m_pApi->ReqUserLogout(&native0, nRequestID);
	}
	

#ifdef __LTS_MA__

	// 将所有回调函数地址传递给SPI，并保存对delegate的引用
	void LTSMDAdapter::RegisterCallbacks()
	{
		m_pSpi->d_FrontConnected = gcnew Internal_FrontConnected(this, &LTSMDAdapter::cbk_OnFrontConnected);
		m_pSpi->p_OnFrontConnected = (Callback_OnFrontConnected)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_FrontConnected).ToPointer();

		m_pSpi->d_FrontDisconnected = gcnew Internal_FrontDisconnected(this, &LTSMDAdapter::cbk_OnFrontDisconnected);
		m_pSpi->p_OnFrontDisconnected = (Callback_OnFrontDisconnected)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_FrontDisconnected).ToPointer();

		m_pSpi->d_HeartBeatWarning = gcnew Internal_HeartBeatWarning(this, &LTSMDAdapter::cbk_OnHeartBeatWarning);
		m_pSpi->p_OnHeartBeatWarning = (Callback_OnHeartBeatWarning)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_HeartBeatWarning).ToPointer();



		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspError = gcnew Internal_RspError(this, &LTSMDAdapter::cbk_OnRspError);
		m_pSpi->p_OnRspError = (Callback_OnRspError)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspError).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspUserLogin = gcnew Internal_RspUserLogin(this, &LTSMDAdapter::cbk_OnRspUserLogin);
		m_pSpi->p_OnRspUserLogin = (Callback_OnRspUserLogin)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspUserLogin).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspUserLogout = gcnew Internal_RspUserLogout(this, &LTSMDAdapter::cbk_OnRspUserLogout);
		m_pSpi->p_OnRspUserLogout = (Callback_OnRspUserLogout)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspUserLogout).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspOrderInsert = gcnew Internal_RspOrderInsert(this, &LTSMDAdapter::cbk_OnRspOrderInsert);
		m_pSpi->p_OnRspOrderInsert = (Callback_OnRspOrderInsert)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspOrderInsert).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspOrderAction = gcnew Internal_RspOrderAction(this, &LTSMDAdapter::cbk_OnRspOrderAction);
		m_pSpi->p_OnRspOrderAction = (Callback_OnRspOrderAction)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspOrderAction).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspUserPasswordUpdate = gcnew Internal_RspUserPasswordUpdate(this, &LTSMDAdapter::cbk_OnRspUserPasswordUpdate);
		m_pSpi->p_OnRspUserPasswordUpdate = (Callback_OnRspUserPasswordUpdate)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspUserPasswordUpdate).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspTradingAccountPasswordUpdate = gcnew Internal_RspTradingAccountPasswordUpdate(this, &LTSMDAdapter::cbk_OnRspTradingAccountPasswordUpdate);
		m_pSpi->p_OnRspTradingAccountPasswordUpdate = (Callback_OnRspTradingAccountPasswordUpdate)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspTradingAccountPasswordUpdate).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryExchange = gcnew Internal_RspQryExchange(this, &LTSMDAdapter::cbk_OnRspQryExchange);
		m_pSpi->p_OnRspQryExchange = (Callback_OnRspQryExchange)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryExchange).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryInstrument = gcnew Internal_RspQryInstrument(this, &LTSMDAdapter::cbk_OnRspQryInstrument);
		m_pSpi->p_OnRspQryInstrument = (Callback_OnRspQryInstrument)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryInstrument).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryInvestor = gcnew Internal_RspQryInvestor(this, &LTSMDAdapter::cbk_OnRspQryInvestor);
		m_pSpi->p_OnRspQryInvestor = (Callback_OnRspQryInvestor)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryInvestor).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryTradingCode = gcnew Internal_RspQryTradingCode(this, &LTSMDAdapter::cbk_OnRspQryTradingCode);
		m_pSpi->p_OnRspQryTradingCode = (Callback_OnRspQryTradingCode)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryTradingCode).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryTradingAccount = gcnew Internal_RspQryTradingAccount(this, &LTSMDAdapter::cbk_OnRspQryTradingAccount);
		m_pSpi->p_OnRspQryTradingAccount = (Callback_OnRspQryTradingAccount)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryTradingAccount).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryDepthMarketData = gcnew Internal_RspQryDepthMarketData(this, &LTSMDAdapter::cbk_OnRspQryDepthMarketData);
		m_pSpi->p_OnRspQryDepthMarketData = (Callback_OnRspQryDepthMarketData)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryDepthMarketData).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryInvestorPositionDetail = gcnew Internal_RspQryInvestorPositionDetail(this, &LTSMDAdapter::cbk_OnRspQryInvestorPositionDetail);
		m_pSpi->p_OnRspQryInvestorPositionDetail = (Callback_OnRspQryInvestorPositionDetail)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryInvestorPositionDetail).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryBondInterest = gcnew Internal_RspQryBondInterest(this, &LTSMDAdapter::cbk_OnRspQryBondInterest);
		m_pSpi->p_OnRspQryBondInterest = (Callback_OnRspQryBondInterest)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryBondInterest).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryOrder = gcnew Internal_RspQryOrder(this, &LTSMDAdapter::cbk_OnRspQryOrder);
		m_pSpi->p_OnRspQryOrder = (Callback_OnRspQryOrder)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryOrder).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryTrade = gcnew Internal_RspQryTrade(this, &LTSMDAdapter::cbk_OnRspQryTrade);
		m_pSpi->p_OnRspQryTrade = (Callback_OnRspQryTrade)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryTrade).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RspQryInvestorPosition = gcnew Internal_RspQryInvestorPosition(this, &LTSMDAdapter::cbk_OnRspQryInvestorPosition);
		m_pSpi->p_OnRspQryInvestorPosition = (Callback_OnRspQryInvestorPosition)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RspQryInvestorPosition).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RtnOrder = gcnew Internal_RtnOrder(this, &LTSMDAdapter::cbk_OnRtnOrder);
		m_pSpi->p_OnRtnOrder = (Callback_OnRtnOrder)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RtnOrder).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_RtnTrade = gcnew Internal_RtnTrade(this, &LTSMDAdapter::cbk_OnRtnTrade);
		m_pSpi->p_OnRtnTrade = (Callback_OnRtnTrade)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_RtnTrade).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_ErrRtnOrderInsert = gcnew Internal_ErrRtnOrderInsert(this, &LTSMDAdapter::cbk_OnErrRtnOrderInsert);
		m_pSpi->p_OnErrRtnOrderInsert = (Callback_OnErrRtnOrderInsert)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_ErrRtnOrderInsert).ToPointer();
		/// <summary>
		/// 
		/// </summary>
		m_pSpi->d_ErrRtnOrderAction = gcnew Internal_ErrRtnOrderAction(this, &LTSMDAdapter::cbk_OnErrRtnOrderAction);
		m_pSpi->p_OnErrRtnOrderAction = (Callback_OnErrRtnOrderAction)Marshal::GetFunctionPointerForDelegate(m_pSpi->d_ErrRtnOrderAction).ToPointer();
	}

	// ------------------------------------ Callbacks ------------------------------------
	void LTSMDAdapter::cbk_OnFrontConnected(){
		this->OnFrontConnected();
	}
	void LTSMDAdapter::cbk_OnFrontDisconnected(int nReason){
		this->OnFrontDisconnected(nReason);
	}
	void LTSMDAdapter::cbk_OnHeartBeatWarning(int nTimeLapse){
		this->OnHeartBeatWarning(nTimeLapse);
	}
	


	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspError(CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspError(RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspUserLogin(CSecurityFtdcRspUserLoginField *pRspUserLogin,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspUserLogin(MNConv<SecurityFtdcRspUserLoginField^, CSecurityFtdcRspUserLoginField>::N2M(pRspUserLogin),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspUserLogout(CSecurityFtdcUserLogoutField *pUserLogout,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspUserLogout(MNConv<SecurityFtdcUserLogoutField^, CSecurityFtdcUserLogoutField>::N2M(pUserLogout),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspOrderInsert(MNConv<SecurityFtdcInputOrderField^, CSecurityFtdcInputOrderField>::N2M(pInputOrder),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspOrderAction(CSecurityFtdcInputOrderActionField *pInputOrderAction,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspOrderAction(MNConv<SecurityFtdcInputOrderActionField^, CSecurityFtdcInputOrderActionField>::N2M(pInputOrderAction),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspUserPasswordUpdate(CSecurityFtdcUserPasswordUpdateField *pUserPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspUserPasswordUpdate(MNConv<SecurityFtdcUserPasswordUpdateField^, CSecurityFtdcUserPasswordUpdateField>::N2M(pUserPasswordUpdate),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspTradingAccountPasswordUpdate(CSecurityFtdcTradingAccountPasswordUpdateField *pTradingAccountPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspTradingAccountPasswordUpdate(MNConv<SecurityFtdcTradingAccountPasswordUpdateField^, CSecurityFtdcTradingAccountPasswordUpdateField>::N2M(pTradingAccountPasswordUpdate),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryExchange(CSecurityFtdcExchangeField *pExchange,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryExchange(MNConv<SecurityFtdcExchangeField^, CSecurityFtdcExchangeField>::N2M(pExchange),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryInstrument(CSecurityFtdcInstrumentField *pInstrument,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryInstrument(MNConv<SecurityFtdcInstrumentField^, CSecurityFtdcInstrumentField>::N2M(pInstrument),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryInvestor(CSecurityFtdcInvestorField *pInvestor,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryInvestor(MNConv<SecurityFtdcInvestorField^, CSecurityFtdcInvestorField>::N2M(pInvestor),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryTradingCode(CSecurityFtdcTradingCodeField *pTradingCode,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryTradingCode(MNConv<SecurityFtdcTradingCodeField^, CSecurityFtdcTradingCodeField>::N2M(pTradingCode),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryTradingAccount(CSecurityFtdcTradingAccountField *pTradingAccount,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryTradingAccount(MNConv<SecurityFtdcTradingAccountField^, CSecurityFtdcTradingAccountField>::N2M(pTradingAccount),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryDepthMarketData(CSecurityFtdcDepthMarketDataField *pDepthMarketData,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryDepthMarketData(MNConv<SecurityFtdcDepthMarketDataField^, CSecurityFtdcDepthMarketDataField>::N2M(pDepthMarketData),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryInvestorPositionDetail(CSecurityFtdcInvestorPositionDetailField *pInvestorPositionDetail,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryInvestorPositionDetail(MNConv<SecurityFtdcInvestorPositionDetailField^, CSecurityFtdcInvestorPositionDetailField>::N2M(pInvestorPositionDetail),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryBondInterest(CSecurityFtdcBondInterestField *pBondInterest,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryBondInterest(MNConv<SecurityFtdcBondInterestField^, CSecurityFtdcBondInterestField>::N2M(pBondInterest),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryOrder(CSecurityFtdcOrderField *pOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryOrder(MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryTrade(CSecurityFtdcTradeField *pTrade,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryTrade(MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRspQryInvestorPosition(CSecurityFtdcInvestorPositionField *pInvestorPosition,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast)
	{
		this->OnRspQryInvestorPosition(MNConv<SecurityFtdcInvestorPositionField^, CSecurityFtdcInvestorPositionField>::N2M(pInvestorPosition),RspInfoField(pRspInfo),nRequestID,bIsLast);
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRtnOrder(CSecurityFtdcOrderField *pOrder,CSecurityFtdcOrderField *pOrder)
	{
		this->OnRtnOrder(MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder),MNConv<SecurityFtdcOrderField^, CSecurityFtdcOrderField>::N2M(pOrder));
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnRtnTrade(CSecurityFtdcTradeField *pTrade,CSecurityFtdcTradeField *pTrade)
	{
		this->OnRtnTrade(MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade),MNConv<SecurityFtdcTradeField^, CSecurityFtdcTradeField>::N2M(pTrade));
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnErrRtnOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo)
	{
		this->OnErrRtnOrderInsert(MNConv<SecurityFtdcInputOrderField^, CSecurityFtdcInputOrderField>::N2M(pInputOrder),RspInfoField(pRspInfo));
	}
	/// <summary>
	/// 
	/// </summary>
	void LTSMDAdapter::cbk_OnErrRtnOrderAction(CSecurityFtdcOrderActionField *pOrderAction,CSecurityFtdcRspInfoField *pRspInfo)
	{
		this->OnErrRtnOrderAction(MNConv<SecurityFtdcOrderActionField^, CSecurityFtdcOrderActionField>::N2M(pOrderAction),RspInfoField(pRspInfo));
	}
#endif


}// end of namespace



