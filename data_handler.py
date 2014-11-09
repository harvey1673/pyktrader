import datetime
import pandas as pd

def conv_ohlc_freq(df, freq):
    highcol = pd.DataFrame(df['high']).resample(freq, how ='max').dropna()
    lowcol  = pd.DataFrame(df['low']).resample(freq, how ='min').dropna()
    opencol = pd.DataFrame(df['open']).resample(freq, how ='first').dropna()
    closecol= pd.DataFrame(df['close']).resample(freq, how ='last').dropna()
    allcol = [opencol, highcol, lowcol, closecol]
    if 'volume' in df.columns:
        volcol  = pd.DataFrame(df['volume']).resample(freq, how ='sum').dropna()
        allcol.append(volcol)
    if 'min_id' in df.columns:
        mincol  = pd.DataFrame(df['min_id']).resample(freq, how ='first').dropna()
        allcol.append(mincol)
    res =  pd.concat(allcol, join='outer', axis =1)
    return res

def TR(df):
    tr_df = pd.concat([df['high'] - df['close'], abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))], join='outer', axis=1)
    ts_tr = pd.Series(tr_df.max(1), name='TR')
    return ts_tr

def tr(df):
    df.ix[-1,'TR'] = max(df.ix[-1,'high'],df.ix[-2,'close']) - min(df.ix[-1,'low'],df.ix[-2,'close'])
    
def ATR(df, n = 20):
    tr = TR(df)
    ts_atr = pd.ewma(tr, span=n,  min_periods = n-1)
    ts_atr.name = 'ATR_'+str(n)
    return ts_atr

def atr(df, n = 20):
    new_tr = max(df.ix[-1,'high'],df.ix[-2,'close']) - min(df.ix[-1,'low'],df.ix[-2,'close'])
    alpha = 2.0/(n+1)
    df.ix[-1,'ATR_'+str(n)] = df.ix[-2,'ATR_'+str(n)]* (1-alpha) + alpha * new_tr
    
def MA(df, n):
    return pd.Series(pd.rolling_mean(df['close'], n), name = 'MA_' + str(n))

def ma(df, n):
    df.ix[-1,'MA_'+str(n)] = df.ix[-2,'MA_'+str(n)] + ( df.ix[-1,'close'] - df.ix[-1-n,'close'])/float(n)

#Exponential Moving Average
def EMA(df, n):
    return pd.Series(pd.ewma(df['close'], span = n, min_periods = n - 1), name = 'EMA_' + str(n))

def ema(df, n):
    alpha = 2.0/(n+1)
    df.ix[-1,'EMA_'+str(n)] = df.ix[-2,'EMA_'+str(n)]*(1-alpha) + df.ix[-1,'close']*alpha
    
#Momentum
def MOM(df, n):
    return pd.Series(df['close'].diff(n), name = 'Momentum_' + str(n))#Rate of Change

def ROC(df, n):
    M = df['close'].diff(n - 1)
    N = df['close'].shift(n - 1)
    return pd.Series(M / N, name = 'ROC_' + str(n))

#Bollinger Bandsy
def BBANDS(df, n):
    MA = pd.Series(pd.rolling_mean(df['close'], n), name ='MA_'+str(n))
    MSD = pd.Series(pd.rolling_std(df['close'], n))
    b1 = 4 * MSD / MA
    B1 = pd.Series(MA + 2*MSD, name = 'BollUp_' + str(n))
    #b2 = (df['close'] - MA + 2 * MSD) / (4 * MSD)
    B2 = pd.Series(MA - 2*MSD, name = 'BollLow_' + str(n))
    return pd.concat([B1,MA,B2], join='outer', axis=1)

#Pivot Points, Supports and Resistances
def PPSR(df):
    PP = pd.Series((df['high'] + df['low'] + df['close']) / 3)
    R1 = pd.Series(2 * PP - df['low'])
    S1 = pd.Series(2 * PP - df['high'])
    R2 = pd.Series(PP + df['high'] - df['low'])
    S2 = pd.Series(PP - df['high'] + df['low'])
    R3 = pd.Series(df['high'] + 2 * (PP - df['low']))
    S3 = pd.Series(df['low'] - 2 * (df['high'] - PP))
    psr = {'PP':PP, 'R1':R1, 'S1':S1, 'R2':R2, 'S2':S2, 'R3':R3, 'S3':S3}
    PSR = pd.DataFrame(psr)
    return PSR

#Stochastic oscillator %K
def STOK(df):
    return pd.Series((df['close'] - df['low']) / (df['high'] - df['low']), name = 'SOk')

#Stochastic oscillator %D
def STO(df, n):
    SOk = STOK(df)
    SOd = pd.Series(pd.ewma(SOk, span = n, min_periods = n - 1), name = 'SOd_' + str(n))
    return SOd

#Trix
def TRIX(df, n):
    EX1 = pd.ewma(df['close'], span = n, min_periods = n - 1)
    EX2 = pd.ewma(EX1, span = n, min_periods = n - 1)
    EX3 = pd.ewma(EX2, span = n, min_periods = n - 1)
    return pd.Series(EX3/EX3.shift(1) - 1, name = 'Trix_' + str(n))

#Average Directional Movement Index
def ADX(df, n, n_ADX):
    UpMove = df['high'] - df['high'].shift(1)
    DoMove = df['low'].shift(1) - df['low']
    UpD = pd.Series(UpMove)
    DoD = pd.Series(DoMove)
    UpD[(UpMove<=DoMove)|(UpMove <= 0)] = 0
    DoD[(DoMove<=UpMove)|(DoMove <= 0)] = 0
    ATRs = ATR(df,span = n, min_periods = n)
    PosDI = pd.Series(pd.ewma(UpD, span = n, min_periods = n - 1) / ATR)
    NegDI = pd.Series(pd.ewma(DoD, span = n, min_periods = n - 1) / ATR)
    ADX = pd.Series(pd.ewma(abs(PosDI - NegDI) / (PosDI + NegDI), span = n_ADX, min_periods = n_ADX - 1), name = 'ADX_' + str(n) + '_' + str(n_ADX))
    return ADX 

#MACD, MACD Signal and MACD difference
def MACD(df, n_fast, n_slow):
    EMAfast = pd.Series(pd.ewma(df['close'], span = n_fast, min_periods = n_slow - 1))
    EMAslow = pd.Series(pd.ewma(df['close'], span = n_slow, min_periods = n_slow - 1))
    MACD = pd.Series(EMAfast - EMAslow, name = 'MACD_' + str(n_fast) + '_' + str(n_slow))
    MACDsign = pd.Series(pd.ewma(MACD, span = 9, min_periods = 8), name = 'MACDsign_' + str(n_fast) + '_' + str(n_slow))
    MACDdiff = pd.Series(MACD - MACDsign, name = 'MACDdiff_' + str(n_fast) + '_' + str(n_slow))
    return pd.concat([MACD, MACDsign, MACDdiff], join='outer', axis=1)

#Mass Index
def MassI(df):
    Range = df['high'] - df['low']
    EX1 = pd.ewma(Range, span = 9, min_periods = 8)
    EX2 = pd.ewma(EX1, span = 9, min_periods = 8)
    Mass = EX1 / EX2
    MassI = pd.Series(pd.rolling_sum(Mass, 25), name = 'MassIndex')
    return MassI

#Vortex Indicator
def Vortex(df, n):
    tr = TR(df)
    vm = abs(df['high'] - df['low'].shift(1)) - abs(df['low']-df['high'].shift(1))
    VI = pd.Series(pd.rolling_sum(vm, n) / pd.rolling_sum(tr, n), name = 'Vortex_' + str(n))
    return VI

#KST Oscillator
def KST(df, r1, r2, r3, r4, n1, n2, n3, n4):
    M = df['close'].diff(r1 - 1)
    N = df['close'].shift(r1 - 1)
    ROC1 = M / N
    M = df['close'].diff(r2 - 1)
    N = df['close'].shift(r2 - 1)
    ROC2 = M / N
    M = df['close'].diff(r3 - 1)
    N = df['close'].shift(r3 - 1)
    ROC3 = M / N
    M = df['close'].diff(r4 - 1)
    N = df['close'].shift(r4 - 1)
    ROC4 = M / N
    KST = pd.Series(pd.rolling_sum(ROC1, n1) + pd.rolling_sum(ROC2, n2) * 2 + pd.rolling_sum(ROC3, n3) * 3 + pd.rolling_sum(ROC4, n4) * 4, name = 'KST_' + str(r1) + '_' + str(r2) + '_' + str(r3) + '_' + str(r4) + '_' + str(n1) + '_' + str(n2) + '_' + str(n3) + '_' + str(n4))
    return KST

#Relative Strength Index
def RSI(df, n):
    UpMove = df['high'] - df['high'].shift(1)
    DoMove = df['low'].shift(1) - df['low']
    UpD = pd.Series(UpMove)
    DoD = pd.Series(DoMove)
    UpD[(UpMove<=DoMove)|(UpMove <= 0)] = 0
    DoD[(DoMove<=UpMove)|(DoMove <= 0)] = 0
    PosDI = pd.Series(pd.ewma(UpD, span = n, min_periods = n - 1))
    NegDI = pd.Series(pd.ewma(DoD, span = n, min_periods = n - 1))
    RSI = pd.Series(PosDI / (PosDI + NegDI), name = 'RSI_' + str(n))
    return RSI

#True Strength Index
def TSI(df, r, s):
    M = pd.Series(df['close'].diff(1))
    aM = abs(M)
    EMA1 = pd.Series(pd.ewma(M, span = r, min_periods = r - 1))
    aEMA1 = pd.Series(pd.ewma(aM, span = r, min_periods = r - 1))
    EMA2 = pd.Series(pd.ewma(EMA1, span = s, min_periods = s - 1))
    aEMA2 = pd.Series(pd.ewma(aEMA1, span = s, min_periods = s - 1))
    TSI = pd.Series(EMA2 / aEMA2, name = 'TSI_' + str(r) + '_' + str(s))
    return TSI

#Accumulation/Distribution
def ACCDIST(df, n):
    ad = (2 * df['close'] - df['high'] - df['low']) / (df['high'] - df['low']) * df['volume']
    M = ad.diff(n - 1)
    N = ad.shift(n - 1)
    ROC = M / N
    AD = pd.Series(ROC, name = 'Acc/Dist_ROC_' + str(n))
    return AD

#Chaikin Oscillator
def Chaikin(df):
    ad = (2 * df['close'] - df['high'] - df['low']) / (df['high'] - df['low']) * df['volume']
    Chaikin = pd.Series(pd.ewma(ad, span = 3, min_periods = 2) - pd.ewma(ad, span = 10, min_periods = 9), name = 'Chaikin')
    return Chaikin

#Money Flow Index and Ratio
def MFI(df, n):
    PP = (df['high'] + df['low'] + df['close']) / 3
    PP > PP.shift(1)
    PosMF = pd.Series(PP)
    PosMF[PosMF <= PosMF.shift(1)] = 0
    PosMF = PosMF * df['volume']
    TotMF = PP * df['volume']
    MFR = pd.Series(PosMF / TotMF)
    MFI = pd.Series(rolling_mean(MFR, n), name = 'MFI_' + str(n))
    return MFI

#On-balance Volume
def OBV(df, n):
    PosVol = pd.Series(df['volume'])
    NegVol = pd.Series(-df['volume'])
    PosVol[df['close'] <= df['close'].shift(1)] = 0
    NegVol[df['close'] >= df['close'].shift(1)] = 0
    OBV = pd.Series(pd.rolling_mean(PosVol + NegVol, n), name = 'OBV_' + str(n))
    return OBV

#Force Index
def FORCE(df, n):
    F = pd.Series(df['close'].diff(n) * df['volume'].diff(n), name = 'Force_' + str(n))
    return F

#Ease of Movement
def EOM(df, n):
    EoM = (df['high'].diff(1) + df['low'].diff(1)) * (df['high'] - df['low']) / (2 * df['volume'])
    Eom_ma = pd.Series(pd.rolling_mean(EoM, n), name = 'EoM_' + str(n))
    return Eom_ma

#Commodity Channel Index
def CCI(df, n):
    PP = (df['high'] + df['low'] + df['close']) / 3
    CCI = pd.Series((PP - pd.rolling_mean(PP, n)) / pd.rolling_std(PP, n), name = 'CCI_' + str(n))
    return CCI

#Coppock Curve
def COPP(df, n):
    M = df['close'].diff(int(n * 11 / 10) - 1)
    N = df['close'].shift(int(n * 11 / 10) - 1)
    ROC1 = M / N
    M = df['close'].diff(int(n * 14 / 10) - 1)
    N = df['close'].shift(int(n * 14 / 10) - 1)
    ROC2 = M / N
    Copp = pd.Series(pd.ewma(ROC1 + ROC2, span = n, min_periods = n), name = 'Copp_' + str(n))
    return Copp

#Keltner Channel
def KELCH(df, n):
    KelChM = pd.Series(pd.rolling_mean((df['high'] + df['low'] + df['close']) / 3, n), name = 'KelChM_' + str(n))
    KelChU = pd.Series(pd.rolling_mean((4 * df['high'] - 2 * df['low'] + df['close']) / 3, n), name = 'KelChU_' + str(n))
    KelChD = pd.Series(pd.rolling_mean((-2 * df['high'] + 4 * df['low'] + df['close']) / 3, n), name = 'KelChD_' + str(n))
    return pd.concat([KelChM, KelChU, KelChD], join='outer', axis=1)

#Ultimate Oscillator
def ULTOSC(df):
    TR_l = TR(df)
    BP_l = df['close'] - pd.concat([df['low'], df['close'].shift(1)], axis=1).min(axis=1)
    UltO = pd.Series((4 * pd.rolling_sum(BP_l, 7) / pd.rolling_sum(TR_l, 7)) + (2 * pd.rolling_sum(BP_l, 14) / pd.rolling_sum(TR_l, 14)) + (pd.rolling_sum(BP_l, 28) / pd.rolling_sum(TR_l, 28)), name = 'Ultimate_Osc')
    return UltO

#Donchian Channel
def DONCH_H(df, n):
    DC_H = pd.rolling_max(df['high'],n)
    return pd.Series(DC_H, name = 'DONCH_H'+ str(n))

def DONCH_L(df, n):    
    DC_L = pd.rolling_min(df['low'], n)
    return pd.Series(DC_L, name = 'DONCH_L'+ str(n))

def donch_h(df, n):
    df.ix[-1,'DONCH_H'+str(n)] = max(df.ix[-n:,'high'])
 
def donch_l(df, n):
    df.ix[-1,'DONCH_L'+str(n)] = min(df.ix[-n:,'low'])
    
#Standard Deviation
def STDDEV(df, n):
    return pd.Series(pd.rolling_std(df['close'], n), name = 'STD_' + str(n))
    
#def var_ratio(
