import bsopt
import copy
import curve

SOLVER_ERROR_EPSILON = 1e-5
ITERATION_NUM = 100
ITERATION_STEP = 0.001
YEARLY_DAYS = 365.0
# Cash flow calculation for delta hedging.
# Inside the period, Vol is constant and hedging frequency is once per ndays
# bussinessDays is number of business days from the startD to expiryT

def delta_cashflow(is_call, ts, strike, vol, expiry, rd = 0.0, rf = 0.0, rehedge_period = 10, column = 'close'):
    # annualized days
    startD = Dates[0]
    endD = Dates[-1]
    lastPrice = ts[startD]
    lastTau = (expiryT - startD).days/YEARLY_DAYS

    date =tenor.RDateAdd(rehedge_period,startD, exceptionDateList)
    CF = 0.0
    while date < endD:
        if date in ts.Dates():
            CF = CF + bsopt.BSDelta(IsCall, lastPrice, strike, vol, lastTau, rd, rf) * (ts[date] - lastPrice)
            lastPrice = ts[date]
            lastTau = (expiryT - date).days/YEARLY_DAYS

        date = tenor.RDateAdd(rehedge_period,date, exceptionDateList)

    CF = CF + bsopt.BSDelta(IsCall, lastPrice, strike, vol, lastTau, rd, rf) * (ts[endD] - lastPrice)
    return CF


def BSrealizedVol(IsCall, ts, strike, expiryT, rd =0.0, rf = 0.0, optPayoff=0.0, rehedge_period = "1d", exceptionDateList = [], refVol = 0.5):
    startD = ts.Dates()[0]
    endD = ts.Dates()[-1]

    if tenor.RDateAdd(rehedge_period, startD, exceptionDateList) > endD :
        raise ValueError, 'the difference between the start and the end is smaller than the hedging step'

    if expiryT < endD :
        raise ValueError, 'Expiry time must be later than the end of the time series'

    F0 = ts.Values()[0]

    numTries = 0
    diff = 1000.0
    tau = (expiryT - startD).days/YEARLY_DAYS
    vol = refVol

    def func(x):
        return bsopt.BSOpt(IsCall, F0, strike, x, tau, rd, rf) + delta_cashflow(IsCall, ts, strike, x, expiryT, rd, rf, rehedge_period, exceptionDateList) - optPayoff

    while diff >= SOLVER_ERROR_EPSILON and numTries <= ITERATION_NUM:
        current = func(vol)
        high = func(vol + ITERATION_STEP)
        low = func(vol - ITERATION_STEP)
        if high == low:
            volnext = max(vol -ITERATION_STEP, 1e-2)
        else:
            volnext = vol - 2* ITERATION_STEP * current/(high-low)
            if volnext < 1e-2:
                volnext = vol/2.0

        diff = abs(volnext - vol)
        vol = volnext
        numTries += 1

    if diff >= SOLVER_ERROR_EPSILON or numTries > ITERATION_NUM:
        return None
    else :
        return vol

def BS_ATMVol_TermStr(IsCall, tsFwd, expiryT, rd = 0.0, rf = 0.0, endVol = 0.0, termTenor="1m", rehedge_period ="1d", exceptionDateList=[]):

    ts = curve.Curve()
    for d in tsFwd.Dates():
        if d not in exceptionDateList and d <= expiryT:
            ts[d] = tsFwd[d]

    rptTenor = '-' + termTenor
    DateList = [x for x in ts.Dates() if x not in exceptionDateList]
    TSstart = DateList[0]
    TSend = DateList[-1]

    date = copy.copy(TSend)
    endDate = tenor.RDateAdd('1d', date)
    startDate = tenor.RDateAdd(rptTenor, date, exceptionDateList)
    finalValue = 0.0

    volTS = curve.Curve()
    while startDate >= TSstart:
        subTS = ts.Slice(startDate, endDate)

        if len(subTS) < 2:
            print 'No data in time series further than ', startDate
            break

        if 0.0 in subTS.Values():
            print 'Price is zero at some date from ', startDate, ' to ', endDate
            break

        # for the moment, consider ATM vol
        strike = subTS.Values()[0]

        if endVol > 0:
            tau = (expiryT - subTS.Dates()[-1]).days/YEARLY_DAYS
            finalValue = bsopt.BSOpt(IsCall, subTS.Values()[-1], strike, endVol, tau, rd, rf)
            refVol = endVol
        elif endVol == 0:
            if IsCall:
                finalValue = max((subTS.Values()[-1] - strike), 0)
            else:
                finalValue = max((strike - subTS.Values()[-1]), 0)
            refVol = 0.5
        elif endVol == None:
            raise ValueError, 'no vol is found to match PnL'

        vol = BSrealizedVol(IsCall, subTS, strike, expiryT, rd, rf, finalValue, rehedge_period, exceptionDateList, refVol = refVol)
        volTS[startDate] = vol
        endVol =vol

        date = startDate
        endDate = tenor.RDateAdd('1d', date)
        startDate = tenor.RDateAdd(rptTenor, date, exceptionDateList)

    return volTS

def BS_VolSurf_TermStr(tsFwd, moneyness, expiryT, rd = 0.0, rf = 0.0, endVol = 0.0, termTenor="1m", rehedge_period ="1d", exceptionDateList=[]):
    ts =curve.Curve()
    rptTenor = '-' + termTenor


def BS_ConstDelta_VolSurf(tsFwd, moneynessList, expiryT, rd = 0.0, rf = 0.0, exceptionDateList=[]):
    ts = curve.Curve()
    rptTenor = '-1m'
    rehedge_period = '1d'
    IsCall = 1

    for d in tsFwd.Dates():
        if d not in exceptionDateList:
            ts[d] = tsFwd[d]

    DateList = [x for x in ts.Dates() if x not in exceptionDateList]
    TSstart = DateList[0]
    TSend = DateList[-1]

    date = copy.copy(TSend)
    endDate = tenor.RDateAdd('1d', date)
    startDate = tenor.RDateAdd(rptTenor, date, exceptionDateList)

    volTS = curve.GRCurve()
    while startDate >= TSstart:
        subTS = ts.Slice(startDate, endDate)
        vol = []
        if len(subTS) < 2:
            print 'No data in time series further than ', startDate
            break

        if 0.0 in subTS.Values():
            print 'Price is zero at some date from ', startDate, ' to ', endDate
            break

        # for the moment, consider ATM vol
        for m in moneynessList:
            strike = subTS.Values()[0] * m
            if IsCall:
                finalValue = max((subTS.Values()[-1] - strike), 0)
            else:
                finalValue = max((strike - subTS.Values()[-1]), 0)

        vol += [BSrealizedVol(IsCall, subTS, strike, expiryT, rd, rf, finalValue, rehedge_period, exceptionDateList)]
        if None in vol:
            print 'no vol is found to match PnL- strike:'+ str(m) + ' expiry:' + expiryT

        volTS[startDate] = vol
        startDate = tenor.RDateAdd(rptTenor, startDate, exceptionDateList)

    return volTS

def Spread_ATMVolCorr_TermStr(ts1, ts2, op, expiryT, r1 = 0, r2 = 0, termTenor="1m", exceptionDateList=[]):
    if op != '*' and op!= '/':
        raise ValueError, 'Operator has to be either * or / for Spread_ATMVolCorr_TermStr'

    dates = [ d for d in ts1.Dates() if d in ts2.Dates() and d <= expiryT]
    F1 = curve.Curve()
    F2 = curve.Curve()
    HR = curve.Curve()
    for d in dates:
        if ts1[d] > 0 and ts2[d]>0 :
            F1[d] = ts1[d]
            F2[d] = ts2[d]
            if op == '/':
                HR[d] = F1[d]/F2[d]
                r = r1 - r2
            else:
                HR[d] = F1[d] * F2[d]
                r = r1 + r2

    IsCall = 1
    HRVol= BS_ATMVol_TermStr(IsCall, HR, expiryT, rd = r, rf = 0.0, endVol = 0.0, termTenor=termTenor, rehedge_period ="1d", exceptionDateList=exceptionDateList)
    VolF1= BS_ATMVol_TermStr(IsCall, F1, expiryT, rd = r1, rf = 0.0, endVol = 0.0, termTenor=termTenor, rehedge_period ="1d", exceptionDateList=exceptionDateList)
    VolF2= BS_ATMVol_TermStr(IsCall, F2, expiryT, rd = r2, rf = 0.0, endVol = 0.0, termTenor=termTenor, rehedge_period ="1d", exceptionDateList=exceptionDateList)

    corr = curve.Curve()
    for d in HRVol.Dates():
        if op == '/':
            corr[d] = (VolF1[d]**2 + VolF2[d]**2 -HRVol[d]**2)/(2* VolF1[d] * VolF2[d])
        else:
            corr[d] = (HRVol[d]**2 - VolF1[d]**2 - VolF2[d]**2)/(2* VolF1[d] * VolF2[d])

    return HRVol, corr, VolF1, VolF2

def Crack_ATMVol_TermStr(tsList, weights, expiryT, termTenor="1m", exceptionDateList=[]):

    dates = []
    if len(tsList) != len(weights):
        raise ValueError, 'The number of elements of weights and time series should be equal'

    for ts in tsList:
        if dates == []:
            dates = ts.Dates()
        else:
            dates = [ d for d in ts.Dates() if d in dates]

    Crk = curve.Curve()
    undFwd = curve.Curve()

    for d in dates:
        Fwd = [ts[d] for ts in tsList]
        Crk[d] = sum([f*w for (f,w) in zip(Fwd, weights)])
        undFwd[d] = tsList[0][d]

    IsCall = 1
    CrkVol = BS_ATMVol_TermStr(IsCall, Crk, expiryT, rd = 0, rf = 0.0, endVol = 0.0, termTenor=termTenor, rehedge_period ="1d", exceptionDateList=exceptionDateList)
    undVol = BS_ATMVol_TermStr(IsCall, undFwd, expiryT, rd = 0, rf = 0.0, endVol = 0.0, termTenor=termTenor, rehedge_period ="1d", exceptionDateList=exceptionDateList)

    return CrkVol, undVol
