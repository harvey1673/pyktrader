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
import datetime
import re

vtype_func_map = {'int':int, 'float':float, 'str': str, 'bool':bool }

def type2str(val, vtype):
    ret = val
    if vtype == 'bool':
        ret = '1' if val else '0'
    elif 'list' in vtype:
        ret = ','.join([str(r) for r in val])
    elif vtype == 'date':
        ret = val.strftime('%Y%m%d')
    elif vtype == 'datetime':
        ret = val.strftime('%Y%m%d %H:%M:%S')
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
                if field in self.entry_fields:
                    ent = self.entries[inst][field]
                    ent.delete(0, tk.END)
                    value = params[field][idx]
                    vtype = self.field_types[field]
                    value = type2str(value, vtype)
                    ent.insert(0, value)
                elif field in self.status_fields:
                    self.stringvars[inst][field].set(str(params[field][idx]))
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
                v = tk.StringVar()
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
        self.entry_fields = ['trade_unit', 'lookbacks', 'ratios', 'close_tday']
        self.status_fields = ['tday_open', 'cur_rng'] 
        self.field_types = {'trade_unit':'int', 
                            'lookbacks':'int', 
                            'ratios': 'floatlist', 
                            'close_tday': 'bool',
                            'tday_open': 'float', 
                            'cur_rng':'float' }
                        
class RBStratGui(StratGui):
    def __init__(self, strat, app, master):
        StratGui.__init__(self, strat, app)
        self.entry_fields = ['trade_unit', 'min_rng', 'ratios', 'close_tday', 'start_min_id']
        self.status_fields = ['sbreak', 'bsetup', 'benter', 'senter', 'ssetup', 'bbreak'] 
        self.field_types = {'trade_unit':'int', 
                            'min_rng':'float', 
                            'ratios': 'floatlist', 
                            'close_tday': 'bool',
                            'start_min_id': 'int',
                            'sbreak': 'float', 
                            'bbreak':'float',
                            'bsetup':'float', 
                            'benter':'float', 
                            'senter':'float', 
                            'ssetup':'float' }        
    
class OptStratGui(object):
    def __init__(self, strat, app, master):
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
        self.frame = None
        self.vsb = None
        self.vol_params = {}
        self.entries = {}
        self.stringvars = {'Inst':{}, 'Volgrid':{}}
        self.entry_fields = []
        self.status_fields = [] 
        self.field_types = {}

    def get_T_table(self):
        params = self.app.get_agent_params(['Inst'])
        inst_labels = ['name', 'price', 'bid_price1', 'bid_vol1','ask_price1']
        for inst in params['Inst']:
            if inst in self.stringvars['Inst']:
                for instlbl in inst_labels:
                    self.stringvars['Inst'][inst][instlbl].set(params['Inst'][inst][instlbl])
        vol_labels = ['expiry', 'under', 'DF', 'fwd', 'atm', 'v90', 'v75', 'v25', 'v10']
        params = self.app.get_strat_params(self.name, ['Volgrid'])
        for expiry in params['Volgrid']:
            if expiry in self.stringvars['Volgrid']:
                for instlbl in inst_labels:
                    self.stringvars['Inst'][inst][instlbl].set(params['Inst'][inst][instlbl]
        return
    
    def get_volgrids(self):
            
    def set_volgrids(self, params):
        pass
    
    def set_frame(self, root):
        self.canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame")
        self.frame.bind("<Configure>", self.OnFrameConfigure)
        self.populate()

    def populate(self):
        vol_labels = ['expiry', 'under', 'DF', 'fwd', 'atm', 'v90', 'v75', 'v25', 'v10']
        inst_labels = ['name', 'price', 'bid_price1', 'bid_vol1','ask_price1','ask_vol1','mPV']
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
                v = tk.StringVar()
                tk.Label(self.frame, textvariable = v).grid(row=row_id+1, column=col_id + idx)
                self.stringvars['Volgrid'][expiry][vlbl] = v
            row_id += 2
            col_id = 0
            for idx, instlbl in enumerate(inst_labels + ['strike']):
                tk.Label(self.frame, text=instlbl).grid(row=row_id, column=col_id + idx)
                if instlbl != 'strike':
                    tk.Label(self.frame, text=instlbl).grid(row=row_id, column=col_id + 2 * len(inst_labels) - idx)
                for idy, strike in enumerate(strikes):
                    if instlbl == 'strike':
                        tk.Label(self.frame, text = str(strike)).grid(row=row_id+idy, column=col_id + idx)
                    else:
                        key1 = (under, cont_mth, 'C', strike)
                        inst1 = self.opt_dict[key1]
                        if idx == 0:
                            self.stringvars[inst1] = {}
                        v1 = tk.StringVar()
                        tk.Label(self.frame, textvariable = v1).grid(row=row_id+idy, column=col_id + idx)
                        self.stringvars[inst1][instlbl] = v1
                        
                        key2 = (under, cont_mth, 'P', strike)
                        inst2 = self.opt_dict[key2]
                        if idx == 0:
                            self.stringvars[inst2] = {}
                        v2 = tk.StringVar()
                        tk.Label(self.frame, textvariable = v2).grid(row=row_id+idy, column=col_id + 2 * len(inst_labels) - idx)
                        self.stringvars[inst2][instlbl] = v2
            row_id = row_id + len(strikes) + 1
        self.get

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
        self.entries = {}
        self.stringvars = {}
        self.status_ents = {}
        self.strat_frame = {}
        self.strat_gui = {}
        self.setup_fields = ['MarketOrderTickMultiple', 'CancelProtectPeriod', 'MarginCap']
        self.status_fields = ['Positions', 'Orders', 'Trades', 'Insts', 'ScurDay', 'EodFlag', 'Initialized', 'ProcLock', \
                              'CurrCapital', 'PrevCapital', 'LockedMargin', 'UsedMargin', 'Available', 'PnlTotal']
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

    # def onStratNewWin(self, name):
        # strat_gui = self.strat_gui[name]
        # top_level = tk.Toplevel(self)
        # top_level.title('strategy: %s' % name)
        # strat_gui.start(top_level)
        # return 
    def market_view(self):
        pass

    def position_view(self):
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
            v = tk.StringVar()
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
            v1 = tk.StringVar()
            lab2 = ttk.Label(lbl_frame, textvariable = v1, anchor='w')
            self.stringvars[field1] = v1
            lab2.grid(column=1, row=row_idx, sticky="ew")

            lab3 = ttk.Label(lbl_frame, text=field2+": ", anchor='w')
            lab3.grid(column=2, row=row_idx, sticky="ew")
            v2 = tk.StringVar()
            lab4 = ttk.Label(lbl_frame, textvariable = v2, anchor='w')
            self.stringvars[field2] = v2
            lab4.grid(column=3, row=row_idx, sticky="ew")
            row_idx += 1      
        all_fields = entry_fields+label_fields+pnl_fields+margin_fields
        self.setup_setbtn = ttk.Button(lbl_frame, text='Set', command= lambda: self.set_agent_params(entry_fields))
        self.setup_setbtn.grid(column=0, row=row_idx, sticky="ew")
        #self.setup_setbtn.pack(side=tk.LEFT, padx=5, pady=5)
        self.setup_loadbtn = ttk.Button(lbl_frame, text='Load', command= lambda: self.get_agent_params(all_fields))
        self.setup_loadbtn.grid(column=2, row=row_idx, sticky="ew")
        #self.setup_loadbtn.pack(side=tk.LEFT, padx=5, pady=5)
        lbl_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.get_agent_params(all_fields)
    
    def set_agent_params(self, fields):
        params = {}
        for field in fields:
            ent = self.entries[field]
            value = ent.get()
            params[field] = value        
        self.app.set_agent_params(params)
        pass
    
    def get_agent_params(self, fields):
        params = self.app.get_agent_params(fields)
        for field in fields:
            if field in self.entries:
                ent = self.entries[field]
                ent.delete(0, tk.END)
                ent.insert(0, str(params[field]))
            elif field in self.stringvars:
                var = self.stringvars[field]
                var.set(str(params[field]))
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
    def __init__(self, name, trader_cfg, user_cfg, strat_cfg, tday, master = None):
        self.trader_cfg = trader_cfg
        self.user_cfg = user_cfg
        self.strat_cfg = strat_cfg
        self.scur_day = tday
        self.name = name
        self.agent = None
        self.master = master
        self.reset_agent()
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
                            'PnlTotal':'float'}
                            
    def reset_agent(self):       
        if self.agent != None:
            self.scur_day = self.agent.scur_day
        all_insts= []
        for strat in self.strat_cfg['strategies']:
            all_insts = list(set(all_insts).union(set(strat.instIDs)))
        self.agent = fut_api.create_agent(self.name, self.user_cfg, self.trader_cfg, all_insts, self.strat_cfg, self.scur_day)
        #self.agent.logger.addHandler(self.text_handler)
        #fut_api.make_user(self.agent, self.user_cfg)
        self.agent.resume()
        return
    
    def get_agent_params(self, fields):
        res = {}
        for f in fields:
            field_list = f.split('.')
            field = field_list[0]
            if field == 'Positions':
                positions = []
                for inst in self.agent.positions:
                    pos = self.agent.positions[inst]
                    positions.append([inst, pos.curr_pos.long, pos.curr_pos.short, self.locked_pos.long, self.locked_pos.short])
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
            elif field == 'Inst':
                if len(field_list) > 1:
                    insts = field_list[1:]
                else:
                    insts = self.agent.instruments.keys()
                inst_dict = {}
                for inst in insts:
                    inst_obj = self.agent.instruments[inst]
                    inst_dict[inst] = {'name': inst, 'price': inst_obj.price, 
                                 'bid_price1': inst_obj.bid_price1, 'bid_vol1': inst_obj.bid_vol1, 
                                 'ask_price1': inst_obj.ask_price1, 'ask_vol1': inst_obj.ask_vol1, 
                                 'prev_close': inst_obj.prev_close, 'marginrate': inst_obj.marginrate, 
                                 'updated': inst_obj.last_update, 'traded': inst_obj.last_traded}
                res[field] = inst_dict
            else:
                var = field2variable(field)
                value = getattr(self.agent, var)
                res[field] = type2str(value, value.__class__.__name__)
        return res

    def set_agent_params(self, params):
        for field in params:
            var = field2variable(field)
            value = params[field]
            if field in self.field_types:
                vtype = self.field_types[field]
                value = str2type(value, vtype)
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
                            vol_info[expiry] = {'under': under, 'DF':strat.DFs[idx], 'fwd': vn.fwd_(), 
                                                'atm': vn.atmVol_(), 'v90': vn.d90Vol_(), 
                                                'v75': vn.d75Vol_(), 'v25': vn.d25Vol_(), 
                                                'v10': vn.d10Vol_()}
                        params[field] = vol_info
                    else:
                        params[field] = getattr(strat, field)
                break 
        return params
    
    def set_strat_params(self, strat_name, params):
        for strat in self.agent.strategies:
            if strat.name == strat_name:
                for field in params:
                    if field == 'Volgrid':
                        for idx, expiry in enumerate(strat.expiries):
                            strat.set_volgrids(expiry, params[field][expiry])
                    else:
                        setattr(strat, field, params[field])
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
    
if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        app_name = 'option_test'
    else:
        app_name = args[1]       
    if len(args) < 1:
        tday = datetime.date.today()
    else:
        tday = datetime.datetime.strptime(args[0], '%Y%m%d').date()

    main(tday, app_name)    
    
