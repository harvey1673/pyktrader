from datetime import *
CHN_Holidays = [date(2014,1,1),  date(2014,1,2), date(2014,1,3), 
                date(2014,1,31), date(2014,2,3), date(2014,2,4),
                date(2014,2,5),  date(2014,2,6), date(2014,4,7),
                date(2014,5,1),  date(2014,5,2), date(2014,6,2),
                date(2014,9,8),  date(2014,10,1),date(2014,10,2),
                date(2014,10,3), date(2014,10,6),date(2014,10,7),
                date(2015,1,1),  date(2015,1,2), date(2015,2,19), 
                date(2015,2,20), date(2015,2,23),date(2015,2,24),
                date(2015,2,25), date(2015,4,6), date(2015,5,1),
                date(2015,6,22), date(2015,9,28),date(2015,10,1),
                date(2015,10,2), date(2015,10,5),date(2015,10,6),date(2015,10,7),
                date(2016,1,1),  date(2016,2,8), date(2016,2,9), 
                date(2016,2,10), date(2016,2,11),date(2016,2,12),
                date(2016,4,4),  date(2016,5,2), date(2016,6,9),
                date(2016,6,10), date(2016,9,15),date(2016,9,16),
                date(2016,10,3), date(2016,10,4),date(2016,10,5),
                date(2016,10,6), date(2016,10,7),
                date(2017,1,2),  date(2017,1,30),date(2017,1,31), 
                date(2017,2,1),  date(2017,2,2), date(2017,2,3),
                date(2017,4,5),  date(2017,5,1), date(2017,5,30),
                date(2017,10,2), date(2017,10,3),date(2017,10,4),
                date(2017,10,5), date(2017,10,6),
                date(2018,1,1),  date(2018,2,16),date(2018,2,19), 
                date(2018,2,20), date(2018,2,21),
                date(2018,4,5),  date(2018,5,1), date(2018,6,18),
                date(2018,9,24), date(2018,10,1),date(2018,10,2),
                date(2018,10,3), date(2018,10,4),date(2018,10,5)]        

product_code = {'SHFE':['cu', 'al', 'zn', 'pb', 'wr', 'rb', 'fu', 'ru', 'bu', 'hc', 'ag', 'au'], 
                'CFFEX': ['IF', 'TF', 'IO'],
                'DCE': ['c', 'j', 'jd', 'a', 'b', 'm', 'y', 'p', 'l', 'v', 'jm', 'i', 'fb', 'bb', 'pp'],
                'ZCE': ['WH', 'PM', 'CF', 'SR', 'TA', 'OI', 'RI', 'ME', 'FG', 'RS', 'RM', 'TC', 'JR'] }

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
                   'FG': 20,
                   'RS': 10,
                   'RM': 10,
                   'TC': 200, 
                   'JR': 20,
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
                   'FG': 1,
                   'RS': 1,
                   'RM': 1,
                   'TC': 0.2, 
                   'JR': 1,
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
