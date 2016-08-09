//+------------------------------------------------------------------+
//|                                                    NRTR Dots.mq4 |
//|                                     Copyright © 2006, Nick Bilak |
//+------------------------------------------------------------------+
#property copyright "Copyright © 2006, Nick Bilak"

//---- indicator settings
#property  indicator_separate_window
#property  indicator_buffers 2
#property  indicator_color1  Magenta
#property  indicator_color2  Aqua
//---- indicator parameters
extern int AveragePeriod=21;
//---- indicator buffers
double e1[];
double e2[];
double tr[],pr[];

int i,bar,trend=1;
double value,price,dK,AvgRange;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
  {
//---- drawing settings
   IndicatorBuffers(4);
   SetIndexStyle(0,DRAW_ARROW);
   SetIndexArrow(0,159);
   SetIndexStyle(1,DRAW_ARROW);
   SetIndexArrow(1,159);
   SetIndexEmptyValue(0,0);
   SetIndexEmptyValue(1,0);
   SetIndexBuffer(0,e1);
   SetIndexBuffer(1,e2);
   SetIndexBuffer(2,tr);
   SetIndexBuffer(3,pr);
//---- name for DataWindow and indicator subwindow label
   IndicatorShortName("NRTR_Dots1("+AveragePeriod+")");
//---- initialization done
   return(0);
   
  }

int start()  {

   int counted_bars=IndicatorCounted();
   if(counted_bars<0) return(-1);
   if(counted_bars>0) counted_bars--;
   int limit=Bars-counted_bars;
   if (counted_bars==0) limit=Bars-AveragePeriod-1;
   double spread=Ask-Bid;
   double ap;
   ap=AveragePeriod;
   for(bar=limit; bar>=0; bar--) {
       e1[bar]=0; e2[bar]=0; tr[bar]=tr[bar+1]; if (tr[bar]==0) tr[bar]=1;
       pr[bar]=pr[bar+1]; 
       AvgRange=0;
       for (i=bar; i<bar+AveragePeriod; i++) {
          AvgRange=AvgRange+MathAbs(spread+High[bar]-Low[bar]);
       }
       dK = AvgRange/ap;
       //if (Close[bar]>10) dK=dK/100.0;
       if (tr[bar] > 0) {
          if (Close[bar] > pr[bar]) pr[bar] = Close[bar];
          value = pr[bar] - dK;
          if (Close[bar] < value) {
             pr[bar] = Close[bar];
             value = pr[bar] + dK;
             tr[bar] = -1;
          }
       }
       if (tr[bar] < 0) {
          if (Close[bar] < pr[bar]) pr[bar] = Close[bar];
          value = pr[bar] + dK;
          if (Close[bar] > value) {
             pr[bar] = Close[bar];
             value = pr[bar] - dK;
             tr[bar] = 1;
          }
       }
      if (tr[bar] < 0) e1[bar]=value; //SetIndexValue(bar, value);
      if (tr[bar] > 0) e2[bar]=value; //SetIndexValue2(bar, value);
   }
}

