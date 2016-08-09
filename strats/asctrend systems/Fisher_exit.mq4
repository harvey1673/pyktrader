//+------------------------------------------------------------------+
//|                                                  Fisher_exit.mq4 |
//|                                                          Kalenzo |
//|                                                  simone@konto.pl |
//+------------------------------------------------------------------+
#property copyright "Kalenzo"
#property link      "simone@konto.pl"
#property indicator_buffers 2
#property indicator_color1 Blue
#property indicator_color2 Red
double exitL[],exitS[];

#property indicator_chart_window
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
  {
//---- indicators
   SetIndexStyle(0,DRAW_ARROW,EMPTY,1);
   SetIndexStyle(1,DRAW_ARROW,EMPTY,1);
   
   SetIndexBuffer(0,exitL);
   SetIndexBuffer(1,exitS);
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
   int limit;
   int counted_bars=IndicatorCounted();
   if(counted_bars<0) counted_bars=0;
   if(counted_bars>0) counted_bars--;
   limit=Bars-counted_bars;
//----
   for(int i = 0 ;i < limit ;i++)
   {
      double f1u = iCustom(Symbol(),0,"Fisher_v1",10,4,0,0,i);//up
      double f2u = iCustom(Symbol(),0,"Fisher_v1",10,4,0,0,i+1);//up
      double f3u = iCustom(Symbol(),0,"Fisher_v1",10,4,0,0,i+2);//up
      
      double f1d = iCustom(Symbol(),0,"Fisher_v1",10,4,0,1,i);//dn
      double f2d = iCustom(Symbol(),0,"Fisher_v1",10,4,0,1,i+1);//dn
      double f3d = iCustom(Symbol(),0,"Fisher_v1",10,4,0,1,i+2);//dn
      
      if(f1u < f2u && f2u > f3u)
      {
         exitL[i] = Low[i];
         exitS[i] = 0.0; 
      }
      else if(f1d > f2d && f2d < f3d)
      {
        exitS[i] = High[i];
        exitL[i] = 0.0; 
      }
   }
//----
   return(0);
  }
//+------------------------------------------------------------------+