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

#pragma once
#include "Util.h"
#include "LTSTraderSpi.h"

using namespace RELib_LTSNative;

namespace  RELib_LTSNative{
	class CLTSTraderSpi;
};


namespace RELib_LTSNet
{

	/// <summary>
	/// 托管类,TraderAPI Adapter
	/// </summary>
	public ref class LTSTraderAdapter
	{
	public:
		/// <summary>
		///创建LTSTraderAdapter
		///存贮订阅信息文件的目录，默认为当前目录
		/// </summary>
		LTSTraderAdapter(void);
		/// <summary>
		///创建LTSTraderAdapter
		/// </summary>
		/// <param name="pszFlowPath">存贮订阅信息文件的目录，默认为当前目录</param>
		/// <param name="bIsUsingUdp">是否使用UDP协议</param>
		LTSTraderAdapter(String^ pszFlowPath,String^ pszUserApiType);
	private:
		~LTSTraderAdapter(void);
		CSecurityFtdcTraderApi* m_pApi;
		CLTSTraderSpi* m_pSpi;
	public:
		///删除接口对象本身
		///@remark 不再使用本接口对象时,调用该函数删除接口对象
		void Release();

		///初始化
		///@remark 初始化运行环境,只有调用后,接口才开始工作
		void Init();

		///等待接口线程结束运行
		///@return 线程退出代码
		int Join();

		///获取当前交易日
		///@retrun 获取到的交易日
		///@remark 只有登录成功后,才能得到正确的交易日
		String^ GetTradingDay();

		///注册前置机网络地址
		///@param pszFrontAddress：前置机网络地址。
		///@remark 网络地址的格式为：“protocol://ipaddress:port”，如：”tcp://127.0.0.1:17001”。 
		///@remark “tcp”代表传输协议，“127.0.0.1”代表服务器地址。”17001”代表服务器端口号。
		void RegisterFront(String^ pszFrontAddress);


		///订阅私有流。
		///@param nResumeType 私有流重传方式  
		///        SECURITY_TERT_RESTART:从本交易日开始重传
		///        SECURITY_TERT_RESUME:从上次收到的续传
		///        SECURITY_TERT_QUICK:只传送登录后私有流的内容
		///@remark 该方法要在Init方法前调用。若不调用则不会收到私有流的数据。
		void SubscribePrivateTopic(EnumRESUMETYPE nResumeType);

		///订阅公共流。
		///@param nResumeType 公共流重传方式  
		///        SECURITY_TERT_RESTART:从本交易日开始重传
		///        SECURITY_TERT_RESUME:从上次收到的续传
		///        SECURITY_TERT_QUICK:只传送登录后公共流的内容
		///@remark 该方法要在Init方法前调用。若不调用则不会收到公共流的数据。
		void SubscribePublicTopic(EnumRESUMETYPE nResumeType);
		

		///用户登录请求
		int ReqUserLogin(SecurityFtdcReqUserLoginField^ pReqUserLoginField, int nRequestID);


		/// <summary>
		/// 
		/// </summary>
		int ReqUserLogout(SecurityFtdcUserLogoutField^ pUserLogout, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqOrderInsert(SecurityFtdcInputOrderField^ pInputOrder, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqOrderAction(SecurityFtdcInputOrderActionField^ pInputOrderAction, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqUserPasswordUpdate(SecurityFtdcUserPasswordUpdateField^ pUserPasswordUpdate, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqTradingAccountPasswordUpdate(SecurityFtdcTradingAccountPasswordUpdateField^ pTradingAccountPasswordUpdate, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqQryExchange(SecurityFtdcQryExchangeField^ pQryExchange, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqQryInstrument(SecurityFtdcQryInstrumentField^ pQryInstrument, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqQryInvestor(SecurityFtdcQryInvestorField^ pQryInvestor, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqQryTradingCode(SecurityFtdcQryTradingCodeField^ pQryTradingCode, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqQryTradingAccount(SecurityFtdcQryTradingAccountField^ pQryTradingAccount, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqQryDepthMarketData(SecurityFtdcQryDepthMarketDataField^ pQryDepthMarketData, int nRequestID);
		/*/// <summary>
		/// 
		/// </summary>
		int ReqQryInvestorPositionDetail(SecurityFtdcQryInvestorPositionDetailField^ pQryInvestorPositionDetail, int nRequestID);*/
		/// <summary>
		/// 
		/// </summary>
		int ReqQryBondInterest(SecurityFtdcQryBondInterestField^ pQryBondInterest, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqQryOrder(SecurityFtdcQryOrderField^ pQryOrder, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqQryTrade(SecurityFtdcQryTradeField^ pQryTrade, int nRequestID);
		/// <summary>
		/// 
		/// </summary>
		int ReqQryInvestorPosition(SecurityFtdcQryInvestorPositionField^ pQryInvestorPosition, int nRequestID);

		///////////////////////////////////////////////////////////////融资融券新增部分
		///请求查询市值配售信息
		 int ReqQryMarketRationInfo(SecurityFtdcQryMarketRationInfoField^ pQryMarketRationInfo, int nRequestID);

		///请求查询合约手续费率
		 int ReqQryInstrumentCommissionRate(SecurityFtdcQryInstrumentCommissionRateField^ pQryInstrumentCommissionRate, int nRequestID);

		 ///Liber发起出金请求
		 virtual int ReqFundOutByLiber(SecurityFtdcInputFundTransferField^ pInputFundTransfer, int nRequestID);

		 ///资金转账查询请求
		 virtual int ReqQryFundTransferSerial(SecurityFtdcQryFundTransferSerialField^ pQryFundTransferSerial, int nRequestID);
		//events
	public:
		/// <summary>
		/// 当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
		/// </summary>
		event FrontConnected^ OnFrontConnected {
			void add(FrontConnected^ handler ) {
				FrontConnected_delegate += handler;
			}
			void remove(FrontConnected^ handler) {
				FrontConnected_delegate -= handler;
			}
			void raise() {
				if(FrontConnected_delegate)
					FrontConnected_delegate();
			}
		}
		/// <summary>
		/// 当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
		/// 错误原因
		/// 0x1001 网络读失败
		/// 0x1002 网络写失败
		/// 0x2001 接收心跳超时
		/// 0x2002 发送心跳失败
		/// 0x2003 收到错误报文
		/// </summary>
		event FrontDisconnected^ OnFrontDisconnected {
			void add(FrontDisconnected^ handler ) {
				FrontDisconnected_delegate += handler;
			}
			void remove(FrontDisconnected^ handler) {
				FrontDisconnected_delegate -= handler;
			}
			void raise(int nReason) {
				if(FrontDisconnected_delegate)
					FrontDisconnected_delegate(nReason);
			}
		}
		///心跳超时警告。当长时间未收到报文时，该方法被调用。
		///@param nTimeLapse 距离上次接收报文的时间
		event HeartBeatWarning^ OnHeartBeatWarning{
			void add(HeartBeatWarning^ handler ) {
				HeartBeatWarning_delegate += handler;
			}
			void remove(HeartBeatWarning^ handler) {
				HeartBeatWarning_delegate -= handler;
			}
			void raise(int nTimeLapse) {
				if(HeartBeatWarning_delegate)
					HeartBeatWarning_delegate(nTimeLapse);
			}
		}


		
		/// <summary>
		/// 
		/// </summary>
		event RspError^ OnRspError{
			void add(RspError^ handler) { RspError_delegate += handler; }
			void remove(RspError^ handler) { RspError_delegate -= handler; }
			void raise(SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspError_delegate) RspError_delegate(pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspUserLogin^ OnRspUserLogin{
			void add(RspUserLogin^ handler) { RspUserLogin_delegate += handler; }
			void remove(RspUserLogin^ handler) { RspUserLogin_delegate -= handler; }
			void raise(SecurityFtdcRspUserLoginField^ pRspUserLogin,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspUserLogin_delegate) RspUserLogin_delegate(pRspUserLogin,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspUserLogout^ OnRspUserLogout{
			void add(RspUserLogout^ handler) { RspUserLogout_delegate += handler; }
			void remove(RspUserLogout^ handler) { RspUserLogout_delegate -= handler; }
			void raise(SecurityFtdcUserLogoutField^ pUserLogout,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspUserLogout_delegate) RspUserLogout_delegate(pUserLogout,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspOrderInsert^ OnRspOrderInsert{
			void add(RspOrderInsert^ handler) { RspOrderInsert_delegate += handler; }
			void remove(RspOrderInsert^ handler) { RspOrderInsert_delegate -= handler; }
			void raise(SecurityFtdcInputOrderField^ pInputOrder,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspOrderInsert_delegate) RspOrderInsert_delegate(pInputOrder,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspOrderAction^ OnRspOrderAction{
			void add(RspOrderAction^ handler) { RspOrderAction_delegate += handler; }
			void remove(RspOrderAction^ handler) { RspOrderAction_delegate -= handler; }
			void raise(SecurityFtdcInputOrderActionField^ pInputOrderAction,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspOrderAction_delegate) RspOrderAction_delegate(pInputOrderAction,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspUserPasswordUpdate^ OnRspUserPasswordUpdate{
			void add(RspUserPasswordUpdate^ handler) { RspUserPasswordUpdate_delegate += handler; }
			void remove(RspUserPasswordUpdate^ handler) { RspUserPasswordUpdate_delegate -= handler; }
			void raise(SecurityFtdcUserPasswordUpdateField^ pUserPasswordUpdate,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspUserPasswordUpdate_delegate) RspUserPasswordUpdate_delegate(pUserPasswordUpdate,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspTradingAccountPasswordUpdate^ OnRspTradingAccountPasswordUpdate{
			void add(RspTradingAccountPasswordUpdate^ handler) { RspTradingAccountPasswordUpdate_delegate += handler; }
			void remove(RspTradingAccountPasswordUpdate^ handler) { RspTradingAccountPasswordUpdate_delegate -= handler; }
			void raise(SecurityFtdcTradingAccountPasswordUpdateField^ pTradingAccountPasswordUpdate,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspTradingAccountPasswordUpdate_delegate) RspTradingAccountPasswordUpdate_delegate(pTradingAccountPasswordUpdate,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryExchange^ OnRspQryExchange{
			void add(RspQryExchange^ handler) { RspQryExchange_delegate += handler; }
			void remove(RspQryExchange^ handler) { RspQryExchange_delegate -= handler; }
			void raise(SecurityFtdcExchangeField^ pExchange,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryExchange_delegate) RspQryExchange_delegate(pExchange,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryInstrument^ OnRspQryInstrument{
			void add(RspQryInstrument^ handler) { RspQryInstrument_delegate += handler; }
			void remove(RspQryInstrument^ handler) { RspQryInstrument_delegate -= handler; }
			void raise(SecurityFtdcInstrumentField^ pInstrument,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryInstrument_delegate) RspQryInstrument_delegate(pInstrument,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryInvestor^ OnRspQryInvestor{
			void add(RspQryInvestor^ handler) { RspQryInvestor_delegate += handler; }
			void remove(RspQryInvestor^ handler) { RspQryInvestor_delegate -= handler; }
			void raise(SecurityFtdcInvestorField^ pInvestor,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryInvestor_delegate) RspQryInvestor_delegate(pInvestor,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryTradingCode^ OnRspQryTradingCode{
			void add(RspQryTradingCode^ handler) { RspQryTradingCode_delegate += handler; }
			void remove(RspQryTradingCode^ handler) { RspQryTradingCode_delegate -= handler; }
			void raise(SecurityFtdcTradingCodeField^ pTradingCode,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryTradingCode_delegate) RspQryTradingCode_delegate(pTradingCode,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryTradingAccount^ OnRspQryTradingAccount{
			void add(RspQryTradingAccount^ handler) { RspQryTradingAccount_delegate += handler; }
			void remove(RspQryTradingAccount^ handler) { RspQryTradingAccount_delegate -= handler; }
			void raise(SecurityFtdcTradingAccountField^ pTradingAccount,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryTradingAccount_delegate) RspQryTradingAccount_delegate(pTradingAccount,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryDepthMarketData^ OnRspQryDepthMarketData{
			void add(RspQryDepthMarketData^ handler) { RspQryDepthMarketData_delegate += handler; }
			void remove(RspQryDepthMarketData^ handler) { RspQryDepthMarketData_delegate -= handler; }
			void raise(SecurityFtdcDepthMarketDataField^ pDepthMarketData,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryDepthMarketData_delegate) RspQryDepthMarketData_delegate(pDepthMarketData,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryInvestorPositionDetail^ OnRspQryInvestorPositionDetail{
			void add(RspQryInvestorPositionDetail^ handler) { RspQryInvestorPositionDetail_delegate += handler; }
			void remove(RspQryInvestorPositionDetail^ handler) { RspQryInvestorPositionDetail_delegate -= handler; }
			void raise(SecurityFtdcInvestorPositionDetailField^ pInvestorPositionDetail,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryInvestorPositionDetail_delegate) RspQryInvestorPositionDetail_delegate(pInvestorPositionDetail,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryBondInterest^ OnRspQryBondInterest{
			void add(RspQryBondInterest^ handler) { RspQryBondInterest_delegate += handler; }
			void remove(RspQryBondInterest^ handler) { RspQryBondInterest_delegate -= handler; }
			void raise(SecurityFtdcBondInterestField^ pBondInterest,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryBondInterest_delegate) RspQryBondInterest_delegate(pBondInterest,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryOrder^ OnRspQryOrder{
			void add(RspQryOrder^ handler) { RspQryOrder_delegate += handler; }
			void remove(RspQryOrder^ handler) { RspQryOrder_delegate -= handler; }
			void raise(SecurityFtdcOrderField^ pOrder,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryOrder_delegate) RspQryOrder_delegate(pOrder,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryTrade^ OnRspQryTrade{
			void add(RspQryTrade^ handler) { RspQryTrade_delegate += handler; }
			void remove(RspQryTrade^ handler) { RspQryTrade_delegate -= handler; }
			void raise(SecurityFtdcTradeField^ pTrade,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryTrade_delegate) RspQryTrade_delegate(pTrade,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RspQryInvestorPosition^ OnRspQryInvestorPosition{
			void add(RspQryInvestorPosition^ handler) { RspQryInvestorPosition_delegate += handler; }
			void remove(RspQryInvestorPosition^ handler) { RspQryInvestorPosition_delegate -= handler; }
			void raise(SecurityFtdcInvestorPositionField^ pInvestorPosition,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(RspQryInvestorPosition_delegate) RspQryInvestorPosition_delegate(pInvestorPosition,pRspInfo,nRequestID,bIsLast);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RtnOrder^ OnRtnOrder{
			void add(RtnOrder^ handler) { RtnOrder_delegate += handler; }
			void remove(RtnOrder^ handler) { RtnOrder_delegate -= handler; }
			void raise(SecurityFtdcOrderField^ pOrder) {
				if(RtnOrder_delegate) RtnOrder_delegate(pOrder);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event RtnTrade^ OnRtnTrade{
			void add(RtnTrade^ handler) { RtnTrade_delegate += handler; }
			void remove(RtnTrade^ handler) { RtnTrade_delegate -= handler; }
			void raise(SecurityFtdcTradeField^ pTrade) {
				if(RtnTrade_delegate) RtnTrade_delegate(pTrade);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event ErrRtnOrderInsert^ OnErrRtnOrderInsert{
			void add(ErrRtnOrderInsert^ handler) { ErrRtnOrderInsert_delegate += handler; }
			void remove(ErrRtnOrderInsert^ handler) { ErrRtnOrderInsert_delegate -= handler; }
			void raise(SecurityFtdcInputOrderField^ pInputOrder,SecurityFtdcRspInfoField^ pRspInfo) {
				if(ErrRtnOrderInsert_delegate) ErrRtnOrderInsert_delegate(pInputOrder,pRspInfo);
			}
		}
		/// <summary>
		/// 
		/// </summary>
		event ErrRtnOrderAction^ OnErrRtnOrderAction{
			void add(ErrRtnOrderAction^ handler) { ErrRtnOrderAction_delegate += handler; }
			void remove(ErrRtnOrderAction^ handler) { ErrRtnOrderAction_delegate -= handler; }
			void raise(SecurityFtdcOrderActionField^ pOrderAction,SecurityFtdcRspInfoField^ pRspInfo) {
				if(ErrRtnOrderAction_delegate) ErrRtnOrderAction_delegate(pOrderAction,pRspInfo);
			}
		}
		
		///////////////////////////////////////////////////////////////融资融券新增部分
		/// <summary>
		/// 发起出金应答
		/// </summary>
		event RspFundOutByLiber^ OnRspFundOutByLiber{
			void add(RspFundOutByLiber^ handler) { OnRspFundOutByLiber_delegate += handler; }
			void remove(RspFundOutByLiber^ handler) { OnRspFundOutByLiber_delegate -= handler; }
			void raise(SecurityFtdcInputFundTransferField^ pInputFundTransfer,SecurityFtdcRspInfoField^ pRspInfo, int nRequestID, bool bIsLast) {
				if(OnRspFundOutByLiber_delegate) OnRspFundOutByLiber_delegate(pInputFundTransfer,pRspInfo,nRequestID,bIsLast);
			}
		}


		event RtnFundOutByLiber^ OnRtnFundOutByLiber{
			void add(RtnFundOutByLiber^ handler) { OnRtnFundOutByLiber_delegate += handler; }
			void remove(RtnFundOutByLiber^ handler) { OnRtnFundOutByLiber_delegate -= handler; }
			void raise(SecurityFtdcFundTransferField^ pInputFundTransfer) {
				if(OnRtnFundOutByLiber_delegate) OnRtnFundOutByLiber_delegate(pInputFundTransfer);
			}
		}

		event ErrRtnFundOutByLiber^ OnErrRtnFundOutByLiber{
			void add(ErrRtnFundOutByLiber^ handler) { OnErrRtnFundOutByLiber_delegate += handler; }
			void remove(ErrRtnFundOutByLiber^ handler) { OnErrRtnFundOutByLiber_delegate -= handler; }
			void raise(SecurityFtdcInputFundTransferField^ pInputFundTransfer,SecurityFtdcRspInfoField^ pRspInfo) {
				if(OnErrRtnFundOutByLiber_delegate) OnErrRtnFundOutByLiber_delegate(pInputFundTransfer,pRspInfo);
			}
		}

		event RtnFundInByBank^ OnRtnFundInByBank{
			void add(RtnFundInByBank^ handler) { OnRtnFundInByBank_delegate += handler; }
			void remove(RtnFundInByBank^ handler) { OnRtnFundInByBank_delegate -= handler; }
			void raise(SecurityFtdcFundTransferField^ pInputFundTransfer) {
				if(OnRtnFundInByBank_delegate) OnRtnFundInByBank_delegate(pInputFundTransfer);
			}
		}

		/// <summary>
		/// 
		/// </summary>
		event RspQryFundTransferSerial^ OnRspQryFundTransferSerial{
			void add(RspQryFundTransferSerial^ handler) { OnRspQryFundTransferSerial_delegate += handler; }
			void remove(RspQryFundTransferSerial^ handler) { OnRspQryFundTransferSerial_delegate -= handler; }
			void raise(SecurityFtdcFundTransferField^ pInvestorPosition,SecurityFtdcRspInfoField^ pRspInfo,int nRequestID, bool bIsLast) {
				if(OnRspQryFundTransferSerial_delegate) OnRspQryFundTransferSerial_delegate(pInvestorPosition,pRspInfo,nRequestID,bIsLast);
			}
		}
		// delegates
	private:
		///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
		FrontConnected^ FrontConnected_delegate;

		///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
		///@param nReason 错误原因
		///        0x1001 网络读失败
		///        0x1002 网络写失败
		///        0x2001 接收心跳超时
		///        0x2002 发送心跳失败
		///        0x2003 收到错误报文
		FrontDisconnected^ FrontDisconnected_delegate;

		///心跳超时警告。当长时间未收到报文时，该方法被调用。
		///@param nTimeLapse 距离上次接收报文的时间
		HeartBeatWarning^ HeartBeatWarning_delegate;

		

		RspError^ RspError_delegate;
		RspUserLogin^ RspUserLogin_delegate;
		RspUserLogout^ RspUserLogout_delegate;
		RspOrderInsert^ RspOrderInsert_delegate;
		RspOrderAction^ RspOrderAction_delegate;
		RspUserPasswordUpdate^ RspUserPasswordUpdate_delegate;
		RspTradingAccountPasswordUpdate^ RspTradingAccountPasswordUpdate_delegate;
		RspQryExchange^ RspQryExchange_delegate;
		RspQryInstrument^ RspQryInstrument_delegate;
		RspQryInvestor^ RspQryInvestor_delegate;
		RspQryTradingCode^ RspQryTradingCode_delegate;
		RspQryTradingAccount^ RspQryTradingAccount_delegate;
		RspQryDepthMarketData^ RspQryDepthMarketData_delegate;
		RspQryInvestorPositionDetail^ RspQryInvestorPositionDetail_delegate;
		RspQryBondInterest^ RspQryBondInterest_delegate;
		RspQryOrder^ RspQryOrder_delegate;
		RspQryTrade^ RspQryTrade_delegate;
		RspQryInvestorPosition^ RspQryInvestorPosition_delegate;
		RtnOrder^ RtnOrder_delegate;
		RtnTrade^ RtnTrade_delegate;
		ErrRtnOrderInsert^ ErrRtnOrderInsert_delegate;
		ErrRtnOrderAction^ ErrRtnOrderAction_delegate;


		///////////////////////////////////////////////////////////////融资融券新增部分
		///Liber发起出金应答
		RspFundOutByLiber^ OnRspFundOutByLiber_delegate;

		///Liber发起出金通知
		RtnFundOutByLiber^ OnRtnFundOutByLiber_delegate;

		///iber发起出金错误回报
		ErrRtnFundOutByLiber^ OnErrRtnFundOutByLiber_delegate;

		///银行发起入金通知
		RtnFundInByBank^ OnRtnFundInByBank_delegate;

		///资金转账查询应答
		RspQryFundTransferSerial^ OnRspQryFundTransferSerial_delegate;
#ifdef __LTS_MA__
		// callbacks for MA
	private:
		///默认
		///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
		void cbk_OnFrontConnected();

		///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
		///@param nReason 错误原因
		///        0x1001 网络读失败
		///        0x1002 网络写失败
		///        0x2001 接收心跳超时
		///        0x2002 发送心跳失败
		///        0x2003 收到错误报文
		void cbk_OnFrontDisconnected(int nReason);

		///心跳超时警告。当长时间未收到报文时，该方法被调用。
		///@param nTimeLapse 距离上次接收报文的时间
		void cbk_OnHeartBeatWarning(int nTimeLapse);


		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspError(CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspUserLogin(CSecurityFtdcRspUserLoginField *pRspUserLogin,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspUserLogout(CSecurityFtdcUserLogoutField *pUserLogout,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspOrderAction(CSecurityFtdcInputOrderActionField *pInputOrderAction,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspUserPasswordUpdate(CSecurityFtdcUserPasswordUpdateField *pUserPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspTradingAccountPasswordUpdate(CSecurityFtdcTradingAccountPasswordUpdateField *pTradingAccountPasswordUpdate,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryExchange(CSecurityFtdcExchangeField *pExchange,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryInstrument(CSecurityFtdcInstrumentField *pInstrument,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryInvestor(CSecurityFtdcInvestorField *pInvestor,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryTradingCode(CSecurityFtdcTradingCodeField *pTradingCode,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryTradingAccount(CSecurityFtdcTradingAccountField *pTradingAccount,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryDepthMarketData(CSecurityFtdcDepthMarketDataField *pDepthMarketData,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryInvestorPositionDetail(CSecurityFtdcInvestorPositionDetailField *pInvestorPositionDetail,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryBondInterest(CSecurityFtdcBondInterestField *pBondInterest,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryOrder(CSecurityFtdcOrderField *pOrder,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryTrade(CSecurityFtdcTradeField *pTrade,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRspQryInvestorPosition(CSecurityFtdcInvestorPositionField *pInvestorPosition,CSecurityFtdcRspInfoField *pRspInfo,int nRequestID, bool bIsLast);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRtnOrder(CSecurityFtdcOrderField *pOrder,CSecurityFtdcOrderField *pOrder);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnRtnTrade(CSecurityFtdcTradeField *pTrade,CSecurityFtdcTradeField *pTrade);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnErrRtnOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo);
		/// <summary>
		/// 
		/// </summary>
		void cbk_OnErrRtnOrderAction(CSecurityFtdcOrderActionField *pOrderAction,CSecurityFtdcRspInfoField *pRspInfo);

		/// <summary>
		/// 将所有回调函数地址传递给SPI
		/// </summary>
		void RegisterCallbacks();
#endif
	};
}
