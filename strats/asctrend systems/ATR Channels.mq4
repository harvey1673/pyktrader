//+------------------------------------------------------------------+
//|                                                 ATR Channels.mq4 |
//|                         Copyright © 2005, Luis Guilherme Damiani |
//|                                      http://www.damianifx.com.br |
//+------------------------------------------------------------------+

#property copyright "Copyright © 2005, Luis Guilherme Damiani"
#property link      "http://www.damianifx.com.br"
#property indicator_chart_window
#property  indicator_buffers 7
#property  indicator_color1  Aqua //Moving Average
#property  indicator_color2  DeepSkyBlue // Lower band 1
#property  indicator_color3  DeepSkyBlue // Upper band 1
#property  indicator_color4  RoyalBlue // Lower band 2
#property  indicator_color5  RoyalBlue // Upper band 2
#property  indicator_color6  BlueViolet // Lower band 3
#property  indicator_color7  BlueViolet // Upper band 3
//---- indicator buffers
double     MA_Buffer0[];
double     Ch1up_Buffer1[];
double     Ch1dn_Buffer2[];
double     Ch2up_Buffer3[];
double     Ch2dn_Buffer4[];
double     Ch3up_Buffer5[];
double     Ch3dn_Buffer6[];

//---- input parameters
extern int       PeriodsATR=18;
extern int       MA_Periods=49;
extern int       MA_type=MODE_LWMA;
extern double       Mult_Factor1= 1.6;
extern double       Mult_Factor2= 3.2;
extern double       Mult_Factor3= 4.8;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
  {
  string mat;
 
//---7- indicators
// MA
   SetIndexStyle(0,DRAW_LINE);
   SetIndexBuffer(0,MA_Buffer0);
   SetIndexDrawBegin(0,0);
   /*if (MA_type==MODE_LWMA)SetIndexLabel(0,"WMA"+MA_Periods) else 
   {
      if (MA_type==MODE_SMA) SetIndexLabel(0,"SMA"+MA_Periods) else
      {
         if (MA_type==MODE_EMA) SetIndexLabel(0,"EMA"+MA_Periods) else 
         SetIndexLabel(0,"SMMA"+MA_Periods);
      }; 
   };*/      
  // ATR 1 up
   SetIndexStyle(1,DRAW_LINE);
   SetIndexBuffer(1,Ch1up_Buffer1);
   SetIndexDrawBegin(1,0);
   SetIndexLabel(1,"ATRu "+PeriodsATR+", "+Mult_Factor1);
  // ATR 1 down
   SetIndexStyle(2,DRAW_LINE);
   SetIndexBuffer(2,Ch1dn_Buffer2);
   SetIndexDrawBegin(2,0);
   SetIndexLabel(2,"ATRd "+PeriodsATR+", "+Mult_Factor1);
// ATR 2 up
   SetIndexStyle(3,DRAW_LINE);
   SetIndexBuffer(3,Ch2up_Buffer3);
   SetIndexDrawBegin(3,0);
   SetIndexLabel(3,"ATRu "+PeriodsATR+", "+Mult_Factor2);
  // ATR 2 down
   SetIndexStyle(4,DRAW_LINE);
   SetIndexBuffer(4,Ch2dn_Buffer4);
   SetIndexDrawBegin(4,0);
   SetIndexLabel(4,"ATRd "+PeriodsATR+", "+Mult_Factor2);
   // ATR 3 up
   SetIndexStyle(5,DRAW_LINE);
   SetIndexBuffer(5,Ch3up_Buffer5);
   SetIndexDrawBegin(5,0);
   SetIndexLabel(5,"ATRu "+PeriodsATR+", "+Mult_Factor3);
  // ATR 3 down
   SetIndexStyle(6,DRAW_LINE);
   SetIndexBuffer(6,Ch3dn_Buffer6);
   SetIndexDrawBegin(6,0);
   SetIndexLabel(6,"ATRd "+PeriodsATR+", "+Mult_Factor3);
//----
   return(0);
  }
//+------------------------------------------------------------------+
//| Custor indicator deinitialization function                       |
//+------------------------------------------------------------------+
int deinit()
  {//---- 
   
//----
   return(0);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int start()
  {
   int fixed_bars=IndicatorCounted();
   for(int i=0;i< Bars - fixed_bars;i++)
     {
         double atr=iATR(NULL,0,PeriodsATR,i);
         double ma=iMA(NULL,0,MA_Periods,0,MA_type,PRICE_TYPICAL,i);
         MA_Buffer0[i]=ma;
         Ch1up_Buffer1[i]=ma+atr*Mult_Factor1;
         Ch1dn_Buffer2[i]=ma-atr*Mult_Factor1;
         
         Ch2up_Buffer3[i]=ma+atr*Mult_Factor2;
         Ch2dn_Buffer4[i]=ma-atr*Mult_Factor2;
         
         Ch3up_Buffer5[i]=ma+atr*Mult_Factor3;
         Ch3dn_Buffer6[i]=ma-atr*Mult_Factor3;
      }  
   
//---- 
   
//----
   return(0);
  }

