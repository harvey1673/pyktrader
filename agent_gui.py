#-*- coding:utf-8 -*-
import ctp_api
import Tkinter as tk
import ttk
import datetime
import re
import pyktlib
import instrument
import math

vtype_func_map = {'int':int, 'float':float, 'str': str, 'bool':bool }

def keepdigit(x, p=5):
    out = x
    if isinstance(x, float):
        if x >= 10**p:
            out = int(x)
        elif x>=1:
            n = p + 1 - len(str(int(x)))
            out = int(x*(10**n)+0.5)/float(10**n)
        elif math.isnan(x):
            out = 0
        else:
            out = int(x*10**p+0.5)/1.0/10**p
    return out    

def get_type_var(vtype):
    if vtype == 'int':
        v=tk.IntVar()
    elif vtype == 'float':
        v=tk.DoubleVar()
    else: 
        v=tk.StringVar()
    return v

def type2str(val, vtype):
    ret = val
    if vtype == 'bool':
        ret = '1' if val else '0'
    elif 'list' in vtype:
        ret = ','.join([str(r) for r in val])
    elif vtype == 'date':
        ret = val.strftime('%Y%m%d')
    elif vtype == 'datetime':
        ret = val.strftime('%Y%m%d')
    else:
        ret = str(val)
    return ret

def str2type(val, vtype):
    ret = val
    if vtype == 'str':
        return ret
    elif vtype == 'bool':
        ret = True if int(float(val))>0 else False
    elif 'list' in vtype:
        key = 'float'    
        if len(vtype) > 4:
            key = vtype[:-4]
        func = vtype_func_map[key]
        ret = [func(s) for s in val.split(',')]
    elif vtype == 'date':
        ret = datetime.datetime.strptime(val,'%y%m%d').date()
    elif vtype == 'datetime':
        ret = datetime.datetime.strptime(val,'%y%m%d %H:%M:%S')
    else:
        func = vtype_func_map[vtype]
        ret = func(float(val))
    return ret

def field2variable(name):
    return '_'.join(re.findall('[A-Z][^A-Z]*', name)).lower()

def variable2field(var):
    return ''.join([s.capitalize() for s in var.split('_')])
    
class StratGui(object):
    def __init__(self, strat, app, master):
        self.root = master
        self.name = strat.name
        self.app = app
        self.underliers = strat.underliers
        self.entries = {}
        self.stringvars = {}
        self.entry_fields = []
        self.status_fields = []
        self.shared_fields = []
        self.field_types = {}
        self.lblframe = None
        self.canvas = None
        self.vsby = None
        self.vsbx = None
                
    def get_params(self):
        fields = self.entry_fields + self.status_fields
        params = self.app.get_strat_params(self.name, fields)
        for field in fields:
            if field in self.shared_fields:
                value = params[field]
                if field in self.entry_fields:
                    ent = self.entries[field]
                    ent.delete(0, tk.END)
                    ent.insert(0, value)
                elif field in self.status_fields:
                    self.stringvars[field].set(keepdigit(value, 4))
            else:
                for idx, underlier in enumerate(self.underliers):
                    under_key = ','.join(underlier)
                    value = params[field][idx]
                    vtype = self.field_types[field]
                    value = type2str(value, vtype)
                    if field in self.entry_fields:
                        ent = self.entries[under_key][field]
                        ent.delete(0, tk.END)
                        ent.insert(0, value)
                    elif field in self.status_fields:
                        self.stringvars[under_key][field].set(keepdigit(value, 4))
        return
        
    def set_params(self):
        params = {}
        for field in self.entry_fields:
            if field in self.shared_fields:
                ent = self.entries[field]
                value = ent.get()
                vtype = self.field_types[field]
                value = str2type(value, vtype)
                params[field] = value
            else:
                params[field] = []
                for underlier in self.underliers:
                    under_key = ','.join(underlier)
                    ent = self.entries[under_key][field]
                    value = ent.get()
                    vtype = self.field_types[field]
                    value = str2type(value, vtype)
                    params[field].append(value)
        self.app.set_strat_params(self.name, params)
        return

    def OnFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))        
        pass
            
    def set_frame(self, root):
        self.canvas = tk.Canvas(root)
        self.lblframe = tk.Frame(self.canvas)
        self.vsby = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.vsbx = tk.Scrollbar(root, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsby.set, xscrollcommand=self.vsbx.set)
        self.vsbx.pack(side="bottom", fill="x")
        self.vsby.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.lblframe, anchor="nw", tags="self.lblframe")
        self.lblframe.bind("<Configure>", self.OnFrameConfigure)        
        #self.lblframe = ttk.Frame(root)        
        #self.lblframe.grid_columnconfigure(1, weight=1)     
        entries = {}
        stringvars = {}
        row_id = 0
        set_btn = ttk.Button(self.lblframe, text='Set', command=self.set_params)
        set_btn.grid(row=row_id, column=1, sticky="ew")
        refresh_btn = ttk.Button(self.lblframe, text='Refresh', command=self.get_params)
        refresh_btn.grid(row=row_id, column=2, sticky="ew")
        recalc_btn = ttk.Button(self.lblframe, text='Recalc', command=self.recalc)
        recalc_btn.grid(row=row_id, column=3, sticky="ew")        
        row_id += 1
        for idx, field in enumerate(self.shared_fields):
            lbl = ttk.Label(self.lblframe, text = field, anchor='w')
            lbl.grid(row=row_id, column=idx, sticky="ew")
            if field in self.entry_fields:
                ent = ttk.Entry(self.lblframe)
                ent.grid(row=row_id+1, column=idx, sticky="ew")
                ent.insert(0, "0")
                entries[field] = ent
            elif field in self.status_fields:
                v= get_type_var(self.field_types[field])
                lab = ttk.Label(self.lblframe, textvariable = v, anchor='w')
                lab.grid(row=row_id+1, column=idx, sticky="ew")
                v.set('0')
                stringvars[field] = v                   
        row_id += 2
        local_entry_fields = [ f for f in self.entry_fields if f not in self.shared_fields]
        local_status_fields = [ f for f in self.status_fields if f not in self.shared_fields]
        fields = ['assets'] + local_entry_fields + local_status_fields
        for idx, field in enumerate(fields):
            lbl = ttk.Label(self.lblframe, text = field, anchor='w')
            lbl.grid(row=row_id, column=idx, sticky="ew")
        row_id += 1
        for underlier in self.underliers:
            under_key = ','.join(underlier)
            inst_lbl = ttk.Label(self.lblframe, text=under_key, anchor="w")
            inst_lbl.grid(row=row_id, column=0, sticky="ew")
            col_id = 1
            entries[under_key] = {}
            for idx, field in enumerate(local_entry_fields):
                ent = ttk.Entry(self.lblframe)
                ent.grid(row=row_id, column=col_id+idx, sticky="ew")
                ent.insert(0, "0")
                entries[under_key][field] = ent
            col_id += len(local_entry_fields)
            stringvars[under_key] = {}            
            for idx, field in enumerate(local_status_fields):
                v= get_type_var(self.field_types[field])
                lab = ttk.Label(self.lblframe, textvariable = v, anchor='w')
                lab.grid(row=row_id, column=col_id+idx, sticky="ew")
                v.set('0')
                stringvars[under_key][field] = v       
            row_id +=1
        self.entries = entries
        self.stringvars = stringvars        
        #self.lblframe.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.get_params()
        return
    
    def recalc(self):
        self.app.run_strat_func(self.name, 'initialize')

class DTStratGui(StratGui):
    def __init__(self, strat, app, master):
        StratGui.__init__(self, strat, app, master)
        self.entry_fields = ['NumTick', 'OrderType', 'MinRng', 'MaWin', 'TradeUnit', 'Lookbacks', 'Ratios', 'CloseTday']
        self.status_fields = ['TdayOpen', 'CurrPrices', 'CurRng', 'CurMa'] 
        self.shared_fields = ['NumTick', 'OrderType', 'MinRng', 'MaWin']
        self.field_types = {'TradeUnit':'int', 
                            'Lookbacks':'int', 
                            'Ratios': 'floatlist', 
                            'CloseTday': 'bool',
                            'TdayOpen': 'float',
                            'CurrPrices': 'float',
                            'CurRng':'float',
                            'CurMa': 'float',
                            'NumTick': 'int', 
                            'MaWin': 'int',
                            'OrderType': 'str',
                            'MinRng': 'float'}
                        
class RBStratGui(StratGui):
    def __init__(self, strat, app, master):
        StratGui.__init__(self, strat, app, master)
        self.root = master
        self.entry_fields = ['NumTick', 'OrderType', 'EntryLimit', 'DailyCloseBuffer', 'TradeUnit', 'MinRng', 'TrailLoss', 'Ratios', 'StartMinId']
        self.status_fields = ['CurrPrices', 'Sbreak', 'Bsetup', 'Benter', 'Senter', 'Ssetup', 'Bbreak']
        self.shared_fields = ['NumTick', 'OrderType', 'EntryLimit', 'DailyCloseBuffer']
        self.field_types = {'TradeUnit':'int', 
                            'MinRng':'float', 
                            'Ratios': 'floatlist', 
                            'StartMinId': 'int',
                            'CurrPrices': 'float',
                            'Sbreak': 'float', 
                            'Bbreak':'float',
                            'Bsetup':'float', 
                            'Benter':'float', 
                            'Senter':'float', 
                            'Ssetup':'float',
                            'TrailLoss':'float',
                            'NumTick': 'int',
                            'EntryLimit': 'int',
                            'DailyCloseBuffer': 'int',
                            'OrderType': 'str' }        

class TLStratGui(StratGui):
    def __init__(self, strat, app, master):
        StratGui.__init__(self, strat, app, master)
        self.root = master
        self.entry_fields = ['NumTick', 'OrderType', 'TradeUnit']
        self.status_fields = ['CurrPrices', 'TrailLoss', 'CurrAtr', 'EntryHigh', 'EntryLow', 'ExitHigh', 'ExitLow'] 
        self.shared_fields = ['NumTick', 'OrderType']
        self.field_types = {'TradeUnit':'int', 
                            'TrailLoss': 'float',
                            'CurrPrices': 'float',
                            'CurrAtr':  'float',
                            'EntryHigh':'float',
                            'EntryLow': 'float',
                            'ExitHigh': 'float',
                            'ExitLow':  'float',
                            'NumTick': 'int',
                            'OrderType': 'str' } 

class OptionArbStratGui(StratGui):
    def __init__(self, strat, app, master):
        StratGui.__init__(self, strat, app, master)
        self.root = master
        self.entry_fields = ['NumTick', 'OrderType', 'ProfitRatio', 'ExitRatio']
        self.status_fields = ['TradeUnit', 'BidPrices', 'AskPrices', 'DaysToExpiry', 'TradeMargin'] 
        self.shared_fields = ['NumTick', 'OrderType', 'ProfitRatio', 'ExitRatio']
        self.field_types = {'TradeUnit':'int', 
                            'BidPrices': 'float',
                            'AskPrices': 'float',
                            'DaysToExpiry':'int',
                            'TradeMargin':'floatlist',
                            'NumTick': 'int',
                            'OrderType': 'str',
                            'ProfitRatio': 'float', 
                            'ExitRatio': 'float'} 
                   
class OptVolgridGui(object):
    def __init__(self, vg, app, master):
        all_insts = app.agent.instruments
        self.root = master
        self.name = vg.name
        self.app = app
        self.expiries = vg.underlier.keys()
        self.expiries.sort()
        self.underliers = [vg.underlier[expiry] for expiry in self.expiries] 
        self.option_insts = list(set().union(*vg.option_insts.values()))
        self.spot_model = vg.spot_model
        self.cont_mth = list(set([ all_insts[inst].cont_mth for inst in self.option_insts]))
        self.cont_mth.sort()
        self.strikes = [list(set([ all_insts[inst].strike for inst in vg.option_insts[expiry]])) for expiry in self.expiries]
        for idx in range(len(self.strikes)):
            self.strikes[idx].sort()
        self.opt_dict = {}
        for inst in self.option_insts:
            key = (all_insts[inst].cont_mth, all_insts[inst].otype, all_insts[inst].strike)
            self.opt_dict[key] = inst
        self.canvas = None
        self.pos_canvas = None
        self.frame = None
        self.pos_frame = None

        #vol_labels = ['Expiry', 'Under', 'Df', 'Fwd', 'Atm', 'V90', 'V75', 'V25', 'V10', 'Updated']
        self.volgrid = instrument.copy_volgrid(vg)
        self.curr_insts = {} 
        self.rf = app.agent.irate
        self.entries = {}
        self.option_map = {}
        self.group_risk = {}
        self.stringvars = {'Insts':{}, 'Volgrid':{}}
        self.entry_fields = []
        self.status_fields = [] 
        self.field_types = {}
        inst_labels = ['Name', 'Price', 'BidPrice', 'BidVol', 'BidIV', 'AskPrice','AskVol','AskIV', 'Volume', 'OI', 'PV', 'Delta', 'Gamma','Vega', 'Theta']
        inst_types  = ['string','float', 'float', 'int', 'float', 'float', 'int','float','float', 'int', 'int', 'float', 'float', 'float', 'float', 'float']
        for inst in self.option_insts:
            if inst not in self.root.stringvars:
                self.root.stringvars[inst] = {}
            for lbl, itype in zip(inst_labels, inst_types):
                self.root.stringvars[inst][lbl] = get_type_var(itype)                
        under_labels = ['Name', 'Price','BidPrice','BidVol','AskPrice','AskVol','UpLimit','DownLimit', 'Volume', 'OI']
        under_types = ['string', 'float', 'float', 'int', 'float', 'int', 'float', 'float',  'int', 'int']        
        for inst in list(set(self.underliers)):
            if inst not in self.root.stringvars:
                self.root.stringvars[inst] = {}
            for ulbl, utype in zip(under_labels, under_types):
                self.root.stringvars[inst][ulbl] = get_type_var(utype)                 
        vol_labels = ['Expiry', 'Under', 'Df', 'Fwd', 'Atm', 'V90', 'V75', 'V25', 'V10','Updated']
        vol_types =  ['string', 'string', 'float','float','float','float','float','float','float','float']
        for expiry in self.expiries:
            self.stringvars['Volgrid'][expiry] = {}
            for vlbl, vtype in zip(vol_labels, vol_types):
                self.stringvars['Volgrid'][expiry][vlbl] = get_type_var(vtype)
                       
    def get_T_table(self):
        params = self.app.get_agent_params(['Insts'])
        self.curr_insts = params['Insts']
        inst_labels = ['Name', 'Price','BidPrice', 'BidVol','AskPrice', 'AskVol', 'Volume', 'OI', 'PV', 'Delta','Gamma','Vega', 'Theta']
        under_labels = ['Name', 'Price','BidPrice','BidVol','AskPrice','AskVol', 'Volume', 'OI', 'UpLimit','DownLimit']
        for inst in self.underliers:
            for instlbl in under_labels:
                value = self.curr_insts[inst][instlbl]
                self.root.stringvars[inst][instlbl].set(keepdigit(value,4))        
        for inst in self.option_insts:
            for instlbl in inst_labels:
                value = self.curr_insts[inst][instlbl] 
                self.root.stringvars[inst][instlbl].set(keepdigit(value,4))

        vol_labels = ['Expiry', 'Under', 'Df', 'Fwd', 'Atm', 'V90', 'V75', 'V25', 'V10','Updated']
        params = self.app.get_agent_params(['Volgrids.'+self.name])
        results = params['Volgrids'][self.name]
        for expiry in results:
            if expiry in self.stringvars['Volgrid']:
                for vlbl in vol_labels:
                    value = results[expiry][vlbl]
                    self.stringvars['Volgrid'][expiry][vlbl].set(keepdigit(value,5))
            vn = self.volgrid.volnode[expiry]
            vn.setFwd(results[expiry]['Fwd'])
            vn.setToday(results[expiry]['Updated'])
            vn.setAtm(results[expiry]['Atm'])
            vn.setD90Vol(results[expiry]['V90'])
            vn.setD75Vol(results[expiry]['V75'])
            vn.setD25Vol(results[expiry]['V25'])
            vn.setD10Vol(results[expiry]['V10'])
            vn.initialize()
            
        for key in self.opt_dict:
            inst = self.opt_dict[key]
            bid_price = self.curr_insts[inst]['BidPrice']
            ask_price = self.curr_insts[inst]['AskPrice']
            idx = self.cont_mth.index(key[0])
            expiry = self.expiries[idx]
            fwd = self.volgrid.volnode[expiry].fwd_()
            strike = key[2]
            otype = key[1]
            Texp =  self.volgrid.volnode[expiry].expiry_()
            bvol = pyktlib.BlackImpliedVol(bid_price, fwd, strike, self.rf, Texp, otype) if bid_price > 0 else 0
            avol = pyktlib.BlackImpliedVol(ask_price, fwd, strike, self.rf, Texp, otype) if bid_price > 0 else 0 
            self.root.stringvars[inst]['BidIV'].set(keepdigit(bvol,4))
            self.curr_insts[inst]['BidIV'] = bvol
            self.root.stringvars[inst]['AskIV'].set(keepdigit(avol,4))
            self.curr_insts[inst]['AskIV'] = avol
        return
    
    def calib_volgrids(self):
        pass
    
    def recalc_risks(self):
        params = (self.name, )
        self.app.run_agent_func('reval_volgrids', params)
        return

    def show_risks(self):
        pos_win   = tk.Toplevel(self.frame)
        self.pos_canvas = tk.Canvas(pos_win)
        self.pos_frame = tk.Frame(self.pos_canvas)
        pos_vsby = tk.Scrollbar(pos_win, orient="vertical", command=self.pos_canvas.yview)
        pos_vsbx = tk.Scrollbar(pos_win, orient="horizontal", command=self.pos_canvas.xview)
        self.pos_canvas.configure(yscrollcommand=pos_vsby.set, xscrollcommand=pos_vsbx.set)
        pos_vsbx.pack(side="bottom", fill="x")
        pos_vsby.pack(side="right", fill="y")
        self.pos_canvas.pack(side="left", fill="both", expand=True)
        self.pos_canvas.create_window((4,4), window=self.pos_frame, anchor="nw", tags="self.pos_frame")
        self.pos_frame.bind("<Configure>", self.OnPosFrameConfigure)
        fields = ['Name', 'Underlying', 'Contract', 'Otype', 'Stike', 'Price', 'BidPrice', 'BidIV', 'AskPrice', 'AskIV', 'PV', 'Delta','Gamma','Vega', 'Theta']
        for idx, field in enumerate(fields):
            tk.Label(self.pos_frame, text = field).grid(row=0, column=idx)
        idy = 0
        for i, cmth in enumerate(self.cont_mth):
            for strike in self.strikes[i]:
                for otype in ['C','P']:
                    key = (cmth, otype, strike)
                    if key in self.opt_dict:
                        idy += 1
                        inst = self.opt_dict[key]
                        for idx, field in enumerate(fields):
                            if idx == 0:
                                txt = inst
                            elif idx == 1:
                                txt = self.underliers[i]
                            elif idx in [2, 3, 4]: 
                                txt = key[idx-2]
                            else:
                                factor = 1
                                if field in ['delta', 'gamma', 'BidIV', 'AskIV']: 
                                    factor = 100
                                txt = self.curr_insts[inst][field]*factor
                            tk.Label(self.pos_frame, text = keepdigit(txt,3)).grid(row=idy, column=idx)
        #pos_win.pack()
        return
        
    def OnPosFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.pos_canvas.configure(scrollregion=self.pos_canvas.bbox("all"))        
        pass
    
    def set_frame(self, root):
        self.canvas = tk.Canvas(root)
        self.frame = tk.Frame(self.canvas)
        self.vsby = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.vsbx = tk.Scrollbar(root, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsby.set, xscrollcommand=self.vsbx.set)
        self.vsbx.pack(side="bottom", fill="x")
        self.vsby.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame")
        self.frame.bind("<Configure>", self.OnFrameConfigure)
        self.populate()

    def populate(self):
        vol_labels = ['Expiry', 'Under', 'Df', 'Fwd', 'Atm', 'V90', 'V75', 'V25', 'V10','Updated']
        vol_types =  ['string', 'string', 'float','float','float','float','float','float','float','float']
        inst_labels = ['Name', 'Price', 'BidPrice', 'BidVol', 'BidIV', 'AskPrice','AskVol','AskIV', 'Volume', 'OI']
        under_labels = ['Name', 'Price','BidPrice','BidVol','AskPrice','AskVol','UpLimit','DownLimit', 'Volume', 'OI']
        row_id = 0
        col_id = 0
        for under_id, (expiry, strikes, cont_mth, under) in enumerate(zip(self.expiries, self.strikes, self.cont_mth, self.underliers)):
            col_id = 0
            for idx, vlbl in enumerate(vol_labels):
                tk.Label(self.frame, text=vlbl).grid(row=row_id, column=col_id + idx)
                tk.Label(self.frame, textvariable = self.stringvars['Volgrid'][expiry][vlbl]).grid(row=row_id+1, column=col_id + idx)
                
            ttk.Button(self.frame, text='Refresh', command= self.get_T_table).grid(row=row_id, column=10, columnspan=2)
            ttk.Button(self.frame, text='CalcRisk', command= self.recalc_risks).grid(row=row_id+1, column=10, columnspan=2) 
            ttk.Button(self.frame, text='CalibVol', command= self.calib_volgrids).grid(row=row_id, column=12, columnspan=2)
            ttk.Button(self.frame, text='RiskGroup', command= self.show_risks).grid(row=row_id+1, column=12, columnspan=2)
            row_id += 2
            col_id = 0
            inst = self.underliers[under_id]
            for idx, ulbl in enumerate(under_labels):
                tk.Label(self.frame, text=ulbl).grid(row=row_id, column=col_id + idx)
                tk.Label(self.frame, textvariable = self.root.stringvars[inst][ulbl]).grid(row=row_id+1, column=col_id + idx)              
            row_id += 2
            col_id = 0
            for idx, instlbl in enumerate(inst_labels + ['strike']):
                tk.Label(self.frame, text=instlbl).grid(row=row_id, column=col_id+idx)
                if instlbl != 'strike':
                    tk.Label(self.frame, text=instlbl).grid(row=row_id, column=col_id+2*len(inst_labels)-idx)
                for idy, strike in enumerate(strikes):
                    if instlbl == 'strike':
                        tk.Label(self.frame, text = str(strike), padx=10).grid(row=row_id+1+idy, column=col_id+idx)
                    else:
                        key1 = (cont_mth, 'C', strike)
                        if key1 in self.opt_dict:
                            inst1 = self.opt_dict[key1]
                            tk.Label(self.frame, textvariable = self.root.stringvars[inst1][instlbl], padx=10).grid(row=row_id+1+idy, column=col_id + idx)

                        key2 = (cont_mth, 'P', strike)
                        if key1 in self.opt_dict:
                            inst2 = self.opt_dict[key2]                            
                            tk.Label(self.frame, textvariable = self.root.stringvars[inst2][instlbl], padx=10).grid(row=row_id+1+idy, column=col_id+2*len(inst_labels)-idx)
            row_id = row_id + len(strikes) + 2
        self.get_T_table()
        return

    def OnFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))        
        pass
    
class Gui(tk.Tk):
    def __init__(self, app = None):
        tk.Tk.__init__(self)       
        self.title(app.name)
        self.app = app
        if app!=None:
            self.app.master = self
        #self.scroll_text = ScrolledText.ScrolledText(self, state='disabled')
        #self.scroll_text.configure(font='TkFixedFont')
        # Create textLogger
        #self.text_handler = TextHandler(self.scroll_text)
        #self.scroll_text.pack()
        self.settings_win = None
        self.status_win = None
        self.pos_frame = None
        self.pos_canvas = None
        self.entries = {}
        self.stringvars = {'Insts':{}}
        self.status_ents = {}
        self.strat_frame = {}
        self.strat_gui = {}
        self.volgrid_gui = {}
        self.volgrid_frame = {}
        self.setup_fields = ['MarketOrderTickMultiple', 'CancelProtectPeriod', 'MarginCap']
        self.status_fields = ['Positions', 'Orders', 'Trades', 'Insts', 'ScurDay', 'EodFlag', 'Initialized', 'ProcLock', \
                              'CurrCapital', 'PrevCapital', 'LockedMargin', 'UsedMargin', 'Available', 'PnlTotal']
        self.field_types = {'ProcLock': 'bool',
                            'ScurDay' : 'date',
                            'EodFlag' : 'bool',
                            'MarketOrderTickMultiple': 'int', 
                            'CancelProtectPeriod': 'int', 
                            'MarginCap': 'float',
                            'CurrCapital':'float', 
                            'PrevCapital':'float', 
                            'LockedMargin':'float', 
                            'UsedMargin':'float', 
                            'Available':'float', 
                            'PnlTotal':'float',
                            'Initialized': 'bool',
                            'QryInst': 'string'}
    
        for strat_name in self.app.agent.strategies:
            strat = self.app.agent.strategies[strat_name]
            if strat.__class__.__name__ == 'DTTrader':
                self.strat_gui[strat_name] = DTStratGui(strat, app, self)
            elif strat.__class__.__name__ == 'RBreakerTrader':
                self.strat_gui[strat_name] = RBStratGui(strat, app, self)
            elif strat.__class__.__name__ == 'TurtleTrader':
                self.strat_gui[strat_name] = TLStratGui(strat, app, self)
            elif strat.__class__.__name__ == 'OptionArbStrat':
                self.strat_gui[strat_name] = OptionArbStratGui(strat, app, self)
                        
        if ('Option' in app.agent.__class__.__name__) and (len(app.agent.volgrids)>0):
            for prod in app.agent.volgrids:
                self.volgrid_gui[prod] = OptVolgridGui(app.agent.volgrids[prod], app, self)
                
        menu = tk.Menu(self)
        toolmenu = tk.Menu(menu, tearoff=0)
        toolmenu.add_command(label = 'MarketViewer', command=self.market_view)
        toolmenu.add_command(label = 'PositionViewer', command=self.position_view)        
        menu.add_cascade(label="Tools", menu=toolmenu)
        menu.add_command(label="Reset", command=self.onReset)
        menu.add_command(label="Exit", command=self.onExit)
        self.config(menu=menu)
        self.notebook = ttk.Notebook(self)
        self.settings_win = ttk.Frame(self.notebook)
        self.config_settings()
        self.notebook.add(self.settings_win, text = 'Settings')
        #self.status_win = ttk.Frame(self.notebook)
        #self.make_status_form()
        #self.notebook.add(self.status_win, text = 'Orders')
        for prod in self.volgrid_gui:
            self.volgrid_frame[prod] = ttk.Frame(self)
            self.volgrid_gui[prod].set_frame(self.volgrid_frame[prod])
            self.notebook.add(self.volgrid_frame[prod], text = 'VG_' + prod)
                    
        for strat_name in self.app.agent.strategies:
            self.strat_frame[strat_name] = ttk.Frame(self)
            self.strat_gui[strat_name].set_frame(self.strat_frame[strat_name])
            self.notebook.add(self.strat_frame[strat_name], text = strat_name)
        self.notebook.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    def market_view(self):
        pass

    def position_view(self):
        params = self.app.get_agent_params(['Positions'])
        positions = params['Positions']
        pos_win   = tk.Toplevel(self)
        self.pos_canvas = tk.Canvas(pos_win)
        self.pos_frame = tk.Frame(self.pos_canvas)
        pos_vsby = tk.Scrollbar(pos_win, orient="vertical", command=self.pos_canvas.yview)
        pos_vsbx = tk.Scrollbar(pos_win, orient="horizontal", command=self.pos_canvas.xview)
        self.pos_canvas.configure(yscrollcommand=pos_vsby.set, xscrollcommand=pos_vsbx.set)
        pos_vsbx.pack(side="bottom", fill="x")
        pos_vsby.pack(side="right", fill="y")
        self.pos_canvas.pack(side="left", fill="both", expand=True)
        self.pos_canvas.create_window((4,4), window=self.pos_frame, anchor="nw", tags="self.pos_frame")
        self.pos_frame.bind("<Configure>", self.OnPosFrameConfigure)
        
        fields = ['inst', 'currlong', 'currshort', 'locklong', 'lockshort', 'ydaylong', 'ydayshort']
        for idx, field in enumerate(fields):
            tk.Label(self.pos_frame, text = field).grid(row=0, column=idx)
            for idy, inst in enumerate(positions.keys()): 
                if field == 'inst':
                    txt = inst
                else:
                    txt = positions[inst][field]
                tk.Label(self.pos_frame, text = txt).grid(row=idy+1, column=idx)
        return      

    def OnPosFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.pos_canvas.configure(scrollregion=self.pos_canvas.bbox("all"))        
        pass
    
    def qry_agent_inst(self):
        instfield = 'QryInst'
        ent = self.entries[instfield]
        inst = ent.get()
        params = self.app.get_agent_params(['Insts.' + inst])
        inst_fields = ['Price', 'PrevClose', 'Volume', 'OI', 'AskPrice', 'AskVol', 'BidPrice', 'BidVol', 'UpLimit', 'DownLimit']
        for field in inst_fields:
            v = self.stringvars['Insts.'+field]
            v.set(params['Insts'][inst][field])
        pass
    
    def recalc_margin(self):
        params = ()
        self.app.run_agent_func('calc_margin', params)
        return

    def run_eod(self):
        params = ()
        self.app.run_agent_func('run_eod', params)
        return
            
    def config_settings(self):
        entry_fields = ['MarketOrderTickMultiple', 'CancelProtectPeriod', 'MarginCap']
        label_fields = ['ScurDay', 'EodFlag', 'Initialized' ]
        lbl_frame = ttk.Labelframe(self.settings_win)
        row_idx = 0
        for field1, field2 in zip(entry_fields, label_fields):
            #row = tk.Frame(root)
            lab = ttk.Label(lbl_frame, text=field1+": ", anchor='w')
            lab.grid(column=0, row=row_idx, sticky="ew")
            ent = tk.Entry(lbl_frame)
            self.entries[field1] = ent
            ent.insert(0,"0")
            ent.grid(column=1, row=row_idx, sticky="ew")
            v = tk.IntVar()
            lab1 = ttk.Label(lbl_frame, text=field2+": ", anchor='w')
            self.stringvars[field2] = v
            lab1.grid(column=2, row=row_idx, sticky="ew")
            lab2 = ttk.Label(lbl_frame, textvariable = v, anchor='w')
            lab2.grid(column=3, row=row_idx, sticky="ew")
            row_idx += 1
        pnl_fields = ['CurrCapital', 'PrevCapital', 'PnlTotal']
        margin_fields = ['LockedMargin', 'UsedMargin', 'Available']
        for field1, field2 in zip(pnl_fields, margin_fields):
            #row = tk.Frame(root)
            lab1 = ttk.Label(lbl_frame, text=field1+": ", anchor='w')
            lab1.grid(column=0, row=row_idx, sticky="ew")
            v1 = tk.DoubleVar()
            lab2 = ttk.Label(lbl_frame, textvariable = v1, anchor='w')
            self.stringvars[field1] = v1
            lab2.grid(column=1, row=row_idx, sticky="ew")

            lab3 = ttk.Label(lbl_frame, text=field2+": ", anchor='w')
            lab3.grid(column=2, row=row_idx, sticky="ew")
            v2 = tk.DoubleVar()
            lab4 = ttk.Label(lbl_frame, textvariable = v2, anchor='w')
            self.stringvars[field2] = v2
            lab4.grid(column=3, row=row_idx, sticky="ew")
            row_idx += 1      
        all_fields = entry_fields+label_fields+pnl_fields+margin_fields
        setup_setbtn = ttk.Button(lbl_frame, text='SetParam', command= lambda: self.set_agent_params(entry_fields))
        setup_setbtn.grid(column=0, row=row_idx, sticky="ew")
        setup_loadbtn = ttk.Button(lbl_frame, text='LoadParam', command= lambda: self.get_agent_params(all_fields))
        setup_loadbtn.grid(column=1, row=row_idx, sticky="ew")
        setup_loadbtn = ttk.Button(lbl_frame, text='ReCalc', command= self.recalc_margin)
        setup_loadbtn.grid(column=2, row=row_idx, sticky="ew")
        setup_loadbtn = ttk.Button(lbl_frame, text='RunEOD', command= self.run_eod)
        setup_loadbtn.grid(column=3, row=row_idx, sticky="ew")
        setup_qrybtn = ttk.Button(lbl_frame, text='QueryInst', command= self.qry_agent_inst)
        setup_qrybtn.grid(column=4, row=row_idx, sticky="ew")
        row_idx +=1
        field = 'QryInst'
        lab = ttk.Label(lbl_frame, text= field, anchor='w')
        lab.grid(column=0, row=row_idx, sticky="ew")
        ent = tk.Entry(lbl_frame)
        ent.grid(column=0, row=row_idx+1, sticky="ew")
        self.entries[field] = ent
        inst_fields = ['Price', 'PrevClose', 'Volume', 'OI', 'AskPrice', 'AskVol', 'BidPrice', 'BidVol', 'UpLimit', 'DownLimit']        
        for idx, field in enumerate(inst_fields):
            lab1 = ttk.Label(lbl_frame, text=field, anchor='w')
            lab1.grid(column=idx+1, row=row_idx, sticky="ew")
            v = tk.DoubleVar()
            lab2 = ttk.Label(lbl_frame, textvariable = v, anchor='w')
            self.stringvars['Insts.' + field] = v
            lab2.grid(column=idx+1, row=row_idx+1, sticky="ew")            
        lbl_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        
        self.get_agent_params(all_fields)
    
    def set_agent_params(self, fields):
        params = {}
        for field in fields:
            ent = self.entries[field]
            value = ent.get()
            vtype = self.field_types[field]
            params[field] = str2type(value, vtype)
        self.app.set_agent_params(params)
        pass
    
    def get_agent_params(self, fields):
        params = self.app.get_agent_params(fields)
        for field in fields:
            vtype = self.field_types[field]
            value = type2str(params[field], vtype)
            if field in self.entries:
                ent = self.entries[field]
                ent.delete(0, tk.END)
                ent.insert(0, value)
            elif field in self.stringvars:
                var = self.stringvars[field]
                var.set(keepdigit(value,4))
        return
        
    def refresh_agent_status(self):
        pass
    
    def make_status_form(self):
        pass
        
    def onStatus(self):
        self.status_win = tk.Toplevel(self)
        self.status_ents = self.make_status_form(self.status_win)        
        
    def onReset(self):
        self.app.reset_agent(self.app.save_test)

    def onExit(self):
        self.app.exit_agent()
        self.destroy()
        #self.quit()
        return
        
class MainApp(object):
    def __init__(self, name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = True):
        self.trader_cfg = trader_cfg
        self.user_cfg = user_cfg
        self.strat_cfg = strat_cfg
        self.scur_day = tday
        self.name = name
        self.agent = None
        self.master = master
        self.save_test = save_test
        self.reset_agent(save_test)
                        
    def reset_agent(self, save_test):       
        if self.agent != None:
            self.scur_day = self.agent.scur_day
        all_insts= []
        for strat in self.strat_cfg['strategies']:
            all_insts = list(set(all_insts).union(set(strat.instIDs)))
        self.agent = ctp_api.create_agent(self.name, self.user_cfg, self.trader_cfg, all_insts, self.strat_cfg, self.scur_day)
        #self.agent.logger.addHandler(self.text_handler)
        #ctp_api.make_user(self.agent, self.user_cfg)
        if save_test:
            self.agent.tick_db_table = 'test_fut_tick'
            self.agent.min_db_table  = 'test_fut_min'
            self.agent.daily_db_table= 'test_fut_daily'
            self.agent.save_flag = True
        self.agent.resume()
        return
    
    def get_agent_params(self, fields):
        res = {}
        for f in fields:
            field_list = f.split('.')
            field = field_list[0]
            if field == 'Positions':
                positions = {}
                for inst in self.agent.positions:
                    pos = self.agent.positions[inst]
                    positions[inst] = {'currlong' : pos.curr_pos.long, 
                                       'currshort': pos.curr_pos.short, 
                                       'locklong' : pos.locked_pos.long, 
                                       'lockshort': pos.locked_pos.short, 
                                       'ydaylong':  pos.pos_yday.long, 
                                       'ydayshort': pos.pos_yday.short}
                res[field] = positions
            elif field == 'Orders':
                order_list = []
                for o in self.agent.ref2order.values():
                    inst = o.position.instrument.name
                    order_list.append([o.order_ref, o.sys_id, inst, o.diretion, o.volume, o.filled_volume,  o.limit_price, o.status])
                res[field] = order_list
            elif field == 'Trades':
                trade_list = []
                for etrade in self.agent.etrades:
                    insts = ' '.join(etrade.instIDs)
                    volumes = ' '.join([str(i) for i in etrade.volumes])
                    filled_vol = ' '.join([str(i) for i in etrade.filled_vol])
                    filled_price = ' '.join([str(i) for i in etrade.filled_price])
                    trade_list.append([etrade.id, insts, volumes, filled_vol, filled_price, etrade.limit_price, etrade.valid_time,
                                  etrade.strategy, etrade.book, etrade.status])
                res[field] = trade_list
            elif field == 'Insts':
                if len(field_list) > 1:
                    insts = field_list[1:]
                else:
                    insts = self.agent.instruments.keys()
                inst_dict = {}
                for inst in insts:
                    inst_obj = self.agent.instruments[inst]
                    inst_dict[inst] = {'Name': inst, 'Price': inst_obj.price, 
                                 'BidPrice': inst_obj.bid_price1, 'BidVol': inst_obj.bid_vol1, 
                                 'AskPrice': inst_obj.ask_price1, 'AskVol': inst_obj.ask_vol1, 
                                 'PrevClose': inst_obj.prev_close, 'MarginRate': inst_obj.marginrate, 
                                 'Updated': inst_obj.last_update, 'Traded': inst_obj.last_traded,
                                 'UpLimit': inst_obj.up_limit, 'DownLimit': inst_obj.down_limit,
                                 'Volume': inst_obj.volume, 'OI': inst_obj.open_interest }
                    if 'Option' in inst_obj.__class__.__name__:
                        inst_dict[inst]['PV'] = inst_obj.pv
                        inst_dict[inst]['Delta'] = inst_obj.delta
                        inst_dict[inst]['Gamma'] = inst_obj.gamma
                        inst_dict[inst]['Vega']  = inst_obj.vega
                        inst_dict[inst]['Theta'] = inst_obj.theta
                        inst_dict[inst]['Otype'] = inst_obj.otype
                        inst_dict[inst]['Strike'] = inst_obj.strike
                        inst_dict[inst]['Underlying'] = inst_obj.underlying
                res[field] = inst_dict
            elif field == 'Volgrids':
                prod = field_list[1]
                vg_param = {}
                if prod in self.agent.volgrids:
                    vg = self.agent.volgrids[prod]
                    for expiry in vg.volnode:
                        vg_param[expiry] = {}
                        vg_param[expiry]['Fwd'] = vg.fwd[expiry]
                        vg_param[expiry]['Updated'] = vg.dtoday
                        vg_param[expiry]['Expiry'] = expiry
                        vg_param[expiry]['Under'] = vg.underlier[expiry]
                        vg_param[expiry]['Df'] = vg.df[expiry]
                        vol_param = vg.volparam[expiry]
                        vg_param[expiry]['Atm'] = vol_param[0]
                        vg_param[expiry]['V90'] = vol_param[1]
                        vg_param[expiry]['V75'] = vol_param[2]
                        vg_param[expiry]['V25'] = vol_param[3]
                        vg_param[expiry]['V10'] = vol_param[4]
                res[field] = {prod: vg_param}
            else:
                var = field2variable(field)
                res[field] = getattr(self.agent, var)
        return res

    def set_agent_params(self, params):
        for field in params:
            var = field2variable(field)
            value = params[field]
            setattr(self.agent, var, value)
        return
    
    def get_strat_params(self, strat_name, fields):
        params = {}
        strat = self.agent.strategies[strat_name]
        for field in fields:
            var = field2variable(field)
            params[field] = getattr(strat, var)
        return params
    
    def set_strat_params(self, strat_name, params):
        strat = self.agent.strategies[strat_name]
        for field in params:
            var = field2variable(field)
            value = params[field]
            setattr(strat, var, value)
    
    def run_strat_func(self, strat_name, func_name):
        strat = self.agent.strategies[strat_name]
        getattr(strat, func_name)()

    def run_agent_func(self, func_name, params):
        getattr(self.agent, func_name)(*params)
        return 
        
    def exit_agent(self):
        if self.agent != None:
            self.agent.exit()
