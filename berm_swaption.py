from QuantLib import *

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
nominal = 1000
for_len = 1
to_len = 5
maturity = calendar.advance(settlementDate, for_len+to_len, Years)
payFixed = True

fixedLegFrequency = Semiannual
fixedLegAdjustment = Unadjusted
fixedLegDayCounter = Thirty360()
strike = 0.0205

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

underlying = VanillaSwap(swapType, nominal,
                   fixedSchedule, strike, fixedLegDayCounter,
                   floatingSchedule, index, spread,
                   floatingLegDayCounter)
underlying.setPricingEngine(swapEngine)
print "spot = %s" % (underlying.fairRate())
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
bermudanDates = [ d for d in floatingSchedule ][4:-1]
print bermudanDates
exercise = BermudanExercise(bermudanDates, False)
target_swaption = Swaption(underlying, exercise)
vv = 0.46
#swaptionVols = [ (d, endDate, vv) for d in bermudanDates ]
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
helpers = [ SwaptionHelper(exerciseDate, endDate, \
                           QuoteHandle(SimpleQuote(vol)), \
                           index, index.tenor(), index.dayCounter(), \
                           index.dayCounter(), discountTermStructure) for exerciseDate, endDate, vol in swaptionVols ]

#volQuote= SimpleQuote(vv)
#swaptionVol = ConstantSwaptionVolatility(0, UnitedStates(), ModifiedFollowing, volQuote, Actual365Fixed())
stepDates = bermudanDates[:-1]
sigmas = [QuoteHandle(SimpleQuote(0.1))]*(len(stepDates)+1)
reversion = [QuoteHandle(SimpleQuote(0.01))]
gsr = Gsr(discountTermStructure, stepDates, sigmas, reversion, 20.0)
swaptionEngine = Gaussian1dSwaptionEngine(gsr, 64, 7.0, True,False, discountTermStructure)
#nonstandardSwaptionEngine =Gaussian1dNonstandardSwaptionEngine( gsr, 64, 7.0, True, False, Quote(), discountTermStructure)
target_swaption.setPricingEngine(swaptionEngine)
#swapBase = SwapIndex( "UsdLiborSwapIsdaFixAm", 6 * Years, USDCurrency(), TARGET(), 6*Months, ModifiedFollowing, Thirty360(),
#                      index, discountTermStructure)
#basket = target_swaption.calibrationBasket(swapBase, swaptionVol)

print "Calibrating..."
for h in helpers:
	h.setPricingEngine(swaptionEngine)

method = LevenbergMarquardt()
ec = EndCriteria(1000, 10, 1E-5, 1E-5, 1E-8)
gsr.calibrateVolatilitiesIterative(helpers, method, ec)

print target_swaption.NPV()

