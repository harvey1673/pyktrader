/*!
* \file Program.cs
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
using System.Windows.Forms;
using RELib_LTSNet;

namespace RELib_LTScsDemo
{
    static class Program
    {
        /// <summary>
        /// 应用程序的主入口点。
        /// </summary>
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            ///
            //SecurityFtdcInstrumentField field1 = new SecurityFtdcInstrumentField
            //{
            //    InstrumentID = "10000031",
            //    InstrumentName = "上汽集团6月1200"
            //};
            //SysConst.InstrumentData[field1.InstrumentID] = field1;
            SecurityFtdcInstrumentField field2 = new SecurityFtdcInstrumentField
            {
                InstrumentID = "000002",
                InstrumentName = "A股指数"
            };
            SysConst.InstrumentData[field2.InstrumentID] = field2;
            SecurityFtdcInstrumentField field3 = new SecurityFtdcInstrumentField
            {
                InstrumentID = "000003",
                InstrumentName = "dddd"
            };
            SysConst.InstrumentData[field3.InstrumentID] = field3;
            SecurityFtdcInstrumentField field4 = new SecurityFtdcInstrumentField
            {
                InstrumentID = "000004",
                InstrumentName = "工业指数"
            };
            SysConst.InstrumentData[field4.InstrumentID] = field4;
            SecurityFtdcInstrumentField field5 = new SecurityFtdcInstrumentField
            {
                InstrumentID = "000005",
                InstrumentName = "商业指数"
            };
            SysConst.InstrumentData[field5.InstrumentID] = field5;
            SecurityFtdcInstrumentField field6 = new SecurityFtdcInstrumentField
            {
                InstrumentID = "000006",
                InstrumentName = "地产指数"
            };

            //SysConst.InstrumentData[field6.InstrumentID] = field6;
            //SecurityFtdcInstrumentField field7 = new SecurityFtdcInstrumentField
            //{
            //    InstrumentID = "10000032",
            //    InstrumentName = "上汽集团6月1300"
            //};
            //SysConst.InstrumentData[field7.InstrumentID] = field7;
            //SecurityFtdcInstrumentField field8 = new SecurityFtdcInstrumentField
            //{
            //    InstrumentID = "10000035",
            //    InstrumentName = "aaaaaaa"
            //};

            //SysConst.InstrumentData[field8.InstrumentID] = field8;
            //SecurityFtdcInstrumentField field9 = new SecurityFtdcInstrumentField
            //{
            //    InstrumentID = "10000037",
            //    InstrumentName = "ccccc"
            //};
            //SysConst.InstrumentData[field9.InstrumentID] = field9;


            //单独测试行情
            //Application.Run(new LTSMarketDemo());
           Application.Run(new LTSDemo());
        }
    }
}
