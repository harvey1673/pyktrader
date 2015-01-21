/*!
* \file AsyncShow.cs
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
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Data;

namespace RELib_LTScsDemo
{
    public class AsyncShowCallbackData
    {
        public AsyncSetProgressMax SetProgressMax
        {
            get;
            set;
        }

        public AsyncProgressPerformStep ProgressPerformStep
        {
            get;
            set;
        }

        public AsyncSetProgressBarStyle SetProgressBarStyle
        {
            get;
            set;
        }

        public AsyncSetTitle AppendMsg
        {
            get;
            set;
        }
        public AsyncSetTitle ShowMsg
        {
            get;
            set;
        }
        public AsyncShowError ShowError
        {
            get;
            set;
        }

        public AsyncDone Done
        {
            get;
            set;
        }

        public bool Abort
        {
            get;
            set;
        }

        public object Tag
        {
            get;
            set;
        }
        public AsyncUpdateGrid UpdateGrid
        {
            get;
            set;
        }
    }
    public delegate void AsyncShowCallback(AsyncShowCallbackData asyncCallBackData);
    public delegate void AsyncSetProgressMax(int value);
    public delegate void AsyncSetProgressValue(int value);
    public delegate void AsyncProgressPerformStep();
    public delegate void AsyncUpdateGrid(DataGridView grid,DataTable table);
    public delegate void AsyncSetProgressBarStyle(System.Windows.Forms.ProgressBarStyle style);

    public delegate void AsyncDone();
    public delegate void AsyncSetTitle(string title);
    public delegate void AsyncShowError(Exception ex);
    /// <summary>
    /// 异步显示
    /// </summary>
    public static class AsyncShowCallbackExtendHelper
    {
        public static AsyncShowCallbackData MakeAsyncShowCallback(this Control ctl, Label label, ProgressBar progressBar)
        {
            return new AsyncShowCallbackData
            {
                AppendMsg = new AsyncSetTitle((p) =>
                {
                    if (ctl.Created)
                    {
                        ctl.Invoke(new Action(() =>
                        {
                            label.Text += "\n" + p;
                        }));
                        Application.DoEvents();
                    }
                }),
                ShowMsg = new AsyncSetTitle((p) =>
                {
                    ctl.Invoke(new Action(() =>
                    {
                        label.Text = p;
                    }));
                    Application.DoEvents();
                }),
                SetProgressMax = new AsyncSetProgressMax((p) =>
                {
                    ctl.Invoke(new Action(() =>
                    {
                        progressBar.Maximum = p;
                    }));
                    Application.DoEvents();
                }),
                UpdateGrid = new AsyncUpdateGrid((grid,table) =>
                {
                    ctl.Invoke(new Action(() =>
                    {
                        grid.DataSource = table;
                    }));
                    Application.DoEvents();
                }),
               
                ProgressPerformStep = new AsyncProgressPerformStep(() =>
                {
                    ctl.Invoke(new Action(() =>
                    {
                        if (progressBar.Value + 1 < progressBar.Maximum)
                        {
                            progressBar.PerformStep();
                        }
                    }));
                    Application.DoEvents();
                }),
               
                Done = new AsyncDone(() =>
                {
                    ctl.Invoke(new Action(() =>
                    {
                        if (ctl is Form)
                            (ctl as Form).Close();
                    }));
                }),
                Abort = false
            };
        }
    }
}
