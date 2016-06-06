//+------------------------------------------------------------------+
//|                                             TrendStrength_v2.mq5 |
//|                                Copyright © 2013, TrendLaboratory |
//|            http://finance.groups.yahoo.com/group/TrendLaboratory |
//|                                   E-mail: igorad2003@yahoo.co.uk |
//+------------------------------------------------------------------+
#property copyright "Copyright © 2013, TrendLaboratory"
#property link      "http://finance.groups.yahoo.com/group/TrendLaboratory"

//--- indicator settings
#property indicator_separate_window
#property indicator_buffers 5
#property indicator_plots   3


#property indicator_label1  "Smoothed RSI"
#property indicator_type1   DRAW_LINE
#property indicator_color1  DarkGray
#property indicator_style1  STYLE_SOLID
#property indicator_width1  1

#property indicator_label2  "UpTrend"
#property indicator_type2   DRAW_LINE
#property indicator_color2  DeepSkyBlue
#property indicator_style2  STYLE_SOLID
#property indicator_width2  2

#property indicator_label3  "DnTrend"
#property indicator_type3   DRAW_LINE
#property indicator_color3  OrangeRed
#property indicator_style3  STYLE_SOLID
#property indicator_width3  2

//---- indicator parameters

input ENUM_APPLIED_PRICE   Price          = PRICE_CLOSE;    // Applied Price
input int                  RSILength      =          14;    // RSI Period
input int                  Smooth         =           5;    // Smoothing Period
input double               K              =       4.236;    // Multiplier


//---- indicator buffers
double smRSI[];
double upTrend[];
double dnTrend[]; 

double rsi[];
double trend[];

double delta1[2], delta2[2], upband[2], loband[2], alpha;
int    rsi_handle; 
datetime prevTime;
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
void OnInit()
{
//--- indicator buffers mapping
   SetIndexBuffer(0,   smRSI,INDICATOR_DATA); 
   SetIndexBuffer(1, upTrend,INDICATOR_DATA); 
   SetIndexBuffer(2, dnTrend,INDICATOR_DATA); 
   
   SetIndexBuffer(3,     rsi,INDICATOR_CALCULATIONS);
   SetIndexBuffer(4,   trend,INDICATOR_CALCULATIONS);
//---
   IndicatorSetInteger(INDICATOR_DIGITS,_Digits + 1);
//--- 
   string short_name = "TrendStrength_v2("+priceToString(Price)+","+(string)RSILength+","+(string)Smooth+","+DoubleToString(K,3)+")";
   IndicatorSetString(INDICATOR_SHORTNAME,short_name);
//--- sets first bar from what index will be drawn
   int begin = (int)MathMax(2,RSILength + Smooth); 
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin);
   PlotIndexSetInteger(1,PLOT_DRAW_BEGIN,begin);
   PlotIndexSetInteger(2,PLOT_DRAW_BEGIN,begin);
//--- 
   rsi_handle = iRSI(NULL,0,RSILength,Price);
   alpha = 1.0/RSILength;
//--- initialization done
}
//+------------------------------------------------------------------+
//| TrendStrength_v2                                                 |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,const int prev_calculated,
                const datetime &Time[],
                const double   &Open[],
                const double   &High[],
                const double   &Low[],
                const double   &Close[],
                const long     &TickVolume[],
                const long     &Volume[],
                const int      &Spread[])
{
   int shift, limit, copied=0;
   double hiRSI, loRSI, rangeRSI;
//--- preliminary calculations
   if(prev_calculated == 0)  
   {
   limit = RSILength + Smooth;
   ArrayInitialize(  smRSI,0);
   ArrayInitialize(upTrend,0);   
   ArrayInitialize(dnTrend,0);
   }
   else limit = prev_calculated-1; 
      
   copied = CopyBuffer(rsi_handle,0,0,rates_total-1,rsi);
   if(copied<0)
   {
   Print("not all RSI copied. Will try on next tick Error =",GetLastError(),", copied =",copied);
   return(0);
   } 
        
//--- the main loop of calculations
   for(shift=limit;shift<rates_total;shift++)
   {
      if(prevTime < Time[shift])
      {
      delta1[1] = delta1[0];
      delta2[1] = delta2[0];
      upband[1] = upband[0];
      loband[1] = loband[0]; 
      
      prevTime  = Time[shift];
      }
   
   
   smRSI[shift] = smRSI[shift-1] + 2./(Smooth+1)*(rsi[shift] - smRSI[shift-1]);
     
      if(smRSI[shift] > smRSI[shift-1]) {hiRSI = smRSI[shift]; loRSI = smRSI[shift-1];}
      else 
      if(smRSI[shift] < smRSI[shift-1]) {hiRSI = smRSI[shift-1]; loRSI = smRSI[shift];}
      else
      {hiRSI = smRSI[shift]; loRSI = smRSI[shift];}
   
   rangeRSI = hiRSI - loRSI;
   
   delta1[0] = delta1[1] + alpha*(rangeRSI  - delta1[1]);
   delta2[0] = delta2[1] + alpha*(delta1[0] - delta2[1]);             
   
   upband[0] = smRSI[shift] + K*delta2[0]; 
   loband[0] = smRSI[shift] - K*delta2[0]; 
      
   trend[shift] = trend[shift-1];
   
   if (smRSI[shift] > upband[1]) trend[shift] = 1; 
	if (smRSI[shift] < loband[1]) trend[shift] =-1;
   
   upTrend[shift] = EMPTY_VALUE;
   dnTrend[shift] = EMPTY_VALUE;
     
      if(trend[shift] > 0)
	   {
	   if(loband[0] < loband[1]) loband[0] = loband[1];
	   upTrend[shift] = loband[0];
	   }
	   else
	   if(trend[shift] < 0)
	   {
	   if(upband[0] > upband[1]) upband[0] = upband[1];
	   dnTrend[shift] = upband[0];
	   }
	   
   }
//--- done
   return(rates_total);
}
//+------------------------------------------------------------------+
string priceToString(ENUM_APPLIED_PRICE app_price)
{
   switch(app_price)
   {
   case PRICE_CLOSE   :    return("Close");
   case PRICE_HIGH    :    return("High");
   case PRICE_LOW     :    return("Low");
   case PRICE_MEDIAN  :    return("Median");
   case PRICE_OPEN    :    return("Open");
   case PRICE_TYPICAL :    return("Typical");
   case PRICE_WEIGHTED:    return("Weighted");
   default            :    return("");
   }
}
