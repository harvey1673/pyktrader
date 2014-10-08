import mysql.connector
import mysqlaccess
import workdays
import datetime
import dateutil
import pandas as pd

month_code_map = {'f': 1,
                  'g': 2,
                  'h': 3,
                  'j': 4,
                  'k': 5,
                  'm': 6,
                  'n': 7,
                  'q': 8,
                  'u': 9,
                  'v': 10,
                  'x': 11,
                  'z': 12}
CHN_Holidays = [datetime.date(2014,1,1),  datetime.date(2014,1,2), datetime.date(2014,1,3), 
                datetime.date(2014,1,31), datetime.date(2014,2,3), datetime.date(2014,2,4),
                datetime.date(2014,2,5),  datetime.date(2014,2,6), datetime.date(2014,4,7),
                datetime.date(2014,5,1),  datetime.date(2014,5,2), datetime.date(2014,6,2),
                datetime.date(2014,9,8),  datetime.date(2014,10,1),datetime.date(2014,10,2),
                datetime.date(2014,10,3), datetime.date(2014,10,6),datetime.date(2014,10,7),
                datetime.date(2015,1,1),  datetime.date(2015,1,2), datetime.date(2015,2,19), 
                datetime.date(2015,2,20), datetime.date(2015,2,23),datetime.date(2015,2,24),
                datetime.date(2015,2,25), datetime.date(2015,4,6), datetime.date(2015,5,1),
                datetime.date(2015,6,22), datetime.date(2015,9,28),datetime.date(2015,10,1),
                datetime.date(2015,10,2), datetime.date(2015,10,5),datetime.date(2015,10,6),datetime.date(2015,10,7),
                datetime.date(2016,1,1),  datetime.date(2016,2,8), datetime.date(2016,2,9), 
                datetime.date(2016,2,10), datetime.date(2016,2,11),datetime.date(2016,2,12),
                datetime.date(2016,4,4),  datetime.date(2016,5,2), datetime.date(2016,6,9),
                datetime.date(2016,6,10), datetime.date(2016,9,15),datetime.date(2016,9,16),
                datetime.date(2016,10,3), datetime.date(2016,10,4),datetime.date(2016,10,5),
                datetime.date(2016,10,6), datetime.date(2016,10,7),
                datetime.date(2017,1,2),  datetime.date(2017,1,30),datetime.date(2017,1,31), 
                datetime.date(2017,2,1),  datetime.date(2017,2,2), datetime.date(2017,2,3),
                datetime.date(2017,4,5),  datetime.date(2017,5,1), datetime.date(2017,5,30),
                datetime.date(2017,10,2), datetime.date(2017,10,3),datetime.date(2017,10,4),
                datetime.date(2017,10,5), datetime.date(2017,10,6),
                datetime.date(2018,1,1),  datetime.date(2018,2,16),datetime.date(2018,2,19), 
                datetime.date(2018,2,20), datetime.date(2018,2,21),
                datetime.date(2018,4,5),  datetime.date(2018,5,1), datetime.date(2018,6,18),
                datetime.date(2018,9,24), datetime.date(2018,10,1),datetime.date(2018,10,2),
                datetime.date(2018,10,3), datetime.date(2018,10,4),datetime.date(2018,10,5)]        

product_code = {'SHFE':['cu', 'al', 'zn', 'pb', 'wr', 'rb', 'fu', 'ru', 'bu', 'hc', 'ag', 'au'], 
                'CFFEX': ['IF', 'TF', 'IO'],
                'DCE': ['c', 'j', 'jd', 'a', 'b', 'm', 'y', 'p', 'l', 'v', 'jm', 'i', 'fb', 'bb', 'pp'],
                'ZCE': ['WH', 'PM', 'CF', 'SR', 'TA', 'OI', 'RI', 'ME', 'FG', 'RS', 'RM', 'TC', 'JR', 'LR', 'MA', 'SM', 'SF'] }

night_session_markets = ['cu', 'al', 'zn', 'pb', 'ag','au']

product_lotsize = {'zn': 5, 
                   'cu': 5,
                   'ru': 10,
                   'rb': 10,
                   'fu': 50,
                   'al': 5,
                   'au': 1000,
                   'wr': 10, 
                   'pb': 25,
                   'ag': 15,
                   'bu': 10,
                   'hc': 10,
                   'WH': 20,
                   'PM': 50, 
                   'CF': 5,
                   'SR': 10,
                   'TA': 5,
                   'OI': 10,
                   'RI': 20,
                   'ME': 50,
                   'MA': 10,
                   'FG': 20,
                   'RS': 10,
                   'RM': 10,
                   'TC': 200, 
                   'JR': 20,
                   'LR': 20,
                   'SM': 5,
                   'SF': 5,
                   'c' : 10, 
                   'j' : 100,
                   'jd': 10,
                   'a' : 10,
                   'b' : 10,
                   'm' : 10,
                   'y' : 10,
                   'p' : 10,
                   'l' : 5,
                   'v' : 5, 
                   'jm': 60,
                   'i' : 100,
                   'fb': 500,
                   'bb': 500,
                   'pp': 5,
                   'IF': 300,
                   'TF': 10000,
                   'IO': 100
                   }

product_ticksize = {'zn': 5, 
                   'cu': 10,
                   'ru': 5,
                   'rb': 1,
                   'fu': 1,
                   'al': 5,
                   'au': 0.01,
                   'wr': 1, 
                   'pb': 5,
                   'ag': 1,
                   'bu': 2,
                   'hc': 2,
                   'WH': 1,
                   'PM': 1, 
                   'CF': 5,
                   'SR': 1,
                   'TA': 2,
                   'OI': 2,
                   'RI': 1,
                   'ME': 1,
                   'MA': 1,
                   'FG': 1,
                   'RS': 1,
                   'RM': 1,
                   'TC': 0.2, 
                   'JR': 1,
                   'LR': 1,
                   'SF': 2,
                   'SM': 2,
                   'c' : 1, 
                   'j' : 1,
                   'jd': 1,
                   'a' : 1,
                   'b' : 1,
                   'm' : 1,
                   'y' : 2,
                   'p' : 2,
                   'l' : 5,
                   'v' : 5, 
                   'jm': 1,
                   'i' : 1,
                   'fb': 0.05,
                   'bb': 0.05,
                   'pp': 1,
                   'IF': 0.2, 
                   'TF': 0.002,
                   'IO': 0.1
                   }

def inst2product(inst):
    if inst[1].isalpha():
        key = inst[:2]
    else:
        key = inst[:1]
    
    return key

def inst2exch(inst):
    key = inst2product(inst)
    for exch in product_code.keys():
        if key in product_code[exch]:
            return exch
    
    return 0

def inst_to_exch(inst):
    key = inst2product(inst)
    cnx = mysql.connector.connect(**mysqlaccess.dbconfig)
    cursor = cnx.cursor()
    stmt = "select exchange from trade_products where product_code='{prod}' ".format(prod=key)
    cursor.execute(stmt)
    out = [exchange for exchange in cursor]
    cnx.close()
    return str(out[0][0])

def nearby(prodcode, n, start_date, end_date, roll_rule, freq, need_shift=False):
    if start_date > end_date: 
        return None
    cnx = mysql.connector.connect(**mysqlaccess.dbconfig)
    cursor = cnx.cursor()
    stmt = "select exchange, contract from trade_products where product_code='{prod}' ".format(prod=prodcode)
    cursor.execute(stmt)
    out = [(exchange, contract) for (exchange, contract) in cursor]
    exch = str(out[0][0])
    cont = str(out[0][1])
    cont_mth = [month_code_map[c] for c in cont]
    cnx.close()  
    contlist = contract_range(prodcode, exch, cont_mth, start_date, end_date)
    exp_dates = [day_shift(contract_expiry(cont), roll_rule) for cont in contlist]
    #print contlist, exp_dates
    sdate = start_date
    is_new = True
    for idx, exp in enumerate(exp_dates):
        if exp < start_date:
            continue
        elif sdate > end_date:
            break
        nb_cont = contlist[idx+n-1]
        if freq == 'd':
            new_df = mysqlaccess.load_daily_data_to_df('fut_daily', nb_cont, sdate, min(exp,end_date))
        else:
            new_df = mysqlaccess.load_min_data_to_df('fut_min', nb_cont, sdate, min(exp,end_date))    

		nn = new_df.shape[0]
        if nn > 0:
            new_df['contract'] = pd.Series([nb_cont]*nn, index=new_df.index)
        if is_new:
            df = new_df
            is_new = False
        else:
			if need_shift:
				last_date = df.index[-1].date()
				tmp_df = load_daily_data_to_df('fut_daily', nb_cont, last_date, last_date)
				shift = tmp_df['close'][-1] - df['close'][-1]
				for ticker in ['open','high','low','close']:
					df[ticker] = df[ticker] + shift
			df = df.append(new_df)
        sdate = min(exp,end_date) + datetime.timedelta(days=1)
    return df        

def rolling_hist_data(product, n, start_date, end_date, cont_roll, freq, win_roll= '-20b'):
    if start_date > end_date: 
        return None
    cnx = mysql.connector.connect(**mysqlaccess.dbconfig)
    cursor = cnx.cursor()
    stmt = "select exchange, contract from trade_products where product_code='{prod}' ".format(prod=product)
    cursor.execute(stmt)
    out = [(exchange, contract) for (exchange, contract) in cursor]
    exch = str(out[0][0])
    cont = str(out[0][1])
    cont_mth = [month_code_map[c] for c in cont]
    cnx.close()  
    contlist = contract_range(product, exch, cont_mth, start_date, end_date)
    exp_dates = [day_shift(contract_expiry(cont), cont_roll) for cont in contlist]
    #print contlist, exp_dates
    sdate = start_date
    all_data = {}
    i = 0
    for idx, exp in enumerate(exp_dates):
        if exp < start_date:
            continue
        elif sdate > end_date:
            break
        nb_cont = contlist[idx+n-1]
        if freq == 'd':
            df = mysqlaccess.load_daily_data_to_df('fut_daily', nb_cont, sdate, min(exp,end_date))
        else:
            df = mysqlaccess.load_min_data_to_df('fut_min', nb_cont, sdate, min(exp,end_date))    
        all_data[i] = {'contract': nb_cont, 'data': df}
        i += 1
        sdate = day_shift(min(exp,end_date), win_roll)
    return all_data    
    
def day_shift(d, roll_rule):
    if 'b' in roll_rule:
        days = int(roll_rule[:-1])
        shft_day = workdays.workday(d,days)
    elif 'm' in roll_rule:
        mths = int(roll_rule[:-1])
        shft_day = d + dateutil.relativedelta.relativedelta(months = mths)
    elif 'd' in roll_rule:
        days = int(roll_rule[:-1])
        shft_day = d + datetime.timedelta(days = days)        
    return shft_day

def contract_expiry(cont, hols='db'):
    if type(hols) == list:
        exch = inst_to_exch(cont)
        mth = int(cont[-2:])
        if cont[-4:-2].isdigit():
            yr = 2000 + int(cont[-4:-2])
        else:
            yr = 2010 + int(cont[-3:-2])
        cont_date = datetime.date(yr,mth,1)
        if exch == 'DCE' or exch == 'ZCE':
            expiry = workdays.workday(cont_date - datetime.timedelta(days=1), 10, CHN_Holidays)
        elif exch =='CFFEX':   
            wkday = cont_date.weekday()
            expiry = cont_date + datetime.timedelta(days=13+(11-wkday)%7)
            expiry = workdays.workday(expiry, 1, CHN_Holidays)
        elif exch == 'SHFE':
            expiry = datetime.date(yr, mth, 14)
            expiry = workdays.workday(expiry, 1, CHN_Holidays)
        else:
            expiry = 0
    else:
        cnx = mysql.connector.connect(**mysqlaccess.dbconfig)
        cursor = cnx.cursor()
        stmt = "select expiry from contract_list where instID='{inst}' ".format(inst=cont)
        cursor.execute(stmt)
        out = [exp for exp in cursor]
        if len(out)>0:
            expiry = out[0][0]
        else:
            expiry = contract_expiry(cont, CHN_Holidays)
    return expiry
        
def contract_range(product, exch, cont_mth, start_date, end_date):
    st_year  = start_date.year
    cont_list = []
    for yr in range(st_year, end_date.year+2):
        for mth in range(1,13):
            if (mth in cont_mth):
                if (datetime.date(yr,mth,28) > start_date) and (datetime.date(yr-1,mth,1) <= end_date):
                    if exch == 'ZCE' and datetime.date(yr,mth,1) < datetime.date(2014,9,30):
                        contLabel = product + "%01d" %(yr%10) + "%02d" % mth
                    else:
                        contLabel = product + "%02d" %(yr%100) + "%02d" % mth
                    
                    cont_list.append(contLabel)
    return cont_list
