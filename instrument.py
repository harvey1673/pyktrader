#-*- coding:utf-8 -*-
import datetime
import pyktlib
import mysqlaccess
import copy
from misc import * 

class ProductType:
    Future, Stock, Option = range(3)

class VolGrid(object):
    def __init__(self, name, accrual = 'COM', tday = datetime.date.today(), is_spot = False, ccy = 'CNY'):
        self.name = name
        self.accrual = accrual
        self.ccy = ccy
        self.dtoday = date2xl(tday)
        self.df = {}
        self.fwd = {}
        self.volnode = {}
        self.volparam = {}
        self.underlier = {}
        self.dexp = {}
        self.main_cont = ''
        self.option_insts = {}
        self.spot_model = is_spot

def copy_volgrid(vg):
    volgrid = VolGrid(vg.name, accrual = vg.accrual, is_spot = vg.spot_model)
    volgrid.main_cont = vg.main_cont
    volgrid.dtoday = vg.dtoday
    for expiry in vg.option_insts:
        volgrid.df[expiry] = vg.df[expiry]
        volgrid.fwd[expiry] = vg.fwd[expiry]
        volgrid.volnode[expiry] = pyktlib.Delta5VolNode(vg.dtoday, vg.dexp[expiry],
                                                          vg.fwd[expiry],
                                                          vg.volparam[expiry][0],
                                                          vg.volparam[expiry][1],
                                                          vg.volparam[expiry][2],
                                                          vg.volparam[expiry][3],
                                                          vg.volparam[expiry][4],
                                                          vg.accrual)
        volgrid.volparam[expiry] = copy.copy(vg.volparam[expiry])
        volgrid.underlier[expiry] = copy.copy(vg.underlier[expiry])
        volgrid.dexp[expiry] = vg.dexp[expiry]
        volgrid.option_insts[expiry] = copy.copy(vg.option_insts[expiry])
    return volgrid

class Instrument(object):
    def __init__(self,name):
        self.name = name
        self.exchange = 'CFFEX'
        self.ptype = ProductType.Future
        self.product = 'IF'
        self.ccy = 'CNY'
        self.broker_fee = 0.0
        self.marginrate = (0,0) 
        self.multiple = 0
        self.tick_base = 0  
        self.start_tick_id = 0
        self.last_tick_id = 0
        # market snapshot
        self.price = 0.0
        self.prev_close = 0.0
        self.volume = 0
        self.open_interest = 0
        self.last_update = 0
        self.ask_price1 = 0.0
        self.ask_vol1 = 0
        self.bid_price1 = 0.0
        self.bid_vol1 = 0
        self.ask_price2 = 0.0
        self.ask_vol2 = 0
        self.bid_price2 = 0.0
        self.bid_vol2 = 0
        self.ask_price3 = 0.0
        self.ask_vol3 = 0
        self.bid_price3 = 0.0
        self.bid_vol3 = 0
        self.ask_price4 = 0.0
        self.ask_vol4 = 0
        self.bid_price4 = 0.0
        self.bid_vol4 = 0
        self.ask_price5 = 0.0
        self.ask_vol5 = 0
        self.bid_price5 = 0.0
        self.bid_vol5 = 0        
        self.up_limit = 0
        self.down_limit = 0
        self.last_traded = 0
        self.max_holding = (100, 100)
        self.mid_price = 0.0
        self.cont_mth = 205012 # only used by option and future
        self.expiry = datetime.date(2050,12,31)
        self.day_finalized = False
    
    def fair_price(self):
        self.mid_price = (self.ask_price1 + self.bid_price1)/2.0
        return self.mid_price

    def initialize(self):
        pass
    
    def update_param(self, tday):
        pass

    def calc_margin_amount(self, direction, price = 0.0):
        my_marginrate = self.marginrate[0] if direction == ORDER_BUY else self.marginrate[1]
        return self.price * self.multiple * my_marginrate

class Stock(Instrument):
    def __init__(self,name):
        Instrument.__init__(self, name)
        self.initialize()
        
    def initialize(self):
        self.product = self.name
        self.ptype = ProductType.Stock
        self.start_tick_id = 1530000
        self.last_tick_id  = 2130000
        self.multiple = 1
        self.tick_base = 0.01
        self.broker_fee = 0    
        self.marginrate = (1,0)
        if self.name in CHN_Stock_Exch['SZE']:
            self.exchange = 'SZE'
        else:
            self.exchange = 'SSE'
        return

class Future(Instrument):
    def __init__(self,name):
        Instrument.__init__(self, name)
        self.initialize()
        
    def initialize(self):
        self.ptype = ProductType.Future
        self.product = inst2product(self.name)
        prod_info = mysqlaccess.load_product_info(self.product)
        self.exchange = prod_info['exch']
        if self.exchange == 'CZCE':
            self.cont_mth = int(self.name[-3:]) + 201000
        else:
            self.cont_mth = int(self.name[-4:]) + 200000
        self.start_tick_id =  prod_info['start_min'] * 1000
        if self.product in night_session_markets:
            self.start_tick_id = 300000
        self.last_tick_id =  prod_info['end_min'] * 1000     
        self.multiple = prod_info['lot_size']
        self.tick_base = prod_info['tick_size']
        self.broker_fee = prod_info['broker_fee']
        return
    
    def update_param(self, tday):
        self.marginrate = mysqlaccess.load_inst_marginrate(self.name)
        
class OptionInst(Instrument):
    def __init__(self,name):
        self.strike = 0.0 # only used by option
        self.otype = ''   # only used by option
        self.underlying = ''   # only used by option
        Instrument.__init__(self, name)
        self.pricer = None
        self.pricer_func = pyktlib.BlackPricer
        self.pv = 0.0
        self.delta = 1
        self.theta = 0.0
        self.gamma = 0.0
        self.vega = 0.0
        self.margin_param = [0.15, 0.1]
        self.initialize()
        
    def initialize(self):
        pass

    def update_param(self, tday):
        pass
    
    def set_pricer(self, vg, irate):
        expiry = self.expiry
        dexp = vg.dexp[expiry]
        fwd = vg.fwd[expiry]
        self.pricer = self.pricer_func(vg.dtoday, 
                                       vg.dexp[expiry],
                                       vg.fwd[expiry], 
                                       vg.volnode[expiry], 
                                       self.strike, 
                                       irate, 
                                       self.otype)
    def update_greeks(self):
        self.pv = self.pricer.price() 
        self.delta = self.pricer.delta()
        self.gamma = self.pricer.gamma()
        self.vega  = self.pricer.vega()/100.0
        self.theta = self.pricer.theta()
        
    def calc_risk(self, risk_name, refresh = True):
        if self.pricer == None:
            return None    
        risk_func = risk_name
        if risk_name == 'pv':
            risk_func = 'price'
        if refresh:
            risk = getattr(self.pricer, risk_func)()
            if risk_name == 'vega':
                risk = risk/100
            setattr(self, risk_name, risk)
        else:
            risk = getattr(self, risk_name)
        return risk
       
    def calc_margin_amount(self, direction, price = 0.0):
        my_margin = self.price
        if direction == ORDER_SELL:
            a = self.margin_param[0]
            b = self.margin_param[1]
            if price == 0.0:
                price = self.strike
            if self.otype == 'C':
                my_margin += max(price * a - max(self.strike-price, 0), price * b)
            else:
                my_margin += max(price * a - max(price - self.strike, 0), self.strike * b)
        return my_margin * self.multiple
        
class StockOptionInst(OptionInst):
    def __init__(self,name):    
        OptionInst.__init__(self, name)
        self.margin_param = [0.12, 0.07]
        self.initialize()
        
    def initialize(self):
        self.ptype = ProductType.Option
        prod_info = mysqlaccess.load_stockopt_info(self.name)
        self.exchange = prod_info['exch']
        self.multiple = prod_info['lot_size']
        self.tick_base = prod_info['tick_size']
        self.strike = prod_info['strike']
        self.otype = prod_info['otype']  
        self.underlying = prod_info['underlying']
        self.product = self.underlying
        self.cont_mth = prod_info['cont_mth']
        self.expiry = get_opt_expiry(self.underlying, self.cont_mth)
        return
        
class FutOptionInst(OptionInst):
    def __init__(self,name):    
        OptionInst.__init__(self, name)
        if self.exchange != 'CFFEX':
            self.pricer_func = pyktlib.AmericanFutPricer
            self.margin_param = [0.15, 0.1]
        else:
            self.pricer_func = pyktlib.BlackPricer
            self.margin_param = [0.15, 0.1]            
        self.initialize()
        
    def initialize(self):
        self.ptype = ProductType.Option
        self.product = inst2product(self.name)
        if self.product == 'IO_Opt':
            self.underlying = self.name[:6].replace('IO','IF')
            self.strike = float(self.name[-4:])
            self.otype = self.name[7]
            self.cont_mth = int(self.underlying[-4:]) + 200000 
            self.expiry = get_opt_expiry(self.underlying, self.cont_mth)
            self.product = 'IO'
        elif '_Opt' in self.product:
            self.underlying = self.name[:5]
            self.strike = float(self.name[-4:])
            self.otype = self.name[7]
            self.cont_mth = int(self.underlying[-4:]) + 200000 
            self.expiry = get_opt_expiry(self.underlying, self.cont_mth)
            self.product = self.product[:-4]
        prod_info = mysqlaccess.load_product_info(self.product)
        self.exchange = prod_info['exch']
        self.start_tick_id =  prod_info['start_min'] * 1000
        if self.product in night_session_markets:
            self.start_tick_id = 300000
        self.last_tick_id =  prod_info['end_min'] * 1000     
        self.multiple = prod_info['lot_size']
        self.tick_base = prod_info['tick_size']
        self.broker_fee = prod_info['broker_fee']
        return
