from agent import *
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

def fut2opt(fut_inst, expiry, otype, strike):
	product = inst2product(fut_inst)
	if product == 'IF':
		optkey = fut_inst.replace('IF','IO')
	else:
		optkey = product
	if product == 'Stock':
		optkey = optkey + otype + expiry.strftime('%y%m')
	else:
		optkey + '-' + upper(type) + '-'
	opt_inst = optkey + str(int(strike))
	return opt_inst

def opt_expiry(fut_inst, expiry_month):
	wkday = expiry_month.weekday()
	if fut_inst[:6].isdigit():
		nbweeks = 4
		if wkday <= 2: 
			nbweeks = 3
		expiry = expiry_month + datetime.timedelta(days = nbweeks*7 - wkday + 1)
		expiry = workdays.workday(expiry, 1, CHN_Holidays)
	elif fut_inst[:2]='IF':
		nbweeks = 2
		if wkday >= 5:
			nbweeks = 3
		expiry = expiry_month + datetime.timedelta(days = nbweeks*7 - wkday + 3)
		expiry = workdays.workday(expiry, 1, CHN_Holidays)
	return expiry

def get_opt_margin(fut_price, strike, type):
	return 0.0
    
class OptInstrument(Instrument):
    def __init__(self, underlying, cont, otype, strike):
        opt_inst = fut2opt(underlying, expiry, otype, strike)
		Instrument.__init__(self, opt_inst)
		self.strike = strike
		self.otype = otype
		self.underlying = underlying
		self.expiry = opt_expiry(underlying, cont)

	def time2exp(self, curr_time):
		curr_date = curr_time.date()
		exp_date = self.expiry.date()
		if curr_time > self.expiry:
			return 0.0
		elif exp_date < curr_date:
			return workdays.networkdays(self.scur_day, self.expiry.date(), misc.CHN_Holidays)/BDAYS_PER_YEAR
		else:
			delta = self.exp - curr_time 
			return (delta.hour*3600+delta.min*60+delta.second)/3600.0/5.5//\BDAYS_PER_YEAR
			
    def get_inst_info(self):
        for exch in CHN_Stock_Exch:
            if self.name in CHN_Stock_Exch[exch]:
                self.product = 'Stock'
                self.exchange = exch
                self.start_tick_id = 1530000
                self.last_tick_id = 2100000
                self.multiple = 0
                self.tick_base = 0.01
                self.broker_fee = 0
                return
        self.product = 'IO'
        self.exchange = 'CFFEX'
        self.start_tick_id =  1515000
        self.last_tick_id =  2115000     
        self.multiple = 100
        self.tick_base = 0.1
        self.broker_fee = 0.0
        return
    
    def get_margin_rate(self):
        return (1,0)

    def calc_margin_amount(self, under_price, strike, direction):
		if direction == ORDER_BUY:
			return price
		else:
			return get_opt_margin(under_price, strike, self.otype)
        return 
     	
class StockOptAgent(Agent):
	def __init__(self, name, trader, cuser, underlyings, expiries, strikes, strategies = [], tday=datetime.date.today(), 
                 folder = 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\'):
		self.underlyings = underlyings
		self.expiries = expiries
		self.strikes = strikes
		self.option_map = dict([((under, expiry, otype, strike), fut2opt(under, expiry, otype, strike))  \
									for strike in strikes for otype in ['C','P']    \
									for expiry in expiries for under in underlyings])
		self.volgrids = dict
		instruments = self.underlyings + self.option_map.values() 
        daily_data_days = 0
        min_data_days = 0
		Agent.__init__(self, name, trader, cuser, instruments, strategies, tday, folder, daily_data_days, min_data_days)	
	
	def create_instruments(self, instruments):
		objs = {}
		for inst in instruments:
			if inst in self.fut_insts:
				objs[inst] = Instrument(inst)
				objs[inst].get_inst_info()
				objs[inst].get_margin_rate()
			elif:
				spec = self.option_map[inst]
				objs[inst] = OptInstrument(spec[0], spec[1], spec[2], spec[3])
				objs[inst].get_inst_info()
				objs[inst].get_margin_rate()
		return objs

    def prepare_data_env(self, mid_day = True): 
        if self.daily_data_days > 0: # for the moment, ignore mid_day flag
            self.logger.info('Updating historical daily data for %s' % self.scur_day.strftime('%Y-%m-%d'))            
            daily_start = workdays.workday(self.scur_day, -self.daily_data_days, CHN_Holidays)
            daily_end = self.scur_day
            for inst in self.underlyings:  
                self.day_data[inst] = mysqlaccess.load_daily_data_to_df('stock_daily', inst, daily_start, daily_end)
                df = self.day_data[inst]
                if len(df) > 0:
                    self.instruments[inst].price = df['close'][-1]
                    self.instruments[inst].last_update = datetime.datetime.fromordinal(df.index[-1].toordinal())
                    self.instruments[inst].prev_close = df['close'][-1]
                for fobj in self.day_data_func:
                    ts = fobj.sfunc(df)
                    df[ts.name]= pd.Series(ts, index=df.index)  

        if self.min_data_days > 0:  # for the moment, ignore mid_day flag
            self.logger.info('Updating historical min data for %s' % self.scur_day.strftime('%Y-%m-%d')) 
            d_start = workdays.workday(self.scur_day, -self.min_data_days, CHN_Holidays)
            d_end = self.scur_day
            for inst in self.underlyings:
                min_start = int(self.instruments[inst].start_tick_id/1000)
                min_end = int(self.instruments[inst].last_tick_id/1000)+1
                mindata = mysqlaccess.load_min_data_to_df('fut_min', inst, d_start, d_end, minid_start=min_start, minid_end=min_end)        
                self.min_data[inst][1] = mindata
                if len(mindata)>0:
                    min_date = mindata.index[-1].date()
                    if (len(self.day_data[inst].index)==0) or (min_date > self.day_data[inst].index[-1]):
                        self.cur_day[inst] = mysqlaccess.get_daily_by_tick(inst, min_date, start_tick=self.instruments[inst].start_tick_id, end_tick=self.instruments[inst].last_tick_id)
                        self.cur_min[inst]['datetime'] = pd.datetime(*mindata.index[-1].timetuple()[0:-3])
                        self.cur_min[inst]['open'] = float(mindata.ix[-1,'open'])
                        self.cur_min[inst]['close'] = float(mindata.ix[-1,'close'])
                        self.cur_min[inst]['high'] = float(mindata.ix[-1,'high'])
                        self.cur_min[inst]['low'] = float(mindata.ix[-1,'low'])
                        self.cur_min[inst]['volume'] = self.cur_day[inst]['volume']
                        self.cur_min[inst]['openInterest'] = self.cur_day[inst]['openInterest']
                        self.cur_min[inst]['min_id'] = int(mindata.ix[-1,'min_id'])
                        self.instruments[inst].price = float(mindata.ix[-1,'close'])
                        self.instruments[inst].last_update = datetime.datetime.now()
                        self.logger.info('inst=%s tick data loaded for date=%s' % (inst, min_date))
                    
                for m in self.min_data_func:
                    if m != 1:
                        self.min_data[inst][m] = data_handler.conv_ohlc_freq(self.min_data[inst][1], str(m)+'min')
                    df = self.min_data[inst][m]
                    for fobj in self.min_data_func[m]:
                        ts = fobj.sfunc(df)
                        df[ts.name]= pd.Series(ts, index=df.index)
        return		
	
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
   
