from QuantLib import *

# global data
calendar = UnitedStates()
todaysDate = Date(28, 5, 2016);
Settings.instance().evaluationDate = todaysDate
settlementDate = Date(1, 6, 2016);

# market quotes
depositsQ = { #(1,Weeks):  0.00259231,
             (3,Months): 0.0067405}

#             (6,Months): 0.0353,
#             (9,Months): 0.0348,
#             (1,Years): 0.0345 }

#FRAs = { (3,6): 0.037125,
#         (6,9): 0.037125,
#         (9,12): 0.037125 }

futuresQ = {
            Date(21, 9,2016): 99.181,
            Date(21,12,2016): 99.07726,
            Date(15, 3,2017): 98.00412,
            Date(21, 6,2017): 98.93144,
            Date(20, 9,2017): 98.86416}

swapsQ = {(2,Years): 0.010044, 
		  (3,Years): 0.0112317,
		  (4,Years): 0.0121606,
          (5,Years): 0.0131619,
          (6,Years): 0.0140259,
          (7,Years): 0.0148052,
		  (8,Years): 0.0155509,
		  (9,Years): 0.0162203,
		  (10,Years):0.0168441,
          (12,Years):0.0179998,
          (15,Years):0.0192506,
          (20,Years):0.0204805,
          (25,Years):0.0211325,
          (30,Years):0.0215845}

# convert them to Quote objects
deposits = {}
futures = {}
swaps = {}
for n,unit in depositsQ.keys():
    deposits[(n,unit)] = SimpleQuote(depositsQ[(n,unit)])
#for n,m in FRAs.keys():
#    FRAs[(n,m)] = SimpleQuote(FRAs[(n,m)])
for d in futuresQ.keys():
    futures[d] = SimpleQuote(futuresQ[d])
for n,unit in swapsQ.keys():
    swaps[(n,unit)] = SimpleQuote(swapsQ[(n,unit)])

# build rate helpers

dayCounter = Actual360()
settlementDays = 2
depositHelpers = [ DepositRateHelper(QuoteHandle(deposits[(n,unit)]),
                                     Period(n,unit), settlementDays,
                                     calendar, ModifiedFollowing,
                                     False, dayCounter)
                   for n, unit in [(3,Months)] ]

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
swapType = VanillaSwap.Receiver
nominal = 10000
for_len = 1
to_len = 2
maturity = calendar.advance(settlementDate, for_len+to_len, Years)
maturity = calendar.advance(maturity, 1, Months)
fwdStart = calendar.advance(settlementDate, for_len, Years)
payFixed = True
print fwdStart, maturity

fixedLegFrequency = Semiannual
fixedLegAdjustment = Unadjusted
fixedLegDayCounter = Thirty360()
strike = 0.01275

floatingLegFrequency = Quarterly
spread = 0.0
fixingDays = 2
index = USDLibor(Period(3, Months), discountTermStructure)
floatingLegAdjustment = ModifiedFollowing
floatingLegDayCounter = index.dayCounter()

fixedSchedule = Schedule(fwdStart, maturity,
                         fixedLegTenor, calendar,
                         fixedLegAdjustment, fixedLegAdjustment,
                         DateGeneration.Forward, False)
floatingSchedule = Schedule(fwdStart, maturity,
                            floatingLegTenor, calendar,
                            floatingLegAdjustment, floatingLegAdjustment,
                            DateGeneration.Forward, False)

underlying = VanillaSwap(swapType, nominal,
                   fixedSchedule, strike, fixedLegDayCounter,
                   floatingSchedule, index, spread,
                   floatingLegDayCounter)
underlying.setPricingEngine(swapEngine)
print "spot = %s" % (underlying.NPV())
#forwardStart = calendar.advance(settlementDate,for_len, Years)
#forwardEnd = calendar.advance(forwardStart, to_len,Years)
#fixedSchedule = Schedule(forwardStart, forwardEnd,
#                         fixedLegTenor, calendar,
#                         fixedLegAdjustment, fixedLegAdjustment,
#                         DateGeneration.Forward, False)
#floatingSchedule = Schedule(forwardStart, forwardEnd,
#                            floatingLegTenor, calendar,
#                            floatingLegAdjustment, floatingLegAdjustment,
#                            DateGeneration.Forward, False)

#underlying = VanillaSwap(swapType, nominal,
#                      fixedSchedule, strike, fixedLegDayCounter,
#                      floatingSchedule, index, spread,
#                      floatingLegDayCounter)
#underlying.setPricingEngine(swapEngine)
endDate = floatingSchedule[-1]
bermudanDates = [ calendar.advance(d, -Period(2, Days)) for (idx, d) in enumerate(floatingSchedule)]
print bermudanDates
exercise = BermudanExercise(bermudanDates[:-1], False)
target_swaption = Swaption(underlying, exercise)
#swaptionVols = [ (d, endDate, vv) for d in bermudanDates ]
swaptionVols = [ # maturity,          length,             volatility
                 (Period(12, Months), Period(25, Months), SimpleQuote(0.55009)),
				 (Period(15, Months), Period(22, Months), SimpleQuote(0.54962)),
				 (Period(18, Months), Period(19, Months), SimpleQuote(0.55264)),
				 (Period(21, Months), Period(16, Months), SimpleQuote(0.56146)),
				 (Period(24, Months), Period(13, Months), SimpleQuote(0.57606)),
				 (Period(27, Months), Period(10, Months), SimpleQuote(0.58882)),
				 (Period(30, Months), Period(7, Months), SimpleQuote(0.59199)),
				 (Period(33, Months), Period(4, Months), SimpleQuote(0.58509)),
				 (Period(36, Months), Period(1, Months), SimpleQuote(0.62226)),
				 #(Period(48, Months), Period(24, Months), SimpleQuote(0.44623)),
				 #(Period(60, Months), Period(12, Months), SimpleQuote(0.45511)),
				 #(Period(27, Months), Period(45, Months), vv),
				 #(Period(30, Months), Period(42, Months), vv),
				 #(Period(33, Months), Period(39, Months), vv),
				 #(Period(36, Months), Period(36, Months), vv),
				 #(Period(39, Months), Period(33, Months), vv),
				 #(Period(42, Months), Period(30, Months), vv),
				 #(Period(45, Months), Period(27, Months), vv),
				 #(Period(48, Months), Period(24, Months), vv),
				 #(Period(51, Months), Period(21, Months), vv),
				 #(Period(54, Months), Period(18, Months), vv),
                 #(Period(57, Months), Period(15, Months), vv),
                 #(Period(60, Months), Period(12, Months), vv),
                 #(Period(63, Months), Period( 9, Months), vv),
				 #(Period(66, Months), Period( 6, Months), vv),
                 #(Period(69, Months), Period( 3, Months), vv),
				 ]
volQuotes = [vol.value() for exerciseDate, endDate, vol in swaptionVols]
helpers = [ SwaptionHelper(exerciseDate, endDate, \
                           QuoteHandle(vol), \
                           index, index.tenor(), index.dayCounter(), \
                           index.dayCounter(), discountTermStructure) for exerciseDate, endDate, vol in swaptionVols ]

stepDates = bermudanDates[:-1]
sigmas = [QuoteHandle(SimpleQuote(0.01))]*(len(stepDates)+1)
reversion = [QuoteHandle(SimpleQuote(0.01))]
gsr = Gsr(discountTermStructure, stepDates, sigmas, reversion, 20.0)
swaptionEngine = Gaussian1dSwaptionEngine(gsr, 64, 7.0, True,False, discountTermStructure)
#nonstandardSwaptionEngine =Gaussian1dNonstandardSwaptionEngine( gsr, 64, 7.0, True, False, QuoteHandle(SimpleQuote(0.0)), discountTermStructure)
#swapBase = SwapIndex( "UsdLiborSwapIsdaFixAm", 6 * Years, USDCurrency(), TARGET(), 6*Months, ModifiedFollowing, Thirty360(),
#                      index, discountTermStructure)
#basket = target_swaption.calibrationBasket(swapBase, swaptionVol)

print "Calibrating..."
for h in helpers:
	h.setPricingEngine(swaptionEngine)

method = LevenbergMarquardt()
ec = EndCriteria(1000, 10, 1E-8, 1E-8, 1E-8)
gsr.calibrateVolatilitiesIterative(helpers, method, ec)
target_swaption.setPricingEngine(swaptionEngine)
ref_pv = target_swaption.NPV()
print "ref_price = %s" % ref_pv

shiftSize = 0.0001
for n,unit in deposits.keys():
    deposits[(n,unit)].setValue(depositsQ[(n,unit)] + shiftSize)
for d in futures.keys():
    futures[d].setValue(futuresQ[d] - shiftSize*100)
for n,unit in swaps.keys():
    swaps[(n,unit)].setValue(swapsQ[(n,unit)] + shiftSize)

gsr = Gsr(discountTermStructure, stepDates, sigmas, reversion, 20.0)
swaptionEngine = Gaussian1dSwaptionEngine(gsr, 64, 7.0, True,False, discountTermStructure)
for h in helpers:
	h.setPricingEngine(swaptionEngine)
gsr.calibrateVolatilitiesIterative(helpers, method, ec)
target_swaption.setPricingEngine(swaptionEngine)
pv_up = target_swaption.NPV()

for n,unit in deposits.keys():
    deposits[(n,unit)].setValue(depositsQ[(n,unit)] - shiftSize)
for d in futures.keys():
    futures[d].setValue(futuresQ[d] + shiftSize * 100)
for n,unit in swaps.keys():
    swaps[(n,unit)].setValue(swapsQ[(n,unit)] - shiftSize)

gsr = Gsr(discountTermStructure, stepDates, sigmas, reversion, 20.0)
swaptionEngine = Gaussian1dSwaptionEngine(gsr, 64, 7.0, True,False, discountTermStructure)
for h in helpers:
	h.setPricingEngine(swaptionEngine)
gsr.calibrateVolatilitiesIterative(helpers, method, ec)
target_swaption.setPricingEngine(swaptionEngine)
pv_down = target_swaption.NPV()

for n,unit in deposits.keys():
    deposits[(n,unit)].setValue(depositsQ[(n,unit)])
for d in futures.keys():
    futures[d].setValue(futuresQ[d])
for n,unit in swaps.keys():
    swaps[(n,unit)].setValue(swapsQ[(n,unit)])

volShift = 0.01
for idx, (exerciseDate, endDate, vol) in enumerate(swaptionVols):
    vol.setValue( volQuotes[idx] + volShift )
gsr = Gsr(discountTermStructure, stepDates, sigmas, reversion, 20.0)
swaptionEngine = Gaussian1dSwaptionEngine(gsr, 64, 7.0, True,False, discountTermStructure)
for h in helpers:
	h.setPricingEngine(swaptionEngine)
gsr.calibrateVolatilitiesIterative(helpers, method, ec)
target_swaption.setPricingEngine(swaptionEngine)
pv_vol = target_swaption.NPV()

delta = (pv_up-pv_down)/2 * 10000
gamma = (pv_down + pv_up - ref_pv * 2) * 10000
vega = -(pv_vol - ref_pv)*10000
print "delta = %s, gamma = %s, vega = %s" % (delta, gamma, vega)
