import tradeagent as agent

class OptArbAgent(agent.Agent):
    def __init__(self,trader,cuser, fut_inst, strikes, caplimit, tday=0):
        if fut_inst[1].isalpha():
            key = fut_inst[:2]
        else:
            key = fut_inst[:1]
        if key == 'IF':
            optkey = fut_inst.replace('IF','IO')
        else:
            optkey = fut_inst
        
        self.strikes = strikes
        self.fut_inst   = fut_inst
        self.call_insts = [optkey+'-C-'+str(s) for s in strikes]
        self.put_insts  = [optkey+'-P-'+str(s) for s in strikes]
        insts = [self.fut_inst]+self.call_insts+self.put_insts        
        Agent.__init__(self, trader, cuser, insts, tday)
        nsize = len(strikes)
        self.curr_strat = {'callsprd': [0.0]*nsize,
                           'putsprd' : [0.0]*nsize,
                           'callfly' : [0.0]*nsize,
                           'putfly'  : [0.0]*nsize,
                           'callput' : [0.0]*nsize }
        self.capital_limit = caplimit
        self.save_flag = False
    
    def trade_on_tick(self, ctick):
        while True:
            while not self.event.is_set():
                self.event.wait()
            print "working"
            self.logger.info(u'Schedule event set, start working on TradeOnSchedule...')
            mkt_data = self.prepare_market_data()
            exch = self.instruments[self.fut_inst].exchange
            fwdmargin = self.instruments[self.fut_inst].marginrate[0]
            newstrat = arbopt.arboptimizer( mkt_data, exch, self.curr_strat, self.capital_limit, fwdmargin );
            newpos = arbopt.strat2pos(newstrat)
                                    
    def prepare_market_data(self):
        mktdata = {'strikes':self.strikes}
        mktdata['fwdbid'] = self.instruments[self.fut_inst].bid_price1
        mktdata['fwdask'] = self.instruments[self.fut_inst].ask_price1
        mktdata['callbid'] = []
        mktdata['callask'] = []
        mktdata['putbid']  = []
        mktdata['putask']  = []
        for c_inst, p_inst in zip(self.strikes, self.call_insts, self.put_insts):
            mktdata['callbid'].append(self.instruments[c_inst].bid_price1)
            mktdata['callask'].append(self.instruments[c_inst].ask_price1)
            mktdata['putbid'].append(self.instruments[p_inst].bid_price1)
            mktdata['putask'].append(self.instruments[p_inst].ask_price1)
        
        return mktdata

def test_main():
    logging.basicConfig(filename="ctp_user_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    fut_inst = 'IF1406'
    strikes = [1950, 2000, 2050, 2100, 2150, 2200, 2250, 2300, 2350]
    caplimit = 1000000
    my_agent = OptArbAgent(None, None, fut_inst, strikes, caplimit)


    usercfg = BaseObject(broker_id = '8000', 
                         investor_id = '*',
                         passwd= '*',
                         port='tcp://qqfz-md1.ctp.shcifco.com:32313')
        
    tradercfg = BaseObject(broker_id = '8000', 
                         investor_id = '24661668',
                         passwd= '121862',
                         port='tcp://qqfz-front1.ctp.shcifco.com:32305')

    user = MdSpiDelegate(instruments=my_agent.instruments, 
                             broker_id=usercfg.broker_id,
                             investor_id= usercfg.investor_id,
                             passwd= usercfg.passwd,
                             agent = my_agent,
                             )
    user.Create('opt arb trader')

    my_agent.trade_on_sched(runperiod=datetime.timedelta(seconds=1))
    user.RegisterFront(usercfg.port)
    user.Init()
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        my_agent.mdapis = [] 
        my_agent.trader = None
