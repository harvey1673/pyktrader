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
    model.calibrate(helpers, method, EndCriteria(1000, 250, 1e-7, 1e-7, 1e-7))

    print('Parameters: %s' % model.params())
    print(rule)

    print(header)
    print(rule)

    totalError = 0.0
    for swaption, helper in zip(swaptionVols, helpers):
        maturity, length, vol = swaption
        NPV = helper.modelValue()
        implied = helper.impliedVolatility(NPV, 1.0e-4, 1000, 0.05, 0.80)
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
calendar = TARGET()
todaysDate = Date(16, 10, 2015);
Settings.instance().evaluationDate = todaysDate
settlementDate = Date(18, 10, 2015);

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

futures = { Date(14,12,2015): 99.6375,
            Date(14, 3,2016): 99.5575,
            Date(13, 6,2016): 99.4575,
            Date(19, 9,2016): 99.3325,
            Date(19,12,2016): 99.1875,
            Date(13, 3,2017): 99.0675,
            Date(19, 6,2017): 98.9375,
            Date(18, 9,2017): 98.8175,
            Date(18,12,2017): 98.6875,	
            Date(13, 3,2018): 98.5775,
            Date(19, 6,2018): 98.4675,
            Date(18, 9,2018): 98.3675 }

swaps = { (4,Years): 0.01070383,
          (5,Years): 0.01290898,
          (6,Years): 0.01480271,
          (7,Years): 0.01669643,
		  (8,Years): 0.01778255,
		  (9,Years): 0.01886868,
		  (10,Years):0.01995480,
          (12,Years):0.02081077,
          (15,Years):0.02209472,
          (20,Years):0.02423464,
          (25,Years):0.02637456,
          (30,Years):0.02851449 }

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
                               fixedLegDayCounter, USDLibor())
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
nominal = 1000
length = 5
maturity = calendar.advance(settlementDate,length,Years)
payFixed = True

fixedLegFrequency = Semiannual
fixedLegAdjustment = Unadjusted
fixedLegDayCounter = Thirty360()
fixedRate = 0.015

floatingLegFrequency = Quarterly
spread = 0.0
fixingDays = 2
index = USDLibor(forecastTermStructure)
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

spot = VanillaSwap(VanillaSwap.Payer, nominal,
                   fixedSchedule, fixedRate, fixedLegDayCounter,
                   floatingSchedule, index, spread,
                   floatingLegDayCounter)
spot.setPricingEngine(swapEngine)
forwardStart = calendar.advance(settlementDate,1,Years)
forwardEnd = calendar.advance(forwardStart,length,Years)
fixedSchedule = Schedule(forwardStart, forwardEnd,
                         fixedLegTenor, calendar,
                         fixedLegAdjustment, fixedLegAdjustment,
                         DateGeneration.Forward, False)
floatingSchedule = Schedule(forwardStart, forwardEnd,
                            floatingLegTenor, calendar,
                            floatingLegAdjustment, floatingLegAdjustment,
                            DateGeneration.Forward, False)

forward = VanillaSwap(VanillaSwap.Payer, nominal,
                      fixedSchedule, fixedRate, fixedLegDayCounter,
                      floatingSchedule, index, spread,
                      floatingLegDayCounter)
forward.setPricingEngine(swapEngine)
atmRate = forward.fairRate()

atmSwap = VanillaSwap(VanillaSwap.Payer, nominal,
                      fixedSchedule, atmRate, fixedLegDayCounter,
                      floatingSchedule, index, spread,
                      floatingLegDayCounter)
otmSwap = VanillaSwap(VanillaSwap.Payer, nominal,
                      fixedSchedule, atmRate*1.2, fixedLegDayCounter,
                      floatingSchedule, index, spread,
                      floatingLegDayCounter)
itmSwap = VanillaSwap(VanillaSwap.Payer, nominal,
                      fixedSchedule, atmRate*0.8, fixedLegDayCounter,
                      floatingSchedule, index, spread,
                      floatingLegDayCounter)
atmSwap.setPricingEngine(swapEngine)
otmSwap.setPricingEngine(swapEngine)
itmSwap.setPricingEngine(swapEngine)

swaptionVols = [ # maturity,          length,             volatility
                 (Period(1.00, Years), Period(5.00, Years), 0.52300),
				 (Period(1.25, Years), Period(4.75, Years), 0.52464),
				 (Period(1.50, Years), Period(4.50, Years), 0.52628),
				 (Period(1.75, Years), Period(4.25, Years), 0.52807),
				 (Period(2.00, Years), Period(4.00, Years), 0.53007),
				 (Period(2.25, Years), Period(3.75, Years), 0.53328),
				 (Period(2.50, Years), Period(3.50, Years), 0.53466),
				 (Period(2.75, Years), Period(3.25, Years), 0.53380),
				 (Period(3.00, Years), Period(3.00, Years), 0.53003),
				 (Period(3.25, Years), Period(2.75, Years), 0.53360),
				 (Period(3.50, Years), Period(2.50, Years), 0.53585),
				 (Period(3.75, Years), Period(2.25, Years), 0.53663),
				 (Period(4.00, Years), Period(2.00, Years), 0.53547),
				 (Period(4.25, Years), Period(1.75, Years), 0.52427),
				 (Period(4.50, Years), Period(1.50, Years), 0.51754),
                 (Period(4.75, Years), Period(1.25, Years), 0.51632),
                 (Period(5.00, Years), Period(1.00, Years), 0.52099),
                 (Period(5.25, Years), Period(0.75, Years), 0.52131),
				 (Period(5.50, Years), Period(0.50, Years), 0.51954),
                 (Period(5.75, Years), Period(0.25, Years), 0.51914) ]

helpers = [ SwaptionHelper(maturity, length,
                           QuoteHandle(SimpleQuote(vol)),
                           index, index.tenor(), index.dayCounter(),
                           index.dayCounter(), discountTermStructure))
            for maturity, length, vol in swaptionVols ]

times = {}
for h in helpers:
    for t in h.times():
        times[t] = 1
times = times.keys()
times.sort()

grid = TimeGrid(times, 30)

G2model = G2(discountTermStructure))
HWmodel = HullWhite(discountTermStructure))
HWmodel2 = HullWhite(discountTermStructure))
BKmodel = BlackKarasinski(discountTermStructure))

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
exercise = BermudanExercise(bermudanDates)

format = '%17s |%17s |%17s |%17s'
header = format % ('model', 'in-the-money', 'at-the-money', 'out-of-the-money')
rule = '-' * len(header)
dblrule = '=' * len(header)

print
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
