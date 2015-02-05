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
		self.option_insts = self.option_map.values()
        self.instIDs = self.underliers + self.option_insts
        self.agent = agent
        self.logger = None
        if self.agent != None:
            self.logger = self.agent.logger 
        self.positions  = [[] for inst in self.instIDs]
        self.submitted_pos = []
        if agent == None:
            self.folder = ''
        else:
            self.folder = self.folder + self.name + '_'

    def reset(self):
        if self.agent == None:
            self.folder = ''
        else:
            self.folder = self.agent.folder + self.name + '_'
            self.logger = self.agent.logger
        self.load_state()

    def initialize(self):
        self.load_state()

	def add_submitted_pos(self, etrade):
        is_added = False
        for trade in self.submitted_pos:
            if trade.id == etrade.id:
                is_added = False
                return
		self.submitted_pos.append(etrade)
        return True

    def day_finalize(self):    
        self.save_state()
        self.logger.info('strat %s is finalizing the day - update trade unit, save state' % self.name)
        pass
		
	def get_opt_map(self, underliers, cont_mths, strikes)
		pass
	
	def run_tick(self, ctick):
		pass
	
	def run_min(self, inst):
		pass

    def save_state(self):
        filename = self.folder + 'strat_status.csv'
        self.logger.info('save state for strat = %s' % (self.name))
        with open(filename,'wb') as log_file:
            file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(tradepos_header)
            for tplist in self.positions:
                for tradepos in tplist:
                    tradedict = tradepos2dict(tradepos)
                    file_writer.writerow([tradedict[itm] for itm in tradepos_header])
        return
    
    def load_state(self):
        logfile = self.folder + 'strat_status.csv'
        positions  = [[] for under in self.underliers]
        if not os.path.isfile(logfile):
            self.positions  = positions
            return 
        self.logger.info('load state for strat = %s' % (self.name))
        with open(logfile, 'rb') as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if idx > 0:
                    insts = row[0].split(' ')
                    vols = [ int(n) for n in row[1].split(' ')]
                    pos = int(row[2])
                    #direction = int(row[3])
                    entry_target = float(row[6])
                    exit_target = float(row[10])
                    price_unit = float(row[14])
                    tradepos = TradePos(insts, vols, pos, entry_target, exit_target, price_unit)
                    if row[5] == '':
                        entry_time = ''
                        entry_price = 0
                    else:
                        entry_time = datetime.datetime.strptime(row[5], '%Y%m%d %H:%M:%S %f')
                        entry_price = float(row[4])
                        tradepos.open(entry_price,entry_time)

                    tradepos.entry_tradeid = int(row[7])           
                    tradepos.exit_tradeid = int(row[11])    
                    
                    if row[9] == '':
                        exit_time = ''
                        exit_price = 0
                    else:                    
                        exit_time = datetime.datetime.strptime(row[9], '%Y%m%d %H:%M:%S %f')
                        exit_price = float(row[8])
                        tradepos.close(exit_price, exit_time)
                    
                    is_added = False
                    for under, tplist in zip(self.underliers, positions):
                        if set(under) == set(insts):
                            tplist.append(tradepos)
                            is_added = True
                            break
                    if is_added == False:
                        self.underliers.append(insts)
                        positions.append([tradepos])
                        self.logger.warning('underlying = %s is missing in strategy=%s. It is added now' % (insts, self.name))
        self.positions = positions
        return    
		
class EquityOptStrat(OptionStrategy):
	def __init__(self, name, underliers, cont_mths, strikes, agent = None):
		OptionStrategy.__init__(name, underliers, cont_mths, strikes, agent)
		
		
	def get_opt_map(self, underliers, cont_mths, strikes):
		for under in underliers:
			map = get_stockopt_map(under, cont_mths, strikes)
			self.option_map.update(map)
		return
	
