/*!
* \file LTSDemo.cs
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

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using RELib_LTSNet;
using System.Diagnostics;
using System.Threading;

namespace RELib_LTScsDemo
{
    public partial class LTSDemo : Form
    {
        /// <summary>
        /// 价格精度
        /// </summary>
        private readonly int minSpreadPriceCount = 3;
        /// <summary>
        /// invoke
        /// </summary>
        public AsyncShowCallbackData asyncMsg = null;
        /// <summary>
        /// 合约查询是否完成
        /// </summary>
        private bool queryIsInit = false;
        public LTSDemo()
        {
            InitializeComponent();
        }
        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            callbackUpdateComboboxInstrument += new CallbackUpdateComboboxInstrument(UpdateComboboxInstrument);
            callbackUpdateDelegate += new CallbackUpdateDelegate(FillDelegateDataGrid);
            callbackUpdateTradeData += new CallbackUpdateTradeData(FillTradeDataGrid);

            LoginWin loginWin = new LoginWin(this);
            Init(loginWin);
            DialogResult result = loginWin.ShowDialog();
            if (result == DialogResult.Cancel)
            {
                this.Close();
            }
            //DataSet ds = GetMarkDataInfo2Client();
            //FillMarketDataGrid(ds.Tables["MarketData"]);



            DataSet ds3 = GetDelegateInfo2Client();
            FillDelegateDataGrid(ds3.Tables["Delegate"]);

            DataSet ds4 = GetTradeInfo2Client();
            FillTradeDataGrid(ds4.Tables["Trade"]);


            //DataSet ds5 = GetFundInfo2Client();
            //FillFundDataGrid(ds5.Tables["Fund"]);



            //明细
            //SecurityFtdcQryInvestorPositionDetailField positionField = new SecurityFtdcQryInvestorPositionDetailField();
            //positionField.BrokerID = SysConst.BrokerID;
            //positionField.InstrumentID = "000002";
            //positionField.InvestorID = SysConst.User.UserID;
            //int r = SysConst.TraderApi.ReqQryInvestorPositionDetail(positionField, SysConst.GetRequestID());

            //SubscribeMarketData();
            // FillMarketDataGrid(new DataTable());

            //MarketDataTimer.Enabled = true;
            //MarketDataTimer.Start();
        }
        /// <summary>
        /// 合约列表委托
        /// </summary>
        private delegate void CallbackUpdateComboboxInstrument();
        CallbackUpdateComboboxInstrument callbackUpdateComboboxInstrument;

        /// <summary>
        /// 更新合约下拉列表
        /// </summary>
        void UpdateComboboxInstrument()
        {
            SysConst.InstrumentData.Clear();
            var arr = SysConst.Instruments.Where(p => p.Key.IndexOf("6") == 0).Take(10);
            foreach (var v in arr)
            {
                SysConst.InstrumentData.Add(v.Key, v.Value);
            }
            //DataSet ds = GetMarkDataInfo2Client();
            //FillMarketDataGrid(ds.Tables["MarketData"]);
            SubscribeMarketData();
            MarketDataTimer.Enabled = true;
            MarketDataTimer.Start();


            List<CBListItem> list = new List<CBListItem>();
            CBListItem item;
            foreach (string key in SysConst.Instruments.Keys)
            {
                item = new CBListItem(key, key + "(" + SysConst.Instruments[key].InstrumentName + ")");
                list.Add(item);
                //comboBoxInstrument.Items.Add(item);
            }
            comboBoxInstrument.DataSource = list;
            comboBoxInstrument.DisplayMember = "Value";
            comboBoxInstrument.ValueMember = "key";
        }
        void InitQuery()
        {
            Thread.Sleep(1000);
            SecurityFtdcQryInvestorPositionField positionField = new SecurityFtdcQryInvestorPositionField();
            positionField.BrokerID = SysConst.User.BrokerID;
            positionField.InvestorID = SysConst.User.UserID;
            int r = SysConst.TraderApi.ReqQryInvestorPosition(positionField, SysConst.GetRequestID());


            ///延迟不是很好，最好弄个队列，等前面查询完了，再处理下一个查询
            Thread.Sleep(1500);
            /////查询资金信息
            //SecurityFtdcQryTradingAccountField accountField = new SecurityFtdcQryTradingAccountField();
            //accountField.BrokerID = SysConst.User.BrokerID;
            //accountField.InvestorID = "";
            //r = SysConst.TraderApi.ReqQryTradingAccount(accountField, SysConst.GetRequestID());
            //延迟显示
            UpdateDelegateDataGrid();
            //延迟显示
            UpdateTradeDataGrid();
        }


        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);

            SysConst.Release();
        }

        #region 处理行情

        public delegate void RefreshMarketDataHanlder();
        public event RefreshMarketDataHanlder MarketDataRefreashed;


        /// <summary>
        /// 更新行情Grid
        /// </summary>
        public void UpDateMarketDataGrid()
        {
           
        }
        /// <summary>
        /// 设置行情表头
        /// </summary>
        private void SetMarketDataGridColText()
        {

            this.MarketDataGrid.ReadOnly = true;
            this.MarketDataGrid.AutoGenerateColumns = false;
            //this.MarketDataGrid.Columns["ColImage"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter;
            //this.MarketDataGrid.Columns["ColImage"].HeaderText = SysConst.m_PMESResourceManager.GetString("");
            //this.MarketDataGrid.Columns["ColImage"].Visible = false;


            this.MarketDataGrid.Columns["InstrumentID"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.MarketDataGrid.Columns["InstrumentID"].HeaderText = "合约";

            this.MarketDataGrid.Columns["InstrumentName"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.MarketDataGrid.Columns["InstrumentName"].HeaderText = "合约名称";

            DataGridViewCellStyle defaultCellStyle = this.MarketDataGrid.Columns["LastPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["LastPrice"].DefaultCellStyle.ApplyStyle(defaultCellStyle);
            this.MarketDataGrid.Columns["LastPrice"].HeaderText = "最新价";

            defaultCellStyle = this.MarketDataGrid.Columns["BidPrice1"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["BidPrice1"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["BidPrice1"].HeaderText = "买入价";

            defaultCellStyle = this.MarketDataGrid.Columns["AskPrice1"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["AskPrice1"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["AskPrice1"].HeaderText = "卖出价";


            defaultCellStyle = this.MarketDataGrid.Columns["UpDown"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["UpDown"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["UpDown"].HeaderText = "涨跌";


            defaultCellStyle = this.MarketDataGrid.Columns["UpDownRatio"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["UpDownRatio"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["UpDownRatio"].HeaderText = "涨跌幅";


            defaultCellStyle = this.MarketDataGrid.Columns["UpperLimitPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["UpperLimitPrice"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["UpperLimitPrice"].HeaderText = "涨停价";

            defaultCellStyle = this.MarketDataGrid.Columns["LowerLimitPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["LowerLimitPrice"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["LowerLimitPrice"].HeaderText = "跌停价";

            defaultCellStyle = this.MarketDataGrid.Columns["PreClosePrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["PreClosePrice"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["PreClosePrice"].HeaderText = "昨收盘";

            defaultCellStyle = this.MarketDataGrid.Columns["OpenPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["OpenPrice"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["OpenPrice"].HeaderText = "今开盘";

            defaultCellStyle = this.MarketDataGrid.Columns["HighestPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["HighestPrice"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["HighestPrice"].HeaderText = "当日最高";

            defaultCellStyle = this.MarketDataGrid.Columns["LowestPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["LowestPrice"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["LowestPrice"].HeaderText = "当日最低";

            defaultCellStyle = this.MarketDataGrid.Columns["Volume"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["Volume"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["Volume"].HeaderText = "成交总量";

            defaultCellStyle = this.MarketDataGrid.Columns["OpenInterest"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["OpenInterest"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["OpenInterest"].HeaderText = "持仓量";

            defaultCellStyle = this.MarketDataGrid.Columns["BondAllPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.MarketDataGrid.Columns["BondAllPrice"].DefaultCellStyle = defaultCellStyle;
            this.MarketDataGrid.Columns["BondAllPrice"].HeaderText = "昨结算价";
        }

        private void FillMarketDataGrid(DataTable table)
        {
            if (this.MarketDataGrid.RowCount == 0)
            {
                DataView view = new DataView(table);

                this.MarketDataGrid.DataSource = view.Table;

                this.MarketDataGrid.ClearSelection();
                this.SetMarketDataGridColText();
            }
            else
            {
                UpdateMarketGridRow();
            }
        }

        private void UpdateMarketGridRow()
        {
            int num = SysConst.MarketData.Count;
            if (num == 0) return;
            Dictionary<string, SecurityFtdcDepthMarketDataField> marketDatas = SysConst.MarketData;
            for (int i = 0; i < num; i++)
            {
                string key = this.MarketDataGrid.Rows[i].Cells["InstrumentID"].Value.ToString();
                if (SysConst.MarketData == null || !SysConst.MarketData.ContainsKey(key))
                {

                }
                else
                {
                    int minSpreadPriceCount = 2;
                    SysConst.MarketData[key].ClosePrice = marketDatas[key].PreClosePrice;

                    // if (agencyCommodityData != null && agencyCommodityData.ContainsKey(key)) minSpreadPriceCount = BizController.GetMinSpreadPriceCount(agencyCommodityData[key]);
                    this.MarketDataGrid.Rows[i].Cells["LastPrice"].Value = marketDatas[key].LastPrice.ToString(string.Format("F{0}", minSpreadPriceCount));
                    this.MarketDataGrid.Rows[i].Cells["BidPrice1"].Value = marketDatas[key].BidPrice1.ToString(string.Format("F{0}", minSpreadPriceCount));
                    this.MarketDataGrid.Rows[i].Cells["AskPrice1"].Value = marketDatas[key].AskPrice1.ToString(string.Format("F{0}", minSpreadPriceCount));
                    this.MarketDataGrid.Rows[i].Cells["HighestPrice"].Value = marketDatas[key].HighestPrice.ToString(string.Format("F{0}", minSpreadPriceCount));
                    this.MarketDataGrid.Rows[i].Cells["LowerLimitPrice"].Value = marketDatas[key].LowerLimitPrice.ToString(string.Format("F{0}", minSpreadPriceCount));
               
                    double UpDown = marketDatas[key].LastPrice - marketDatas[key].PreClosePrice;//.ToString("n2");m_MarketData.LastPrice - m_MarketData.PreClosePrice
                    string v = UpDown.ToString("n2");
                    this.MarketDataGrid.Rows[i].Cells["UpDown"].Value = v;
                    double UpDownRatio = marketDatas[key].LastPrice / marketDatas[key].PreClosePrice - 1;
                    this.MarketDataGrid.Rows[i].Cells["UpDownRatio"].Value = UpDownRatio.ToString("p2");
                    if (v.Contains("-"))
                    {
                        this.MarketDataGrid.Rows[i].Cells["UpDown"].Style.ForeColor = System.Drawing.Color.Green;
                        this.MarketDataGrid.Rows[i].Cells["UpDownRatio"].Style.ForeColor = System.Drawing.Color.Green;
                    }
                    else
                    {
                        this.MarketDataGrid.Rows[i].Cells["UpDown"].Style.ForeColor = System.Drawing.Color.Red;
                        this.MarketDataGrid.Rows[i].Cells["UpDownRatio"].Style.ForeColor = System.Drawing.Color.Red;
                    }


                    this.MarketDataGrid.Rows[i].Cells["PreClosePrice"].Value = marketDatas[key].PreClosePrice.ToString();
                }

            }
        }

        public DataSet GetMarkDataInfo2Client()
        {
            Dictionary<string, SecurityFtdcInstrumentField> instrumentDatas = SysConst.InstrumentData;

            ///DataSet
            DataSet set = new DataSet("tradeDataSet");
            ///行情表
            DataTable table = new DataTable("MarketData");
            //合约ID
            table.Columns.Add(new DataColumn("InstrumentID"));
            //名称
            table.Columns.Add(new DataColumn("InstrumentName"));

            table.Columns.Add(new DataColumn("LastPrice"));
            table.Columns.Add(new DataColumn("BidPrice1"));
            table.Columns.Add(new DataColumn("AskPrice1"));
            table.Columns.Add(new DataColumn("UpDown"));
            table.Columns.Add(new DataColumn("UpDownRatio"));

            table.Columns.Add(new DataColumn("LowerLimitPrice"));
            //涨停价
            table.Columns.Add(new DataColumn("UpperLimitPrice"));

            //昨收盘
            table.Columns.Add(new DataColumn("PreClosePrice"));
            //今开盘
            table.Columns.Add(new DataColumn("OpenPrice"));

            //当日最高
            table.Columns.Add(new DataColumn("HighestPrice"));
            //当日最低
            table.Columns.Add(new DataColumn("LowestPrice"));

            //成交总量
            table.Columns.Add(new DataColumn("Volume"));
            //持仓量
            table.Columns.Add(new DataColumn("OpenInterest"));
            //昨结算价
            table.Columns.Add(new DataColumn("BondAllPrice"));

            ///set Add table
            set.Tables.Add(table);


            try
            {
                //UpdateMarketGridRow();
                if (SysConst.MarketData.Count == 0) return set;
                DataRow row;
                Dictionary<string, SecurityFtdcDepthMarketDataField> marketData = SysConst.MarketData;
                ///初始化 价格相关信息
                foreach (KeyValuePair<string, SecurityFtdcInstrumentField> pair3 in instrumentDatas)
                {
                    if (!marketData.ContainsKey(pair3.Value.InstrumentID)) continue;

                    row = table.NewRow();
                    row["InstrumentName"] = pair3.Value.InstrumentName;
                    row["InstrumentID"] = pair3.Value.InstrumentID;
                    if (instrumentDatas.ContainsKey(pair3.Value.InstrumentID))
                    {
                        row["LastPrice"] = marketData[pair3.Value.InstrumentID].LastPrice.ToString("n2");
                        row["BidPrice1"] = marketData[pair3.Value.InstrumentID].BidPrice1.ToString("n2");
                        row["AskPrice1"] = marketData[pair3.Value.InstrumentID].AskPrice1.ToString("n2");

                        double upDown = marketData[pair3.Value.InstrumentID].LastPrice - marketData[pair3.Value.InstrumentID].PreClosePrice;
                        row["UpDown"] = upDown.ToString("n2");
                        double upDownRatio = 0;
                        if (marketData[pair3.Value.InstrumentID].PreClosePrice > 0)
                        {
                            upDownRatio = marketData[pair3.Value.InstrumentID].LastPrice / marketData[pair3.Value.InstrumentID].PreClosePrice - 1;
                        }

                        row["UpDownRatio"] = upDownRatio.ToString("p2");
                        row["UpperLimitPrice"] = marketData[pair3.Value.InstrumentID].UpperLimitPrice.ToString();
                        //row["UpdateTime"] = marketData[pair3.Value.InstrumentID].UpdateTime.ToString();
                        row["PreClosePrice"] = marketData[pair3.Value.InstrumentID].PreClosePrice.ToString("n2");
                        row["OpenPrice"] = marketData[pair3.Value.InstrumentID].OpenPrice.ToString("n2");
                        row["HighestPrice"] = marketData[pair3.Value.InstrumentID].HighestPrice.ToString("n2");
                        row["LowestPrice"] = marketData[pair3.Value.InstrumentID].LowestPrice.ToString("n2");
                        row["LowestPrice"] = marketData[pair3.Value.InstrumentID].LowestPrice.ToString("n2");
                        row["Volume"] = marketData[pair3.Value.InstrumentID].Volume.ToString();
                        row["OpenInterest"] = marketData[pair3.Value.InstrumentID].OpenInterest.ToString("n2");

                        row["BondAllPrice"] = "0";



                    }
                    table.Rows.Add(row);
                }
                return set;
            }
            catch (Exception exception)
            {

                return set;
            }
        }
        #endregion

        /// <summary>
        /// 订阅行情
        /// </summary>
        void SubscribeMarketData()
        {
            String[] ppInstrumentID = SysConst.InstrumentData.Keys.ToArray();
            int iResult = SysConst.MarketDataApi.SubscribeMarketData(ppInstrumentID, ppInstrumentID.Count(), "SSE");
            // Console.WriteLine("--->>> 发送行情订阅请求: " + ((iResult == 0) ? "成功" : "失败"));
            String msg = "\n--->>> 发送行情订阅请求: " + ((iResult == 0) ? "成功" : "失败");
            // MarketLabel.Text += msg;
            Debug.WriteLine(msg);
        }


        #region 回调函数
        /// <summary>
        /// 连接回调函数
        /// </summary>
        public void OnFrontConnected()
        {
            asyncMsg.AppendMsg(DateTime.Now + " 交易前置机连接成功！");
            
        }
        public void OnFrontConnectedMarket()
        {
            //Debug.WriteLine("前置机连接成功！");
            asyncMsg.AppendMsg(DateTime.Now + " 行情前置机连接成功！");
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
            //IsErrorRspInfo(pRspInfo);
            asyncMsg.AppendMsg(pRspInfo.ErrorMsg);
        }

        void OnHeartBeatWarning(int nTimeLapse)
        {
            DebugPrintFunc(new StackTrace());
            Debug.WriteLine("--->>> nTimerLapse = " + nTimeLapse);
        }
        public static bool IsErrorRspInfo(SecurityFtdcRspInfoField pRspInfo)
        {
            // 如果ErrorID != 0, 说明收到了错误的响应
            bool bResult = ((pRspInfo != null) && (pRspInfo.ErrorID != 0));
            if (bResult)
            {
                String msg = "\n--->>> ErrorID=" + pRspInfo.ErrorID + ", ErrorMsg=" + pRspInfo.ErrorMsg;

                Debug.WriteLine(msg);
            }
            return bResult;
        }
        void OnRspUserLogin(SecurityFtdcRspUserLoginField pRspUserLogin, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {

            if (bIsLast && !IsErrorRspInfo(pRspInfo))
            {
                ///获取当前交易日
                String msg = "\n--->>> 获取当前交易日 = " + SysConst.MarketDataApi.GetTradingDay();
                //Console.WriteLine(msg);
                asyncMsg.AppendMsg("\n--->>> 行情登录成功！");
                Debug.WriteLine(msg);
                // 请求订阅行情,获取合约之后再来订阅行情
                //SubscribeMarketData();
            }
            else
            {
                asyncMsg.AppendMsg("登录失败：账号或者密码错误！");
                Debug.WriteLine(pRspInfo.ErrorMsg);

            }
        }

        void OnRspUnSubMarketData(SecurityFtdcSpecificInstrumentField pSpecificInstrument, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            DebugPrintFunc(new StackTrace());
        }

        void OnRspSubMarketData(SecurityFtdcSpecificInstrumentField pSpecificInstrument, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            DebugPrintFunc(new StackTrace());
            //asyncMsg.AppendMsg("行情订阅！");
        }
        /// <summary>
        /// 深度行情回调
        /// 每次返回一条行情？
        /// </summary>
        /// <param name="pDepthMarketData"></param>
        void OnRtnDepthMarketData(SecurityFtdcDepthMarketDataField pDepthMarketData)
        {
            if (SysConst.MarketData.ContainsKey(pDepthMarketData.InstrumentID))
            {
                SysConst.MarketData[pDepthMarketData.InstrumentID].LastPrice = pDepthMarketData.LastPrice;
                SysConst.MarketData[pDepthMarketData.InstrumentID].UpdateMillisec = pDepthMarketData.UpdateMillisec;
                SysConst.MarketData[pDepthMarketData.InstrumentID].UpdateTime = pDepthMarketData.UpdateTime;
            }
            else
            {
                SysConst.MarketData[pDepthMarketData.InstrumentID] = pDepthMarketData;
            }
            //DebugPrintFunc(new StackTrace());

            //DateTime now = DateTime.Parse(pDepthMarketData.UpdateTime);
            //now.AddMilliseconds(pDepthMarketData.UpdateMillisec);
            string msg = string.Format("\n{0,-6} : UpdateTime = {1}.{2:D3},  LasPrice = {3}", pDepthMarketData.InstrumentID, pDepthMarketData.UpdateTime, pDepthMarketData.UpdateMillisec, pDepthMarketData.LastPrice);
            // MarketLabel.Text += msg;
            // asyncMsg.AppendMsg(msg);
            Debug.WriteLine(msg);
        }
        void DebugPrintFunc(StackTrace stkTrace)
        {
            string s = stkTrace.GetFrame(0).ToString();
            s = s.Split(new char[] { ' ' })[0];
            Debug.WriteLine("\n\n--->>> " + DateTime.Now + "    ===========    " + s);

        }
        /// <summary>
        /// 持仓信息回调
        /// </summary>
        /// <param name="pInvestorPosition"></param>
        /// <param name="pRspInfo"></param>
        /// <param name="nRequestID"></param>
        /// <param name="bIsLast"></param>
        void OnRspQryInvestorPosition(SecurityFtdcInvestorPositionField pInvestorPosition, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            if (pInvestorPosition != null)
            {
                SysConst.PositionDatas[pInvestorPosition.InstrumentID] = pInvestorPosition;

                if (bIsLast)
                {
                    DataSet ds2 = GetPositionInfo2Client();
                    if (this.PositionDataGrid.InvokeRequired)
                    {
                        base.BeginInvoke(callbackUpdatePositionDataGrid, ds2.Tables["Position"]);
                    }
                    else
                    {
                        FillPositionDataGrid(ds2.Tables["Position"]);
                    }
                    // asyncMsg.UpdateGrid(this.PositionDataGrid, ds2.Tables["Position"]);
                    Debug.WriteLine("持仓信息查询完毕！");
                    queryIsInit = true;
                }
            }
            else
            {
                queryIsInit = true;
            }
        }
        /// <summary>
        /// 资金账号回调
        /// </summary>
        /// <param name="pTradingAccount"></param>
        /// <param name="pRspInfo"></param>
        /// <param name="nRequestID"></param>
        /// <param name="bIsLast"></param>
        void OnRspQryTradingAccount(SecurityFtdcTradingAccountField pTradingAccount, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            // if(SysConst.Accounts.ContainsKey(pTradingAccount.AccountID))
            if (pTradingAccount != null)
            {
                SysConst.Accounts[pTradingAccount.AccountID] = pTradingAccount;
                if (bIsLast)
                {
                    DataSet ds2 = GetFundInfo2Client();
                    if (this.FundDataGrid.InvokeRequired)
                    {
                        base.BeginInvoke(callbackUpdateFundDataGrid, ds2.Tables["Fund"]);
                    }
                    else
                    {
                        FillPositionDataGrid(ds2.Tables["Fund"]);
                    }
                    // asyncMsg.UpdateGrid(this.PositionDataGrid, ds2.Tables["Position"]);
                    Debug.WriteLine("资金信息查询完毕！");
                }
            }
            else
            {

            }
        }
        /// <summary>
        /// 合约查询回调
        /// </summary>
        /// <param name="pInstrument"></param>
        /// <param name="pRspInfo"></param>
        /// <param name="nRequestID"></param>
        /// <param name="bIsLast"></param>
        void OnRspQryInstrument(SecurityFtdcInstrumentField pInstrument, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            if (pInstrument != null)
            {
                SysConst.Instruments[pInstrument.InstrumentID.Trim()] = pInstrument;
                if (bIsLast)
                {
                    InitQuery();
                    ///
                    if (comboBoxInstrument.InvokeRequired)
                    {
                        base.Invoke(callbackUpdateComboboxInstrument);
                    }
                    else
                        UpdateComboboxInstrument();
                    Debug.WriteLine("合约查询完毕！");
                }
            }
            else
            {
                Debug.WriteLine("没有合约信息！");
            }
        }
        /// <summary>
        /// 报单回调
        /// </summary>
        /// <param name="pInputOrder"></param>
        /// <param name="pRspInfo"></param>
        /// <param name="nRequestID"></param>
        /// <param name="bIsLast"></param>
        void OnRspOrderInsert(SecurityFtdcInputOrderField pInputOrder, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {
            if (pInputOrder != null)
            {
                SysConst.SendOrders[pInputOrder] = pRspInfo;
                if (bIsLast)
                {
                    UpdateDelegateDataGrid();

                    Debug.WriteLine(pRspInfo.ErrorMsg);
                }
            }
        }

        /// <summary>
        /// 委托回报
        /// </summary>
        /// <param name="pOrder"></param>
        void OnRtnOrder(SecurityFtdcOrderField pOrder)
        {
            if (pOrder == null) return;
            SysConst.Orders.Add(pOrder);
            if(queryIsInit)// 由于合约信息没有得到，所以需要延迟显示，如果得到就直接显示
                UpdateDelegateDataGrid();
            Debug.WriteLine("报单回报 " + pOrder.OrderLocalID);
        }
        void OnRtnTrade(SecurityFtdcTradeField pTrade)
        {
            if (pTrade == null) return;
            SysConst.Trades.Add(pTrade);
            if (queryIsInit)
                UpdateTradeDataGrid();
            Debug.WriteLine("成交回报 " + pTrade.OrderLocalID);
        }
        #endregion
        /// <summary>
        /// 查询合约
        /// </summary>
        public void QryInstrument()
        {
            ///不需要登录就能查询合约
            SecurityFtdcQryInstrumentField instrumentField = new SecurityFtdcQryInstrumentField();
            instrumentField.ExchangeID = String.Empty;
            instrumentField.ExchangeInstID = String.Empty;
            instrumentField.InstrumentID = String.Empty;
            instrumentField.ProductID = String.Empty;
            int r = SysConst.TraderApi.ReqQryInstrument(instrumentField, SysConst.GetRequestID());
        }
        /// <summary>
        ///  初始化API
        /// </summary>
        /// <param name="loginWin"></param>
        public void Init(LoginWin loginWin)
        {
            if (SysConst.TraderApi == null)
            {
                SysConst.TraderApi = new LTSTraderAdapter();

                SysConst.MarketDataApi = new LTSMDAdapter();
                try
                {
                    SysConst.TraderApi.OnFrontConnected += new FrontConnected(OnFrontConnected);
                    SysConst.TraderApi.OnRspUserLogin += new RspUserLogin(loginWin.OnRspUserLogin);


                    ///客户持仓信息
                    SysConst.TraderApi.OnRspQryInvestorPosition += new RspQryInvestorPosition(OnRspQryInvestorPosition);
                    //资金信息
                    SysConst.TraderApi.OnRspQryTradingAccount += new RspQryTradingAccount(OnRspQryTradingAccount);
                    //合约信息
                    SysConst.TraderApi.OnRspQryInstrument += new RspQryInstrument(OnRspQryInstrument);

                    SysConst.TraderApi.OnRspOrderInsert += new RspOrderInsert(OnRspOrderInsert);

                    SysConst.TraderApi.OnRtnOrder += new RtnOrder(OnRtnOrder);

                    SysConst.TraderApi.OnRtnTrade += new RtnTrade(OnRtnTrade);
                    // 注册一事件处理的实例
                    //m_pTdApi->RegisterSpi(this);

                    // 订阅私有流
                    //        TERT_RESTART:从本交易日开始重传
                    //        TERT_RESUME:从上次收到的续传
                    //        TERT_QUICK:只传送登录后私有流的内容
                    SysConst.TraderApi.SubscribePrivateTopic(EnumRESUMETYPE.TERT_RESTART);

                    // 订阅公共流
                    //        TERT_RESTART:从本交易日开始重传
                    //        TERT_RESUME:从上次收到的续传
                    //        TERT_QUICK:只传送登录后公共流的内容
                    SysConst.TraderApi.SubscribePublicTopic(EnumRESUMETYPE.TERT_RESTART);


                    SysConst.TraderApi.RegisterFront(SysConst.TradeFrontAddress);
                    SysConst.TraderApi.Init();


                }
                catch (Exception ex)
                {

                }

                try
                {
                    SysConst.MarketDataApi.OnFrontConnected += new FrontConnected(OnFrontConnectedMarket);
                    SysConst.MarketDataApi.OnRspSubMarketData += new RspSubMarketData(OnRspSubMarketData);
                    SysConst.MarketDataApi.OnRspUnSubMarketData += new RspUnSubMarketData(OnRspUnSubMarketData);
                    SysConst.MarketDataApi.OnRtnDepthMarketData += new RtnDepthMarketData(OnRtnDepthMarketData);
                    SysConst.MarketDataApi.OnHeartBeatWarning += new HeartBeatWarning(OnHeartBeatWarning);
                    SysConst.MarketDataApi.OnRspError += new RspError(OnRspError);

                    SysConst.MarketDataApi.OnRspUserLogin += new RspUserLogin(OnRspUserLogin);


                    SysConst.MarketDataApi.RegisterFront(SysConst.MarketDataFrontAddress);
                    SysConst.MarketDataApi.Init();


                }
                catch (Exception ex)
                {

                }
            }
        }

        private void MarketDataTimer_Tick(object sender, EventArgs e)
        {
            //UpdateMarketGridRow();
            DataSet ds = GetMarkDataInfo2Client();
            FillMarketDataGrid(ds.Tables["MarketData"]);
        }


        #region 持仓查询
        private delegate void CallbackUpdatePositionDataGrid(DataTable dataTable);

        private CallbackUpdatePositionDataGrid callbackUpdatePositionDataGrid;
        private void FillPositionDataGrid(DataTable table)
        {
            if (this.PositionDataGrid.RowCount == 0)
            {

                DataView view = new DataView(table);

                this.PositionDataGrid.DataSource = view.Table;

                this.PositionDataGrid.ClearSelection();
                this.SetPositionDataGridColText();

            }
            else
            {
                // UpdatePositionGridRow();
                //DataSet ds2 = GetPositionInfo2Client();
                DataView view = new DataView(table);

                this.PositionDataGrid.DataSource = view.Table;

                this.PositionDataGrid.ClearSelection();
            }
        }
        private void UpdatePositionGridRow()
        {
            int num = SysConst.PositionDatas.Count;
            if (num == 0) return;
            Dictionary<string, SecurityFtdcInvestorPositionField> positionDatas = SysConst.PositionDatas;

            this.PositionDataGrid.ClearSelection();


            //if (this.PositionDataGrid.Rows.Count < num)
            //{
            //    this.PositionDataGrid.Rows.Add(num - this.PositionDataGrid.Rows.Count);
            //}
            ///行情表
            DataTable table = new DataTable("Position");

            foreach (string key in positionDatas.Keys)
            {
                DataRow row = table.NewRow();
                {
                    int minSpreadPriceCount = 2;

                    row["InstrumentID"] = positionDatas[key].InstrumentID;
                    row["InstrumentName"] = SysConst.Instruments[key].InstrumentName;
                    row["PositionDirection"] = positionDatas[key].PosiDirection.ToString();
                    row["Position"] = positionDatas[key].Position;
                    row["TodayPosition"] = positionDatas[key].TodayPosition;
                    row["PositionPrice"] = positionDatas[key].PositionCost.ToString("n" + minSpreadPriceCount);

                    double lastPrice = 0;
                    if (SysConst.MarketData.ContainsKey(key))
                        lastPrice = SysConst.MarketData[key].LastPrice;
                    row["LastPrice"] = lastPrice.ToString("n" + minSpreadPriceCount);
                    double v = 0;
                    if (lastPrice <= 0 || lastPrice >= SysConst.MaxFloatExceed)
                    {
                        v = (positionDatas[key].YdPosition + positionDatas[key].Position) * positionDatas[key].PreSettlementPrice * SysConst.InstrumentData[key].VolumeMultiple - (positionDatas[key].PositionCost + positionDatas[key].OpenCost);
                    }
                    else
                    {
                        v = (positionDatas[key].YdPosition + positionDatas[key].Position) * lastPrice * SysConst.InstrumentData[key].VolumeMultiple - (positionDatas[key].PositionCost + positionDatas[key].OpenCost);
                    }
                    row["PositionProfit"] = v.ToString("n" + minSpreadPriceCount);

                    table.Rows.Add(row);
                }

            }
            this.PositionDataGrid.DataSource = table;
        }
        /// <summary>
        /// 
        /// </summary>
        private void SetPositionDataGridColText()
        {
            this.PositionDataGrid.ReadOnly = true;
            this.PositionDataGrid.AutoGenerateColumns = false;


            this.PositionDataGrid.Columns["InstrumentID"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.PositionDataGrid.Columns["InstrumentID"].HeaderText = "证券代码";

            this.PositionDataGrid.Columns["InstrumentName"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.PositionDataGrid.Columns["InstrumentName"].HeaderText = "证券名称";

            DataGridViewCellStyle defaultCellStyle = this.PositionDataGrid.Columns["PositionDirection"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.PositionDataGrid.Columns["PositionDirection"].DefaultCellStyle.ApplyStyle(defaultCellStyle);
            this.PositionDataGrid.Columns["PositionDirection"].HeaderText = "多空";

            defaultCellStyle = this.PositionDataGrid.Columns["Position"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.PositionDataGrid.Columns["Position"].DefaultCellStyle = defaultCellStyle;
            this.PositionDataGrid.Columns["Position"].HeaderText = "总持仓";

            defaultCellStyle = this.PositionDataGrid.Columns["TodayPosition"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.PositionDataGrid.Columns["TodayPosition"].DefaultCellStyle = defaultCellStyle;
            this.PositionDataGrid.Columns["TodayPosition"].HeaderText = "今持仓";


            defaultCellStyle = this.PositionDataGrid.Columns["PositionPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.PositionDataGrid.Columns["PositionPrice"].DefaultCellStyle = defaultCellStyle;
            this.PositionDataGrid.Columns["PositionPrice"].HeaderText = "持仓均价";


            defaultCellStyle = this.PositionDataGrid.Columns["LastPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.PositionDataGrid.Columns["LastPrice"].DefaultCellStyle = defaultCellStyle;
            this.PositionDataGrid.Columns["LastPrice"].HeaderText = "最新价";


            defaultCellStyle = this.PositionDataGrid.Columns["PositionProfit"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.PositionDataGrid.Columns["PositionProfit"].DefaultCellStyle = defaultCellStyle;
            this.PositionDataGrid.Columns["PositionProfit"].HeaderText = "浮动盈亏";


        }

        private DataSet GetPositionInfo2Client()
        {
            if (callbackUpdatePositionDataGrid == null)
                callbackUpdatePositionDataGrid += new CallbackUpdatePositionDataGrid(FillPositionDataGrid);
            ///DataSet
            DataSet set = new DataSet("tradeDataSet");
            ///行情表
            DataTable table = new DataTable("Position");
            //合约ID
            table.Columns.Add(new DataColumn("InstrumentID"));
            //名称
            table.Columns.Add(new DataColumn("InstrumentName"));

            table.Columns.Add(new DataColumn("PositionDirection"));
            table.Columns.Add(new DataColumn("Position"));
            table.Columns.Add(new DataColumn("TodayPosition"));
            table.Columns.Add(new DataColumn("PositionPrice"));
            table.Columns.Add(new DataColumn("LastPrice"));

            table.Columns.Add(new DataColumn("PositionProfit"));

            ///set Add table
            set.Tables.Add(table);

            Dictionary<string, SecurityFtdcInvestorPositionField> positionDatas = SysConst.PositionDatas;
            foreach (string key in positionDatas.Keys)
            {
                DataRow row = table.NewRow();
                {
                    int minSpreadPriceCount = 2;
                    string InstrumentName = String.Empty;
                    int VolumeMultiple = 10;
                    if (SysConst.Instruments.ContainsKey(key))
                    {
                        InstrumentName = SysConst.Instruments[key].InstrumentName;
                        VolumeMultiple = SysConst.Instruments[key].VolumeMultiple;
                    }


                    row["InstrumentID"] = positionDatas[key].InstrumentID;
                    row["InstrumentName"] = InstrumentName;
                    row["PositionDirection"] = positionDatas[key].PosiDirection.ToString();
                    row["Position"] = positionDatas[key].Position;
                    row["TodayPosition"] = positionDatas[key].TodayPosition;
                   
                    row["PositionPrice"] = positionDatas[key].PositionCost.ToString("n" + minSpreadPriceCount);

                    double lastPrice = 0;
                    if (SysConst.MarketData.ContainsKey(key))
                        lastPrice = SysConst.MarketData[key].LastPrice;
                    row["LastPrice"] = lastPrice.ToString("n" + minSpreadPriceCount);
                    double v = 0;
                    if (lastPrice <= 0 || lastPrice >= SysConst.MaxFloatExceed)
                    {
                        v = (positionDatas[key].YdPosition + positionDatas[key].Position) * positionDatas[key].PreSettlementPrice * VolumeMultiple - (positionDatas[key].PositionCost + positionDatas[key].OpenCost);
                    }
                    else
                    {
                        v = (positionDatas[key].YdPosition + positionDatas[key].Position) * lastPrice * VolumeMultiple - (positionDatas[key].PositionCost + positionDatas[key].OpenCost);
                    }
                    row["PositionProfit"] = v.ToString("n" + minSpreadPriceCount);

                    table.Rows.Add(row);
                }

            }
            return set;
        }
        #endregion

        #region 委托回报
        private delegate void CallbackUpdateDelegate(DataTable table);
        private event CallbackUpdateDelegate callbackUpdateDelegate;
        private void FillDelegateDataGrid(DataTable table)
        {
            // if (this.DelegateDataGrid.RowCount == 0)
            {
                DataView view = new DataView(table);

                this.DelegateDataGrid.DataSource = view.Table;

                this.DelegateDataGrid.ClearSelection();
                this.SetDelegateDataGridColText();
            }
            //else
            //{
            //    UpdateMarketGridRow();
            //}
        }
        /// <summary>
        /// 更新委托回报
        /// </summary>
        void UpdateDelegateDataGrid()
        {
            DataSet ds2 = GetDelegateInfo2Client();
            if (DelegateDataGrid.InvokeRequired)
            {

                base.Invoke(callbackUpdateDelegate, ds2.Tables["Delegate"]);
            }
            else
                FillDelegateDataGrid(ds2.Tables["Delegate"]);
        }
        /// <summary>
        /// 
        /// </summary>
        private void SetDelegateDataGridColText()
        {
            this.DelegateDataGrid.ReadOnly = true;
            this.DelegateDataGrid.AutoGenerateColumns = false;


            this.DelegateDataGrid.Columns["InstrumentID"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.DelegateDataGrid.Columns["InstrumentID"].HeaderText = "证券代码";

            this.DelegateDataGrid.Columns["InstrumentName"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.DelegateDataGrid.Columns["InstrumentName"].HeaderText = "证券名称";

            DataGridViewCellStyle defaultCellStyle = this.DelegateDataGrid.Columns["OrderSysID"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["OrderSysID"].DefaultCellStyle.ApplyStyle(defaultCellStyle);
            this.DelegateDataGrid.Columns["OrderSysID"].HeaderText = "报单编号";

            defaultCellStyle = this.DelegateDataGrid.Columns["Direction"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["Direction"].DefaultCellStyle = defaultCellStyle;
            this.DelegateDataGrid.Columns["Direction"].HeaderText = "买卖";

            defaultCellStyle = this.DelegateDataGrid.Columns["OffSetFlag"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["OffSetFlag"].DefaultCellStyle = defaultCellStyle;
            this.DelegateDataGrid.Columns["OffSetFlag"].HeaderText = "开平";


            defaultCellStyle = this.DelegateDataGrid.Columns["OrderStatus"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["OrderStatus"].DefaultCellStyle = defaultCellStyle;
            this.DelegateDataGrid.Columns["OrderStatus"].HeaderText = "挂单状态";


            defaultCellStyle = this.DelegateDataGrid.Columns["LimitPrice"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["LimitPrice"].DefaultCellStyle = defaultCellStyle;
            this.DelegateDataGrid.Columns["LimitPrice"].HeaderText = "报单价格";


            defaultCellStyle = this.DelegateDataGrid.Columns["VolumeTotalOriginal"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["VolumeTotalOriginal"].DefaultCellStyle = defaultCellStyle;
            this.DelegateDataGrid.Columns["VolumeTotalOriginal"].HeaderText = "报单手数";

            defaultCellStyle = this.DelegateDataGrid.Columns["VolumeTotal"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["VolumeTotal"].DefaultCellStyle = defaultCellStyle;
            this.DelegateDataGrid.Columns["VolumeTotal"].HeaderText = "未成交手数";


            defaultCellStyle = this.DelegateDataGrid.Columns["VolumeTraded"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["VolumeTraded"].DefaultCellStyle = defaultCellStyle;
            this.DelegateDataGrid.Columns["VolumeTraded"].HeaderText = "成交手数";

            defaultCellStyle = this.DelegateDataGrid.Columns["OrderStatusMsg"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["OrderStatusMsg"].DefaultCellStyle = defaultCellStyle;
            this.DelegateDataGrid.Columns["OrderStatusMsg"].HeaderText = "详细状态";


            defaultCellStyle = this.DelegateDataGrid.Columns["InsertTime"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.DelegateDataGrid.Columns["InsertTime"].DefaultCellStyle = defaultCellStyle;
            this.DelegateDataGrid.Columns["InsertTime"].HeaderText = "报单时间";
        }

        private DataSet GetDelegateInfo2Client()
        {
            ///DataSet
            DataSet set = new DataSet("tradeDataSet");
            ///行情表
            DataTable table = new DataTable("Delegate");
            //合约ID
            table.Columns.Add(new DataColumn("OrderSysID"));
            //合约ID
            table.Columns.Add(new DataColumn("InstrumentID"));
            //名称
            table.Columns.Add(new DataColumn("InstrumentName"));
            table.Columns.Add(new DataColumn("Direction"));
            table.Columns.Add(new DataColumn("OffSetFlag"));

            table.Columns.Add(new DataColumn("OrderStatus"));
            table.Columns.Add(new DataColumn("LimitPrice"));

            table.Columns.Add(new DataColumn("VolumeTotalOriginal"));
            table.Columns.Add(new DataColumn("VolumeTotal"));
            table.Columns.Add(new DataColumn("VolumeTraded"));

            table.Columns.Add(new DataColumn("OrderStatusMsg"));

            table.Columns.Add(new DataColumn("InsertTime"));

            ///set Add table
            set.Tables.Add(table);

            //UpdateMarketGridRow();
            if (SysConst.MarketData.Count == 0) return set;
            DataRow row;
            ///初始化 价格相关信息
            foreach (SecurityFtdcInputOrderField field in SysConst.SendOrders.Keys)
            {
                row = table.NewRow();
                row["OrderSysID"] = field.OrderRef;
                row["InstrumentID"] = field.InstrumentID;
                row["InstrumentName"] = SysConst.Instruments[field.InstrumentID].InstrumentName;
                row["Direction"] = field.Direction;
                row["OffSetFlag"] = field.CombOffsetFlag;
                row["OrderStatus"] = SysConst.SendOrders[field].ErrorID;
                row["LimitPrice"] = field.LimitPrice;
                row["VolumeTotalOriginal"] = field.VolumeTotalOriginal;
                row["VolumeTotal"] = field.VolumeTotalOriginal;

                row["VolumeTraded"] = field.VolumeTotalOriginal;
                row["OrderStatusMsg"] = SysConst.SendOrders[field].ErrorMsg;
                row["InsertTime"] = "";
                table.Rows.Add(row);
            }
            foreach (SecurityFtdcOrderField field in SysConst.Orders)
            {
                string instrumentName = string.Empty;
                if (SysConst.Instruments.ContainsKey(field.InstrumentID))
                    instrumentName = SysConst.Instruments[field.InstrumentID].InstrumentName;
                row = table.NewRow();
                row["OrderSysID"] = field.OrderRef;
                row["InstrumentID"] = field.InstrumentID;
                row["InstrumentName"] = instrumentName;
                row["Direction"] = field.Direction;
                row["OffSetFlag"] = field.CombOffsetFlag;
                row["OrderStatus"] = field.OrderStatus;
                row["LimitPrice"] = field.LimitPrice;
                row["VolumeTotalOriginal"] = field.VolumeTotalOriginal;
                row["VolumeTotal"] = field.VolumeTotal;

                row["VolumeTraded"] = field.VolumeTraded;
                row["OrderStatusMsg"] = field.StatusMsg;
                row["InsertTime"] = field.InsertTime;
                table.Rows.Add(row);
            }

            return set;
        }
        #endregion
        #region 成交回报
        private delegate void CallbackUpdateTradeData(DataTable table);
        private event CallbackUpdateTradeData callbackUpdateTradeData = null;

        private void FillTradeDataGrid(DataTable table)
        {

            DataView view = new DataView(table);

            this.TradeDataGrid.DataSource = view.Table;

            this.TradeDataGrid.ClearSelection();
            this.SetTradeDataGridColText();

        }
        void UpdateTradeDataGrid()
        {
            DataSet ds4 = GetTradeInfo2Client();

            if (TradeDataGrid.InvokeRequired)
            {
                base.Invoke(callbackUpdateTradeData, ds4.Tables["Trade"]);

            }
            else
                FillTradeDataGrid(ds4.Tables["Trade"]);
        }
        /// <summary>
        /// 
        /// </summary>
        private void SetTradeDataGridColText()
        {
            this.TradeDataGrid.ReadOnly = true;
            this.TradeDataGrid.AutoGenerateColumns = false;


            this.TradeDataGrid.Columns["InstrumentID"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.TradeDataGrid.Columns["InstrumentID"].HeaderText = "证券代码";
            this.DelegateDataGrid.Columns["InstrumentName"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.DelegateDataGrid.Columns["InstrumentName"].HeaderText = "证券名称";

            DataGridViewCellStyle defaultCellStyle = this.TradeDataGrid.Columns["TradeID"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.TradeDataGrid.Columns["TradeID"].DefaultCellStyle.ApplyStyle(defaultCellStyle);
            this.TradeDataGrid.Columns["TradeID"].HeaderText = "报单编号";



            defaultCellStyle = this.TradeDataGrid.Columns["Direction"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.TradeDataGrid.Columns["Direction"].DefaultCellStyle = defaultCellStyle;
            this.TradeDataGrid.Columns["Direction"].HeaderText = "买卖";

            defaultCellStyle = this.TradeDataGrid.Columns["OffSetFlag"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.TradeDataGrid.Columns["OffSetFlag"].DefaultCellStyle = defaultCellStyle;
            this.TradeDataGrid.Columns["OffSetFlag"].HeaderText = "开平";


            defaultCellStyle = this.TradeDataGrid.Columns["Price"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.TradeDataGrid.Columns["Price"].DefaultCellStyle = defaultCellStyle;
            this.TradeDataGrid.Columns["Price"].HeaderText = "成交价格";


            defaultCellStyle = this.TradeDataGrid.Columns["Volume"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.TradeDataGrid.Columns["Volume"].DefaultCellStyle = defaultCellStyle;
            this.TradeDataGrid.Columns["Volume"].HeaderText = "成交手数";


            defaultCellStyle = this.TradeDataGrid.Columns["TradeTime"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.TradeDataGrid.Columns["TradeTime"].DefaultCellStyle = defaultCellStyle;
            this.TradeDataGrid.Columns["TradeTime"].HeaderText = "成交时间";


            this.TradeDataGrid.Columns["OrderSysID"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.TradeDataGrid.Columns["OrderSysID"].HeaderText = "报单编号";

            defaultCellStyle = this.TradeDataGrid.Columns["TradeType"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.TradeDataGrid.Columns["TradeType"].DefaultCellStyle = defaultCellStyle;
            this.TradeDataGrid.Columns["TradeType"].HeaderText = "成交类型";


            defaultCellStyle = this.TradeDataGrid.Columns["HedgeFlag"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.TradeDataGrid.Columns["HedgeFlag"].DefaultCellStyle = defaultCellStyle;
            this.TradeDataGrid.Columns["HedgeFlag"].HeaderText = "投保";

            defaultCellStyle = this.TradeDataGrid.Columns["ExchangeID"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.TradeDataGrid.Columns["ExchangeID"].DefaultCellStyle = defaultCellStyle;
            this.TradeDataGrid.Columns["ExchangeID"].HeaderText = "交易所";
        }

        private DataSet GetTradeInfo2Client()
        {
            ///DataSet
            DataSet set = new DataSet("tradeDataSet");
            ///行情表
            DataTable table = new DataTable("Trade");

            //合约ID
            table.Columns.Add(new DataColumn("InstrumentID"));
            //名称
            table.Columns.Add(new DataColumn("InstrumentName"));

            table.Columns.Add(new DataColumn("TradeID"));
            table.Columns.Add(new DataColumn("Direction"));
            table.Columns.Add(new DataColumn("OffSetFlag"));



            table.Columns.Add(new DataColumn("Price"));
            table.Columns.Add(new DataColumn("Volume"));

            table.Columns.Add(new DataColumn("TradeTime"));

            //合约ID
            table.Columns.Add(new DataColumn("OrderSysID"));
            table.Columns.Add(new DataColumn("TradeType"));

            table.Columns.Add(new DataColumn("HedgeFlag"));

            table.Columns.Add(new DataColumn("ExchangeID"));

            ///set Add table
            set.Tables.Add(table);
            DataRow row;
            foreach (SecurityFtdcTradeField field in SysConst.Trades)
            {
                string instrumentName = string.Empty;
                if (SysConst.Instruments.ContainsKey(field.InstrumentID))
                    instrumentName = SysConst.Instruments[field.InstrumentID].InstrumentName;
                row = table.NewRow();
                row["TradeID"] = field.OrderRef;
                row["InstrumentID"] = field.InstrumentID;
                row["InstrumentName"] = instrumentName;
                row["Direction"] = field.Direction;
                row["OffSetFlag"] = field.OffsetFlag;
                row["Price"] = field.Price;
                row["Volume"] = field.Volume;
                row["TradeTime"] = field.TradeTime;
                row["OrderSysID"] = field.OrderSysID;

                row["TradeType"] = field.TradeType;
                row["HedgeFlag"] = field.HedgeFlag;
                row["ExchangeID"] = field.ExchangeID;
                table.Rows.Add(row);
            }

            return set;
        }
        #endregion

        #region 资金查询
        private delegate void CallbackUpdateFundDataGrid(DataTable dataTable);

        private CallbackUpdateFundDataGrid callbackUpdateFundDataGrid = null;
        private void FillFundDataGrid(DataTable table)
        {
            if (this.FundDataGrid.RowCount == 0)
            {
                DataView view = new DataView(table);

                this.FundDataGrid.DataSource = view.Table;

                this.FundDataGrid.ClearSelection();
                this.SetFundDataGridColText();
            }
            else
            {

                UpdateMarketGridRow();
            }
        }
        /// <summary>
        /// 
        /// </summary>
        private void SetFundDataGridColText()
        {
            this.FundDataGrid.ReadOnly = true;
            this.FundDataGrid.AutoGenerateColumns = false;


            this.FundDataGrid.Columns["AccountID"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.FundDataGrid.Columns["AccountID"].HeaderText = "资金账号";


            DataGridViewCellStyle defaultCellStyle = this.FundDataGrid.Columns["Withdraw"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["Withdraw"].DefaultCellStyle.ApplyStyle(defaultCellStyle);
            this.FundDataGrid.Columns["Withdraw"].HeaderText = "出金";

            defaultCellStyle = this.FundDataGrid.Columns["Deposit"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["Deposit"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["Deposit"].HeaderText = "入金";

            defaultCellStyle = this.FundDataGrid.Columns["FrozenStampTax"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["FrozenStampTax"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["FrozenStampTax"].HeaderText = "冻结的印花税";


            defaultCellStyle = this.FundDataGrid.Columns["FrozenCommission"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["FrozenCommission"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["FrozenCommission"].HeaderText = "冻结的手续费";


            defaultCellStyle = this.FundDataGrid.Columns["FrozenTransferFee"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["FrozenTransferFee"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["FrozenTransferFee"].HeaderText = "冻结的过户费";


            defaultCellStyle = this.FundDataGrid.Columns["FrozenCash"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["FrozenCash"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["FrozenCash"].HeaderText = "冻结资金";


            this.FundDataGrid.Columns["StampTax"].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.FundDataGrid.Columns["StampTax"].HeaderText = "印花税";

            defaultCellStyle = this.FundDataGrid.Columns["Commission"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["Commission"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["Commission"].HeaderText = "手续费";


            defaultCellStyle = this.FundDataGrid.Columns["TransferFee"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["TransferFee"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["TransferFee"].HeaderText = "过户费";

            defaultCellStyle = this.FundDataGrid.Columns["StockValue"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["StockValue"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["StockValue"].HeaderText = "市值";

            defaultCellStyle = this.FundDataGrid.Columns["Available"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["Available"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["Available"].HeaderText = "可用资金";

            defaultCellStyle = this.FundDataGrid.Columns["TotalEuity"].DefaultCellStyle;
            defaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
            this.FundDataGrid.Columns["TotalEuity"].DefaultCellStyle = defaultCellStyle;
            this.FundDataGrid.Columns["TotalEuity"].HeaderText = "总资产";
        }

        private DataSet GetFundInfo2Client()
        {
            if (callbackUpdateFundDataGrid == null)
                callbackUpdateFundDataGrid += new CallbackUpdateFundDataGrid(FillFundDataGrid);
            ///DataSet
            DataSet set = new DataSet("tradeDataSet");
            ///行情表
            DataTable table = new DataTable("Fund");
            table.Columns.Add(new DataColumn("AccountID"));
            table.Columns.Add(new DataColumn("Withdraw"));
            table.Columns.Add(new DataColumn("Deposit"));
            //名称
            table.Columns.Add(new DataColumn("FrozenStampTax"));



            table.Columns.Add(new DataColumn("FrozenCommission"));
            table.Columns.Add(new DataColumn("FrozenTransferFee"));
            table.Columns.Add(new DataColumn("FrozenCash"));

            table.Columns.Add(new DataColumn("StampTax"));
            table.Columns.Add(new DataColumn("Commission"));

            //合约ID
            table.Columns.Add(new DataColumn("TransferFee"));
            table.Columns.Add(new DataColumn("StockValue"));

            table.Columns.Add(new DataColumn("Available"));

            table.Columns.Add(new DataColumn("TotalEuity"));

            ///set Add table
            set.Tables.Add(table);

            Dictionary<string, SecurityFtdcTradingAccountField> accounts = SysConst.Accounts;
            foreach (string key in accounts.Keys)
            {
                DataRow row = table.NewRow();
                {

                    row["AccountID"] = accounts[key].AccountID;
                    row["Withdraw"] = accounts[key].Withdraw.ToString("n" + minSpreadPriceCount);
                    row["Deposit"] = accounts[key].Deposit.ToString("n" + minSpreadPriceCount);
                    row["FrozenStampTax"] = accounts[key].FrozenStampTax.ToString("n" + minSpreadPriceCount);
                    row["FrozenCommission"] = accounts[key].FrozenCommission.ToString("n" + minSpreadPriceCount);
                    row["FrozenTransferFee"] = accounts[key].FrozenTransferFee.ToString("n" + minSpreadPriceCount);
                    row["FrozenCash"] = accounts[key].FrozenCash.ToString("n" + minSpreadPriceCount);

                    row["StampTax"] = accounts[key].StampTax.ToString("n" + minSpreadPriceCount);
                    row["Commission"] = accounts[key].Commission.ToString("n" + minSpreadPriceCount);
                    row["TransferFee"] = accounts[key].TransferFee.ToString("n" + minSpreadPriceCount);

                    row["StockValue"] = accounts[key].StockValue.ToString("n" + minSpreadPriceCount);
                    row["Available"] = accounts[key].Available.ToString("n" + minSpreadPriceCount);
                    ///总资产
                    double totalEuity = accounts[key].Available + accounts[key].StockValue + accounts[key].FrozenCash + accounts[key].FrozenStampTax + accounts[key].FrozenCommission + accounts[key].FrozenTransferFee;

                    row["TotalEuity"] = totalEuity.ToString("n" + minSpreadPriceCount);

                    table.Rows.Add(row);
                }

            }

            return set;
        }
        #endregion

        private void MarketDataGrid_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {
            if (e.RowIndex < 0) return;
            int colIndex = e.ColumnIndex;

            object value = this.MarketDataGrid.Rows[e.RowIndex].Cells["InstrumentID"].Value;
            if (value != null)
            {
                string key = value.ToString();
                int count = comboBoxInstrument.Items.Count;
                for (int i = 0; i < count; i++)
                {
                    CBListItem item = (CBListItem)comboBoxInstrument.Items[i];
                    if (item.Key == key) { comboBoxInstrument.SelectedIndex = i; break; }
                }
                ///设置选中项
                comboBoxInstrument.SelectedItem = new CBListItem(key, key + "(" + SysConst.Instruments[key].InstrumentName + ")");
                textBoxName.Text = SysConst.Instruments[key].InstrumentName;
                if (colIndex <= 3)
                {
                    radioButtonSell.Checked = true;
                    if (colIndex == 2)
                        textBoxPrice.Text = this.MarketDataGrid.Rows[e.RowIndex].Cells[colIndex].Value.ToString();
                    else
                        textBoxPrice.Text = this.MarketDataGrid.Rows[e.RowIndex].Cells["BidPrice1"].Value.ToString();
                }
                else
                {
                    radioButtonBuy.Checked = true;

                    textBoxPrice.Text = this.MarketDataGrid.Rows[e.RowIndex].Cells["AskPrice1"].Value.ToString();
                }
                textBoxVolume.Text = "1";
            }
        }
        /// <summary>
        /// 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button1_Click(object sender, EventArgs e)
        {
            CBListItem item = (CBListItem)comboBoxInstrument.SelectedItem;
            if (item == null)
            {
                MessageBox.Show("请选择合约！");
                comboBoxInstrument.Focus();
                return;
            }
            if (textBoxPrice.Text == "")
            {
                MessageBox.Show("请输入价格！");
                textBoxPrice.Focus();
                return;
            }
            if (textBoxVolume.Text == "")
            {
                MessageBox.Show("请输入数量！");
                textBoxVolume.Focus();
                return;
            }
            double price = 0;
            int volume = 0;
            Int32.TryParse(textBoxVolume.Text, out volume);
            double.TryParse(textBoxPrice.Text, out price);
            string instrumentID = item.Key;
            string instrumentName = SysConst.Instruments[instrumentID].InstrumentName;


            int requestID = SysConst.GetRequestID();

            SecurityFtdcInputOrderField field = new SecurityFtdcInputOrderField();
            field.BrokerID = SysConst.User.BrokerID;
            field.InvestorID = field.UserID = SysConst.User.UserID;
            field.ExchangeID = SysConst.Instruments[instrumentID].ExchangeID;
            field.InstrumentID = instrumentID;
            field.OrderPriceType = EnumOrderPriceTypeType.LimitPrice;
            field.LimitPrice = price.ToString("n" + minSpreadPriceCount);
            field.VolumeTotalOriginal = volume;///数量		

            field.OrderRef = SysConst.GetOrderID();

            field.GTDDate = SysConst.TraderApi.GetTradingDay();
            field.MinVolume = 0;//最小成交量:1	
            field.ContingentCondition = EnumContingentConditionType.Immediately;//触发条件:立即,
            field.StopPrice = 0;
            field.ForceCloseReason = EnumForceCloseReasonType.NotForceClose;// ((char)EnumForceCloseReasonType.NotForceClose).ToString();
            field.IsAutoSuspend = 0;//自动挂起标志:否	
            field.RequestID = requestID;
            field.UserForceClose = 0;//用户强评标志:否
            field.VolumeCondition = EnumVolumeConditionType.AV; //成交量类型:任何数量
            field.TimeCondition = EnumTimeConditionType.GFD;
            if (this.radioButtonBuy.Checked)
            {
                field.Direction = EnumDirectionType.Buy;
            }
            else if (this.radioButtonSell.Checked)
            {
                field.Direction = EnumDirectionType.Sell;
            }
            char v ='0';
            if (radioButtonOpenPosi.Checked)
            {
                v = (char)EnumOffsetFlagType.Open;
            }
            else if (radioButtonOpenPosi.Checked)
            {
                v = (char)EnumOffsetFlagType.Close;
            }
            char flag = (char)EnumHedgeFlagType.Speculation;
            field.CombHedgeFlag = flag.ToString();

            field.CombOffsetFlag = v.ToString();
            // OffSetFlag = SECURITY_FTDC_OF_Open;
            field.BusinessUnit = "";

            int nRes = SysConst.TraderApi.ReqOrderInsert(field, requestID);
            string msg = string.Format("报单发送{0}", nRes == 0 ? "成功" : "失败");
            Debug.WriteLine(msg);
            MessageBox.Show(msg);
        }


        private void comboBoxInstrument_SelectedIndexChanged(object sender, EventArgs e)
        {
            ComboBox box = (ComboBox)sender;
            string key = ((CBListItem)box.SelectedItem).Key;
            textBoxName.Text = SysConst.Instruments[key].InstrumentName;
            textBoxVolume.Text = "1";
        }

        private void tabControlQuery_SelectedIndexChanged(object sender, EventArgs e)
        {
            int index = tabControlQuery.SelectedIndex;
            if (index == 2 && this.FundDataGrid.RowCount == 0 && queryIsInit)
            {
                ///查询资金信息
                SecurityFtdcQryTradingAccountField accountField = new SecurityFtdcQryTradingAccountField();
                accountField.BrokerID = SysConst.User.BrokerID;
                accountField.InvestorID = "";
                int r = SysConst.TraderApi.ReqQryTradingAccount(accountField, SysConst.GetRequestID());
            }

        }
        /// <summary>
        /// 取消报单
        /// </summary>
        /// <param name="order"></param>
        void CancelOrder(SecurityFtdcOrderField order)
        {
            SecurityFtdcInputOrderActionField field = new SecurityFtdcInputOrderActionField();
            field.BrokerID = order.BrokerID;
            field.UserID = order.UserID;
            field.InvestorID = order.UserID;
            // field.OrderActionRef = SysConst.GetOrderID();


            field.RequestID = order.RequestID;
            field.FrontID = order.FrontID;
            field.SessionID = order.SessionID;
            field.ExchangeID = order.ExchangeID;
            field.ActionFlag = EnumActionFlagType.Delete;

            Double.TryParse(order.LimitPrice, out field.LimitPrice);
            field.VolumeChange = order.VolumeTotalOriginal;
            field.InstrumentID = order.InstrumentID;
            field.OrderLocalID = order.OrderLocalID;

            int nReqID = SysConst.GetRequestID();
            int nRes = SysConst.TraderApi.ReqOrderAction(field, nReqID);
        }
    }


}
