//+------------------------------------------------------------------+
//|                                                   BAT ATR v2.mq4 |
//+------------------------------------------------------------------+
#property  copyright "Copyright Team Aphid"
#property  link      ""
//---- indicator settings
#property  indicator_chart_window
#property  indicator_buffers 3
#property  indicator_color1  RoyalBlue
#property  indicator_color2  RoyalBlue
#property  indicator_color3  255255255
#property  indicator_width3  1

#define EMPV	-1

//---- indicator parameters
extern int ATRPeriod = 10;
extern double Factor = 2;
extern bool MedianPrice = true;
extern bool MedianBase = true;
extern bool CloseBase = false;
extern double distance = 0;

//---- indicator buffers
double     up_line[];
double     dn_line[];
double     sig_dot[];

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
{
	//---- drawing settings  
	SetIndexStyle(0,DRAW_LINE);
	SetIndexDrawBegin(0,ATRPeriod);
	SetIndexBuffer(0,up_line);
	SetIndexEmptyValue(0,EMPV);
	SetIndexStyle(1,DRAW_LINE);
	SetIndexDrawBegin(1,ATRPeriod);
	SetIndexBuffer(1,dn_line);
	SetIndexEmptyValue(1,EMPV);
	SetIndexStyle(2,DRAW_ARROW);
	SetIndexArrow(2,108);
	SetIndexDrawBegin(2,ATRPeriod);
	SetIndexBuffer(2,sig_dot);
	SetIndexEmptyValue(2,EMPV);

	IndicatorDigits(MarketInfo(Symbol(),MODE_DIGITS)+2);
	//---- name for DataWindow and indicator subwindow label
	IndicatorShortName("BAT ATR("+ATRPeriod+" * "+Factor+")");
	SetIndexLabel(0,"Support");
	SetIndexLabel(1,"Resistance");
	//---- initialization done
	return(0);
}
//+------------------------------------------------------------------+
//| Moving Averages Convergence/Divergence                           |
//+------------------------------------------------------------------+
int start()
{
	int counted_bars=IndicatorCounted();
	int limit;
	static int dir=1;
	double PrevUp, PrevDn;
	double CurrUp, CurrDn;
	double PriceLvl;
	double PriceHLorC;
	static double LvlUp=0,LvlDn=100000;
	//---- check for possible errors
	if (counted_bars<0) return(-1);
	//---- last counted bar will be recounted
	if (counted_bars>=ATRPeriod) limit=Bars-counted_bars;
	else limit=Bars-ATRPeriod-1;
	if (limit<0) return (-1);
	//---- fill in buffervalues
	for(int i=limit; i>0; i--) {
		if (MedianPrice) PriceLvl = (High[i] + Low[i])/2;
		else PriceLvl = Close[i];  
		
		CurrUp=PriceLvl - (iATR(NULL,0,ATRPeriod,i) * Factor);
		CurrDn=PriceLvl + (iATR(NULL,0,ATRPeriod,i) * Factor);

		up_line[i]=EMPV;
		dn_line[i]=EMPV;
		sig_dot[i]=EMPV;

		if (dir>0) {
			if (CloseBase) PriceHLorC = Close[i]; else PriceHLorC=Low[i];
			if (PriceHLorC<LvlUp) {
				dir=-1;
				LvlDn=CurrDn;
				dn_line[i]=LvlDn+distance;
				sig_dot[i]=LvlDn+distance;
			} else {
				if (CurrUp>LvlUp) LvlUp=CurrUp;
				up_line[i] = LvlUp-distance;
			}
		} else {
			if (CloseBase) PriceHLorC = Close[i]; else PriceHLorC=High[i];
			if (PriceHLorC>LvlDn) {
				dir=1;
				LvlUp=CurrUp;
				up_line[i]=LvlUp-distance;
				sig_dot[i]=LvlUp-distance;
			} else {
				if (CurrDn<LvlDn) LvlDn=CurrDn;
				dn_line[i] = LvlDn+distance;
			}
		}
	}
	sig_dot[0]=EMPV;
	CurrUp=PriceLvl - (iATR(NULL,0,ATRPeriod,0) * Factor);
	CurrDn=PriceLvl + (iATR(NULL,0,ATRPeriod,0) * Factor);
	if (dir>0) {
		if (CloseBase) PriceHLorC = Close[0]; else PriceHLorC=Low[0];
		if (PriceHLorC<LvlUp) {
			dn_line[0]=CurrDn+distance;
			sig_dot[0]=CurrDn+distance;
		} else {
			if (CurrUp>LvlUp) up_line[0] = CurrUp-distance;
			up_line[0] = LvlUp-distance;
		}
	} else {
		if (CloseBase) PriceHLorC = Close[0]; else PriceHLorC=High[0];
		if (PriceHLorC>LvlDn) {
			up_line[0]=CurrUp-distance;
			sig_dot[0]=CurrUp-distance;
		} else {
			if (CurrDn<LvlDn) dn_line[0] = CurrDn+distance;
			dn_line[0] = LvlDn+distance;
		}
	}
	//---- done
	return(0);
}