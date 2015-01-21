/*!
* \file Util.cpp
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
#include "Util.h"

#include <string.h>
#include <memory.h>
#include <stdlib.h>

using namespace System::Runtime::InteropServices;

namespace RELib_LTSNative
{
	CAutoStrPtr::CAutoStrPtr(String^ str)
	{
		if(str != nullptr)
		{
			//吧string类型转换为char指针
			m_pChar = (char*) Marshal::StringToHGlobalAnsi(str).ToPointer();
			//m_Length = strlen(m_pChar);
		}
		else
			 m_pChar = nullptr;//空指针
	}
	/*CAutoStrPtr::CAutoStrPtr(String^ str, void* pDst, int length)
	{
		if(str != nullptr && pDst!= nullptr)
		{
			m_pChar = (char*) Marshal::StringToHGlobalAnsi(str).ToPointer();
			m_Length = strlen(m_pChar);
			memcpy(pDst, m_pChar, __min(length, m_Length));
		}
		else
			 m_pChar = nullptr;
	}*/

	CAutoStrPtr::~CAutoStrPtr()
	{
		if(m_pChar != nullptr)
			//释放以前从进程的非托管内存中分配的内存。
			Marshal::FreeHGlobal(IntPtr(m_pChar));
	}

	///其实只要用模板来解决就好了，详见Util.h
	SecurityFtdcRspInfoField^ RspInfoField(CSecurityFtdcRspInfoField *pRspInfo)
	{
		//提供了一个方法集，这些方法用于分配非托管内存、复制非托管内存块、将托管类型转换为非托管类型，此外还提供了在与非托管代码交互时使用的其他杂项方法。
		//将数据从非托管内存块封送到新分配的指定类型的托管对象。
		//IntPtr(pRspInfo) 指向非托管内存块的指针。
		// ThostFtdcRspInfoField::typeid =>Type
		//PtrToStructure 返回的是Object^, 所以要用safe_cast进行类别转换
		return safe_cast<SecurityFtdcRspInfoField^>(Marshal::PtrToStructure(IntPtr(pRspInfo), SecurityFtdcRspInfoField::typeid));
	}

}
/*
//释放非托管内存中分配的内存。
static void Main()
{
	Console.WriteLine("\nStringToGlobalAnsi\n");

	// Create a managed string.
	String  managedString = "I am a managed String";
	Console.WriteLine("1) managedString = " + managedString );

	// Marshal the managed string to unmanaged memory.
	IntPtr stringPointer = (IntPtr)Marshal.StringToHGlobalAnsi(managedString);
	Console.WriteLine("2) stringPointer = {0}", stringPointer );

	// Get the string back from unmanaged memory
	String RetrievedString = Marshal.PtrToStringAnsi( stringPointer);
	Console.WriteLine("3) Retrieved from unmanaged memory = " + RetrievedString );

	// Always free the unmanaged string.
	Marshal.FreeHGlobal(stringPointer);

	// IntPtr handle value is still the same:
	Console.WriteLine("4) stringPointer = " + stringPointer );

	// However, it contains no data after being freed:
	String RetrievedString2 = Marshal.PtrToStringAnsi( stringPointer);
	Console.WriteLine("5) RetrievedString2 = " + RetrievedString2 );
}


using namespace System;
using namespace System::Runtime::InteropServices;

#include <iostream>                                                 // for printf


int main()
{
	// Create a managed string.
	String^ managedString = "Hello unmanaged world (from the managed world).";

	// Marshal the managed string to unmanaged memory.
	//托管的string^ 转换为 非托管的char*（需要手动释放该内存空间）
	char* stringPointer = (char*) Marshal::StringToHGlobalAnsi(managedString ).ToPointer();

	printf("stringPointer = %s\n", stringPointer);

	// Always free the unmanaged string.
	Marshal::FreeHGlobal(IntPtr(stringPointer));

	return 0;
}
*/