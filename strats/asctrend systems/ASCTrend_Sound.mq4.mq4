//+-------------------------------------------------------------------+
//|                                     ASCTrendExpert snd e-mail.mq4 |
//|                       Copyright © 2004, MetaQuotes Software Corp. |
//|                                         http://www.metaquotes.net |
//|                                Made/Modified by Alejandro Galindo |
//|                                                                   |
//|                                            You are free to use it |
//|                                                                   |
//|       If you want and if this work/modification is helpful to you |
//|                      send me a PayPal donation to ag@elcactus.com |
//|                                         any help is apreciated :) |
//|                                                           Thanks. |
//+-------------------------------------------------------------------+
//| Original Version ASCTrend1sig_noSound.mq4 
//| Ramdass - Conversion only
//+------------------------------------------------------------------+

#property indicator_chart_window
#property indicator_buffers 2
#property indicator_color1 Magenta
#property indicator_color2 Aqua

//---- input parameters
extern int RISK=3;
extern int CountBars=300;
extern int SoundON=1;
extern int EmailON=0;
  

//---- buffers
double val1[];
double val2[];
int flagval1 = 0;
int flagval2 = 0;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
  {
//---- indicator line
   IndicatorBuffers(2);
   SetIndexStyle(0,DRAW_ARROW);
   SetIndexArrow(0,234);
   SetIndexStyle(1,DRAW_ARROW);
   SetIndexArrow(1,233);
   SetIndexBuffer(0,val1);
   SetIndexBuffer(1,val2);
   GlobalVariableSet("AlertTime"+Symbol()+Period(),CurTime());
   GlobalVariableSet("SignalType"+Symbol()+Period(),OP_SELLSTOP);
//----
   return(0);
  }
  
int deinit()
{
   GlobalVariableDel("AlertTime"+Symbol()+Period());
   GlobalVariableDel("SignalType"+Symbol()+Period());
   return(0);
}
  
//+------------------------------------------------------------------+
//| ASCTrend1sig                                                     |
//+------------------------------------------------------------------+
int start()
  {
   if (CountBars>=1000) CountBars=950;
   SetIndexDrawBegin(0,Bars-CountBars+11+1);
   SetIndexDrawBegin(1,Bars-CountBars+11+1);
   int i,shift,counted_bars=IndicatorCounted();
   int Counter,i1,value10,value11;
   double value1,x1,x2;
   double value2,value3;
   double TrueCount,Range,AvgRange,MRO1,MRO2;
   double Table_value2[1000];
   double tmp=0;

   value10=3+RISK*2;
   x1=67+RISK;
   x2=33-RISK;
   value11=value10;
//----
   if(Bars<=11+1) return(0);
//---- initial zero
   if(counted_bars<11+1)
   {
      for(i=1;i<=0;i++) val1[CountBars-i]=0.0;
      for(i=1;i<=0;i++) val2[CountBars-i]=0.0;
   }
//----
   shift=CountBars-11-1;
   while(shift>=0)
     {
     
   Counter=shift;
	Range=0.0;
	AvgRange=0.0;
	for (Counter=shift; Counter<=shift+9; Counter++) AvgRange=AvgRange+MathAbs(High[Counter]-Low[Counter]);
		
	Range=AvgRange/10;
	Counter=shift;
	TrueCount=0;
	while (Counter<shift+9 && TrueCount<1)
		{if (MathAbs(Open[Counter]-Close[Counter+1])>=Range*2.0) TrueCount=TrueCount+1;
		Counter=Counter+1;
		}
	if (TrueCount>=1) {MRO1=Counter;} else {MRO1=-1;}
	Counter=shift;
	TrueCount=0;
	while (Counter<shift+6 && TrueCount<1)
		{if (MathAbs(Close[Counter+3]-Close[Counter])>=Range*4.6) TrueCount=TrueCount+1;
		Counter=Counter+1;
		}
	if (TrueCount>=1) {MRO2=Counter;} else {MRO2=-1;}
	if (MRO1>-1) {value11=3;} else {value11=value10;}
	if (MRO2>-1) {value11=4;} else {value11=value10;}
	value2=100-MathAbs(iWPR(NULL,0,value11,shift)); // PercentR(value11=9)
	Table_value2[shift]=value2;
	val1[shift]=0;
	val2[shift]=0;
	value3=0;
	if (value2<x2)
		{i1=1;
		while (Table_value2[shift+i1]>=x2 && Table_value2[shift+i1]<=x1){i1++;}
		if (Table_value2[shift+i1]>x1) 
			{
			value3=High[shift]+Range*0.5;
		   if (shift == 1 && flagval1==0){  flagval1=1; flagval2=0; }
			val1[shift]=value3;			
			} 
		}
	if (value2>x1)
		{i1=1;
		while (Table_value2[shift+i1]>=x2 && Table_value2[shift+i1]<=x1){i1++;}
		if (Table_value2[shift+i1]<x2) 
			{
			value3=Low[shift]-Range*0.5;
			if (shift == 1 && flagval2==0) { flagval2=1; flagval1=0; }
			val2[shift]=value3;			
			}
		}
      
      shift--;
     }

   if (flagval1==1 && CurTime() > GlobalVariableGet("AlertTime"+Symbol()+Period()) && GlobalVariableGet("SignalType"+Symbol()+Period())!=OP_BUY) {
      if (SoundON==1) Alert("SELL signal at Ask=",Ask,", Bid=",Bid,", Date=",TimeToStr(CurTime(),TIME_DATE)," ",TimeHour(CurTime()),":",TimeMinute(CurTime())," Symbol=",Symbol()," Period=",Period());
      if (EmailON==1) SendMail("SELL signal alert","SELL signal at Ask="+DoubleToStr(Ask,4)+", Bid="+DoubleToStr(Bid,4)+", Date="+TimeToStr(CurTime(),TIME_DATE)+" "+TimeHour(CurTime())+":"+TimeMinute(CurTime())+" Symbol="+Symbol()+" Period="+Period());
      tmp = CurTime() + (Period()-MathMod(Minute(),Period()))*60;
      GlobalVariableSet("AlertTime"+Symbol()+Period(),tmp);
      GlobalVariableSet("SignalType"+Symbol()+Period(),OP_BUY);
   }
   
   if (flagval2==1 && CurTime() > GlobalVariableGet("AlertTime"+Symbol()+Period()) && GlobalVariableGet("SignalType"+Symbol()+Period())!=OP_SELL) {
      if (SoundON==1) Alert("BUY signal at Ask=",Ask,", Bid=",Bid,", Time=",TimeToStr(CurTime(),TIME_DATE)," ",TimeHour(CurTime()),":",TimeMinute(CurTime())," Symbol=",Symbol()," Period=",Period());
      if (EmailON==1) SendMail("BUY signal alert","BUY signal at Ask="+DoubleToStr(Ask,4)+", Bid="+DoubleToStr(Bid,4)+", Date="+TimeToStr(CurTime(),TIME_DATE)+" "+TimeHour(CurTime())+":"+TimeMinute(CurTime())+" Symbol="+Symbol()+" Period="+Period());
      tmp = CurTime() + (Period()-MathMod(Minute(),Period()))*60;
      GlobalVariableSet("AlertTime"+Symbol()+Period(),tmp);
      GlobalVariableSet("SignalType"+Symbol()+Period(),OP_SELL);
   }

   return(0);
  }
//+------------------------------------------------------------------+


