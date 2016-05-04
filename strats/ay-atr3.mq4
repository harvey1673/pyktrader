//+------------------------------------------------------------------+
//|                                                      ay-atr2.mq4 |
//|                      Copyright © 2010, MetaQuotes Software Corp. |
//|                                        http://www.metaquotes.net |
//+------------------------------------------------------------------+
#property copyright "Copyright © 2010, MetaQuotes Software Corp."
#property link      "http://www.metaquotes.net"

#property indicator_chart_window
#property indicator_buffers 4
#property indicator_color1 Blue
#property indicator_color2 Red
#property indicator_color3 DarkGreen
#property indicator_color4 Brown
//---- input parameters
extern int       per=20;
extern int       tf=0;
extern double    percent = 0.7;

//---- buffers
double Buffer1[];
double Buffer2[];
double Buffer3[];
double Buffer4[];
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
  {
//---- indicators
   SetIndexStyle(0,DRAW_LINE);
   SetIndexBuffer(0,Buffer1);
   SetIndexStyle(1,DRAW_LINE);
   SetIndexBuffer(1,Buffer2);
   SetIndexStyle(2,DRAW_LINE);
   SetIndexBuffer(2,Buffer3);
   SetIndexStyle(3,DRAW_LINE);
   SetIndexBuffer(3,Buffer4);   
   

//----
   return(0);
  }
//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
int deinit()
  {
//----
   
//----
   return(0);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int start()
  {
   int limit, i, j;
   int counted_bars=IndicatorCounted();
   //---- check for possible errors
   if(counted_bars<0) return(-1);
   //---- the last counted bar will be recounted
   if(counted_bars>0) counted_bars--;
   limit=Bars-counted_bars;
     
   for(i=limit; i>=0; i--)
   {
      int ibs_d1 = iBarShift(NULL,tf,Time[i]) ;
      double atrtf = iATR(NULL, tf, per, ibs_d1 + 1);

      Buffer1[i] = Open[i] + atrtf;
      Buffer2[i] = Open[i] - atrtf; 
      Buffer3[i] = Open[i] + (percent*atrtf);
      Buffer4[i] = Open[i] - (percent*atrtf);      
     

   }
   return(0);
  }

//+------------------------------------------------------------------+