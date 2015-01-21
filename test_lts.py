import lts_api 
import logging
import datetime
from agent import *
from misc import *

def test_main(tday=datetime.date.today()):
    logging.basicConfig(filename="test_lts_agent.log",level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    app_name = 'lts_agent'
    insts = ['510050', '510050C1502M02500', '510050P1502M02500']
    strategies = []
    trader_cfg = LTS_SO_TRADER
    user_cfg = LTS_SO_USER
    strat_cfg = {'strategies': strategies, \
                 'folder': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\', \
                 'daily_data_days':0, \
                 'min_data_days':0 }
    myagent = lts_api.create_agent(app_name, user_cfg, trader_cfg, insts, strat_cfg, tday)
    try:
        myagent.resume()
    except KeyboardInterrupt:
        myagent.mdapis = []; myagent.trader = None

if __name__=="__main__":
    test_main()