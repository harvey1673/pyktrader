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
        
def filter_main_cont(sdate):
    insts, prods  = mysqlaccess.load_alive_cont(sdate)
    main_cont = {}
    for pc in prods:
        main_cont[pc], exch = mysqlaccess.prod_main_cont_exch(pc)
    main_insts = []
    for inst in insts:
        pc = misc.inst2product(inst)
        mth = int(inst[-2:])
        if mth in main_cont[pc]:
            main_insts.append(inst)
    return main_insts 

class MainApp(object):
    def __init__(self,name='SaveAgent', tday = datetime.date.today()):
        self.name = name        
        app = self.app = tk.Tk()
        app.title("Save Data Tool")
        self.scroll_text = ScrolledText.ScrolledText(self.app, state='disabled')
        self.scroll_text.configure(font='TkFixedFont')
        # Create textLogger
        self.text_handler = TextHandler(self.scroll_text)
        self.scroll_text.pack()
        self.agent = None
        self.trader = None
        self.user = None
        self.scur_day = tday
        menu = tk.Menu(self.app)
        menu.add_command(label="Update contracts", command=self.onUpdateCont)
        menu.add_command(label="Restart agent", command=self.onRestart)
        menu.add_command(label="Exit", command=self.onExit)
        app.config(menu=menu)

    def onUpdateCont(self):
        t = threading.Thread(target=update_contract_table.main)
        t.start()

    def onRestart(self):
        if self.agent != None:
            self.scur_day = self.agent.scur_day
        save_insts = filter_main_cont(self.scur_day)
        self.agent = agent.SaveAgent(name = self.name, trader = None, cuser = None, instruments=save_insts, daily_data_days=0, min_data_days=0, tday = tday)
        self.agent.logger.addHandler(self.text_handler)
        fut_api.make_user(self.agent, misc.PROD_USER)
        return
    
    def onExit(self):
        if self.agent != None:
            self.agent.mdapis = []
            self.agent.trader = None
        self.app.destroy()
        return
        
def main(app_name, tday):
    logging.basicConfig(filename="save_all_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    m=MainApp(app_name, tday)
    m.app.mainloop()        
        
if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        tday = datetime.date.today()
    else:
        tday = datetime.datetime.strptime(args[1], '%Y%m%d').date()
    if len(args) < 1:
        app_name = 'SaveAgent'
    else:
        app_name = args[0]    
    main(app_name, tday)