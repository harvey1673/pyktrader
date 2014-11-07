#-*- coding:utf-8 -*-
import pandas as pd
from base import *
import data_handler
import order as order
from ctp.futures import ApiStruct
import math
import logging

sign = lambda x: math.copysign(1, x)

class PosRecord(object):
	def __init__(self, insts, vols, target):
		self.instIDs = insts
		self.volumes = vols
		self.entry_target = entry_target
		self.entry_price = None
		self.entry_time = None
		self.entry_tradeid = None
		self.exit_price = None
		self.exit_price = None
		self.exit_tradeid = None
		self.is_closed = False
	
	def open(self, price, pos, pexit, start_time):
		self.pos = pos
		self.direction = 1 if pos > 0 else -1
		self.price_in = price
		self.exit = pexit
		self.start_time = start_time
		self.is_closed = False
		
	def close(self, price, end_time):
		self.end_time = end_time
		self.price_out = price
		self.profit = (self.price_out - self.price_in) * self.pos
		self.is_closed = True
		
class Strategy(object):
	def __init__(self, name, underliers, agent = None, data_func = {}, trade_unit = [] ):
		self.name = name
		self.underliers = underliers
		self.agent = agent
		self.logger = None
		if self.agent != None:
			self.logger = self.agent.logger 
		if len(trade_unit) > 0: 
			self.trade_unit = trade_unit
		else:
			self.trade_unit = [ [1]*len(under) for under in underliers ]
		self.positions  = [[] for under in underliers]
		self.submitted_pos = [ [] for under in underliers ]
		self.data_func = data_func
		if agent == None:
			self.folder = ''
		else:
			self.folder = self.folder + self.name + '\\'
		
	def initialize(self):
		if self.agent == None:
			self.folder = ''
		else:
			self.folder = self.agent.folder + self.name + '\\'
			self.logger = self.agent.logger
		if len(self.data_func)>0:
			for (freq, fobj) in self.data_func:
				self.agent.register_data_func(freq,fobj)
		self.update_trade_unit()
	
	def resume(self):
		pass
	
	def add_submitted_pos(self, etrade):
		is_added = False
		for under, sub_pos in zip(self.underliers, self.submitted_pos):
			if set(under) == set(etrade.instIDs):
				sub_pos.append(etrade)
				is_added = True
				break
		return is_added
	
	def day_finalize(self):	
		self.update_trade_unit()
		self.save_state()
		pass
		
	def run_tick(self, ctick):
		pass
	
	def run_min(self, inst):
		pass
	
	def liquidate(self):
		pass
	
	def update_trade_unit(self):
		pass
	
	def save_state(self):
		pass
	
	def load_state(self):
		pass	
	
	
class TurtleTrader(Strategy):
	def __init__(self, name, underliers,  capital, agent = None):
		Strategy.__init__(name, underliers, agent)
		self.data_func = [ 
				('d', BaseObject(name = 'ATR_20', sfunc=fcustom(data_handler.ATR, n=20), rfunc=fcustom(data_handler.atr, n=20))), \
				('d', BaseObject(name = 'DONCH_L10', sfunc=fcustom(data_handler.DONCH_L, n=10), rfunc=fcustom(data_handler.donch_l, n=10))),\
				('d', BaseObject(name = 'DONCH_H10', sfunc=fcustom(data_handler.DONCH_H, n=10), rfunc=fcustom(data_handler.donch_h, n=10))),\
				('d', BaseObject(name = 'DONCH_L20', sfunc=fcustom(data_handler.DONCH_L, n=20), rfunc=fcustom(data_handler.donch_l, n=20))),\
				('d', BaseObject(name = 'DONCH_H20', sfunc=fcustom(data_handler.DONCH_H, n=20), rfunc=fcustom(data_handler.donch_h, n=10))),\
				('d', BaseObject(name = 'DONCH_L55', sfunc=fcustom(data_handler.DONCH_L, n=55), rfunc=fcustom(data_handler.donch_l, n=10))),\
				('d', BaseObject(name = 'DONCH_H55', sfunc=fcustom(data_handler.DONCH_H, n=55), rfunc=fcustom(data_handler.donch_h, n=55)))]	
		self.capital = capital 
		self.pos_ratio = 0.01
		self.stop_loss = 2.0
		self.breakout_signals = [0] * len(underliers)
		self.last_flag = [True] * len(underliers)
	
	def save_state(self):
		
		pass
	
	def load_state(self):
		pass	
	
	def run_tick(self, ctick):
		inst = ctick.instID
		under = [inst]
		df = self.agent.day_data[inst]
		cur_atr = df.ix[-1,'ATR_20']
		hh = [df.ix[-1,'DONCH_H55'],df.ix[-1,'DONCH_H20'],df.ix[-1,'DONCH_H10']]
		ll  = [df.ix[-1,'DONCH_L55'],df.ix[-1,'DONCH_L20'],df.ix[-1,'DONCH_H10']]
		idx = 0
		for i, under in enumerate(self.underliers):
			if inst == under[0]:
				idx = i
				break
		sub_pos = self.submitted_pos[idx]
		if len(sub_pos) > 0:
			
			if pos['trade'].status == order.ETradeStatus.Done:
				traded_price = pos['trade'].filled_price[0]
				traded_vol = pos['trade'].volumes[0]
				pos.pop('trade', None)
				if pos['serialno'] >= len(self.positions[inst]):
					pexit = pos['exit']
					for p in self.positions[inst]:
						p['exit'] = pexit
					self.positions[inst].append(pos)
				else:
					pos_inst = self.positions[inst]
					cancelled_vol = sum([pos_inst[i].volume for i in range(pos.sn, len(pos_inst))])
					if cancelled_vol + pos.volume!=0:
						logging.warning('the cancelled trade volume is not matching, current=%s, cancelled=%s' % (cancelled_vol, traded_vol))
					avg_price = sum([pos_inst[i].volume*pos_inst[i].entry for i in range(pos.sn, len(pos_inst))])/cancelled_vol
					logging.info('the position for inst=%s is cut, entry avg price =%s, traded price=%, volume=%s' \
											% (inst, avg_price, traded_price, traded_vol))
					self.positions[inst] = self.positions[inst][:pos.sn]
					if len(self.positions[inst]) == 0:
						if ((avg_price - traded_price) * cancelled_vol <0) and self.breakout_signals[inst]>2:
							self.last_flag = True
						else:
							self.last_flag = False
				self.submitted_pos[inst] = None
			elif pos.trade.status == order.ETradeStatus.Cancelled:
				self.submitted_pos[inst] = None
		cur_price = (ctick.askPrice1 + ctick.bidPrice1)/2.0
		if self.submitted_pos[inst] == None:
			#开仓 
			if len(self.positions[inst]) == 0: 
				for idx in range(2):
					buysell = 0
					if (cur_price > hh[idx]) and (idx==0 or self.last_flag):
						buysell = 1
						self.breakout_signals[inst] = idx*2+1
						order_size = 1
					elif (cur_price < ll[idx]) and (idx==0 or self.last_flag):
						buysell = -1
						self.breakout_signals[inst] = idx*2+2
						order_size = 1						
					if buysell !=0:
						valid_time = self.agent.tick_id + 600
						etrade = order.ETrade( [inst], [self.trade_unit[inst]*order_size*buysell], [ApiStruct.OPT_LimitPrice], cur_price, [3], valid_time, self.name, self.agent.name)
						self.submitted_pos[inst] = BaseObject(entry = cur_price, 
										exit = cur_price - cur_atr*self.stop_loss*buysell,
										volume = etrade.volumes[0],
										trade = etrade,
										units = order_size,
										sn = 0 )
						self.agent.submit_trade(etrade)
						return 1
			#加仓或清仓
			else:
				buysell = sign(self.positions[inst][0])
				#清仓1
				units = sum([pos.units for pos in self.positions[inst]])
				for idx in range(2):
					if (cur_price < ll[idx+1] and buysell == 1 ) \
							or (cur_price > hh[idx+1] and buysell == -1):
						vol = sum([pos.volume for pos in self.positions[inst]])
						valid_time = self.agent.tick_id + 600
						etrade = order.ETrade( [inst], [-vol], [ApiStruct.OPT_LimitPrice], cur_price, [3], valid_time, self.name, self.agent.name)
						self.submitted_pos[inst] = BaseObject(entry = 0, 
										exit = 0,
										volume = -vol,
										trade = etrade,
										units = -units,
										sn = 0 )
						return 1
				for pos in self.positions[inst]:
					if (cur_price - pos.exit)*buysell < 0:
						vol = sum([pos.volume for pos in self.positions[inst]])
						units = sum([pos.units for pos in self.positions[inst]])
						valid_time = self.agent.tick_id + 600
						etrade = order.ETrade( [inst], [-vol], [ApiStruct.OPT_LimitPrice], cur_price, [3], valid_time, self.name, self.agent.name)
						self.submitted_pos[inst] = BaseObject(entry = 0, 
										exit = 0,
										volume = -vol,
										trade = etrade,
										units = -units,
										sn = pos.sn )
						return 1
				if units < 4 and (cur_price - self.positions[inst][-1].entry)*sign(self.positions[inst][-1].volume) >= cur_atr/2.0:
					nunit = len(self.positions[inst])
					valid_time = self.agent.tick_id + 600
					etrade = order.ETrade( [inst], [self.trade_unit[inst]*buysell], [ApiStruct.OPT_LimitPrice], cur_price, [3], valid_time, self.name, self.agent.name)
					self.submitted_pos[inst] = BaseObject(entry = cur_price, 
										exit = cur_price - cur_atr*self.stop_loss*buysell,
										volume = etrade.volumes[0],
										trade = etrade,
										units = 1,
										sn = nunit )					
					return 1
		
	def update_trade_unit(self):
		for under, pos in zip(self.underliers,self.positions):
			if self.pos == 0: 
				inst = under[0]
				pinst  = self.agent.instruments[inst]
				df  = self.agent.day_data[inst]				
				self.trade_unit = int(self.capital*self.pos_ratio/(pinst.multiple*df.ix[-1,'ATR_20']))
