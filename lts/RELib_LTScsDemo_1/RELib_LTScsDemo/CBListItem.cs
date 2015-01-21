/*!
* \file CBListItem.cs
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

namespace RELib_LTScsDemo
{
    using System;
    /// <summary>
    /// comboboxItem
    /// </summary>
    public class CBListItem
    {
        private string _key = string.Empty;
        private string _value = string.Empty;
        /// <summary>
        /// key  Value
        /// </summary>
        /// <param name="pKey"></param>
        /// <param name="pValue"></param>
        public CBListItem(string pKey, string pValue)
        {
            this._key = pKey;
            this._value = pValue;
        }

        public override string ToString()
        {
            return this._value;
        }

        public string Key
        {
            get
            {
                return this._key;
            }
            set
            {
                this._key = value;
            }
        }

        public string Value
        {
            get
            {
                return this._value;
            }
            set
            {
                this._value = value;
            }
        }
    }
}

