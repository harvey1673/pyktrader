import agent as agent
import fut_api
#import lts_api
import logging
import mysqlaccess
import misc
import Tkinter as tk
import threading
import ScrolledText
import update_contract_table
import sys
import datetime
import threading

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

    def onSetup(self):
        self.setup_win = tk.Toplevel(self)
        self.setup_app = SetupGui(self.setup_win)
    
    def onStatus(self):
        self.status_win = tk.Toplevel(self)
        self.status_app = StatusGui(self.status_win)        
        
    def onReset(self):
        self.app.reset_agent()

    def onExit(self):
        self.app.exit_agent()
        self.destroy()
        return

class SetupGui(object):
    def __init__(self, master):
        self.master = master
        
class StatusGui(object):
    def __init__(self, master):
        self.master = master
        
class MainApp(object):
	def __init__(self, name, trader_cfg, user_cfg, strat_cfg, master = None):
		self.trader_cfg = trader_cfg
		self.user_cfg = user_cfg
		self.name = name
		self.agent = None
		self.trader = None
		self.user= None
        self.master = master
        self.reset_agent()
        
	def reset_agent(self):       
        if self.agent != None:
            self.scur_day = self.agent.scur_day
        self.agent = agent.SaveAgent(name = self.name, trader = None, cuser = None, instruments=save_insts, daily_data_days=0, min_data_days=0, tday = tday)
        self.agent.logger.addHandler(self.text_handler)
        fut_api.make_user(self.agent, misc.PROD_USER)
        return
	
	def setup_agent(self):
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
    
