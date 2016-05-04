//+------------------------------------------------------------------+
//|                                               ATR Trail Stop.mq4 |
//+------------------------------------------------------------------+

//---- indicator settings
#property  indicator_chart_window
#property  indicator_buffers 2
#property  indicator_color1  RoyalBlue
#property  indicator_width1  0
#property  indicator_style1  0
#property  indicator_color2  RoyalBlue
#property  indicator_width2  0
#property  indicator_style2  0

//---- indicator parameters
extern int BackPeriod = 2000;
extern int ATRPeriod = 20;
extern double Factor = 2;
extern bool MedianPrice = true;
extern bool MedianBase = true;
extern bool CloseBase = false;
extern double distance = 0;


//---- indicator buffers
double     ind_buffer1[];
double     ind_buffer2[];

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
  {
//---- drawing settings  
   //SetIndexStyle(0,DRAW_LINE,EMPTY,2);
   SetIndexStyle(0, DRAW_ARROW);
   SetIndexArrow(0, 159);
   SetIndexDrawBegin(0,ATRPeriod);
   SetIndexBuffer(0,ind_buffer1);
   //SetIndexStyle(1,DRAW_LINE,EMPTY,2);
   SetIndexStyle(1, DRAW_ARROW);
   SetIndexArrow(1, 159);
   SetIndexDrawBegin(1,ATRPeriod);
   SetIndexBuffer(1,ind_buffer2);

   IndicatorDigits(MarketInfo(Symbol(),MODE_DIGITS)+2);
//---- name for DataWindow and indicator subwindow label
   IndicatorShortName("ATR Stop("+ATRPeriod+" * "+Factor+")");
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
   int limit;
   int counted_bars=IndicatorCounted();
   double PrevUp, PrevDn;
   double CurrUp, CurrDn;
   double PriceCurr, PricePrev;
   double PriceLvl;
   double PriceHLorC;
   double LvlUp = 0;
   double LvlDn = 1000;
   int Dir = 1;
   int InitDir;
//---- check for possible errors
   if(counted_bars<0) return(-1);
//---- last counted bar will be recounted
   //if(counted_bars>0) counted_bars--;
   if(counted_bars==0) counted_bars++;
   if (BackPeriod==0) limit=Bars-counted_bars; else limit=BackPeriod;
//---- fill in buffervalues
   InitDir = 0;
   for(int i=limit; i>=0; i--)
   {
      if (MedianPrice) PriceLvl = (High[i] + Low[i])/2;
      else PriceLvl = Close[i];  
      
      if (MedianBase) {
          PriceCurr = (High[i] + Low[i])/2;
          PricePrev = (High[i-1] + Low[i-1])/2;
          }
      else {
          PriceCurr = Close[i];
          PricePrev = Close[i-1];
         }
      
      if(InitDir == 0) {
         CurrUp=PriceCurr - (iATR(NULL,0,ATRPeriod,i) * Factor);
         PrevUp=PricePrev - (iATR(NULL,0,ATRPeriod,i-1) * Factor);
         CurrDn=PriceCurr + (iATR(NULL,0,ATRPeriod,i) * Factor);
         PrevDn=PricePrev + (iATR(NULL,0,ATRPeriod,i-1) * Factor);
           
         if (CurrUp > PrevUp) Dir = 1;
         LvlUp = CurrUp;
         if (CurrDn < PrevDn) Dir = -1;
         LvlDn = CurrDn;
         InitDir = 1;
       
      }
      
      CurrUp=PriceLvl - (iATR(NULL,0,ATRPeriod,i) * Factor);
      CurrDn=PriceLvl + (iATR(NULL,0,ATRPeriod,i) * Factor);
      
      //if (i==0) Comment("Dir:",Dir,",CurrUp:",CurrUp,",PrevUp:",PrevUp,",CurrDn:",CurrDn,",PrevDn:",PrevDn);
      if (Dir == 1) {
         if (CurrUp > LvlUp) {
            ind_buffer1[i] = CurrUp-distance;
            LvlUp = CurrUp;
         }
         else {
            ind_buffer1[i] = LvlUp-distance;
         }
         ind_buffer2[i] = EMPTY_VALUE;
         if (CloseBase) PriceHLorC = Close[i]; else PriceHLorC=Low[i];
         if (PriceHLorC < ind_buffer1[i]) {
            Dir = -1;
            LvlDn = 1000;
         }
      }
      
      if (Dir == -1) {
         if (CurrDn < LvlDn) {
            ind_buffer2[i] = CurrDn+distance;
            LvlDn = CurrDn;
         }
         else {
            ind_buffer2[i] = LvlDn+distance;
         }
         ind_buffer1[i] = EMPTY_VALUE;
         if (CloseBase) PriceHLorC = Close[i]; else PriceHLorC=High[i];
         if (PriceHLorC > ind_buffer2[i]) {
            Dir = 1;
            LvlUp = 0;
         }
      }
      
      if (Dir == 1) {
         if (CurrUp > LvlUp) {
            ind_buffer1[i] = CurrUp-distance;
            LvlUp = CurrUp;
         }
         else {
            ind_buffer1[i] = LvlUp-distance;
         }
         ind_buffer2[i] = EMPTY_VALUE;
         if (CloseBase) PriceHLorC = Close[i]; else PriceHLorC=Low[i];
         if (PriceHLorC < ind_buffer1[i]) {
            Dir = -1;
            LvlDn = 1000;
         }
      }
      
      //if (ind_buffer1[0]!=EMPTY_VALUE && ind_buffer1[1]==EMPTY_VALUE) {ind_buffer1[i+1]=ind_buffer1[i];}
      //if (ind_buffer2[0]!=EMPTY_VALUE && ind_buffer2[1]==EMPTY_VALUE) {ind_buffer2[i+1]=ind_buffer2[i];}
 
   }  
   

//---- done
   return(0);
  }