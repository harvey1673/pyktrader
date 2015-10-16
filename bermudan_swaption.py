from QuantLib import *

def formatVol(v, digits = 2):
    format = '%%.%df %%%%' % digits
    return format % (v * 100)

def formatPrice(p, digits = 2):
    format = '%%.%df' % digits
    return format % p

def calibrate(model, helpers, l, name):

    format = '%12s |%12s |%12s |%12s |%12s'
    header = format % ('maturity','length','volatility','implied','error')
    rule = '-' * len(header)
    dblrule = '=' * len(header)

    print('')
    print(dblrule)
    print(name)
    print(rule)

    method = Simplex(l);
    model.calibrate(helpers, method, EndCriteria(1000, 250, 1e-4, 1e-4, 1e-4))

    print('Parameters: %s' % model.params())
    print(rule)

    print(header)
    print(rule)

    totalError = 0.0
    for swaption, helper in zip(swaptionVols, helpers):
        maturity, length, vol = swaption
        NPV = helper.modelValue()
        implied = helper.impliedVolatility(NPV, 1.0e-4, 1000, 0.25, 0.70)
        error = implied - vol
        totalError += abs(error)
        print(format % (maturity, length,
                        formatVol(vol,4), formatVol(implied,4),
                        formatVol(error,4)))
    averageError = totalError/len(helpers)

    print(rule)
    format = '%%%ds' % len(header)
    print(format % ('Average error: ' + formatVol(averageError,4)))
    print(dblrule)

# global data
calendar = UnitedStates()
todaysDate = Date(15, 10, 2015);
Settings.instance().evaluationDate = todaysDate
settlementDate = Date(19, 10, 2015);

# market quotes
deposits = { (1,Weeks):  0.002749,
             (1,Months): 0.002881,
             (2,Months): 0.002983 } 
#             (6,Months): 0.0353,
#             (9,Months): 0.0348,
#             (1,Years): 0.0345 }

#FRAs = { (3,6): 0.037125,
#         (6,9): 0.037125,
#         (9,12): 0.037125 }

futures = { Date(16,12,2015): 99.6375,
            Date(16, 3,2016): 99.5575,
            Date(15, 6,2016): 99.4575,
            Date(21, 9,2016): 99.3325,
            Date(21,12,2016): 99.1875,
            Date(15, 3,2017): 99.0675,
            Date(21, 6,2017): 98.9375,
            Date(20, 9,2017): 98.8175,
            Date(20,12,2017): 98.6875,
            Date(21, 3,2018): 98.5775,
            Date(20, 6,2018): 98.4675,
            Date(19, 9,2018): 98.3675 }

swaps = { (4,Years): 0.0114274,
          (5,Years): 0.0132988,
          (6,Years): 0.0149687,
          (7,Years): 0.0163994,
		  (8,Years): 0.0176033,
		  (9,Years): 0.0186200,
		  (10,Years):0.0194827,
          (12,Years):0.0202205,
          (15,Years):0.0223418,
          (20,Years):0.0237100,
          (25,Years):0.0243868,
          (30,Years):0.0248008 }

# convert them to Quote objects
for n,unit in deposits.keys():
    deposits[(n,unit)] = SimpleQuote(deposits[(n,unit)])
#for n,m in FRAs.keys():
#    FRAs[(n,m)] = SimpleQuote(FRAs[(n,m)])
for d in futures.keys():
    futures[d] = SimpleQuote(futures[d])
for n,unit in swaps.keys():
    swaps[(n,unit)] = SimpleQuote(swaps[(n,unit)])

# build rate helpers

dayCounter = Actual360()
settlementDays = 2
depositHelpers = [ DepositRateHelper(QuoteHandle(deposits[(n,unit)]),
                                     Period(n,unit), settlementDays,
                                     calendar, ModifiedFollowing,
                                     False, dayCounter)
                   for n, unit in [(1,Weeks),(1,Months),(2,Months)] ]

#dayCounter = Actual360()
#settlementDays = 2
#fraHelpers = [ FraRateHelper(QuoteHandle(FRAs[(n,m)]),
#                             n, m, settlementDays,
#                             calendar, ModifiedFollowing,
#                             False, dayCounter)
#               for n, m in FRAs.keys() ]

dayCounter = Actual360()
months = 3
futuresHelpers = [ FuturesRateHelper(QuoteHandle(futures[d]),
                                     d, months,
                                     calendar, ModifiedFollowing,
                                     True, dayCounter,
                                     QuoteHandle(SimpleQuote(0.0)))
                   for d in futures.keys() ]

settlementDays = 2
fixedLegFrequency = Semiannual
fixedLegTenor = Period(6,Months)
fixedLegAdjustment = Unadjusted
fixedLegDayCounter = Thirty360()
floatingLegFrequency = Quarterly
floatingLegTenor = Period(3,Months)
floatingLegAdjustment = ModifiedFollowing
swapHelpers = [ SwapRateHelper(QuoteHandle(swaps[(n,unit)]),
                               Period(n,unit), calendar,
                               fixedLegFrequency, fixedLegAdjustment,
                               fixedLegDayCounter, USDLibor(Period(3, Months)))
                for n, unit in swaps.keys() ]

# term structure handles

discountTermStructure = RelinkableYieldTermStructureHandle()
forecastTermStructure = RelinkableYieldTermStructureHandle()

# term-structure construction

helpers = depositHelpers + futuresHelpers + swapHelpers
depoFuturesSwapCurve = PiecewiseFlatForward(settlementDate, helpers,
                                            Actual360())

#helpers = depositHelpers[:3] + fraHelpers + swapHelpers
#depoFraSwapCurve = PiecewiseFlatForward(settlementDate, helpers, Actual360())

# swaps to be priced

swapEngine = DiscountingSwapEngine(discountTermStructure)
discountTermStructure.linkTo(depoFuturesSwapCurve)
swapType = VanillaSwap.Payer
nominal = 10000000
for_len = 1
to_len = 5
maturity = calendar.advance(settlementDate, for_len+to_len, Years)
payFixed = True

fixedLegFrequency = Semiannual
fixedLegAdjustment = Unadjusted
fixedLegDayCounter = Thirty360()
fixedRate = 0.015

floatingLegFrequency = Quarterly
spread = 0.0
fixingDays = 2
index = USDLibor(Period(3, Months), discountTermStructure)
floatingLegAdjustment = ModifiedFollowing
floatingLegDayCounter = index.dayCounter()

fixedSchedule = Schedule(settlementDate, maturity,
                         fixedLegTenor, calendar,
                         fixedLegAdjustment, fixedLegAdjustment,
                         DateGeneration.Forward, False)
floatingSchedule = Schedule(settlementDate, maturity,
                            floatingLegTenor, calendar,
                            floatingLegAdjustment, floatingLegAdjustment,
                            DateGeneration.Forward, False)

spot = VanillaSwap(swapType, nominal,
                   fixedSchedule, fixedRate, fixedLegDayCounter,
                   floatingSchedule, index, spread,
                   floatingLegDayCounter)
spot.setPricingEngine(swapEngine)
print "spot = %s" % (spot.fairRate())
forwardStart = calendar.advance(settlementDate,for_len, Years)
forwardEnd = calendar.advance(forwardStart, to_len,Years)
fixedSchedule = Schedule(forwardStart, forwardEnd,
                         fixedLegTenor, calendar,
                         fixedLegAdjustment, fixedLegAdjustment,
                         DateGeneration.Forward, False)
floatingSchedule = Schedule(forwardStart, forwardEnd,
                            floatingLegTenor, calendar,
                            floatingLegAdjustment, floatingLegAdjustment,
                            DateGeneration.Forward, False)

forward = VanillaSwap(swapType, nominal,
                      fixedSchedule, fixedRate, fixedLegDayCounter,
                      floatingSchedule, index, spread,
                      floatingLegDayCounter)
forward.setPricingEngine(swapEngine)
atmRate = forward.fairRate()
atmSwap = VanillaSwap(swapType, nominal,
                      fixedSchedule, atmRate, fixedLegDayCounter,
                      floatingSchedule, index, spread,
                      floatingLegDayCounter)
otmSwap = VanillaSwap(swapType, nominal,
                      fixedSchedule, atmRate*1.2, fixedLegDayCounter,
                      floatingSchedule, index, spread,
                      floatingLegDayCounter)
itmSwap = VanillaSwap(swapType, nominal,
                      fixedSchedule, atmRate*0.8, fixedLegDayCounter,
                      floatingSchedule, index, spread,
                      floatingLegDayCounter)
atmSwap.setPricingEngine(swapEngine)
otmSwap.setPricingEngine(swapEngine)
itmSwap.setPricingEngine(swapEngine)

vv = 0.46
swaptionVols = [ # maturity,          length,             volatility
                 (Period(12, Months), Period(60, Months), vv),
				 (Period(15, Months), Period(57, Months), vv),
				 (Period(18, Months), Period(54, Months), vv),
				 (Period(21, Months), Period(51, Months), vv),
				 (Period(24, Months), Period(48, Months), vv),
				 (Period(27, Months), Period(45, Months), vv),
				 (Period(30, Months), Period(42, Months), vv),
				 (Period(33, Months), Period(39, Months), vv),
				 (Period(36, Months), Period(36, Months), vv),
				 (Period(39, Months), Period(33, Months), vv),
				 (Period(42, Months), Period(30, Months), vv),
				 (Period(45, Months), Period(27, Months), vv),
				 (Period(48, Months), Period(24, Months), vv),
				 (Period(51, Months), Period(21, Months), vv),
				 (Period(54, Months), Period(18, Months), vv),
                 (Period(57, Months), Period(15, Months), vv),
                 (Period(60, Months), Period(12, Months), vv),
                 (Period(63, Months), Period( 9, Months), vv),
				 (Period(66, Months), Period( 6, Months), vv),
                 (Period(69, Months), Period( 3, Months), vv) ]

helpers = [ SwaptionHelper(maturity, length, \
                           QuoteHandle(SimpleQuote(vol)), \
                           index, index.tenor(), index.dayCounter(), \
                           index.dayCounter(), discountTermStructure) for maturity, length, vol in swaptionVols ]

times = {}
for h in helpers:
    for t in h.times():
        times[t] = 1
times = times.keys()
times.sort()

grid = TimeGrid(times, 30)

G2model = G2(discountTermStructure)
HWmodel = HullWhite(discountTermStructure)
HWmodel2 = HullWhite(discountTermStructure)
BKmodel = BlackKarasinski(discountTermStructure)

print "Calibrating..."

for h in helpers:
    h.setPricingEngine(G2SwaptionEngine(G2model,6.0,16))
calibrate(G2model, helpers, 0.05, "G2 (analytic formulae)")

for h in helpers:
    h.setPricingEngine(JamshidianSwaptionEngine(HWmodel))
calibrate(HWmodel, helpers, 0.05, "Hull-White (analytic formulae)")

for h in helpers:
    h.setPricingEngine(TreeSwaptionEngine(HWmodel2,grid))
calibrate(HWmodel2, helpers, 0.05, "Hull-White (numerical calibration)")

for h in helpers:
    h.setPricingEngine(TreeSwaptionEngine(BKmodel,grid))
calibrate(BKmodel, helpers, 0.05, "Black-Karasinski (numerical calibration)")


# price Bermudan swaptions on defined swaps

bermudanDates = [ d for d in floatingSchedule ][4:-1]
print bermudanDates
exercise = BermudanExercise(bermudanDates)

format = '%17s |%17s |%17s |%17s'
header = format % ('model', 'in-the-money', 'at-the-money', 'out-of-the-money')
rule = '-' * len(header)
dblrule = '=' * len(header)

print "forward rate = %s, ITM = %s, OTM = %s" % (atmRate, atmRate*0.8, atmRate*1.2)
print dblrule
print 'Pricing Bermudan swaptions...'
print rule
print header
print rule

atmSwaption = Swaption(atmSwap, exercise)
otmSwaption = Swaption(otmSwap, exercise)
itmSwaption = Swaption(itmSwap, exercise)
time_steps = 50
atmSwaption.setPricingEngine(TreeSwaptionEngine(G2model, time_steps))
otmSwaption.setPricingEngine(TreeSwaptionEngine(G2model, time_steps))
itmSwaption.setPricingEngine(TreeSwaptionEngine(G2model, time_steps))

print format % ('G2 analytic', formatPrice(itmSwaption.NPV()),
                formatPrice(atmSwaption.NPV()), formatPrice(otmSwaption.NPV()))

atmSwaption.setPricingEngine(TreeSwaptionEngine(HWmodel, time_steps))
otmSwaption.setPricingEngine(TreeSwaptionEngine(HWmodel, time_steps))
itmSwaption.setPricingEngine(TreeSwaptionEngine(HWmodel, time_steps))

print format % ('HW analytic', formatPrice(itmSwaption.NPV()),
                formatPrice(atmSwaption.NPV()), formatPrice(otmSwaption.NPV()))

atmSwaption.setPricingEngine(TreeSwaptionEngine(HWmodel2, time_steps))
otmSwaption.setPricingEngine(TreeSwaptionEngine(HWmodel2, time_steps))
itmSwaption.setPricingEngine(TreeSwaptionEngine(HWmodel2, time_steps))

print format % ('HW numerical', formatPrice(itmSwaption.NPV()),
                formatPrice(atmSwaption.NPV()), formatPrice(otmSwaption.NPV()))

atmSwaption.setPricingEngine(TreeSwaptionEngine(BKmodel, time_steps))
otmSwaption.setPricingEngine(TreeSwaptionEngine(BKmodel, time_steps))
itmSwaption.setPricingEngine(TreeSwaptionEngine(BKmodel, time_steps))

print format % ('BK numerical', formatPrice(itmSwaption.NPV()),
                formatPrice(atmSwaption.NPV()), formatPrice(otmSwaption.NPV()))

print dblrule
