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
    public partial class LoginWin : Form
    {
        private LTSDemo parent = null;
      //  private AsyncShowCallbackData asyncMsg = null;
        public LoginWin(LTSDemo parent)
        {
            this.parent = parent;
            InitializeComponent();
           this.parent.asyncMsg =  AsyncShowCallbackExtendHelper.MakeAsyncShowCallback(this, msglabel, null);
            //Init();
        }
        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);


        }
        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);

            Debug.WriteLine("LoginWin 退出！");
        }
        private void button1_Click(object sender, EventArgs e)
        {
            if (!CheckForm()) return;
            //登录失败 继续停留在这个登录窗口
            if (!Login()) return;



        }
        /// <summary>
        /// 验证表单
        /// </summary>
        /// <returns></returns
        private bool CheckForm()
        {
            bool isOk = true;

            if (textBoxBrokerID.Text == "")
            {
                MessageBox.Show("机构代码不能为空！");
                textBoxBrokerID.Focus();
                isOk = false;
            }
            else if (textBoxUserID.Text == "")
            {
                MessageBox.Show("账号不能为空！");
                textBoxUserID.Focus();
                isOk = false;
            }
            else if (textBoxPassword.Text == "")
            {
                MessageBox.Show("密码不能为空！");
                textBoxPassword.Focus();
                isOk = false;
            }


            return isOk;
        }

        private bool Login()
        {
            bool isLogin = false;
            SysConst.User.BrokerID = textBoxBrokerID.Text.Trim();
            SysConst.User.UserID = textBoxUserID.Text.Trim();
            SysConst.User.Password = textBoxPassword.Text.Trim();

            int result = SysConst.TraderApi.ReqUserLogin(SysConst.User, SysConst.GetRequestID());
            if (result == 0) isLogin = true;
            String msg = "--->>> 发送用户登录请求: " + ((result == 0) ? "成功" : "失败");
            parent.asyncMsg.ShowMsg(msg);
            Debug.WriteLine(msg);
            return isLogin;
        }

      

       

        private void button2_Click(object sender, EventArgs e)
        {
            SysConst.Release();
            DialogResult = System.Windows.Forms.DialogResult.Cancel;
        }

        /// <summary>
        /// 登录回调函数
        /// </summary>
        /// <param name="pRspUserLogin"></param>
        /// <param name="pRspInfo"></param>
        /// <param name="nRequestID"></param>
        /// <param name="bIsLast"></param>
        public void OnRspUserLogin(SecurityFtdcRspUserLoginField pRspUserLogin, SecurityFtdcRspInfoField pRspInfo, int nRequestID, bool bIsLast)
        {

            if (bIsLast && !SysConst.IsErrorRspInfo(pRspInfo))
            {
                ///获取当前交易日,说明登录成功了
                String msg = "\n--->>> 获取当前交易日 = " + SysConst.TraderApi.GetTradingDay();
                //Console.WriteLine(msg);

                Debug.WriteLine(msg);
                // 请求订阅行情
                //SubscribeMarketData();
                parent.asyncMsg.ShowMsg("交易账号登录成功！");

                SecurityFtdcReqUserLoginField req = new SecurityFtdcReqUserLoginField();
                req.BrokerID = SysConst.User.BrokerID;
                req.UserID = SysConst.User.UserID;
                req.Password = SysConst.User.Password;
                int iResult = SysConst.MarketDataApi.ReqUserLogin(req, SysConst.GetRequestID());

                msg = "\n--->>> 发送用户登录请求: " + ((iResult == 0) ? "成功" : "失败");
                parent.asyncMsg.AppendMsg(msg);
                Debug.WriteLine(msg);
                parent.QryInstrument();
                ///留点行情处理时间
                Thread.Sleep(1000);
                DialogResult = System.Windows.Forms.DialogResult.OK;
                
            }
            else
            {
                parent.asyncMsg.ShowMsg("登录失败：账号或者密码错误！");
                Debug.WriteLine(pRspInfo.ErrorMsg);
            }
        }
    }
}
