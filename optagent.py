import * from tradeagent
import workdays
import numpy as np
import datetime
from ctp.futures import ApiStruct, MdApi, TraderApi

THOST_TERT_RESTART  = ApiStruct.TERT_RESTART
THOST_TERT_RESUME   = ApiStruct.TERT_RESUME
THOST_TERT_QUICK    = ApiStruct.TERT_QUICK

BDAYS_PER_YEAR = 252.0

OptExpiryDict = {'IO1409': datetime.date(2014, 9, 19),
			  'IO1410': datetime.date(2014,10, 17),
			  'IO1411': datetime.date(2014,11, 21),
			  'IO1412': datetime.date(2014,12, 19),
			  'IO1503': datetime.date(2015, 3, 20) }

def tick2time(curr_date, tick_id):
	microsec = tick_id % 10
	dtime = tick_id / 10
	sec  = dtime % 100
	dtime = dtime/100
	min = dtime % 100
	hrs = dtime/100
	return datetime.datetime(curr_date.year,curr_date.month,curr_date.day, hrs, min, dtime, sec, microsec)
	
class OptArbAgent(Agent):
	def __init__(self, name, trader, cuser, fut_inst, strikes, caplimit, tday=datetime.date.today()):
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
		Agent.__init__(self, name, trader, cuser, insts, tday)
	
	def init_init(self):
		self.opt_expiry = OptExpiryDict[optkey]
		self.ir = 0.0
		
	
	def time2expiry(self):
		if self.scur_day < self.opt_expiry:
			return workdays.networkdays(self.scur_day, self.opt_expiry, misc.CHN_Holidays)/BDAYS_PER_YEAR
		else:
			sec = int((self.tick_id % 1000)/10.0)
			min = int((self.tick_id % 100000)/1000.0)
			hr  = self.tick_id / 100000
			return max(((21.0 -(hr+(min+sec/60.0)/60.0))/5.75)/BDAYS_PER_YEAR, 0.0)
	
	def discf(self):
		return np.exp(-self.ir*self.time2expiry())
		
	def run_strats(self, ctick):
		pass
		
def test_main():
    logging.basicConfig(filename="ctp_user_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    fut_inst = 'IF1409'
    strikes = [2300, 2350, 2400, 2450, 2500, 2550, 2600 ]
    caplimit = 500000
    agent_name = 'optarb'
	test_user = BaseObject( broker_id="8000", 
								 investor_id="*", 
								 passwd="*", 
								 port="tcp://qqfz-md1.ctp.shcifco.com:32313"
								 )
	test_trader = BaseObject( broker_id="8000", 
								 investor_id="24661668", 
								 passwd ="121862", 
								 ports  = ["tcp://qqfz-front1.ctp.shcifco.com:32305",
										   "tcp://qqfz-front2.ctp.shcifco.com:32305",
										   "tcp://qqfz-front3.ctp.shcifco.com:32305"])
	user_cfg = test_user
	trader_cfg = test_trader
	tday = datetime.date(2014,9,9)
	myagent = OptArbAgent(agent_name, None, None, fut_inst, strikes, caplimit, tday=0)
	myagent.trader = trader = TraderSpiDelegate(instruments=myagent.instruments, 
							 broker_id=trader_cfg.broker_id,
							 investor_id= trader_cfg.investor_id,
							 passwd= trader_cfg.passwd,
							 agent = myagent,
					   )
	trader.Create('trader')
	trader.SubscribePublicTopic(THOST_TERT_QUICK)
	trader.SubscribePrivateTopic(THOST_TERT_QUICK)
	for port in trader_cfg.ports:
		trader.RegisterFront(port)
	trader.Init()	
	make_user(myagent, user_cfg)
    
    try:
    	myagent.resume()
    	
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        my_agent.mdapis = [] 
        my_agent.trader = None

if __name__=="__main__":
    test_main()
