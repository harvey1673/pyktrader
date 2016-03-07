import order 
import agent
import misc
import csv

def get_eod_positions(logfile):
    capital = 0.0;
    pos = {}
    with open(logfile, 'rb') as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            if row[0] == 'capital':
                capital = float(row[1])
            elif row[0] == 'pos':
                inst = row[1]
                plong = int(row[2])
                pshort = int(row[3])
                pclose = float(row[4])
                pos[inst] = {'long': plong, 'short':pshort, 'close':pclose}            
    return (capital, pos)

def check_pnl(log_folder, sdate, edate):
    logfile = log_folder + 'EOD_Pos_' + sdate.strftime('%y%m%d')+'.csv'    
    (s_capital, s_pos) = get_eod_positions(logfile)
    logfile = log_folder + 'EOD_Pos_' + edate.strftime('%y%m%d')+'.csv'    
    (e_capital, e_pos) = get_eod_positions(logfile)
    instruments = agent.Instrument.create_instruments(s_pos.keys())
    positions = dict([(inst, order.Position(instruments[inst])) for inst in s_pos])
    order_list = order.load_order_list(edate, log_folder, positions)
    pnl_tday = 0.0
    pnl_yday = [(s_pos[inst]['long'] - s_pos[inst]['short'])*(e_pos[inst]['close']-s_pos[inst]['close'])*instruments[inst].multiple for inst in s_pos]
    print sum(pnl_yday), pnl_yday
    for o in order_list.values():
        v = o.filled_volume
        inst = o.position.instrument.name
        if o.direction == misc.ORDER_SELL:
            v = -v
        pnl_tday += v * (e_pos[inst]['close'] - o.filled_price) * instruments[inst].multiple
    print pnl_tday

        