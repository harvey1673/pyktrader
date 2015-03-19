import agent
import fut_api
#import lts_api
import logging
import misc
import Tkinter as tk
import ScrolledText
import sys
import optstrat
import strat_dual_thrust as strat_dt
import datetime

class GuiDTTrader(object):
	def __init__(self, strat):
		self.master = None
		self.lblframe = None
		self.name = strat.name
		self.underliers = strat.underliers
		self.trade_units = strat.trade_unit
		self.ratios = strat.ratios
		self.lookbacks = strat.lookbacks
		self.cur_rng = strat.cur_rng
		self.tday_open = strat.tday_open
		self.close_tday = strat.close_tday
		self.daily_close_buffer = strat_daily_close_buffer
		self.email_notify = strat.email_notify
		self.entries = {}
		self.stringvars = {}
		self.entry_fields = ['trade_units', 'lookbacks', 'ratios', 'close_tday']
		self.status_fields = ['tday_open', 'cur_rng'] 
		
	def get_params(self):
		fields = self.entry_fields + self.status_fields
        params = self.app.get_strat_params(self.name, fields)
        for field in self.fields:
			for idx, underlier in enumerate(self.underliers):
				inst = underlier[0]
				if field in self.entry_fields:
					ent = self.entries[inst][field]
					ent.delete(0, tk.END)
					value = params[field][idx]
					if field == 'close_tday':
						value = 1 if value else 0
					elif field == 'ratios':
						value = ','.join([str(r) for r in value])
					ent.insert(0, str(value))
				elif field in self.status_fields:
					self.stringvars[inst][field].set(str(params[field][idx])
        return
		
	def set_params(self):
        params = {}
		for field in self.entry_fields:
			params[field] = []
			for underlier in self.underliers:
				inst = underlier[0]
				ent = self.entries[field]
				value = ent.get()
				if field == 'close_tday':
					value = True if int(value)>0 else False
				elif field == 'ratios':
					value = tuple(value.split(','))
				params[field].append(value)
        self.app.set_strat_params(self.name, params)
		return
		
	def start(self, root):
		self.master = root
		self.lblframe = tk.LabelFrame(root)
		self.lblframe.grid_columnconfigure(1, weight=1)
		fields = ['inst'] + self.entry_fields + self.status_fields
		for idx, field in enumerate(fields):
			lab = tk.Label(self.lblframe, text = field, anchor='w').grid(row=0, column=idx, sticky="ew")
		row_id = 1
		entries = {}
		stringvars = {}
        for underlier in self.underliers:
			inst = str(underlier[0])
			inst_lbl = tk.Label(self.lblframe, text=inst, anchor="w").grid(row=row_id, column=0, sticky="ew")
			col_id = 1
			entries[inst] = {}
            for idx, field in enumerate(self.entry_fields):
				ent = tk.Entry(self.lblframe).grid(row=row_id, column=col_id+idx, sticky="ew")
				ent.insert(0, "0")
				entries[inst][field] = ent
			col_id += len(self.entry_fields)
			stringvars[inst] = {}
			for idx, field in enumerate(self.status_fields):
				v = tk.StringVar()
				v.set('0')
				lab = tk.Label(self.lblframe, textvariable = v, anchor='w').grid(row=row_id, column=col_id+idx, sticky="ew")
				stringvars[inst][field] = v
			row_id +=1
		self.entries = entries
		self.stringvars = stringvars
		self.lblframe.pack(side="top", fill="both", expand=True, padx=10, pady=10)		
		set_btn = tk.Button(self.lblframe, text='Set', command=self.set_params).pack()
		refresh_btn = tk.Button(self.lblframe, text='Refresh', command=self.get_params).pack()
		recalc_btn = tk.Button(self.lblframe, text='Recalc', command=self.recalc).pack()
	
	def recalc(self):
		self.app.run_strat_func(self.name, 'initialize')
		
class GuiRBTrader(object):
	def __init__(self, strat):

class GuiOptionTrader(object):
	def __init__(self, strat):
	
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
        self.setup_win = None
        self.setup_app = None
        self.status_win = None
        self.status_app = None
        self.setup_ents = {}
        self.status_ents = {}
		self.strat_func = {}
		self.strat_status_gui = {}
		for strat in self.app.agent.strategies:
			if strat.__class__.__name__ == 'DTTrader':
				self.strat_status_gui[strat.name] = GuiDTTrader(strat)
			elif strat.__class__.__name__ == 'RBreakerTrader':
				self.strat_status_gui[strat.name] = GuiRBTrader(strat)
			elif 'Opt' in strat.__class__.__name__:
				self.strat_status_gui[strat.name] = GuiOptionTrader(strat)
        menu = tk.Menu(self)
        menu.add_command(label="Settings", command=self.onSetup)
        menu.add_command(label="Status", command=self.onStatus)
        stratmenu = tk.Menu(menu)
        menu.add_cascade(label="Strategies", menu=stratmenu)
        for strat in self.app.agent.strategies:
            stratmenu.add_command(label = strat.name, command=(lambda name = strat.name: self.onStratNewWin(name)))
        menu.add_command(label="Reset", command=self.onReset)
        menu.add_command(label="Exit", command=self.onExit)
        self.config(menu=menu)
        self.setup_fields = ['MarketOrderTickMultiple', 'CancelProtectPeriod', 'MarginCap']
        self.status_fields = ['Positions', 'Orders', 'Trades', 'Insts', 'CurrDay', 'EOD', 'Initialized', 'AgentStatus', \
                              'CurrCapital', 'PrevCapital', 'LockedMargin', 'UsedMargin', 'Avail', 'PNL']

    def onStratNewWin(self, name):
		strat_gui = self.strat_status_gui[name]
		top_level = tk.Toplevel(self)
		strat_gui.start(top_level)
		return 
		
	def onSetup(self):
        self.setup_win = tk.Toplevel(self)
        self.setup_ents = self.make_setup_form(self.setup_win, self.setup_fields)
        #self.setup_win.bind('<Return>', self.set_agent_params)
        self.setup_setbtn = tk.Button(self.setup_win, text='Set', command=self.set_agent_params)
        self.setup_setbtn.pack(side=tk.LEFT, padx=5, pady=5)
        self.setup_loadbtn = tk.Button(self.setup_win, text='Load', command=self.get_agent_params)
        self.setup_loadbtn.pack(side=tk.LEFT, padx=5, pady=5)
        self.get_agent_params()
    
    def set_agent_params(self):
        params = {}
        for field in self.setup_fields:
            ent = self.setup_ents[field]
            value = ent.get()
            params[field] = value        
        self.app.set_agent_params(params)
        pass
    
    def get_agent_params(self):
        params = self.app.get_agent_params(self.setup_fields)
        for field in self.setup_fields:
            ent = self.setup_ents[field]
            ent.delete(0, tk.END)
            ent.insert(0, str(params[field]))
        return

#    def fetch(self, entries):
#        for entry in entries:
#            field = entry[0]
#            text  = entry[1].get()
#            print('%s: "%s"' % (field, text)) 
          
    def make_setup_form(self, root, fields):
        entries = {}
        for field in fields:
            row = tk.Frame(root)
            lab = tk.Label(row, width=22, text=field+": ", anchor='w')
            ent = tk.Entry(row)
            ent.insert(0,"0")
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            entries[field] = ent
        return entries
        
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
        for field in fields:
            if field == 'MarketOrderTickMultiple':
                res[field] = self.agent.market_order_tick_multiple
            elif field == 'CancelProtectPeriod':
                res[field] = self.agent.cancel_protect_period
            elif field == 'MarginCap':
                res[field] = self.agent.margin_cap
            elif field == 'PNL':
                res[field] = self.agent.pnl_total
            elif field == 'Avail':
                res[field] = self.agent.available
            elif field == 'UsedMargin':
                res[field] = self.agent.used_margin
            elif field == 'LockedMargin':
                res[field] = self.agent.locked_margin                
            elif field == 'PrevCapital':
                res[field] = self.agent.prev_capital
            elif field == 'CurrCapital':
                res[field] = self.agent.curr_capital
            elif field == 'AgentStatus':
                res[field] = 0 if self.agent.proc_lock else 1
            elif field == 'Initialized':
                res[field] = 1 if self.agent.initialized else 0
            elif field == 'EOD':
                res[field] = 1 if self.agent.eod_flag else 0
            elif field == 'CurrDay':
                res[field] = self.agent.scur_day
            elif field == 'Positions':
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
            elif field == 'Insts':
                inst_list = []
                for inst in self.agent.instruments:
                    inst_obj = self.agent.instruments[inst]
                    inst_list.append([inst, inst_obj.price, inst_obj.bid_price1, inst_obj.bid_vol1, 
                                      inst_obj.ask_price1, inst_obj.ask_vol1, inst_obj.prev_close, 
                                      inst_obj.marginrate, inst_obj.last_update, inst_obj.last_traded])
                res[field] = inst_list
        return res

    def set_agent_params(self, params):
        for field in params:
            if field == 'MarketOrderTickMultiple':
                self.agent.market_order_tick_multiple = float(params[field])
            elif field == 'MarketOrderTickMultiple':
                self.agent.cancel_protect_period = int(params[field])
            elif field == 'MarginCap':
                self.agent.margin_cap = float(params[field])
        return
    
	def get_strat_params(self, strat_name, fields):
		params = {}
		for strat in self.agent.strategies:
			if strat.name == strat_name:
				for field in fields:
					params[field] = getattr(strat, field)
				break 
		return params
	
	def set_strat_params(self, strat_name, params):
		for strat in self.agent.strategies:
			if strat.name == strat_name:
				for field in params:
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
                                    ['IF1503', 'IF1506'], 
                                    [datetime.datetime(2015, 3, 20, 15, 0, 0), datetime.datetime(2015,6,19,15,0,0)],
                                    [[3400, 3450, 3500, 3550, 3600, 3650]]*2)
    insts_dt = ['IF1503']
    units_dt = [1]*len(insts_dt)
    under_dt = [[inst] for inst in insts_dt]
    vols_dt = [[1]]*len(insts_dt)
    lookbacks_dt = [0]*len(insts_dt)
    
    insts_daily = ['IF1503']
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
