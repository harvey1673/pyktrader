/*!
* \file EntityKey.cs
* \brief 示例代码主程序接口
*
* 本项目是基于华宝技术LTS证券接口开发的示例程序，用于展示如何在LTS
* 环境下进行开发。示例代码演示了LTS各类接口的调用，在编写相关项目时
* 可以参考。
* 由尔易信息提供开源，最新代码可从http://github.com/REInfo获取。
* 上海尔易信息科技有限公司提供证券、期货、期权、现货等市场交易、结算、
* 风控业务的客户化定制服务。
*
* \author Christian
* \version 1.0
* \date 2014-6-16
* 
*/

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace RELib_LTScsDemo
{
    /// <summary>
    /// 主键类
    /// </summary>
    public class EntityKey
    {
        private string id = String.Empty;

        public string ID
        {
            get { return id; }
            set { id = value; }
        }

        private string exchangeID = String.Empty;

        public string ExchangeID
        {
            get { return exchangeID; }
            set { exchangeID = value; }
        }

        public override string ToString()
        {
            return id + "#" + exchangeID;
        }
        private string sessionID = string.Empty;

        public string SessionID
        {
            get { return sessionID; }
            set { sessionID = value; }
        }

        public override bool Equals(object obj)
        {
            EntityKey target = (EntityKey)obj;
            if (target != null)
                return this == target;
            return false;
        }
        /// <summary>
        /// 等于
        /// </summary>
        /// <param name="source"></param>
        /// <param name="target"></param>
        /// <returns></returns>
        public static bool operator ==(EntityKey source, EntityKey target)
        {
            if (source.id == target.ID && source.exchangeID == target.ExchangeID && source.sessionID == target.sessionID)
                return true;
            return false;
        }
        /// <summary>
        /// 不等于
        /// </summary>
        /// <param name="source"></param>
        /// <param name="target"></param>
        /// <returns></returns>
        public static bool operator !=(EntityKey source, EntityKey target)
        {
            if (source.id == target.ID && source.exchangeID == target.ExchangeID && source.sessionID == target.sessionID)
                return false;
            return true;
        }
    }
}
