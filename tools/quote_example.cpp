int CTraderApi::ReqOrderInsert(
	OrderField* pOrder,
	int count,
	OrderIDType* pInOut)
{
	int OrderRef = -1;
	if (nullptr == m_pApi)
		return -1;

	CThostFtdcInputOrderField body = {0};

	strncpy(body.BrokerID, m_RspUserLogin.BrokerID, sizeof(TThostFtdcBrokerIDType));
	strncpy(body.InvestorID, m_RspUserLogin.UserID, sizeof(TThostFtdcInvestorIDType));

	body.MinVolume = 1;
	body.ForceCloseReason = THOST_FTDC_FCC_NotForceClose;
	body.IsAutoSuspend = 0;
	body.UserForceClose = 0;
	body.IsSwapOrder = 0;

	//合约
	strncpy(body.InstrumentID, pOrder->InstrumentID, sizeof(TThostFtdcInstrumentIDType));
	strncpy(body.ExchangeID, pOrder->ExchangeID, sizeof(TThostFtdcExchangeIDType));
	//买卖
	body.Direction = OrderSide_2_TThostFtdcDirectionType(pOrder->Side);
	//开平
	body.CombOffsetFlag[0] = OpenCloseType_2_TThostFtdcOffsetFlagType(pOrder->OpenClose);
	//投保
	body.CombHedgeFlag[0] = HedgeFlagType_2_TThostFtdcHedgeFlagType(pOrder->HedgeFlag);
	//数量
	body.VolumeTotalOriginal = (int)pOrder->Qty;

	// 对于套利单，是用第一个参数的价格，还是用两个参数的价格差呢？
	body.LimitPrice = pOrder->Price;
	body.StopPrice = pOrder->StopPx;

	// 针对第二个进行处理，如果有第二个参数，认为是交易所套利单
	if (count>1)
	{
		body.CombOffsetFlag[1] = OpenCloseType_2_TThostFtdcOffsetFlagType(pOrder[1].OpenClose);
		body.CombHedgeFlag[1] = HedgeFlagType_2_TThostFtdcHedgeFlagType(pOrder[1].HedgeFlag);
		// 交易所的移仓换月功能，没有实测过
		body.IsSwapOrder = (body.CombOffsetFlag[0] != body.CombOffsetFlag[1]);
	}

	// 市价与限价
	switch (pOrder->Type)
	{
	case Market:
	case Stop:
	case MarketOnClose:
	case TrailingStop:
		body.OrderPriceType = THOST_FTDC_OPT_AnyPrice;
		body.TimeCondition = THOST_FTDC_TC_IOC;
		body.LimitPrice = 0;
		break;
	case Limit:
	case StopLimit:
	case TrailingStopLimit:
	default:
		body.OrderPriceType = THOST_FTDC_OPT_LimitPrice;
		body.TimeCondition = THOST_FTDC_TC_GFD;
		break;
	}

	// IOC与FOK
	switch (pOrder->TimeInForce)
	{
	case IOC:
		body.TimeCondition = THOST_FTDC_TC_IOC;
		body.VolumeCondition = THOST_FTDC_VC_AV;
		break;
	case FOK:
		body.TimeCondition = THOST_FTDC_TC_IOC;
		body.VolumeCondition = THOST_FTDC_VC_CV;
		//body.MinVolume = body.VolumeTotalOriginal; // 这个地方必须加吗？
		break;
	default:
		body.VolumeCondition = THOST_FTDC_VC_AV;
		break;
	}

	// 条件单
	switch (pOrder->Type)
	{
	case Stop:
	case TrailingStop:
	case StopLimit:
	case TrailingStopLimit:
		// 条件单没有测试，先留空
		body.ContingentCondition = THOST_FTDC_CC_Immediately;
		break;
	default:
		body.ContingentCondition = THOST_FTDC_CC_Immediately;
		break;
	}

	int nRet = 0;
	{
		//可能报单太快，m_nMaxOrderRef还没有改变就提交了
		lock_guard<mutex> cl(m_csOrderRef);

		if (OrderRef < 0)
		{
			nRet = m_nMaxOrderRef;
			++m_nMaxOrderRef;
		}
		else
		{
			nRet = OrderRef;
		}
		sprintf(body.OrderRef, "%d", nRet);

		// 测试平台穿越速度，用完后需要注释掉
		//WriteLog("CTP:ReqOrderInsert:%s %d", body.InstrumentID, nRet);


		//不保存到队列，而是直接发送
		int n = m_pApi->ReqOrderInsert(&body, ++m_lRequestID);
		if (n < 0)
		{
			nRet = n;
			sprintf(m_orderInsert_Id, "%d", nRet);
		}
		else
		{
			// 用于各种情况下找到原订单，用于进行响应的通知
			sprintf(m_orderInsert_Id, "%d:%d:%d", m_RspUserLogin.FrontID, m_RspUserLogin.SessionID, nRet);

			OrderField* pField = (OrderField*)m_msgQueue->new_block(sizeof(OrderField));
			memcpy(pField, pOrder, sizeof(OrderField));
			strcpy(pField->ID, m_orderInsert_Id);
			m_id_platform_order.insert(pair<string, OrderField*>(m_orderInsert_Id, pField));

		}
		strncpy((char*)pInOut, m_orderInsert_Id, sizeof(OrderIDType));
	}

	return nRet;
}

char* CTraderApi::ReqQuoteInsert(
	QuoteField* pQuote,
	OrderIDType* pAskRef,
	OrderIDType* pBidRef)
{
	int QuoteRef = -1;
	if (nullptr == m_pApi)
		return nullptr;

	CThostFtdcInputQuoteField body = {0};

	strcpy(body.BrokerID, m_RspUserLogin.BrokerID);
	strcpy(body.InvestorID, m_RspUserLogin.UserID);

	//合约,目前只从订单1中取
	strncpy(body.InstrumentID, pQuote->InstrumentID, sizeof(TThostFtdcInstrumentIDType));
	strncpy(body.ExchangeID, pQuote->ExchangeID, sizeof(TThostFtdcExchangeIDType));
	//开平
	body.AskOffsetFlag = OpenCloseType_2_TThostFtdcOffsetFlagType(pQuote->AskOpenClose);
	body.BidOffsetFlag = OpenCloseType_2_TThostFtdcOffsetFlagType(pQuote->BidOpenClose);
	//投保
	body.AskHedgeFlag = HedgeFlagType_2_TThostFtdcHedgeFlagType(pQuote->AskHedgeFlag);
	body.BidHedgeFlag = HedgeFlagType_2_TThostFtdcHedgeFlagType(pQuote->BidHedgeFlag);

	//价格
	body.AskPrice = pQuote->AskPrice;
	body.BidPrice = pQuote->BidPrice;

	//数量
	body.AskVolume = (int)pQuote->AskQty;
	body.BidVolume = (int)pQuote->BidQty;

	strncpy(body.ForQuoteSysID, pQuote->QuoteReqID, sizeof(TThostFtdcOrderSysIDType));

	int nRet = 0;
	{
		//可能报单太快，m_nMaxOrderRef还没有改变就提交了
		lock_guard<mutex> cl(m_csOrderRef);

		if (QuoteRef < 0)
		{
			nRet = m_nMaxOrderRef;
			sprintf(body.QuoteRef, "%d", m_nMaxOrderRef);
			sprintf(body.AskOrderRef, "%d", m_nMaxOrderRef);
			sprintf(body.BidOrderRef, "%d", ++m_nMaxOrderRef);
			++m_nMaxOrderRef;
		}
		else
		{
			nRet = QuoteRef;
			sprintf(body.QuoteRef, "%d", QuoteRef);
			sprintf(body.AskOrderRef, "%d", QuoteRef);
			sprintf(body.BidOrderRef, "%d", ++QuoteRef);
			++QuoteRef;
		}

		//不保存到队列，而是直接发送
		int n = m_pApi->ReqQuoteInsert(&body, ++m_lRequestID);
		if (n < 0)
		{
			nRet = n;
			return nullptr;
		}
		else
		{
			sprintf(m_orderInsert_Id, "%d:%d:%d", m_RspUserLogin.FrontID, m_RspUserLogin.SessionID, nRet);

			QuoteField* pField = (QuoteField*)m_msgQueue->new_block(sizeof(QuoteField));
			memcpy(pField, pQuote, sizeof(QuoteField));
			strcpy(pField->ID, m_orderInsert_Id);
			strcpy(pField->AskID, m_orderInsert_Id);
			sprintf(pField->BidID, "%d:%d:%d", m_RspUserLogin.FrontID, m_RspUserLogin.SessionID, nRet + 1);

			m_id_platform_quote.insert(pair<string, QuoteField*>(m_orderInsert_Id, pField));
		}
	}

	return m_orderInsert_Id;
}

void CTraderApi::OnRspQuoteInsert(CThostFtdcInputQuoteField *pInputQuote, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	OrderIDType quoteId = { 0 };

	if (pInputQuote)
	{
		sprintf(quoteId, "%d:%d:%s", m_RspUserLogin.FrontID, m_RspUserLogin.SessionID, pInputQuote->QuoteRef);
	}
	else
	{
		IsErrorRspInfo(pRspInfo, nRequestID, bIsLast);
	}

	unordered_map<string, QuoteField*>::iterator it = m_id_platform_quote.find(quoteId);
	if (it == m_id_platform_quote.end())
	{
		// 没找到？不应当，这表示出错了
		//assert(false);
	}
	else
	{
		// 找到了，要更新状态
		// 得使用上次的状态
		QuoteField* pField = it->second;
		pField->ExecType = ExecType::ExecRejected;
		pField->Status = OrderStatus::Rejected;
		pField->ErrorID = pRspInfo->ErrorID;
		strncpy(pField->Text, pRspInfo->ErrorMsg, sizeof(ErrorMsgType));
		m_msgQueue->Input_Copy(ResponeType::OnRtnQuote, m_msgQueue, m_pClass, 0, 0, pField, sizeof(QuoteField), nullptr, 0, nullptr, 0);
	}
}

void CTraderApi::OnErrRtnQuoteInsert(CThostFtdcInputQuoteField *pInputQuote, CThostFtdcRspInfoField *pRspInfo)
{
	OrderIDType quoteId = { 0 };

	if (pInputQuote)
	{
		sprintf(quoteId, "%d:%d:%s", m_RspUserLogin.FrontID, m_RspUserLogin.SessionID, pInputQuote->QuoteRef);
	}
	else
	{
		IsErrorRspInfo(pRspInfo, 0, true);
	}

	unordered_map<string, QuoteField*>::iterator it = m_id_platform_quote.find(quoteId);
	if (it == m_id_platform_quote.end())
	{
		// 没找到？不应当，这表示出错了
		//assert(false);
	}
	else
	{
		// 找到了，要更新状态
		// 得使用上次的状态
		QuoteField* pField = it->second;
		pField->ExecType = ExecType::ExecRejected;
		pField->Status = OrderStatus::Rejected;
		pField->ErrorID = pRspInfo->ErrorID;
		strncpy(pField->Text, pRspInfo->ErrorMsg, sizeof(ErrorMsgType));
		m_msgQueue->Input_Copy(ResponeType::OnRtnQuote, m_msgQueue, m_pClass, 0, 0, pField, sizeof(QuoteField), nullptr, 0, nullptr, 0);
	}
}

void CTraderApi::OnRtnQuote(CThostFtdcQuoteField *pQuote)
{
	OnQuote(pQuote);
}

int CTraderApi::ReqQuoteAction(const string& szId,OrderIDType* pOutput)
{
	unordered_map<string, CThostFtdcQuoteField*>::iterator it = m_id_api_quote.find(szId);
	if (it == m_id_api_quote.end())
	{
		sprintf((char*)pOutput, "%d", -100);
		return -100;
	}
	else
	{
		// 找到了订单
		ReqQuoteAction(it->second,pOutput);
	}
	return 0;
}

int CTraderApi::ReqQuoteAction(CThostFtdcQuoteField *pQuote, OrderIDType* pOutput)
{
	if (nullptr == m_pApi)
		return 0;

	CThostFtdcInputQuoteActionField body = {0};

	///经纪公司代码
	strcpy(body.BrokerID, pQuote->BrokerID);
	///投资者代码
	strcpy(body.InvestorID, pQuote->InvestorID);
	///报单引用
	strcpy(body.QuoteRef, pQuote->QuoteRef);
	///前置编号
	body.FrontID = pQuote->FrontID;
	///会话编号
	body.SessionID = pQuote->SessionID;
	///交易所代码
	strcpy(body.ExchangeID, pQuote->ExchangeID);
	///报单编号
	strcpy(body.QuoteSysID, pQuote->QuoteSysID);
	///操作标志
	body.ActionFlag = THOST_FTDC_AF_Delete;
	///合约代码
	strcpy(body.InstrumentID, pQuote->InstrumentID);

	int nRet = m_pApi->ReqQuoteAction(&body, ++m_lRequestID);
	if (nRet < 0)
	{
		sprintf(m_orderAction_Id, "%d", nRet);
	}
	else
	{
		memset(m_orderAction_Id, 0, sizeof(OrderIDType));
	}
	strncpy((char*)pOutput, m_orderAction_Id, sizeof(OrderIDType));

	return nRet;
}

void CTraderApi::OnRspQuoteAction(CThostFtdcInputQuoteActionField *pInputQuoteAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	OrderIDType quoteId = { 0 };
	if (pInputQuoteAction)
	{
		sprintf(quoteId, "%d:%d:%s", pInputQuoteAction->FrontID, pInputQuoteAction->SessionID, pInputQuoteAction->QuoteRef);
	}
	else
	{
		IsErrorRspInfo(pRspInfo, nRequestID, bIsLast);
	}

	unordered_map<string, QuoteField*>::iterator it = m_id_platform_quote.find(quoteId);
	if (it == m_id_platform_quote.end())
	{
		// 没找到？不应当，这表示出错了
		//assert(false);
	}
	else
	{
		// 找到了，要更新状态
		// 得使用上次的状态
		QuoteField* pField = it->second;
		strcpy(pField->ID, quoteId);
		//sprintf(pField->AskID, "%d:%d:%s", pInputQuoteAction->FrontID, pInputQuoteAction->SessionID, pInputQuoteAction->);
		//sprintf(pField->BidID, "%d:%d:%s", pInputQuoteAction->FrontID, pInputQuoteAction->SessionID, pInputQuoteAction->QuoteRef);
		pField->ExecType = ExecType::ExecCancelReject;
		pField->ErrorID = pRspInfo->ErrorID;
		strncpy(pField->Text, pRspInfo->ErrorMsg, sizeof(ErrorMsgType));
		m_msgQueue->Input_Copy(ResponeType::OnRtnQuote, m_msgQueue, m_pClass, 0, 0, pField, sizeof(QuoteField), nullptr, 0, nullptr, 0);
	}
}

void CTraderApi::OnErrRtnQuoteAction(CThostFtdcQuoteActionField *pQuoteAction, CThostFtdcRspInfoField *pRspInfo)
{
	OrderIDType quoteId = { 0 };

	if (pQuoteAction)
	{
		sprintf(quoteId, "%d:%d:%s", pQuoteAction->FrontID, pQuoteAction->SessionID, pQuoteAction->QuoteRef);
	}
	else
	{
		IsErrorRspInfo(pRspInfo, 0, true);
	}

	unordered_map<string, QuoteField*>::iterator it = m_id_platform_quote.find(quoteId);
	if (it == m_id_platform_quote.end())
	{
		// 没找到？不应当，这表示出错了
		//assert(false);
	}
	else
	{
		// 找到了，要更新状态
		// 得使用上次的状态
		QuoteField* pField = it->second;
		strcpy(pField->ID, quoteId);
		pField->ExecType = ExecType::ExecCancelReject;
		pField->ErrorID = pRspInfo->ErrorID;
		strncpy(pField->Text, pRspInfo->ErrorMsg, sizeof(ErrorMsgType));
		m_msgQueue->Input_Copy(ResponeType::OnRtnQuote, m_msgQueue, m_pClass, 0, 0, pField, sizeof(QuoteField), nullptr, 0, nullptr, 0);
	}
}

