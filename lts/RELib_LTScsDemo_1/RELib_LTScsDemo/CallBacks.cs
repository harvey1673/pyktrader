using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Diagnostics;

namespace RELib_LTScsDemo
{
    public class CallBacks
    {
       // private AsyncShowCallbackData asyncMsg = null;
       // public CallBacks
        public void OnFrontConnected()
        {
            //DebugPrintFunc(new StackTrace());
            //ReqUserLogin();
           // asyncMsg.AppendMsg("行情服务器连接成功！");
            Debug.WriteLine("行情服务器连接成功");
        } 
    }
}
