import scipy.stats
import numpy
from   math import exp, log, pi, sqrt
import scipy
from   scipy.optimize import brenth, brentq, newton
import time

def cnorm(x):
    return scipy.stats.norm.cdf(x)

def cnorminv(x):
    return scipy.stats.norm.ppf(x)

def pnorm(x):
    scipy.stats.norm.pdf(x)

def BlackSholesFormula(IsCall, S, K, Sigma, Texp, rf, rd):
    d1 = (log(S/K) + (rf - rd + 0.5* Sigma**2) * Texp)/(Sigma*sqrt(Texp))
    d2 = d1 - Sigma*sqrt(Texp)
    x1 = cnorm(d1)
    x2 = cnorm(d2)
    y = pnorm(d1)
    res = {}

    if IsCall:
        res['Price'] = S * exp(-rd*Texp)* x1 - K * exp(-rf*Texp) * x2
        res['Delta'] = x1 * exp(-rd*Texp)
    elif CallPut == 'P':
        res['Price'] = K * exp(-rf*Texp) * (1 - x2) - S * exp(-rd*Texp) * (1 - x1)
        res['Delta'] = (x1  - 1) * exp(-rd*Texp)

    res['Vega'] = S * sqrt(Texp) * y * exp(-rd*Texp)
    res['Gamma'] = y/(S*Sigma* sqrt(T))

    return res

def KirkApprox(IsCall, F1, F2, Sigma1, Sigma2, Corr, K, Texp, r):
    FA = F1/(F2+K)
    Sigma = sqrt(Sigma1**2 + (Sigma2*F2/(F2+K))**2 - \
                       2*Corr*Sigma1*Sigma2*F2/(F2+K))
    d1 = (numpy.log(FA) + 0.5* Sigma**2 * T)/(Sigma*sqrt(Texp))
    d2 = d1 - Sigma*sqrt(Texp)
    x1 = scipy.stats.norm.cdf(d1)
    x2 = scipy.stats.norm.cdf(d2)
    if IsCall:
        res['Price'] = (F2+K)*(FA * x1 - x2) * exp(-r*Texp)
    else:
        res['Price'] = (F2+K)*((1 - x2) - FA*(1 - x1)) * exp(-r*Texp)

    return res

def BSOpt( IsCall, Spot, Strike, Vol, Texp, Rd, Rf ):
    'Standard Black-Scholes European vanilla pricing.'

    if Strike <= 1e-12 * Spot:
        if IsCall:
            return Spot * exp( -Rf * Texp )
        else:
            return 0.

    if IsCall:
        return Spot   * exp( -Rf * Texp ) * cnorm( d1( Spot, Strike, Vol, Texp, Rd, Rf ) ) \
             - Strike * exp( -Rd * Texp ) * cnorm( d2( Spot, Strike, Vol, Texp, Rd, Rf ) )
    else:
        return Strike * exp( -Rd * Texp ) * cnorm( -d2( Spot, Strike, Vol, Texp, Rd, Rf ) ) \
             - Spot   * exp( -Rf * Texp ) * cnorm( -d1( Spot, Strike, Vol, Texp, Rd, Rf ) )


def BSOptFwd( IsCall, Fwd, Strike, Vol, Texp ):
    'Standard Black-Scholes European vanilla pricing.'

    if Strike <= 1e-12 * Fwd:
        if IsCall:
            return Fwd
        else:
            return 0.

    if IsCall:
        return Fwd  * cnorm( fd1( Fwd, Strike, Vol, Texp ) ) \
             - Strike * cnorm( fd2( Fwd, Strike, Vol, Texp ) )
    else:
        return Strike * cnorm( -fd2( Fwd, Strike, Vol, Texp ) ) \
             - Fwd * cnorm( -fd1( Fwd, Strike, Vol, Texp ) )

def BSOptFwdNormal( IsCall, Fwd, Strike, Vol, Texp ):
    'Standard Bachelier European vanilla pricing.'
    d = (Fwd-Strike)/Vol/sqrt(Texp)
    p = (Fwd-Strike)  * cnorm( d ) + Vol * sqrt(Texp) * pnorm(d)
    if not IsCall:
        p = Fwd - Strike - p
    return p

def BSBin( IsCall, Spot, Strike, Vol, Texp, Rd, Rf ):
    'Standard Black-Scholes European binary call/put pricing.'

    Bin = cnorm( d2( Spot, Strike, Vol, Texp, Rd, Rf ) )
    if not IsCall:
        Bin = 1 - Bin
    Bin = Bin * exp( -Rd * Texp )
    return Bin

def BSDelta( IsCall, Spot, Strike, Vol, Texp, Rd, Rf ):
    'Standard Black-Scholes Delta calculation. Over-currency spot delta.'

    if IsCall:
        return exp( -Rf * Texp ) * cnorma( d1( Spot, Strike, Vol, Texp, Rd, Rf ) )
    else:
        return -exp( -Rf * Texp ) * cnorma( -d1( Spot, Strike, Vol, Texp, Rd, Rf ) )

def BSVega( Spot, Strike, Vol, Texp, Rd, Rf ):
    'Standard Black-Scholes Vega calculation.'

    d = d1( Spot, Strike, Vol, Texp, Rd, Rf )
    return Spot * exp( -Rf * Texp ) * sqrt( Texp / 2. / pi ) * exp( -d * d / 2. )

def BSImpVol( IsCall, Spot, Strike, Texp, Rd, Rf, Price ):
    '''Calculates Black-Scholes implied volatility from a European price.
    It uses Brent rootfinding, and tries to isolate the root somewhat using
    a lower limit based on recognizing that the time value of the option is
    less than or equal to the time value of an ATM option, and an upper limit
    by calculating the vega at the lower limit and recognizing that vanillas
    have positive vol convexity (or zero for ATM options).'''

    Dd = exp( -Rd * Texp )
    Df = exp( -Rf * Texp )

    if IsCall:
        IntVal = max( Df * Spot - Dd * Strike, 0. )
    else:
        IntVal = max( Dd * Strike - Df * Spot, 0. )

    TimeVal = Price - IntVal

    VolMin    = sqrt( 2 * pi / Texp ) * TimeVal / Df / Spot
    PriceMin  = BSOpt( IsCall, Spot, Strike, VolMin, Texp, Rd, Rf )
    PriceDiff = Price - PriceMin
    VegaMin   = BSVega( Spot, Strike, VolMin, Texp, Rd, Rf )

    if VegaMin == 0:
        VolMax = 10
        VolMin = 0.001
    else:
        VolMax    = VolMin + PriceDiff / VegaMin
        VolMin    = max( 0.00001, VolMin - 0.001 )
        VolMax    = min( 10, VolMax + 0.001 )

    def ArgFunc( Vol ):
        PriceCalc = BSOpt( IsCall, Spot, Strike, Vol, Texp, Rd, Rf )
        return PriceCalc - Price

    Vol = brenth( ArgFunc, VolMin, VolMax )
    return Vol

def BSImpVolSimple( IsCall, Spot, Strike, Texp, Rd, Rf, Price ):
    '''Calculates Black-Scholes implied volatility from a European price.
    It uses Brent rootfinding and assumes the vol is between 0.0000001 and 1.'''

    def ArgFunc( Vol ):
        PriceCalc = BSOpt( IsCall, Spot, Strike, Vol, Texp, Rd, Rf )
        return PriceCalc - Price

    Vol = brenth( ArgFunc, 0.0000001, 1 )
    return Vol

def BSImpVolNormal( IsCall, Fwd, Strike, Texp, Rd, Price ):
    '''Calculates the normal-model implied vol to match the option price.'''

    def ArgFunc( Vol ):
        PriceCalc = BSOptNormal( IsCall, Fwd, Strike, Vol, Texp, Rd )
        return PriceCalc - Price

    Vol = brenth( ArgFunc, 0.0000001, Fwd )
    return Vol

def StrikeFromDelta( IsCall, Spot, Vol, Texp, Rd, Rf, Delta ):
    '''Calculates the strike of a European vanilla option gives its Black-Scholes Delta.
    It assumes the Delta is an over-ccy spot Delta.'''

    def ArgFunc( Strike ):
        DeltaCalc = BSDelta( IsCall, Spot, Strike, Vol, Texp, Rd, Rf )
        return DeltaCalc - Delta

    LoStrike = Spot * exp( ( Rd - Rf ) * Texp - 4 * Vol * sqrt( Texp ) )
    HiStrike = Spot * exp( ( Rd - Rf ) * Texp + 4 * Vol * sqrt( Texp ) )

    Strike = brenth( ArgFunc, LoStrike, HiStrike )
    return Strike

def OneTouch( IsHigh, IsDelayed, Spot, Strike, Vol, Texp, Rd, Rf ):
    '''Prices a one touch option. IsHigh=True means it knocks up and in; False
    means down and in. IsDelayed=True means it pays at the end; False means it
    pays on hit.'''

    if ( IsHigh and Spot >= Strike ) or ( not IsHigh and Spot <= Strike ):
        if IsDelayed:
            return exp( -Rd * Texp )
        else:
            return 1

    if Vol <= 0 or Texp <= 0: return 0

    Alpha = log( Strike / float( Spot ) )
    Mu    = Rd - Rf - Vol * Vol / 2.

    if IsDelayed:
        if IsHigh:
            Price = exp( -Rd * Texp ) * ( cnorm( ( -Alpha + Mu * Texp ) / Vol / sqrt( Texp ) ) \
                  + exp( 2 * Mu * Alpha / Vol / Vol ) * cnorma( ( -Alpha - Mu * Texp ) / Vol / sqrt( Texp ) ) )
        else:
            Price = exp( -Rd * Texp ) * ( cnorm( (  Alpha - Mu * Texp ) / Vol / sqrt( Texp ) ) \
                  + exp( 2 * Mu * Alpha / Vol / Vol ) * cnorma( (  Alpha + Mu * Texp ) / Vol / sqrt( Texp ) ) )
    else:
        MuHat = sqrt( Mu * Mu + 2 * Rd * Vol * Vol )
        if IsHigh:
            Price = exp( Alpha / Vol / Vol * ( Mu - MuHat ) ) * cnorm( ( -Alpha + MuHat * Texp ) / Vol / sqrt( Texp ) ) \
                  + exp( Alpha / Vol / Vol * ( Mu + MuHat ) ) * cnorm( ( -Alpha - MuHat * Texp ) / Vol / sqrt( Texp ) )
        else:
            Price = exp( Alpha / Vol / Vol * ( Mu + MuHat ) ) * cnorm( (  Alpha + MuHat * Texp ) / Vol / sqrt( Texp ) ) \
                  + exp( Alpha / Vol / Vol * ( Mu - MuHat ) ) * cnorm( (  Alpha - MuHat * Texp ) / Vol / sqrt( Texp ) )

    return Price

def BSKnockout( IsCall, Spot, Strike, KO, IsUp, Vol, Texp, Rd, Rf ):
    '''Knockout option with a continuous barrier: price under constant vol, constant drift BS model.'''

    if ( Spot >= KO and IsUp ) or ( Spot <= KO and not IsUp ): return 0. # knocked

    Mu = Rd - Rf
    SqrtT = sqrt( Texp )

    # as per Haug

    Phi = IsCall and 1 or -1
    Eta = IsUp and -1 or 1

    m  = ( Mu - 0.5 * Vol * Vol ) / Vol / Vol
    Lambda = sqrt( m * m + 2. * Mu / Vol / Vol )
    x1 = log( Spot / Strike ) / Vol / SqrtT + ( 1 + m ) * Vol * SqrtT
    x2 = log( Spot / KO ) / Vol / SqrtT + ( 1 + m ) * Vol * SqrtT
    y1 = log( KO * KO / Spot / Strike ) / Vol / SqrtT + ( 1 + m ) * Vol * SqrtT
    y2 = log( KO / Spot ) / Vol / SqrtT + ( 1 + m ) * Vol * SqrtT

    A = Phi * Spot * exp( -Rf * Texp ) * cnorm( Phi * x1 ) - Phi * Strike * exp( -Rd * Texp ) * cnorma( Phi * x1 - Phi * Vol * SqrtT )
    B = Phi * Spot * exp( -Rf * Texp ) * cnorm( Phi * x2 ) - Phi * Strike * exp( -Rd * Texp ) * cnorma( Phi * x2 - Phi * Vol * SqrtT )
    C = Phi * Spot * exp( -Rf * Texp ) * ( KO / Spot ) ** ( 2 * ( m + 1 ) ) * cnorm( Eta * y1 ) - Phi * Strike * exp( -Rd * Texp ) * ( KO / Spot ) ** ( 2 * m ) * cnorm( Eta * y1 - Eta * Vol * SqrtT )
    D = Phi * Spot * exp( -Rf * Texp ) * ( KO / Spot ) ** ( 2 * ( m + 1 ) ) * cnorm( Eta * y2 ) - Phi * Strike * exp( -Rd * Texp ) * ( KO / Spot ) ** ( 2 * m ) * cnorm( Eta * y2 - Eta * Vol * SqrtT )

    if Strike < KO:
        if IsCall and IsUp:
            return A - B + C - D
        elif IsCall and not IsUp:
            return B - D
        elif not IsCall and IsUp:
            return A - C
        else:
            return 0
    else:
        if IsCall and IsUp:
            return 0
        elif IsCall and not IsUp:
            return A - C
        elif not IsCall and IsUp:
            return B - D
        else:
            return A - B + C - D

def WhaleyPremium( IsCall, Fwd, Strike, Vol, Texp, Df, Tr ):
    '''
    Early exercise premium for american futures options based on Whaley approximation
    formula. To compute the options prices, this needs to be added to the european
    options prices.
    '''
    if Texp <= 0.:
        return False,0.

    T   = Texp
    K   = Strike
    D   = Df
    Phi = (IsCall and 1 or -1)

    # handle zero vol case explicitly
    if Vol == 0.0:
        eePrem = max(Phi*(Fwd-Strike)*(1. - D), 0.)
        return ( bool(eePrem > 0.), eePrem )

    k = (D==1.) and 2./Tr/Vol/Vol or -2.*log(D)/Tr/Vol/Vol/(1-D)
    # the expression in the middle is really the expression on the right in the limit D -> 1
    # note that lim_{D -> 1.} log(D)/(1-D) = -1.

    try:

        if Phi == 1:
            q2=(1.+sqrt(1.+4.*k))/2.
            def EarlyExerBdry( eeb ):
                x = D*BSOptFwd(True,eeb,K,Vol,T) + (1.-D*cnorm(fd1(eeb,K,Vol,T)))*eeb/q2 - eeb + K
                return x

            eeBdry = D*BSOptFwd(True,Fwd,K,Vol,T) + (1.-D*cnorm(fd1(Fwd,K,Vol,T)))*Fwd/q2 + K
            eeBdry = newton(EarlyExerBdry,eeBdry)
            if Fwd >= eeBdry:
                eePrem = -D*BSOptFwd(True,Fwd,K,Vol,T) + Fwd - K
                earlyExercise = True
            else:
                A2=(eeBdry/q2)*(1.-D*cnorm(fd1(eeBdry,K,Vol,T)))
                eePrem = A2 * pow(Fwd/eeBdry,q2)
                earlyExercise = False
        elif Phi == -1:
            q1=(1.-sqrt(1.+4.*k))/2.
            def EarlyExerBdry( eeb ):
                x = D*BSOptFwd(False,eeb,K,Vol,T) - (1.-D*cnorm(-fd1(eeb,K,Vol,T)))*eeb/q1 + eeb - K
                return x

            eeBdry = -D*BSOptFwd(False,Fwd,K,Vol,T) + (1.-D*cnorm(-fd1(Fwd,K,Vol,T)))*Fwd/q1 + K
            eeBdry = newton(EarlyExerBdry,eeBdry)
            if Fwd <= eeBdry:
                eePrem = -D*BSOptFwd(False,Fwd,K,Vol,T) + K - Fwd
                earlyExercise = True
            else:
                A1=-(eeBdry/q1)*(1.-D*cnorm(-fd1(eeBdry,K,Vol,T)))
                eePrem = A1 * pow(Fwd/eeBdry,q1)
                earlyExercise = False
        else:
            raise ValueError, 'option type can only be call or put'

    except:
        eePrem = max( Phi * ( Fwd - Strike ) - Phi * Df * ( Fwd - Strike ), 0. )
        earlyExercise = True

    return earlyExercise, eePrem

def WhaleyDelta( IsCall, Spot, Fwd, Strike, Vol, Texp, Df, Tr, D,\
                deltaTerms='FORWARD', smileTerms='RISK', premiumTerms='BASE' ):
    '''
    This calculates the delta for american options under various conventions.
    D = discount until Texp (Df < D)
    '''
    Blip = .0001*Fwd

    def ECall(Fwd, Strike, Vol, Texp, Df):
        return Df * BSOptFwd(True, Fwd, Strike, Vol, Texp)
    def EPut(Fwd, Strike, Vol, Texp, Df):
        return Df * BSOptFwd(False, Fwd, Strike, Vol, Texp)

    def ACall(Fwd, Strike, Vol, Texp, Df, Tr, D):
        return ECall(Fwd, Strike, Vol, Texp, Df)+WhaleyPremium(True, Fwd, Strike, Vol, Texp, D, Texp)[1] * Df/D
    def APut(Fwd, Strike, Vol, Texp, Df, Tr, D):
        return EPut(Fwd, Strike, Vol, Texp, Df)+WhaleyPremium(False, Fwd, Strike, Vol, Texp, D, Texp)[1] * Df/D

    def Price( Fwd, Strike, Vol, Texp, Df, Tr, D ):
        if IsCall:
            return ACall( Fwd, Strike, Vol, Texp, Df, Tr, D )
        else:
            return APut( Fwd, Strike, Vol, Texp, Df, Tr, D )

    if premiumTerms=='RISK':
        PriceMid = Price( Fwd, Strike, Vol, Texp, Df, Tr, D )
    PriceUp = Price( Fwd+Blip, Strike, Vol, Texp, Df, Tr, D )
    PriceDn = Price( Fwd-Blip, Strike, Vol, Texp, Df, Tr, D )
    fD = (PriceUp-PriceDn)/2./Blip

    if deltaTerms=='FORWARD':
        if smileTerms=='RISK':
            if premiumTerms=='BASE':
                fD = fD
            else:
                fD = fD - PriceMid / Fwd
        else:
            if premiumTerms=='BASE':
                fD = - fD * Fwd / Strike
            else:
                fD = - fD * Fwd / Strike + PriceMid / Strike
        return fD  / Df
    else:
        if smileTerms=='RISK':
            if premiumTerms=='BASE':
                fD = fD * Fwd / Spot
            else:
                fD = fD * Fwd / Spot - PriceMid / Spot
        else:
            if premiumTerms=='BASE':
                fD = - fD * Fwd / Strike
            else:
                fD = - fD * Fwd / Strike + PriceMid / Strike
        return fD

def fd1(Fwd,K,Vol,T):
    return log(Fwd/K)/Vol/sqrt(T) + Vol*sqrt(T)/2.

def fd2(Fwd,K,Vol,T):
    return log(Fwd/K)/Vol/sqrt(T) - Vol*sqrt(T)/2.

def BAWPremium( IsCall, Fwd, Strike, Vol, Texp, rf, rd ):
    '''
    Early exercise premium for american spot options based on Barone-Adesi, Whaley
    approximation formula. To compute the options prices, this needs to be added to
    the european options prices.
    '''
    if Texp <= 0. or Vol <=0:
        return 0.

    T   = Texp
    K   = Strike
    D   = exp( -rf * Texp)
    Dq  = exp( -rd * Texp )
    Phi = (IsCall and 1 or -1)

    k = (D==1.) and 2./Vol/Vol or 2.* rf/Vol/Vol/(1-D)
    # the expression in the middle is really the expression on the right in the limit D -> 1
    # note that lim_{D -> 1.} log(D)/(1-D) = -1.

    beta = 2.*(rf-rd)/Vol/Vol
    if Phi == 1:
        q2=(-(beta-1.)+sqrt((beta-1.)**2+4.*k))/2.
        def EarlyExerBdry( eeb ):
            x = D*BSOptFwd(True,eeb,K,Vol,T) + (1.-Dq*cnorm(fd1(eeb,K,Vol,T)))*eeb/q2 - eeb + K
            return x

        eeBdry = D*BSOptFwd(True,Fwd,K,Vol,T) + (1.-Dq*cnorm(fd1(Fwd,K,Vol,T)))* Fwd/q2 + K
        eeBdry = newton(EarlyExerBdry,eeBdry)
        if Fwd >= eeBdry:
            eePrem = -D*BSOptFwd(True,Fwd,K,Vol,T) + Fwd - K
        else:
            A2=(eeBdry/q2)*(1.-Dq*cnorm(fd1(eeBdry,K,Vol,T)))
            eePrem = A2 * pow(Fwd/eeBdry,q2)
    elif Phi == -1:
        q1=(-(beta-1.)-sqrt((beta-1.)**2+4.*k))/2.
        def EarlyExerBdry( eeb ):
            x = D*BSOptFwd(False,eeb,K,Vol,T) - (1.-Dq*cnorm(-fd1(eeb,K,Vol,T)))*eeb/q1 + eeb - K
            return x

        eeBdry = -D*BSOptFwd(False,Fwd,K,Vol,T) + (1.-Dq*cnorm(-fd1(Fwd,K,Vol,T)))*Fwd/q1 + K
        eeBdry = brentq(EarlyExerBdry,1e-12, K)
        if Fwd <= eeBdry:
            eePrem = -D*BSOptFwd(False,Fwd,K,Vol,T) + K - Fwd
        else:
            A1=-(eeBdry/q1)*(1.-Dq*cnorm(-fd1(eeBdry,K,Vol,T)))
            eePrem = A1 * pow(Fwd/eeBdry,q1)
    else:
        raise ValueError, 'option type can only be call or put'

    return eePrem

def BAWAmOptPricer( IsCall, Fwd, Strike, Vol, Texp, rf, rd ):
    prem = BAWPremium( IsCall, Fwd, Strike, Vol, Texp, rf, rd )
    D    = exp( -rf * Texp)
    Euro = D * BSOptFwd(IsCall, Fwd, Strike, Vol, Texp)
    return Euro + prem

def IBAWVol( IsCall, Fwd, Strike, Price, Texp, rf, rd):
    '''
    Implied vol for american options according to BAW
    '''
    Df   = exp( -rf * Texp)
    if Texp <= 0.:
        raise ValueError, 'maturity must be > 0'

    def f( vol ):
        return Price - Df * BSOptFwd(IsCall, Fwd, Strike, vol, Texp) - BAWPremium(IsCall, Fwd, Strike, vol, Texp, rf, rd)

    Vol = brentq(f,0.001, 10.0)

    if Vol<0 or Vol>100.:
        raise ValueError, 'the implied vol solver fails'

    return Vol

def LogNormalPaths(mu, cov, fwd, numPaths):
    ''' mu and fwd are 1d lists/arrays (1xn); cov is a 2d scipy.array (nxn); numPaths is int '''
    return (fwd*scipy.exp(numpy.random.multivariate_normal(mu, cov, numPaths) - 0.5*cov.diagonal())).transpose()
