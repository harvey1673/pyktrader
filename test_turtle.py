import misc
import data_handler as dh
import pandas as pd

	
def turtle_sim( assets, start_date, end_date ):
	NN = 2
	data = {}
	for pc in assets:
		data[pc] = misc.rolling_hist_data(pc, 1, start_date, end_date, '-20b', 'd', '-55b')
		for i in range(len(data[pc]):
			df = data[pc][i]['data']
            cont = data[pc][i]['contract']
            expiry = df.index[-1].date()
			ts = dh.ATR(df, n=20)
			df.join(ts)
			ts = dh.DONCH(df, 55):
			df.join(ts)
			ts = dh.DONCH(df, 20)
			df.join(ts)
			ts = dh.DONCH(df, 10)
			df.join(ts)
            df['new_price']=pd.Series()
            df['new_pos']=pd.Series()
            df['pos'] = pd.Series()
			df['exit'] = pd.Series()
            df['OL_1'] = pd.concat([df.DONCH_H20.shift(1), df.open], join='outer', axis=1).max(axis=1)
            df['OS_1'] = pd.concat([df.DONCH_L20.shift(1), df.open], join='outer', axis=1).min(axis=1)
            df['CL_1'] = pd.concat([df.DONCH_L10.shift(1), df.open], join='outer', axis=1).min(axis=1)
            df['CS_1'] = pd.concat([df.DONCH_H10.shift(1), df.open], join='outer', axis=1).max(axis=1)
            #df['OL_2'] = pd.concat([df.DONCH_H55.shift(1), df.open], join='outer', axis=1).max(axis=1)
            #df['OS_2'] = pd.concat([df.DONCH_L55.shift(1), df.open], join='outer', axis=1).min(axis=1)
            #df['CL_2'] = pd.concat([df.DONCH_L20.shift(1), df.open], join='outer', axis=1).min(axis=1)
            #df['CS_2'] = pd.concat([df.DONCH_H20.shift(1), df.open], join='outer', axis=1).max(axis=1)
			curr_pos = []
			for idx, dd in enumerate(df.index):
                u = df[dd]
                if idx >0:
                    if last_pos == 0:
                        if u.high > u.OL_1:
                            n_unit = min(max(int((u.high - u.OL_1)*2.0/u.ATR_20 + 1),0),4)
							direction = 1
						elif u.low > u.OS_1:
							n_unit = min(max(int((u.OS_1 - u.low) *2.0/u.ATR_20 + 1),0),4)
							direction = -1
						u.new_pos = n_unit * direction
						last_pos = n_unit * direction
						if n_unit > 0:
							u.new_price = u.OL_1 + direction*(n_unit-1)/4 * u.ATR_20
							u.exit = u.OL_1 + direction * (n_unit-1)*u.ATR_20/2 - direction * u.ATR_20 * NN
							curr_pos.append((direction, n_unit, u.new_price, u.exit))
					else:
						
				
								
                        
                else:
                    u.pos = 0
                last_pos = u.pos
                    
                
		
