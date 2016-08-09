//+------------------------------------------------------------------+
//|                                                  ATRStops_v1.mq4 |
//|                                  Copyright © 2006, Forex-TSD.com |
//|                         Written by IgorAD,igorad2003@yahoo.co.uk |   
//|            http://finance.groups.yahoo.com/group/TrendLaboratory |                                      
//+------------------------------------------------------------------+
#property copyright "Copyright © 2006, Forex-TSD.com "
#property link      "http://www.forex-tsd.com/"

#property indicator_separate_window
#property indicator_buffers 2
#property indicator_color1 Blue
#property indicator_color2 Red


//---- input parameters
extern int Length=10;
extern int ATRperiod=5;
extern int Kv=2.5;

//---- indicator buffers
double UpBuffer1[];
double DnBuffer1[];
double smin[];
double smax[];
double trend[];
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
  int init()
  {
   string short_name;
//---- indicator line
   SetIndexStyle(0,DRAW_LINE);
   SetIndexStyle(1,DRAW_LINE);
   IndicatorBuffers(5);
   SetIndexBuffer(0,UpBuffer1);
   SetIndexBuffer(1,DnBuffer1);
   SetIndexBuffer(2,smin);
   SetIndexBuffer(3,smax);
   SetIndexBuffer(4,trend);
//---- name for DataWindow and indicator subwindow label
   short_name="ATRStops("+Length+")";
   IndicatorShortName(short_name);
   SetIndexLabel(0,"Up");
   SetIndexLabel(1,"Dn");
//----
   SetIndexDrawBegin(0,Length);
   SetIndexDrawBegin(1,Length);
//----
   return(0);
  }

//+------------------------------------------------------------------+
//| ATRStops_v1                                                     |
//+------------------------------------------------------------------+
int start()
  {
   
   int shift,limit, counted_bars=IndicatorCounted();
   
   if ( counted_bars > 0 )  limit=Bars-counted_bars;
   if ( counted_bars < 0 )  return(0);
   if ( counted_bars ==0 )  limit=Bars-Length-1; 
     
	for(shift=limit;shift>=0;shift--) 
   {	
      smin[shift] = -100000; smax[shift] = 100000;
      for (int i = Length-1;i>=0;i--)
      {
      smin[shift] = MathMax( smin[shift], High[shift+i] - Kv*iATR(NULL,0,ATRperiod,shift+i)); 
      smax[shift] = MathMin( smax[shift], Low[shift+i] + Kv*iATR(NULL,0,ATRperiod,shift+i));
      }
	
	  trend[shift]=trend[shift+1];
	  if ( Close[shift] > smax[shift+1] ) trend[shift] =  1;
	  if ( Close[shift] < smin[shift+1] ) trend[shift] = -1;
	
	  if ( trend[shift] >0 ) 
	  {
	  if( smin[shift]<smin[shift+1] ) smin[shift]=smin[shift+1];
	  UpBuffer1[shift]=smin[shift];
	  DnBuffer1[shift] = EMPTY_VALUE;
	  }
	  if ( trend[shift] <0 ) 
	  {
	  if( smax[shift]>smax[shift+1] ) smax[shift]=smax[shift+1];
	  UpBuffer1[shift]=EMPTY_VALUE;
	  DnBuffer1[shift] = smax[shift];
	  }
	
	}
	return(0);	
 }

