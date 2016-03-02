#-*- coding:utf-8 -*-
import logging
from base import *
from misc import *
import itertools
import datetime
import csv
import os.path

class ETradeStatus:
    Pending, Processed, PFilled, Done, Cancelled, StratConfirm = range(6)

class OrderStatus:
    Waiting, Ready, Sent, Done, Cancelled = range(5)

def save_trade_list(curr_date, trade_list, file_prefix):
    filename = file_prefix + 'trade_' + curr_date.strftime('%y%m%d')+'.csv'
    with open(filename,'wb') as log_file:
        file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL);
        
        file_writer.writerow(['id', 'insts', 'volumes', 'filledvol', 'filledprice', 'otypes', 'slipticks',
                              'order_dict','limitprice', 'validtime',
                              'strategy','book','status', 'price_unit', 'conv_f'])
        for trade in trade_list.values():
            insts = ' '.join(trade.instIDs)
            volumes = ' '.join([str(i) for i in trade.volumes])
            filled_vol = ' '.join([str(i) for i in trade.filled_vol])
            filled_price = ' '.join([str(i) for i in trade.filled_price])
            otypes = ' '.join([str(i) for i in trade.order_types])
            slip_ticks = ' '.join([str(i) for i in trade.slip_ticks])
            cfactors = ' '.join([str(i) for i in trade.conv_f])
            if len(trade.order_dict)>0:
                order_dict = ' '.join([inst +':'+'_'.join([str(o.order_ref) for o in trade.order_dict[inst]]) 
                                    for inst in trade.order_dict])
            else:
                order_dict = ''
                                
            file_writer.writerow([trade.id, insts, volumes, filled_vol, filled_price, otypes, slip_ticks,
                                  order_dict, trade.limit_price, trade.valid_time,
                                  trade.strategy, trade.book, trade.status, trade.price_unit, cfactors])  
    pass

def load_trade_list(curr_date, file_prefix):
    logfile = file_prefix + 'trade_' + curr_date.strftime('%y%m%d')+'.csv'
    if not os.path.isfile(logfile):
        return {}

    trade_dict = {} 
    with open(logfile, 'rb') as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            if idx > 0:
                instIDs = row[1].split(' ')
                volumes = [ int(n) for n in row[2].split(' ')]
                filled_vol = [ int(n) for n in row[3].split(' ')]
                filled_price = [ float(n) for n in row[4].split(' ')]
                otypes = [ int(n) for n in row[5].split(' ')]
                ticks = [ int(n) for n in row[6].split(' ')]
                if ':' in row[7]:
                    order_dict =  dict([tuple(s.split(':')) for s in row[7].split(' ')])
                    for inst in order_dict:
                        if len(order_dict[inst])>0:
                            order_dict[inst] = [int(o_id) for o_id in order_dict[inst].split('_')]
                        else:
                            order_dict[inst] = []
                else:
                    order_dict = {}
                limit_price = float(row[8])
                valid_time = int(row[9])
                strategy = row[10]
                book = row[11]
                price_unit = float(row[13])
                conv_factor = [ int(n) for n in row[14].split(' ')]
                etrade = ETrade(instIDs, volumes, otypes, limit_price, ticks, valid_time, strategy, book, price_unit, conv_factor)
                etrade.id = int(row[0])
                etrade.status = int(row[12])
                etrade.order_dict = order_dict
                etrade.filled_vol = filled_vol 
                etrade.filled_price = filled_price 
                trade_dict[etrade.id] = etrade    
    return trade_dict

def save_order_list(curr_date, order_dict, file_prefix):
    orders = order_dict.keys()
    if len(order_dict)>1:
        orders.sort()
    order_list = [order_dict[key] for key in orders]
    filename = file_prefix + 'order_' + curr_date.strftime('%y%m%d')+'.csv'
    with open(filename,'wb') as log_file:
        file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL);
        
        file_writer.writerow(['order_ref', 'local_id', 'sysID', 'inst', 'volume', 'filledvolume', 'filledprice', 'action_type', 'direction',
                              'price_type','limitprice','order_time', 'status', 'conditionals', 'trade_ref'])

        for order in order_list:
            inst = order.position.instrument.name
            cond = [ str(o.order_ref)+':'+str(order.conditionals[o]) for o in order.conditionals]
            cond_str = ' '.join(cond)
            file_writer.writerow([order.order_ref, order.local_id, order.sys_id, inst, order.volume, order.filled_volume, order.filled_price,
                                  order.action_type, order.direction, order.price_type,
                                  order.limit_price, order.start_tick, order.status, cond_str, order.trade_ref])  
    pass

def load_order_list(curr_date, file_prefix, positions):
    logfile = file_prefix + 'order_' + curr_date.strftime('%y%m%d')+'.csv'
    if not os.path.isfile(logfile):
        return {}
    ref2order = {}
    with open(logfile, 'rb') as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            if idx > 0:
                inst = row[3]
                pos = positions[inst]
                if ':' in row[13]:
                    cond = dict([ tuple([int(k) for k in n.split(':')]) for n in row[13].split(' ')])
                else:
                    cond = {}
                iorder = Order(pos, float(row[10]), int(row[4]), int(row[11]),
                               row[7], row[8], row[9], cond)
                iorder.sys_id = row[1]
                iorder.local_id = row[2]
                iorder.filled_volume = int(row[5])
                iorder.filled_price = float(row[6])
                iorder.order_ref = int(row[0])
                iorder.trade_ref = int(row[14])
                iorder.status = int(row[12])
                ref2order[iorder.order_ref] = iorder
                pos.add_order(iorder)                
    return ref2order
    
class ETrade(object):
    #instances = weakref.WeakSet()
    id_generator = itertools.count(int(datetime.datetime.strftime(datetime.datetime.now(),'%d%H%M%S')))

    #@classmethod
    #def get_instances(cls):
    #    return list(ETrade.instances)
            
    def __init__(self, instIDs, volumes, otypes, limit_price, ticks, valid_time, strategy, book, price_unit = 1, conv_factor = []):
        self.id = next(self.id_generator)
        self.instIDs = instIDs
        self.volumes = volumes
        self.filled_vol = [0]*len(volumes)
        self.filled_price = [0]*len(volumes)
        self.order_types = otypes
        self.slip_ticks  = ticks
        self.limit_price = limit_price
        self.price_unit = price_unit
        self.valid_time = valid_time
        self.strategy = strategy
        self.book = book
        self.status = ETradeStatus.Pending
        self.conv_f = [1] * len(instIDs)
        if len(conv_factor) > 0:
            self.conv_f = conv_factor
        self.order_dict = {}
        #ETrade.instances.add(self)

    def final_price(self):
        return sum([ v*p*cf for (v,p,cf) in zip(self.filled_vol, self.filled_price, self.conv_f)])/self.price_unit
    
    def update(self):
        pending_orders = []
        if self.status in [ETradeStatus.Done, ETradeStatus.Cancelled, ETradeStatus.StratConfirm]:
            return pending_orders
        elif len(self.order_dict) == 0:
            self.status = ETradeStatus.Pending
            return pending_orders
        Done_status = True
        PFill_status = False
        Zero_Volume = True
        volumes = [0] * len(self.instIDs)
        for idx, inst in enumerate(self.instIDs):
            for iorder in self.order_dict[inst]:
                if (iorder.status in [OrderStatus.Done, OrderStatus.Cancelled]) and (len(iorder.conditionals) == 0):
                    continue
                if len(iorder.conditionals) == 1 and (OrderStatus.Cancelled in iorder.conditionals.values()):
                    sorder = iorder.conditionals.keys()[0]
                    if sorder.status == OrderStatus.Cancelled and iorder.status == OrderStatus.Waiting:
                        iorder.volume = sorder.cancelled_volume
                        iorder.status = OrderStatus.Ready
                        iorder.conditionals = {}
                        pending_orders.append(iorder.order_ref)
                        logging.debug('order %s is ready after %s is canceld, the remaining volume is %s' \
                                        % (iorder.order_ref, sorder.order_ref, iorder.volume))
                elif len(iorder.conditionals)> 0:
                    for o in iorder.conditionals:
                        if ((o.status == OrderStatus.Cancelled) and (iorder.conditionals[o] == OrderStatus.Done)) \
                            or ((o.status == OrderStatus.Done) and (iorder.conditionals[o] == OrderStatus.Cancelled)):
                            iorder.on_cancel()
                            iorder.conditions = {}
                            break
                        elif (o.status != iorder.conditionals[o]):
                            break    
                    else:
                        logging.debug('conditions for order %s are met, changing status to be ready' % iorder.order_ref)
                        iorder.status = OrderStatus.Ready
                        pending_orders.append(iorder.order_ref)
                        iorder.conditionals = {}
            self.filled_vol[idx] = sum([iorder.filled_volume for iorder in self.order_dict[inst]])
            if self.filled_vol[idx] > 0:
                self.filled_price[idx] = sum([iorder.filled_volume*iorder.filled_price for iorder in self.order_dict[inst]])/self.filled_vol[idx]
            volumes[idx] = sum([iorder.volume for iorder in self.order_dict[inst]])                    
            if volumes[idx] > 0:
                Zero_Volume = False
            if self.filled_vol[idx] < volumes[idx]:
                Done_status = False
            if self.filled_vol[idx] > 0:
                PFill_status = True                            
        if Zero_Volume:
            self.status = ETradeStatus.Cancelled
        elif Done_status:
            self.status = ETradeStatus.Done
        elif PFill_status:
            self.status = ETradeStatus.PFilled
        return pending_orders
    
####下单
class Order(object):
    id_generator = itertools.count(int(datetime.datetime.strftime(datetime.datetime.now(),'%d%H%M%S')))
    def __init__(self,position,limit_price,vol,order_time,action_type,direction, price_type, conditionals={}, trade_ref = 0, gateway = 'CTP'):
        self.position = position
        self.limit_price = limit_price        #开仓基准价
        self.start_tick  = order_time
        self.order_ref = next(self.id_generator)
        self.local_id  = self.order_ref
        ##衍生
        self.instrument = position.instrument
        self.sys_id = ''
        self.trade_ref = trade_ref
        self.direction = direction # ORDER_BUY, ORDER_SELL
        ##操作类型
        self.action_type = action_type # OF_CLOSE_TDAY, OF_CLOSE, OF_OPEN
        self.price_type = price_type
        ##
        self.volume = vol #目标成交手数,锁定总数
        self.filled_volume = 0  #实际成交手数
        self.filled_price  = 0
        self.cancelled_volume = 0
        self.filled_orders = []
        self.conditionals = conditionals
        self.gateway = gateway
        if len(self.conditionals) == 0:
            self.status = OrderStatus.Ready
        else:
            self.status = OrderStatus.Waiting
        #self.close_lock = False #平仓锁定，即已经发出平仓信号

    def on_trade(self, price, volume, trade_id):
        ''' 返回是否完全成交
        '''
        if self.status == OrderStatus.Done:
            return True
        if trade_id in [o.trade_id for o in self.filled_orders]:
            return False
        self.filled_orders.append(BaseObject(price = price, volume = volume, trade_id = trade_id))
        self.filled_volume = sum([o.volume for o in self.filled_orders])
        self.filled_price = sum([o.volume*o.price for o in self.filled_orders])/self.filled_volume
        if self.filled_volume > self.volume:
            self.filled_volume = self.volume
            self.status = OrderStatus.Done
            logging.warning(u'a new trade confirm exceeds the order volume price=%s, filled_vol=%s, order_vol =%s' % \
                                (price, volume, self.volume))
        elif (self.filled_volume == self.volume) and (self.volume>0):
            self.status = OrderStatus.Done
        logging.debug(u'成交纪录:price=%s,volume=%s,filled_vol=%s, is_closed=%s' % (price,volume,self.filled_volume,self.is_closed()))
        self.position.re_calc()
        return self.filled_volume == self.volume
    
    def on_order(self, sys_id, price = 0, volume = 0):
        self.sys_id = sys_id
        if volume > 0:
            self.filled_price = price
            self.filled_volume = volume
            if self.filled_volume == self.volume:
                self.status = OrderStatus.Done
                self.position.re_calc()
                return True
        return False

    def on_cancel(self):    #已经撤单
        if self.status != OrderStatus.Cancelled:
            self.status = OrderStatus.Cancelled
            self.cancelled_volume = max(self.volume - self.filled_volume, 0)
            self.volume = self.filled_volume    #不会再有成交回报
            logging.debug(u'撤单记录: OrderRef=%s, instID=%s, volume=%s, filled=%s, cancelled=%s' \
                % (self.order_ref, self.instrument.name, self.volume, self.filled_volume, self.cancelled_volume))
        self.position.re_calc()

    def is_closed(self): #是否已经完全平仓
        return (self.status in [OrderStatus.Cancelled,OrderStatus.Done]) and (self.filled_volume == self.volume)

    #def release_close_lock(self):
    #    logging.info(u'释放平仓锁,order=%s' % self.__str__())
    #    self.close_lock = False

    def __unicode__(self):
        return u'Order_A: 合约=%s,方向=%s,目标数=%s,开仓数=%s,状态=%s' % (self.instrument.name,
                u'多' if self.direction==ORDER_BUY else u'空',
                self.volume,
                self.filled_volume,
                self.status,
            )
        
    def __str__(self):
        return unicode(self).encode('utf-8')

        ####头寸
class Position(object):
    def __init__(self, instrument, gateway = 'CTP'):
        self.instrument = instrument
        self.gateway = gateway
        self.orders = []    #元素为Order
        self.tday_pos = BaseObject(long=0, short=0) 
        self.tday_avp = BaseObject(long=0.0, short=0.0)
        
        self.pos_tday = BaseObject(long=0, short=0)
        self.pos_yday = BaseObject(long=0, short=0) # yday's overnight position
        
        self.curr_pos = BaseObject(long=0, short=0)
        self.locked_pos = BaseObject(long=0, short=0)
        
        self.can_yclose = BaseObject(long=0, short=0)
        self.can_close  = BaseObject(long=0, short=0)
        self.can_open = BaseObject(long=0, short=0)

    def re_calc(self): #
        #print self.orders
        #self.orders = [order for order in self.orders if not order.is_closed()]
        #print self.orders
        tday_opened = BaseObject(long=0, short=0)
        tday_o_locked = BaseObject(long=0, short=0)
        tday_closed = BaseObject(long=0,short=0)
        tday_c_locked = BaseObject(long=0,short=0)
        yday_closed = BaseObject(long=0,short=0)
        yday_c_locked = BaseObject(long=0,short=0)
        
        for mo in self.orders:
            logging.debug(str(mo))
            if mo.action_type == OF_OPEN:
                if mo.direction == ORDER_BUY:
                    tday_opened.long += mo.filled_volume
                    tday_o_locked.long += mo.volume
                else:
                    tday_opened.short += mo.filled_volume
                    tday_o_locked.short += mo.volume            
            elif (mo.action_type == OF_CLOSE) or (mo.action_type == OF_CLOSE_TDAY):
                if mo.direction == ORDER_BUY:
                    tday_closed.long  += mo.filled_volume
                    tday_c_locked.long += mo.volume
                else: 
                    tday_closed.short += mo.filled_volume
                    tday_c_locked.short += mo.volume
            elif mo.action_type == OF_CLOSE_YDAY:
                if mo.direction == ORDER_BUY:
                    yday_closed.long  += mo.filled_volume
                    yday_c_locked.long += mo.volume
                else:
                    yday_closed.short += mo.filled_volume
                    yday_c_locked.short += mo.volume    

        if self.instrument.exchange == 'SHFE':
            self.can_yclose.long  = max(self.pos_yday.short - yday_c_locked.long, 0)
            self.can_yclose.short = max(self.pos_yday.long  - yday_c_locked.short,0)
            self.can_close.long  = max(tday_opened.short - tday_c_locked.long, 0) 
            self.can_close.short = max(tday_opened.long  - tday_c_locked.short,0)
        else:
            self.can_yclose.long  = 0
            self.can_yclose.short = 0
            self.can_close.long  = max(self.pos_yday.short + tday_opened.short - tday_c_locked.long, 0) 
            self.can_close.short = max(self.pos_yday.long  + tday_opened.long  - tday_c_locked.short,0)                     
        
        self.tday_pos.long  = tday_opened.long + tday_closed.long + yday_closed.long
        self.tday_pos.short = tday_opened.short + tday_closed.short + yday_closed.short
        
        if self.tday_pos.long > 0:
            self.tday_avp.long = sum([o.filled_price*o.filled_volume for o in self.orders if o.direction == ORDER_BUY])/self.tday_pos.long
        else:
            self.tday_avp.long = 0.0
        if self.tday_pos.short > 0:
            self.tday_avp.short= sum([o.filled_price*o.filled_volume for o in self.orders if o.direction == ORDER_SELL])/self.tday_pos.short
        else:
            self.tday_avp.short = 0.0        
        
        self.curr_pos.long = tday_opened.long - tday_closed.short + self.pos_yday.long - yday_closed.short
        self.curr_pos.short =tday_opened.short- tday_closed.long  + self.pos_yday.short- yday_closed.long
        self.locked_pos.long = self.pos_yday.long -yday_closed.short+ tday_o_locked.long - tday_closed.short
        self.locked_pos.short =self.pos_yday.short-yday_closed.long + tday_o_locked.short- tday_closed.long
        
        self.can_open.long  = max(self.instrument.max_holding[0] - self.locked_pos.long,0)
        self.can_open.short = max(self.instrument.max_holding[1] - self.locked_pos.short,0)
        logging.debug(u'P_RC_1:%s 重算头寸，当前已开数 long=%s,short=%s 当前锁定数 long=%s,short=%s, 昨日仓位long=%s,short=%s' \
                    % (str(self), self.curr_pos.long,self.curr_pos.short,self.locked_pos.long,self.locked_pos.short, self.pos_yday.long, self.pos_yday.short))
        
    def get_open_volume(self):
        return (self.can_open.long, self.can_open.short)
    
    def get_close_volume(self):
        return (self.can_close.long, self.can_close.short)
    
    def get_yclose_volume(self):
        return (self.can_yclose.long, self.can_yclose.short)

    def add_orders(self, orders):
        for iorder in orders:
            self.add_order(iorder)
    
    def add_order(self, order):
        self.orders.append(order)
        self.gateway.id2order[order.local_id] = order

    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return '%s' % (self.instrument.name) 
