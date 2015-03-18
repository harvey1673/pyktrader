import agent as agent
import fut_api
#import lts_api
import logging
import mysqlaccess
import misc
import Tkinter as tk
import threading
import ScrolledText
import sys
import datetime

class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text
 
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)
		
class Gui(tk.Tk):
    def __init__(self, app):
		tk.Tk.__init__(self)       
        self.title(app.name)
        self.app = app
        self.scroll_text = ScrolledText.ScrolledText(self, state='disabled')
        self.scroll_text.configure(font='TkFixedFont')
        # Create textLogger
        self.text_handler = TextHandler(self.scroll_text)
        self.scroll_text.pack()
        self.setup_win = None
        self.setup_app = None
        self.status_win = None
        self.status_app = None
		self.setup_ents = {}
		self.status_ents = {}
        menu = tk.Menu(self)
        menu.add_command(label="Agent Settings", command=self.onSetup)
        menu.add_command(label="Agent Status", command=self.onStatus)
        stratmenu = tk.Menu(menu)
        menu.add_cascade(label="Strategies", menu=stratmenu)
        for strat in self.app.agent.strategies:
            stratmenu.add_command(label = strat.name, command=self.app.strat_func[strat.name])
        menu.add_command(label="Reset agent", command=self.onReset)
        menu.add_command(label="Exit", command=self.app.onExit)
        self.config(menu=menu)
		self.setup_fields = ['MarketOrderTickMultiple', 'CancelProtectPeriod', 'MarginCap']
		self.status_fields = ['Positions', 'Orders', 'Trades', 'Insts', 'CurrDay', 'EOD', 'Initialized', 'AgentStatus', \
							  'CurrCapital', 'PrevCapital', 'LockedMargin', 'UsedMargin', 'Avail', 'PNL']

    def onSetup(self):
        self.setup_win = tk.Toplevel(self)
        self.setup_ents = self.make_setup_form(self.setup_win, self.setup_fields)
		self.setup_win.bind('<Return>', (lambda event, e=self.setup_ents: fetch(e)))
		self.setup_setbtn = tk.Button(self.setup_win, text='Set', command=self.set_agent_params)
		self.setup_setbtn.pack(side=tk.LEFT, padx=5, pady=5)
		self.setup_loadbtn = tk.Button(self.setup_win, text='Load', command=self.get_agent_params)
		self.setup_loadbtn.pack(side=tk.LEFT, padx=5, pady=5)
    
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
			ent.insert(0, str(params[fields]))
		return
	
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
	def __init__(self, name, trader_cfg, user_cfg, strat_cfg, master = None):
		self.trader_cfg = trader_cfg
		self.user_cfg = user_cfg
		self.strat_cfg = strat_cfg
		self.name = name
		self.agent = None
        self.master = master
    
	def reset_agent(self):       
        if self.agent != None:
            self.scur_day = self.agent.scur_day
        self.agent = agent.SaveAgent(name = self.name, trader = None, cuser = None, instruments=save_insts, daily_data_days=0, min_data_days=0, tday = tday)
        self.agent.logger.addHandler(self.text_handler)
        fut_api.make_user(self.agent, misc.PROD_USER)
        return
	
	def get_agent_params(self, fields):
		res = {}
		for field in fields:
			if field == 'MarketOrderTickMultiple':
				res[field] = self.agent.market_order_tick_multiple
			elif field == 'MarketOrderTickMultiple':
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
								
	def setup_agent(self, status):
        pass
    
    def exit_agent(self):
        if self.agent != None:
            self.agent.mdapis = []
            self.agent.trader = None
		return

def restart(tday, name='option_test'):

    logging.basicConfig(filename="ctp_" + name + ".log",level=logging.DEBUG,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    trader_cfg = TEST_TRADER
    user_cfg = TEST_USER
    agent_name = name
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
    all_insts = opt_strat.instIDs
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':3, \
                 'min_data_days':1 }
    #myagent, my_trader = emulator.create_agent_with_mocktrader(agent_name, all_insts, strat_cfg, tday)
    myagent = fut_api.create_agent(agent_name, user_cfg, trader_cfg, all_insts, strat_cfg, tday)
    #fut_api.make_user(myagent,user_cfg)
    myagent.resume()
    
