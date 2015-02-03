#-*- coding:utf-8 -*-
'''
optstrat.py
Created on Feb 03, 2015
@author: Harvey
'''
BDAYS_PER_YEAR = 261.0

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

def time2exp(opt_expiry, curr_time):
	curr_date = curr_time.date()
	exp_date = opt_expiry.date()
	if curr_time > opt_expiry:
		return 0.0
	elif exp_date < curr_date:
		return workdays.networkdays(curr_date, exp_date, misc.CHN_Holidays)/BDAYS_PER_YEAR
	else:
		delta = opt_expiry - curr_time 
		return (delta.hour*3600+delta.min*60+delta.second)/3600.0/5.5/BDAYS_PER_YEAR

def load_stockopt_info(inst):
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    stmt = "select underlying, opt_mth, otype, exchange, strike, strike_scale, lot_size, tick_base from stock_opt_map where instID='{product}' ".format(product = inst)    
    cursor.execute(stmt)
    out = {}
    for (underlying, opt_mth, otype, exchange, strike, strike_scale, lot_size, tick_size) in cursor:
        out = {'exch': str(exchange), 
               'lot_size': int(lot_size), 
               'tick_size': float(tick_size), 
               'strike': float(strike)/float(strike_scale),
               'cont_mth': opt_mth, 
               'otype': str(otype),
               'underlying': str(underlying)
               }
    cnx.close()
    return out

def get_stockopt_map(underlying, cont_mths, strikes):
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    stmt = "select underlying, opt_mth, otype, strike, strike_scale, instID from stock_opt_map where underlying='{under}' and opt_mth in ({opt_mth_str}) and strike in ({strikes}) ".format(under=underlying, 
			opt_mth_str=','.join([str(mth) for mth in cont_mths]), strikes = ','.join([str(s) for s in strikes]))     
    cursor.execute(stmt)
    out = {}
    for (underlying, opt_mth, otype, strike, strike_scale, instID) in cursor:
		key = (underlying, opt_mth, otype, float(strike)/float(strike_scale))
		out[key] = instID
    cnx.close()
    return out
	
class OptionStrategy(object):
    def __init__(self, name, underliers, cont_mths, strikes, agent = None):
        self.name = name
        self.underliers = underliers
		self.option_map = {}
		self.get_option_map(underliers, cont_mths, strikes)
        self.instIDs = list(set().union(*underliers))
        self.agent = agent
        self.logger = None
        if self.agent != None:
            self.logger = self.agent.logger 
        self.positions  = [[] for under in underliers]
        self.submitted_pos = [ [] for under in underliers ]
        if agent == None:
            self.folder = ''
        else:
            self.folder = self.folder + self.name + '_'
	
	def get_opt_map(self, underliers, cont_mths, strikes)
		pass
		
class EquityOptStrat(OptionStrategy):
	def __init__(self, name, underliers, cont_mths, strikes, agent = None):
		OptionStrategy.__init__(name, underliers, cont_mths, strikes, agent)
	
	
		
	def get_opt_map(self, underliers, cont_mths, strikes):
		for under in underliers:
			map = get_stockopt_map(under, cont_mths, strikes)
			self.option_map.update(map)
		return
	
