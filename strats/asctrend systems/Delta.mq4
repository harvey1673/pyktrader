//+------------------------------------------------------------------+
//|                                                        SmWPR.mq4 |
//|                      Copyright © 2006, MetaQuotes Software Corp. |
//|                                        http://www.metaquotes.net |
//+------------------------------------------------------------------+
#property copyright "Copyright © 2006, MetaQuotes Software Corp."
#property link      "http://www.metaquotes.net"

#property indicator_separate_window
#property indicator_buffers 2
#property indicator_color1 Blue
#property indicator_color2 Red
//---- input parameters

extern int       sper=60;
extern int       fper=13;
extern int       test=0;
extern int       nBars=100;
//---- buffers
double ExtMapBuffer1[];
double ExtMapBuffer2[];
double shift, sdel, fdel, mas, maf, mBar;
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
  {
//---- indicators
   SetIndexStyle(0,DRAW_LINE);
   SetIndexBuffer(0,ExtMapBuffer1);
   SetIndexStyle(1,DRAW_LINE);
   SetIndexBuffer(1,ExtMapBuffer2);
//----
   return(0);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int start()
  {

      for(int shift=Bars-1; shift>0; shift--)
      {
         ExtMapBuffer1[shift]=0;
         ExtMapBuffer2[shift]=0;
      }
   
      if (test==1) {mBar=nBars;} else {mBar=Bars;}

      for(shift=Bars-1; shift>0; shift--)
      {
         mas=iMA(NULL, 0, sper, 0, MODE_EMA, PRICE_CLOSE,shift-1);
         maf=iMA(NULL, 0, fper, 0, MODE_EMA, PRICE_CLOSE,shift-1);
         sdel=MathRound((mas-Close[0])/Point);
         fdel=MathRound((maf-Close[0])/Point);
         if (sdel==0) {sdel=0.0001;}
         if (fdel==0) {fdel=0.0001;}
         if (sdel!=0) {ExtMapBuffer1[shift-1]=sdel;}
         if (fdel!=0) {ExtMapBuffer2[shift-1]=fdel;}
      }
   
   return(0);
  }
//+------------------------------------------------------------------+