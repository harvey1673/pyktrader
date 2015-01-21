using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using RELib_LTSNet;
using System.Diagnostics;

namespace RELib_LTScsDemo
{
    public partial class LTSMarketDemo : Form
    {
        private AsyncShowCallbackData asyncMsg = null;
        private LTSMDAdapter marketDataApi = null;
        private string marketDrontAddress = "tcp://211.144.195.163:34513";  // 行情前置地址
        private string BrokerID = "2011";                       // 经纪公司代码
        private string UserID = "xxxxxxxxxxxxx";                 // 投资者代码
        private string Password = "123321";                     // 用户密码
        // 大连,上海代码为小写
        // 郑州,中金所代码为大写
        // 郑州品种年份为一位数
        string[] ppInstrumentID = { "10000031", "000002", "000003", "000004", "000005", "000006", "10000032", "10000035", "10000037" };	// 行情订阅列表
        private int iRequestID = 0;
        public LTSMarketDemo()
        {
            InitializeComponent();
            asyncMsg = AsyncShowCallbackExtendHelper.MakeAsyncShowCallback(this, MarketLabel, null);
        }


        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);

            InitMarket();
        }
        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            try
            {
                marketDataApi.Release();
            }
            catch (Exception ex) { }


        }
        private bool InitMarket()
        {

            marketDataApi = new LTSMDAdapter();// new LTSMDAdapter(marketDrontAddress);

            marketDataApi.OnFrontConnected += new FrontConnected(OnFrontConnected);
            marketDataApi.OnFrontDisconnected += new FrontDisconnected(OnFrontDisconnected);
            marketDataApi.OnHeartBeatWarning += new HeartBeatWarning(OnHeartBeatWarning);
            marketDataApi.OnRspError += new RspError(OnRspError);

            marketDataApi.OnRspUserLogin += new RspUserLogin(OnRspUserLogin);

            marketDataApi.OnRspUserLogout += new RspUserLogout(OnRspUserLogout);

           


            try
            {
                marketDataApi.RegisterFront(marketDrontAddress);
                marketDataApi.Init();
            }
            catch (Exception e)
            {
                Debug.WriteLine(e.Message);
            }
           
            return true;
        }

        #region 回调函数
        /// <summary>
        /// 连接回调函数
        /// </summary>
        private void OnFrontConnected()
        {
            //DebugPrintFunc(new StackTrace());
            //ReqUserLogin();
            asyncMsg.AppendMsg("行情服务器连接成功！");
            Debug.WriteLine("OnFrontConnected");
        }
        /// 登录行情请求
        /// </summary>
        private void ReqUserLogin()
        {
            SecurityFtdcReqUserLoginField req = new SecurityFtdcReqUserLoginField();
            req.BrokerID = BrokerID;
            req.UserID = UserID;
            req.Password = Password;
            int iResult = marketDataApi.ReqUserLogin(req, ++iRequestID);

            String msg = "--->>> 发送用户登录请求: " + ((iResult == 0) ? "成功" : "失败");

            Debug.WriteLine(msg);
           
        }
        /// <summary>
        ///   退出行情请求
        ///   交易模块需要登出，行情模块不需要。
        /// </summary>
        private void ReqUserLogout()
        {
            SecurityFtdcUserLogoutField user = new SecurityFtdcUserLogoutField();
            user.BrokerID = BrokerID;
            user.UserID = UserID;
            int iResult = marketDataApi.ReqUserLogout(user, iRequestID++);

            String msg = "--->>> 发送用户退出请求: " + ((iResult == 0) ? "成功" : "失败");

            Debug.WriteLine(msg);
        }

        void OnRspUserLogin(SecurityFtdcRspUserLoginField pRspUserLogin, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {

            if (bIsLast && !IsErrorRspInfo(pRspInfo))
            {
                ///获取当前交易日
                String msg = "\n--->>> 获取当前交易日 = " + marketDataApi.GetTradingDay();
                //Console.WriteLine(msg);
                asyncMsg.AppendMsg("用户登录成功！");
                Debug.WriteLine(msg);
                // 请求订阅行情
                SubscribeMarketData();
            }
            else
            {
                asyncMsg.AppendMsg("登录失败：账号或者密码错误！");
                Debug.WriteLine(pRspInfo.ErrorMsg);

            }
        }
        void OnRspUserLogout(SecurityFtdcUserLogoutField pUserLogout, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            DebugPrintFunc(new StackTrace());
            asyncMsg.AppendMsg("--->>> 退出行情！");
            Debug.WriteLine("--->>> 退出行情！");
        }
        bool IsErrorRspInfo(SecurityFtdcRspInfoField pRspInfo)
        {
            // 如果ErrorID != 0, 说明收到了错误的响应
            bool bResult = ((pRspInfo != null) && (pRspInfo.ErrorID != 0));
            if (bResult)
            {
                String msg="\n--->>> ErrorID="+pRspInfo.ErrorID+", ErrorMsg="+ pRspInfo.ErrorMsg;
                asyncMsg.AppendMsg(msg);
                Debug.WriteLine(msg);
            }
            return bResult;
        }
        /// <summary>
        ///断开连接事件
        /// </summary>
        /// <param name="nReason"></param>
        void OnFrontDisconnected(int nReason)
        {
            DebugPrintFunc(new StackTrace());
            Debug.WriteLine("--->>> Reason = {0}", nReason);
        }
        /// <summary>
        /// 发生错误
        /// </summary>
        /// <param name="pRspInfo"></param>
        /// <param name="nRequestID"></param>
        /// <param name="bIsLast"></param>
        void OnRspError(SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            DebugPrintFunc(new StackTrace());
            IsErrorRspInfo(pRspInfo);
            asyncMsg.AppendMsg(pRspInfo.ErrorMsg);
        }

        void OnHeartBeatWarning(int nTimeLapse)
        {
            DebugPrintFunc(new StackTrace());
            Debug.WriteLine("--->>> nTimerLapse = " + nTimeLapse);
        }
       
      

        void OnRspUnSubMarketData(SecurityFtdcSpecificInstrumentField pSpecificInstrument, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            DebugPrintFunc(new StackTrace());
        }

        void OnRspSubMarketData(SecurityFtdcSpecificInstrumentField pSpecificInstrument, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            DebugPrintFunc(new StackTrace());
            asyncMsg.AppendMsg("行情订阅！");
        }
        /// <summary>
        /// 深度行情回调
        /// 每次返回一条行情？
        /// </summary>
        /// <param name="pDepthMarketData"></param>
        void OnRtnDepthMarketData(SecurityFtdcDepthMarketDataField pDepthMarketData)
        {
            //DebugPrintFunc(new StackTrace());

            //DateTime now = DateTime.Parse(pDepthMarketData.UpdateTime);
            //now.AddMilliseconds(pDepthMarketData.UpdateMillisec);
            string msg = string.Format("\n{0,-6} : UpdateTime = {1}.{2:D3},  LasPrice = {3}", pDepthMarketData.InstrumentID, pDepthMarketData.UpdateTime, pDepthMarketData.UpdateMillisec, pDepthMarketData.LastPrice);
           // MarketLabel.Text += msg;
            asyncMsg.AppendMsg(msg);
            Debug.WriteLine(msg);
        }
        #endregion

        #region 按钮事件
        /// <summary>
        /// 登录行情按钮
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void loginBtn_Click(object sender, EventArgs e)
        {
            ReqUserLogin();
        }
        
        /// <summary>
        /// 订阅行情按钮
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button1_Click(object sender, EventArgs e)
        {
            this.subcribeBtn.Enabled = false;
            SubscribeMarketData();
            this.unSubcribeBtn.Enabled = true;
        }
       
        /// <summary>
        /// 取消订阅行情
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button2_Click(object sender, EventArgs e)
        {
            this.unSubcribeBtn.Enabled = false;
            UnSubscribeMarketData();
            this.subcribeBtn.Enabled = true;
        }
        /// <summary>
        /// 退出登录
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button3_Click(object sender, EventArgs e)
        {
            UnSubscribeMarketData();
            this.Close();
            //ReqUserLogout();
        }
        #endregion

        #region 行情订阅接口

        /// <summary>
        /// 订阅行情
        /// </summary>
        void SubscribeMarketData()
        {
            marketDataApi.OnRspSubMarketData += new RspSubMarketData(OnRspSubMarketData);
            marketDataApi.OnRspUnSubMarketData += new RspUnSubMarketData(OnRspUnSubMarketData);
            marketDataApi.OnRtnDepthMarketData += new RtnDepthMarketData(OnRtnDepthMarketData);

            int iResult = marketDataApi.SubscribeMarketData(ppInstrumentID, 9, "SSE");
            // Console.WriteLine("--->>> 发送行情订阅请求: " + ((iResult == 0) ? "成功" : "失败"));
            String msg = "\n--->>> 发送行情订阅请求: " + ((iResult == 0) ? "成功" : "失败");
           // MarketLabel.Text += msg;
            Debug.WriteLine(msg);
        }
        /// <summary>
        ///  取消订阅行情
        /// </summary>
        void UnSubscribeMarketData()
        {
            int iResult = marketDataApi.UnSubscribeMarketData(ppInstrumentID, 9, "SSE");
            String msg = "\n--->>> 发送取消行情订阅请求: " + ((iResult == 0) ? "成功" : "失败");
            MarketLabel.Text += msg;
            Debug.WriteLine(msg);
        }

        #endregion

        void DebugPrintFunc(StackTrace stkTrace)
        {
            string s = stkTrace.GetFrame(0).ToString();
            s = s.Split(new char[] { ' ' })[0];
            Debug.WriteLine("\n\n--->>> " + DateTime.Now + "    ===========    " + s);

        }

       
    }
}
