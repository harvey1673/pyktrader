import pandas as pd

class Strategy(object):
	def __init__(self, instIDs, agent, capital):
		self.instIDs = instIDs
		self.agent = agent
		self.capital = capital
		self.trade_unit = dict([(inst, 1) for inst in instIDs])
		self.trade_pos  = dict([(inst, 0) for inst in instIDs])
		self.daily_func = []
		self.min_func = {}
		
	def initialize(self):
		if len(self.daily_func)>0:
			curr_fobjs = [ fobj.name for fobj in self.agent.day_data_func ]
			for fobj in self.daily_func:
				if fobj.name not in curr_fobjs:
					self.agent.register_data_func('d', fobj)
		for mfreq in self.min_func:
			if len(self.min_func[mfreq])>0:
				curr_fobjs = [ fobj.name for fobj in self.agent.min_data_func[mfreq] ]
				for fobj in self.min_func[mfreq]:
					if fobj.name not in curr_fobjs:
						self.agent.register_data_func( str(mfreq) + 'm', fobj)
		self.update_trade_unit()
	
	def day_finalize(self):	
		self.update_trade_unit()
		pass
		
	def run(self, ctick):
		pass
	
	def liquidate(self):
		pass
	
	def update_trade_unit(self):
		pass
	
	

class TurtleTrader(Strategy):
	def __init__(self, instIDs, agent, capital):
		Strategy.__init__(instIDs, agent, capital)
		self.daily_func = [ 
					BaseObject(name = 'ATR_20', sfunc=fcustom(data_handler.ATR, n=20), rfunc=fcustom(data_handler.atr, n=20)), \
					BaseObject(name = 'DonChanHigh_20', sfunc=fcustom(data_handler.Don_Chan_High, n=20), rfunc=fcustom(data_handler.don_chan_high, n=20)),\
					BaseObject(name = 'DonChanLow_20', sfunc=fcustom(data_handler.Don_Chan_Low, n=20), rfunc=fcustom(data_handler.don_chan_low, n=20)),
					BaseObject(name = 'DonChanHigh_55', sfunc=fcustom(data_handler.Don_Chan_High, n=55), rfunc=fcustom(data_handler.don_chan_high, n=55)),\
					BaseObject(name = 'DonChanLow_55', sfunc=fcustom(data_handler.Don_Chan_Low, n=55), rfunc=fcustom(data_handler.don_chan_low, n=55)) 
					]	'
		self.captal_scaler = 0.01*self.capital/(se			
		self.min_func = {}
		self.pos_ratio = 0.01
	
	def day_finalize(self):
		pass
		
	def run(self, ctick):
		inst = ctick.instID
		
		
	def update_trade_unit(self):
		for inst in self.instIDs:
			if self.trade_pos[inst] == 0: 
				pinst  = self.agent.instruments[inst]
				df  = self.agent.day_data[inst]				
				self.trade_unit = int(self.capital * self.pos_ratio /(pinst.multiple*df.ix[-1,'ATR_20']))
