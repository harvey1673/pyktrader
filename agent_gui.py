import agent
import fut_api
#import lts_api
import logging
import misc
import Tkinter as tk
import ttk
import ScrolledText
import sys
import optstrat
import strat_dual_thrust as strat_dt
import strat_rbreaker as strat_rb
import datetime
import re
import pyktlib

vtype_func_map = {'int':int, 'float':float, 'str': str, 'bool':bool }

def keepdigit(x, pow=5): 
    out = x
    if isinstance(x, float):
        if x >= 10**pow:
            out = int(x)
        elif x>=1:
            n = pow + 1- len(str(int(x)))
            out = int(x*(10**n)+0.5)/float(10**n)
        else:
            out = int(x*10**pow+0.5)/1.0/10**pow
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
    if vtype == 'bool':
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
        self.field_types = {}
        
    def get_params(self):
        fields = self.entry_fields + self.status_fields
        params = self.app.get_strat_params(self.name, fields)
        for field in fields:
            for idx, underlier in enumerate(self.underliers):
                inst = underlier[0]
                value = params[field][idx]
                vtype = self.field_types[field]
                value = type2str(value, vtype)
                if field in self.entry_fields:
                    ent = self.entries[inst][field]
                    ent.delete(0, tk.END)
                    ent.insert(0, value)
                elif field in self.status_fields:
                    self.stringvars[inst][field].set(keepdigit(value, 4))
        return
        
    def set_params(self):
        params = {}
        for field in self.entry_fields:
            params[field] = []
            for underlier in self.underliers:
                inst = underlier[0]
                ent = self.entries[inst][field]
                value = ent.get()
                vtype = self.field_types[field]
                value = str2type(value, vtype)
                params[field].append(value)
        self.app.set_strat_params(self.name, params)
        return
        
    def set_frame(self, root):
        self.lblframe = ttk.Frame(root)
        self.lblframe.grid_columnconfigure(1, weight=1)
        fields = ['inst'] + self.entry_fields + self.status_fields
        for idx, field in enumerate(fields):
            lbl = ttk.Label(self.lblframe, text = field, anchor='w')
            lbl.grid(row=0, column=idx, sticky="ew")
        row_id = 1
        entries = {}
        stringvars = {}
        for underlier in self.underliers:
            inst = str(underlier[0])
            inst_lbl = ttk.Label(self.lblframe, text=inst, anchor="w")
            inst_lbl.grid(row=row_id, column=0, sticky="ew")
            col_id = 1
            entries[inst] = {}
            for idx, field in enumerate(self.entry_fields):
                ent = ttk.Entry(self.lblframe)
                ent.grid(row=row_id, column=col_id+idx, sticky="ew")
                ent.insert(0, "0")
                entries[inst][field] = ent
            col_id += len(self.entry_fields)
            stringvars[inst] = {}
            for idx, field in enumerate(self.status_fields):
                v= get_type_var(self.field_types[field])
                lab = ttk.Label(self.lblframe, textvariable = v, anchor='w')
                lab.grid(row=row_id, column=col_id+idx, sticky="ew")
                v.set('0')
                stringvars[inst][field] = v       
            row_id +=1
        self.entries = entries
        self.stringvars = stringvars
        
        set_btn = ttk.Button(self.lblframe, text='Set', command=self.set_params)
        set_btn.grid(row=row_id, column=1, sticky="ew")
        refresh_btn = ttk.Button(self.lblframe, text='Refresh', command=self.get_params)
        refresh_btn.grid(row=row_id, column=2, sticky="ew")
        recalc_btn = ttk.Button(self.lblframe, text='Recalc', command=self.recalc)
        recalc_btn.grid(row=row_id, column=3, sticky="ew")
        self.lblframe.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.get_params()
        return
    
    def recalc(self):
        self.app.run_strat_func(self.name, 'initialize')

class DTStratGui(StratGui):
    def __init__(self, strat, app, master):
        StratGui.__init__(self, strat, app, master)
        self.entry_fields = ['TradeUnit', 'Lookbacks', 'Ratios', 'CloseTday']
        self.status_fields = ['TdayOpen', 'CurRng'] 
        self.field_types = {'TradeUnit':'int', 
                            'Lookbacks':'int', 
                            'Ratios': 'floatlist', 
                            'CloseTday': 'bool',
                            'TdayOpen': 'float', 
                            'CurRng':'float' }
                        
class RBStratGui(StratGui):
    def __init__(self, strat, app, master):
        StratGui.__init__(self, strat, app, master)
        self.root = master
        self.entry_fields = ['TradeUnit', 'MinRng', 'Ratios', 'CloseTday', 'StartMinId']
        self.status_fields = ['Sbreak', 'Bsetup', 'Benter', 'Senter', 'Ssetup', 'Bbreak'] 
        self.field_types = {'TradeUnit':'int', 
                            'MinRng':'float', 
                            'Ratios': 'floatlist', 
                            'CloseTday': 'bool',
                            'StartMinId': 'int',
                            'Sbreak': 'float', 
                            'Bbreak':'float',
                            'Bsetup':'float', 
                            'Benter':'float', 
                            'Senter':'float', 
                            'Ssetup':'float' }        
    
class OptStratGui(object):
    def __init__(self, strat, app, master):
        self.pricer = strat.pricer
        self.root = master
        self.name = strat.name
        self.app = app
        self.underliers = strat.underliers
        self.option_insts = strat.option_insts.keys()
        self.expiries = strat.expiries
        self.cont_mth = []
        if len(self.underliers) == 1:
            self.cont_mth = [ d.year*100+d.month for d in self.expiries]
        else:
            self.cont_mth = [ 201000 + int(inst[-3:]) for inst in self.underliers]
        self.strikes = strat.strikes
        self.opt_dict = strat.opt_dict
        self.canvas = None
        self.pos_canvas = None
        self.frame = None
        self.pos_frame = None

        #vol_labels = ['Expiry', 'Under', 'Df', 'Fwd', 'Atm', 'V90', 'V75', 'V25', 'V10', 'Updated']
        self.volgrids = {}
        self.fwds = {}
        self.vol_params = {}
        self.curr_insts = {} 
        self.rf = optstrat.RISK_FREE_RATE
        for expiry in self.expiries:
            vol = strat.volgrids[expiry]
            dtoday = vol.dtoday_()
            dexp = vol.dexp_()
            fwd = vol.fwd_()
            self.fwds[expiry] = fwd
            atm = vol.atmVol_()
            v90 = vol.d90Vol_()
            v75 = vol.d75Vol_()
            v25 = vol.d25Vol_()
            v10 = vol.d10Vol_()
            self.vol_params = [atm, v90, v75, v25, v10]
            accr= strat.accrual
            #print dtoday, dexp, fwd, atm, v90, v75, v25, v10, accr
            self.volgrids[expiry] = pyktlib.Delta5VolNode(dtoday, dexp, fwd, atm, v90, v75, v25, v10, accr)
        self.entries = {}
        self.option_map = {}
        self.group_risk = {}
        self.stringvars = {'Insts':{}, 'Volgrid':{}}
        self.entry_fields = []
        self.status_fields = [] 
        self.field_types = {}

    def get_T_table(self):
        params = self.app.get_agent_params(['Insts'])
        inst_labels = ['Name', 'Price','BidPrice', 'BidVol','AskPrice', 'AskVol']
        for inst in self.opt_dict.values():
            if inst not in self.curr_insts:
                self.curr_insts[inst] = {}
            for instlbl in inst_labels:
                value = params['Insts'][inst][instlbl]
                self.curr_insts[inst][instlbl] = value
                #value = type2str(value, value.__class__.__name__)
                self.root.stringvars[inst][instlbl].set(keepdigit(value,4))

        vol_labels = ['Expiry', 'Under', 'Df', 'Fwd', 'Atm', 'V90', 'V75', 'V25', 'V10','Updated']
        params = self.app.get_strat_params(self.name, ['Volgrid'])
        for expiry in params['Volgrid']:
            if expiry in self.stringvars['Volgrid']:
                for vlbl in vol_labels:
                    value = params['Volgrid'][expiry][vlbl]
                    #value = type2str(value, value.__class__.__name__)
                    self.stringvars['Volgrid'][expiry][vlbl].set(keepdigit(value,5))
            self.volgrids[expiry].setFwd(params['Volgrid'][expiry]['Fwd'])
            self.volgrids[expiry].setAtm(params['Volgrid'][expiry]['Atm'])
            self.volgrids[expiry].setD90Vol(params['Volgrid'][expiry]['V90'])
            self.volgrids[expiry].setD75Vol(params['Volgrid'][expiry]['V75'])
            self.volgrids[expiry].setD25Vol(params['Volgrid'][expiry]['V25'])
            self.volgrids[expiry].setD10Vol(params['Volgrid'][expiry]['V10'])
            self.volgrids[expiry].initialize()
            
        for key in self.opt_dict:
            inst = self.opt_dict[key]
            bid_price = self.curr_insts[inst]['BidPrice']
            ask_price = self.curr_insts[inst]['AskPrice']
            idx = self.cont_mth.index(key[1])
            expiry = self.expiries[idx]
            fwd = self.volgrids[expiry].fwd_()
            strike = key[3]
            otype = key[2]
            Texp =  self.volgrids[expiry].expiry_()
            bvol = pyktlib.BlackImpliedVol(bid_price, fwd, strike, self.rf, Texp, otype) if bid_price > 0 else 0
            avol = pyktlib.BlackImpliedVol(ask_price, fwd, strike, self.rf, Texp, otype) if bid_price > 0 else 0 
            self.stringvars[inst]['BidIV'].set(keepdigit(bvol,4))
            self.curr_insts[inst]['BidIV'] = bvol
            self.stringvars[inst]['AskIV'].set(keepdigit(avol,4))
            self.curr_insts[inst]['AskIV'] = avol
        return
    
    def calib_volgrids(self):
        pass
    
    def recalc_risks(self):
        self.app.run_strat_func(self.name, 'reval_all')
        return
    
    def group_risks(self):
        params = self.app.get_strat_params(self.name, ['GroupRisk'])
        self.group_risk = params['GroupRisk']
        risk_win   = tk.Toplevel(self.frame)
        fields = ['cont_mth', 'ppv', 'pdelta', 'pgamma','pvega','ptheta']
        for idx, field in enumerate(fields):
            tk.Label(risk_win, text = field).grid(row=0, column=idx)
            for idy, mth in enumerate(self.cont_mth): 
                if field == 'cont_mth':
                    txt = mth
                else:
                    txt = self.group_risk[field][mth]
                tk.Label(risk_win, text = keepdigit(txt,3)).grid(row=idy+1, column=idx)
        return        
                
    def pos_greeks(self):
        params = self.app.get_strat_params(self.name, ['OptionMap'])
        self.option_map = params['OptionMap']
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
        insts = self.underliers + self.option_insts
        fields = ['inst', 'underlier', 'cont_mth', 'pv', 'delta', 'gamma', 'vega', 'theta', \
                  'pos', 'ppv', 'pdelta', 'pgamma', 'pvega', 'ptheta']
        for idx, field in enumerate(fields):
            tk.Label(self.pos_frame, text = field).grid(row=0, column=idx)
            for idy, inst in enumerate(insts): 
                if idx == 0:
                    txt = inst
                else:
                    factor = 1
                    if field in ['delta', 'gamma']: 
                        factor = 100
                    txt = self.option_map[field][inst]*factor
                tk.Label(self.pos_frame, text = keepdigit(txt,3)).grid(row=idy+1, column=idx)
        #pos_win.pack()
        return

    def OnPosFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.pos_canvas.configure(scrollregion=self.pos_canvas.bbox("all"))        
        pass
        
    def trade_setup(self):
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
        inst_labels = ['Name', 'Price', 'BidPrice', 'BidVol', 'BidIV', 'AskPrice','AskVol','AskIV']
        inst_types  = ['string','float', 'float', 'int', 'float', 'float', 'int','float','float']
        calc_labels = [ 'BidIV', 'AskIV']
        underliers = self.underliers
        if len(self.underliers) == 1:
            underliers = self.underliers * len(self.expiries)
        row_id = 0
        col_id = 0
        for expiry, strikes, cont_mth, under in zip(self.expiries, self.strikes, self.cont_mth, underliers):
            self.stringvars['Volgrid'][expiry] = {}
            col_id = 0
            for idx, vlbl in enumerate(vol_labels):
                tk.Label(self.frame, text=vlbl).grid(row=row_id, column=col_id + idx)
                v= get_type_var(vol_types[idx])
                tk.Label(self.frame, textvariable = v).grid(row=row_id+1, column=col_id + idx)
                self.stringvars['Volgrid'][expiry][vlbl] = v
            ttk.Button(self.frame, text='Refresh', command= self.get_T_table).grid(row=row_id, column=10, columnspan=2)
            ttk.Button(self.frame, text='CalcRisk', command= self.recalc_risks).grid(row=row_id+1, column=10, columnspan=2) 
            ttk.Button(self.frame, text='PosGreeks', command= self.pos_greeks).grid(row=row_id, column=12, columnspan=2)
            ttk.Button(self.frame, text='CalibVol', command= self.calib_volgrids).grid(row=row_id+1, column=12, columnspan=2)
            ttk.Button(self.frame, text='RiskGroup', command= self.group_risks).grid(row=row_id, column=14, columnspan=2)
            ttk.Button(self.frame, text='SetupTrade', command= self.trade_setup).grid(row=row_id+1, column=14, columnspan=2)
            #ttk.Button(self.frame, text=
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
                        key1 = (under, cont_mth, 'C', strike)
                        inst1 = self.opt_dict[key1]
                        if instlbl in calc_labels:
                            if inst1 not in self.stringvars:
                                self.stringvars[inst1] = {}
                            v1 = tk.DoubleVar()
                            self.stringvars[inst1][instlbl] = v1
                        elif (inst1 in self.root.stringvars) and (instlbl in self.root.stringvars[inst1]):
                            v1 = self.root.stringvars[inst1][instlbl]
                        else:
                            if inst1 not in self.root.stringvars:
                                self.root.stringvars[inst1] = {}
                            v1 = get_type_var(inst_types[idx])
                            self.root.stringvars[inst1][instlbl] = v1
                        tk.Label(self.frame, textvariable = v1, padx=10).grid(row=row_id+1+idy, column=col_id + idx)

                        key2 = (under, cont_mth, 'P', strike)
                        inst2 = self.opt_dict[key2]
                        if instlbl in calc_labels:
                            if inst2 not in self.stringvars:
                                self.stringvars[inst2] = {}
                            v2 = tk.DoubleVar()
                            self.stringvars[inst2][instlbl] = v2
                        elif (inst2 in self.root.stringvars) and (instlbl in self.root.stringvars[inst2]):
                            v2 = self.root.stringvars[inst2][instlbl]
                        else:
                            if inst2 not in self.root.stringvars:
                                self.root.stringvars[inst2] = {}
                            v2 = get_type_var(inst_types[idx])
                            self.root.stringvars[inst2][instlbl] = v2
                        tk.Label(self.frame, textvariable = v2, padx=10).grid(row=row_id+1+idy, column=col_id+2*len(inst_labels)-idx)
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
    
        for strat in self.app.agent.strategies:
            if strat.__class__.__name__ == 'DTTrader':
                self.strat_gui[strat.name] = DTStratGui(strat, app, self)
            elif strat.__class__.__name__ == 'RBreakerTrader':
                self.strat_gui[strat.name] = RBStratGui(strat, app, self)
            elif 'Opt' in strat.__class__.__name__:
                self.strat_gui[strat.name] = OptStratGui(strat, app, self)
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
        for strat in self.app.agent.strategies:
            name = strat.name
            self.strat_frame[name] = ttk.Frame(self)
            self.strat_gui[name].set_frame(self.strat_frame[name])
            self.notebook.add(self.strat_frame[name], text = name)
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
        setup_qrybtn = ttk.Button(lbl_frame, text='QueryInst', command= self.qry_agent_inst)
        setup_qrybtn.grid(column=2, row=row_idx, sticky="ew")
        row_idx +=1
        field = 'QryInst'
        lab = ttk.Label(lbl_frame, text= field, anchor='w')
        lab.grid(column=0, row=row_idx, sticky="ew")
        ent = tk.Entry(lbl_frame)
        ent.grid(column=0, row=row_idx+1, sticky="ew")
        self.entries[field] = ent
        ent.insert(0,"IF1503")
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
        self.app.reset_agent()

    def onExit(self):
        self.app.exit_agent()
        self.destroy()
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
        self.reset_agent(save_test)
                        
    def reset_agent(self, save_test):       
        if self.agent != None:
            self.scur_day = self.agent.scur_day
        all_insts= []
        for strat in self.strat_cfg['strategies']:
            all_insts = list(set(all_insts).union(set(strat.instIDs)))
        self.agent = fut_api.create_agent(self.name, self.user_cfg, self.trader_cfg, all_insts, self.strat_cfg, self.scur_day)
        #self.agent.logger.addHandler(self.text_handler)
        #fut_api.make_user(self.agent, self.user_cfg)
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
                res[field] = inst_dict
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
        for strat in self.agent.strategies:
            if strat.name == strat_name:
                for field in fields:
                    if field == 'Volgrid':
                        vol_info = {}
                        for idx, expiry in enumerate(strat.expiries):
                            if strat.spot_model:
                                under = strat.underlers[0]
                            else:
                                under = strat.underliers[idx]
                            vn = strat.volgrids[expiry]
                            vol_info[expiry] = {'Under': under, 'Df':strat.DFs[idx], 'Fwd': vn.fwd_(), 'Expiry': expiry,
                                                'Atm': vn.atmVol_(), 'V90': vn.d90Vol_(), 
                                                'V75': vn.d75Vol_(), 'V25': vn.d25Vol_(), 
                                                'V10': vn.d10Vol_(), 'Updated': strat.last_updated[expiry]['dtoday']}
                        params[field] = vol_info
                    elif (field == 'OptionMap') or (field == 'GroupRisk'):
                        var = field2variable(field)
                        value = getattr(strat, var)
                        params[field] = value.to_dict()
                    else:
                        var = field2variable(field)
                        params[field] = getattr(strat, var)
                break 
        return params
    
    def set_strat_params(self, strat_name, params):
        for strat in self.agent.strategies:
            if strat.name == strat_name:
                for field in params:
                    if field == 'Volgrid':
                        for expiry in strat.expiries:
                            strat.set_volgrids(expiry, params[field][expiry])
                    else:
                        var = field2variable(field)
                        value = params[field]
                        setattr(strat, var, value)
                break 
        return
    
    def run_strat_func(self, strat_name, func_name):
        for strat in self.agent.strategies:
            if strat.name == strat_name:
                getattr(strat, func_name)()
                break 
        return 
        
    def exit_agent(self):
        if self.agent != None:
            self.agent.mdapis = []
            self.agent.trader = None
        return

def main(tday, name='option_test'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = misc.TEST_TRADER
    user_cfg = misc.TEST_USER
    opt_strat = optstrat.IndexFutOptStrat(name, 
                                    ['IF1504', 'IF1506'], 
                                    [datetime.datetime(2015, 4, 17, 15, 0, 0), datetime.datetime(2015,6,19,15,0,0)],
                                    [[3400, 3450, 3500, 3550, 3600, 3650]]*2)
    insts_dt = ['IF1504']
    units_dt = [1]*len(insts_dt)
    under_dt = [[inst] for inst in insts_dt]
    vols_dt = [[1]]*len(insts_dt)
    lookbacks_dt = [0]*len(insts_dt)
    
    insts_daily = ['IF1504']
    under_daily = [[inst] for inst in insts_daily]
    vols_daily = [[1]]*len(insts_daily)
    units_daily = [1]*len(insts_daily)
    lookbacks_daily = [0]*len(insts_daily)

    dt_strat = strat_dt.DTTrader('DT_test', under_dt, vols_dt, trade_unit = units_dt, lookbacks = lookbacks_dt, agent = None, daily_close = False, email_notify = [])
    dt_daily = strat_dt.DTTrader('DT_Daily', under_daily, vols_daily, trade_unit = units_daily, lookbacks = lookbacks_daily, agent = None, daily_close = True, email_notify = ['harvey_wwu@hotmail.com'])
    
    strategies = [dt_strat, dt_daily, opt_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':3, \
                 'min_data_days':1 }
    
    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None)
    myGui = Gui(myApp)
    myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
    myGui.mainloop()
    
def m_opt_sim(tday, name='Soymeal_Opt'):
    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = misc.DCE_OPT_TRADER
    user_cfg = misc.DCE_OPT_USER
    opt_strat = optstrat.CommodOptStrat(name, 
                                    ['m1505', 'm1509', 'm1601'], 
                                    [datetime.datetime(2015, 4, 8, 15, 0, 0), 
                                     datetime.datetime(2015, 8, 7, 15, 0, 0), 
                                     datetime.datetime(2015, 12,7, 15, 0, 0)],
                                    [[2700 + 50 * i for i in range(7)], 
                                     [2600 + 50 * i for i in range(10)],
                                     [2500 + 50 * i for i in range(13)]])
    insts_dt = ['m1509']
    units_dt = [2]*len(insts_dt)
    under_dt = [[inst] for inst in insts_dt]
    vols_dt = [[1]]*len(insts_dt)
    lookbacks_dt = [0]*len(insts_dt)
    
    ins_setup = {'m1509': [[0.35, 0.07, 0.25], 2,  30]}
    insts_rb = ins_setup.keys()
    units_rb = [ins_setup[inst][1] for inst in insts_rb]
    under_rb = [[inst] for inst in insts_rb]
    vol_rb = [[1] for inst in insts_rb]
    ratios = [ins_setup[inst][0] for inst in insts_rb]
    min_rng = [ins_setup[inst][2] for inst in insts_rb]
    stop_loss = 0.0
    
    dt_strat = strat_dt.DTTrader('DT_test', under_dt, vols_dt, trade_unit = units_dt, lookbacks = lookbacks_dt, agent = None, daily_close = False, email_notify = [])
    rb_strat = strat_rb.RBreakerTrader('RBreaker', under_rb, vol_rb, trade_unit = units_rb,
                                 ratios = ratios, min_rng = min_rng, trail_loss = stop_loss, freq = 1, 
                                 agent = None, email_notify = [])
    strategies = [opt_strat, dt_strat, rb_strat]
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':3, \
                 'min_data_days':1 }
    
    myApp = MainApp(name, trader_cfg, user_cfg, strat_cfg, tday, master = None, save_test = True)
    myGui = Gui(myApp)
    myGui.iconbitmap(r'c:\Python27\DLLs\thumbs-up-emoticon.ico')
    myGui.mainloop()
    
if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        app_name = 'Soymeal_Opt'
    else:
        app_name = args[1]       
    if len(args) < 1:
        tday = datetime.date.today()
    else:
        tday = datetime.datetime.strptime(args[0], '%Y%m%d').date()

    m_opt_sim(tday, app_name)    
    
