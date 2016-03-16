#-*- coding:utf-8 -*-
import instrument
import pyktlib
import os
import csv
import numpy as np
import datetime
from tradeagent import *
from misc import *

def discount(irate, dtoday, dexp):
    return np.exp(-irate * max(dexp - dtoday,0)/365.0)
                
class OptAgentMixin(object):
    def __init__(self, name, tday=datetime.date.today(), config = {}):
        self.volgrids = {}
        self.irate = config.get('irate', {'CNY': 0.03,})
    
    def load_volgrids(self):
        self.logger.info('loading volgrids')
        dtoday = datetime2xl(datetime.datetime.now())
        for prod in self.volgrids.keys():
            logfile = self.folder + 'volgrids_' + prod + '.csv'
            self.volgrids[prod].dtoday = dtoday
            if os.path.isfile(logfile):       
                with open(logfile, 'rb') as f:
                    reader = csv.reader(f)
                    for row in enumerate(reader):
                        inst = row[0]
                        expiry = datetime.date.strptime(row[1], '%Y%m%d')
                        fwd = float(row[2]) 
                        atm = float(row[3])
                        v90 = float(row[4])
                        v75 = float(row[5])
                        v25 = float(row[6])
                        v10 = float(row[7])
                        if len(row) > 8:
                            ccy = str(row[8])
                        else:
                            ccy = 'CNY'
                        dexp   = date2xl(expiry) + 15.0/24.0
                        self.volgrids[prod].underlier[expiry] = inst
                        self.volgrids[prod].df[expiry] = discount(self.irate[ccy], dtoday, dexp)
                        self.volgrids[prod].fwd[expiry] = fwd
                        self.volgrids[prod].dexp[expiry] = dexp
                        self.volgrids[prod].volparam[expiry] = [atm, v90, v75, v25, v10]
                        self.volgrids[prod].volnode[expiry] = pyktlib.Delta5VolNode(dtoday, dexp, fwd, atm, v90, v75, v25, v10, self.volgrids[prod].accrual)
            else:
                for expiry in self.volgrids[prod].option_insts:
                    dexp = date2xl(expiry) + 15.0/24.0
                    under_instID = self.volgrids[prod].underlier[expiry]
                    fwd = self.instruments[under_instID].price
                    ccy = self.instruments[under_instID].ccy
                    if self.volgrids[prod].spot_model:
                        fwd = fwd / self.volgrids[prod].df[expiry]
                    self.volgrids[prod].fwd[expiry] = fwd
                    self.volgrids[prod].dexp[expiry] = dexp
                    self.volgrids[prod].df[expiry] = discount(self.irate[ccy], dtoday, dexp)
                    atm = self.volgrids[prod].volparam[expiry][0]
                    v90 = self.volgrids[prod].volparam[expiry][1]
                    v75 = self.volgrids[prod].volparam[expiry][2]
                    v25 = self.volgrids[prod].volparam[expiry][3]
                    v10 = self.volgrids[prod].volparam[expiry][4]
                    self.volgrids[prod].volnode[expiry] = pyktlib.Delta5VolNode(dtoday, dexp, fwd, atm, v90, v75, v25, v10, self.volgrids[prod].accrual)
        return   

    def save_volgrids(self):
        self.logger.info('saving volgrids')
        for prod in self.volgrids.keys():
            logfile = self.folder + 'volgrids_' + prod + '.csv'
            with open(logfile,'wb') as log_file:
                file_writer = csv.writer(log_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for expiry in self.volgrids[prod].volparam:
                    if len(self.volgrids[prod].volparam[expiry]) == 5:
                        volparam = self.volgrids[prod].volparam[expiry]
                        row = [ self.volgrids[prod].underlier[expiry], 
                                expiry.strftime('%Y%m%d'), 
                                self.volgrids[prod].fwd[expiry] ] + volparam
                        if self.volgrids[prod].ccy != 'CNY':
                            row.append(self.volgrids[prod].ccy)
                        file_writer.writerow(row)
        return
    
    def set_opt_pricers(self):
        for instID in self.instruments:
            inst = self.instruments[instID]
            if inst.ptype == instrument.ProductType.Option:
                expiry = inst.expiry
                prod = inst.product
                if expiry in self.volgrids[prod].volnode:
                    inst.set_pricer(self.volgrids[prod], self.irate)
                    inst.update_greeks()
                else:
                    print "missing %s volgrid for %s" % (prod, expiry)
                
        return

    def set_volgrids(self, product, expiry, fwd, vol_param):
        if (expiry in self.volgrids[product].volparam):
            dtoday = date2xl(self.scur_day) + max(self.tick_id - 600000, 0)/2400000.0
            self.volgrids[product].dtoday = dtoday
            self.volgrids[product].fwd[expiry] = fwd
            self.volgrids[product].volparam[expiry] = vol_param
            vg = self.volgrids[product].volnode[expiry]
            vg.setFwd(fwd)
            vg.setToday(dtoday)
            vg.setAtm(vol_param[0])
            vg.setD90Vol(vol_param[1])
            vg.setD75Vol(vol_param[2])
            vg.setD25Vol(vol_param[3])
            vg.setD10Vol(vol_param[4])
            vg.initialize()
        else:
            self.logger.info('expiry %s is not in the volgrid expiry for %s' % (expiry, product))     
        return
    
    def calc_volgrid(self, product, expiry, is_recalib=True):
        dtoday = date2xl(self.scur_day) + max(self.tick_id - 600000, 0)/2400000.0
        under = self.volgrids[product].underlier[expiry]
        fwd = self.instruments[under].price
        if self.volgrids[product].spot_model:
            fwd = fwd/self.volgrids[product].df[expiry]
        vg = self.volgrids[product].volnode[expiry]        
        if is_recalib:
            self.volgrids[product].dtoday = dtoday
            self.volgrids[product].fwd[expiry] = fwd            
            vg.setFwd(fwd)
            vg.setToday(dtoday)            
            vg.initialize()        
        for instID in self.volgrids[product].option_insts[expiry]:            
            inst = self.instruments[instID]
            optpricer = inst.pricer                                        
            optpricer.setFwd(fwd)
            optpricer.setToday(dtoday)            
            inst.update_greeks()            
        return
    
    def reval_volgrids(self, prod, is_recalib = True):
        for expiry in self.volgrids[prod].option_insts:
            self.calc_volgrid(prod, expiry, is_recalib)
        return
    
    def create_volgrids(self):
        volgrids = {}
        opt_insts = [inst for inst in self.instruments.values() if inst.ptype == instrument.ProductType.Option]
        for inst in opt_insts:
            is_spot = False
            accr = 'COM'
            prod = inst.product
            expiry = inst.expiry
            if 'Stock' in inst.__class__.__name__:
                is_spot = True
                accr = 'SSE'
            else:
                if inst.exchange == 'CFFEX':
                    accr = 'CFFEX'
            if prod not in volgrids:
                volgrids[prod] = instrument.VolGrid(prod, accrual= accr, is_spot = is_spot, ccy = 'CNY')
            if expiry not in volgrids[prod].option_insts:
                volgrids[prod].option_insts[expiry] = []
                volgrids[prod].underlier[expiry] = inst.underlying
                volgrids[prod].volparam[expiry] = [0.2, 0.0, 0.0, 0.0, 0.0]
            volgrids[prod].option_insts[expiry].append(inst.name)
        self.volgrids = volgrids
        return
      
class OptionAgent(Agent, OptAgentMixin):
    def __init__(self, name, tday=datetime.date.today(), config = {}):
        Agent.__init__(self, name, tday, config)
        OptAgentMixin.__init__(self, name, tday, config)
        self.create_volgrids()
        self.load_volgrids()
        self.set_opt_pricers()
    
    def restart(self):
        for prod in self.volgrids:
            self.reval_volgrids(prod, True)
        Agent.restart()
