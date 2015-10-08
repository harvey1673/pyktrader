//+------------------------------------------------------------------+
//|                                                    AscTrend2.mq4 |
//|                                     Copyright © 2006, Nick Bilak |
//+------------------------------------------------------------------+
#property copyright "Copyright © 2006, Nick Bilak"

//---- indicator settings
#property  indicator_chart_window
#property  indicator_buffers 2
#property  indicator_color1  Aqua
#property  indicator_color2  Magenta
//---- indicator parameters
extern int Risk=5;
extern double MONYRISK=2.0;
//---- indicator buffers
double e1[];
double e2[];

int i,value2=1,Counter,DCounter,TrueCount=0,MRO1=0,MRO2=0,MRO3=0,MRO4=0;
double  value3=18,value4=0,value5=0,value6=0,value7=0,value8=0,value9=0,
   value10=10,value11=10000,value12=0,value13=0,value14=0,value19=0,
   value4_1=0,value4_2=0,value9_1=0,value10_1=0,value11_1=0,value12_1=0,
   Range=0,AvgRange=0,AvgRange_1=0,AvgRange_2=0,
   val1=0,val2=0,NumBars=0;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
  {
//---- drawing settings
   SetIndexStyle(0,DRAW_ARROW);
   SetIndexStyle(1,DRAW_ARROW);
   SetIndexArrow(0,159);
   SetIndexArrow(1,159);
   SetIndexEmptyValue(0,0);
   SetIndexEmptyValue(1,0);
   if(
   	!SetIndexBuffer(0,e1) ||
      !SetIndexBuffer(1,e2)
      )
      Print("cannot set indicator buffers!");
//---- name for DataWindow and indicator subwindow label
   IndicatorShortName("AscT2("+Risk+")");
//---- initialization done
   return(0);
   
  }

int start()  {

   int counted_bars=IndicatorCounted();
   if(counted_bars<0) return(-1);
   if(counted_bars>0) counted_bars--;
   int limit=Bars-20-counted_bars;
   double spread=Ask-Bid;
   for(i=limit; i>=0; i--) {
	   Range=0;
	   AvgRange=0;
	   for (Counter=i; Counter<=i+9; Counter++) {
	     AvgRange=AvgRange+MathAbs(spread+High[Counter]-Low[Counter]);
	   }
	   Range=AvgRange/10.0;
      if (i==Bars-20)  {
            value2=1; value3=18; value10=10000; value10_1=0;
		      value19=MONYRISK*Range*Point;
		      value2=Risk;
		      value3=18+3*value2;
		      value9=0;
      }
	   Counter=i;
	   AvgRange=0;
	   for (Counter=i; Counter<=i+9-1; Counter++) {
		   AvgRange=AvgRange+Close[Counter];
		}
	   value11=AvgRange/9.0;
	   // -----
	   //value12=UserFunction("AverageClose",value3,i);
	   Counter=i;
	   AvgRange=0;
	   for (Counter=i; Counter<=i+value3-1; Counter++) {
		   AvgRange=AvgRange+Close[Counter];
		}
	   value12=AvgRange/value3;
	   // -----
	   value13=Range;
	   // -----
	   //value4=UserFunction("JESSD",High[i],Low[i],High[i+value2],Low[i+value2],Close[i+value2]);
	   AvgRange=(spread+High[i]+Low[i])/2.0;
	   if (Close[i+value2]<AvgRange) {
	     value4=2*AvgRange-Low[i+value2];
	   } else {
		   value4=2*AvgRange-spread+High[i+value2];
		}
	   // -----
	   Counter=i;
	   TrueCount=0;
	   while (Counter<i+2 && TrueCount<1) {
		   //value4=UserFunction("JESSD",High[Counter],Low[Counter],High[Counter+value2],Low[Counter+value2],Close[Counter+value2]);
		    AvgRange=(spread+High[Counter]+Low[Counter])/2.0;
		    if (Close[Counter+value2]<AvgRange) {
		 	   value4=2*AvgRange-Low[Counter+value2];
		 	 } else {
		 	   value4=2*AvgRange-spread+High[Counter+value2];
		 	 }
		    value4=NormalizeDouble(value4,2);
		    //value4_1=UserFunction("JESSD",High[Counter+1],Low[Counter+1],High[Counter+value2],Low[Counter+value2],Close[Counter+value2]);
		    AvgRange_1=(spread+High[Counter+1]+Low[Counter+1])/2.0;
		    if (Close[Counter+1+value2]<AvgRange_1) {
		 	   value4_1=2*AvgRange_1-Low[Counter+1+value2];
		 	 } else {
		 	   value4_1=2*AvgRange_1-spread+High[Counter+1+value2];
		 	 }
		    value4_1=NormalizeDouble(value4_1,2);
		    //value4_2=UserFunction("JESSD",High[Counter+2],Low[Counter+2],High[Counter+value2],Low[Counter+value2],Close[Counter+value2]);
		    AvgRange_2=(spread+High[Counter+2]+Low[Counter+2])/2.0;
		    if (Close[Counter+2+value2]<AvgRange_2) {
		 	   value4_2=2*AvgRange_2-Low[Counter+2+value2];
		 	 } else {
		 	   value4_2=2*AvgRange_2-spread+High[Counter+2+value2];
		 	 }
		    value4_2=NormalizeDouble(value4_2,2);
		    if (value4>value4_1 && value4_1<value4_2) TrueCount=TrueCount+1;
		    Counter=Counter+1;
		}
	   if (TrueCount>=1) MRO1=Counter-i-1; else MRO1=-1;
	   // -----
	   Counter=i;
	   TrueCount=0;
	   while (Counter<i+2 && TrueCount<1) {
		   //value4=UserFunction("JESSD",High[Counter],Low[Counter],High[Counter+value2],Low[Counter+value2],Close[Counter+value2]);
		    AvgRange=(spread+High[Counter]+Low[Counter])/2.0;
		    if (Close[Counter+value2]<AvgRange) {
		 	   value4=2*AvgRange-Low[Counter+value2];
		 	 } else {
		 	   value4=2*AvgRange-spread+High[Counter+value2];
		 	 }
		    value4=NormalizeDouble(value4,2);
		    //value4_1=UserFunction("JESSD",High[Counter+1],Low[Counter+1],High[Counter+value2],Low[Counter+value2],Close[Counter+value2]);
		    AvgRange_1=(spread+High[Counter+1]+Low[Counter+1])/2.0;
		    if (Close[Counter+1+value2]<AvgRange_1) {
		 	   value4_1=2*AvgRange_1-Low[Counter+1+value2];
		 	 } else {
		 	   value4_1=2*AvgRange_1-spread+High[Counter+1+value2];
		 	 }
		    value4_1=NormalizeDouble(value4_1,2);
		    //value4_2=UserFunction("JESSD",High[Counter+2],Low[Counter+2],High[Counter+value2],Low[Counter+value2],Close[Counter+value2]);
		    AvgRange_2=(spread+High[Counter+2]+Low[Counter+2])/2.0;
		    if (Close[Counter+2+value2]<AvgRange_2) {
		 	   value4_2=2*AvgRange_2-Low[Counter+2+value2];
		 	 } else {
		 	   value4_2=2*AvgRange_2-spread+High[Counter+2+value2];
		 	 }
		    value4_2=NormalizeDouble(value4_2,2);
		    if (value4<value4_1 && value4_1>value4_2) TrueCount=TrueCount+1;
		    Counter=Counter+1;
		}
	   if (TrueCount>=1) MRO2=Counter-i-1; else MRO2=-1;
	   // -----
	   //value4_1=UserFunction("JESSD",High[i+1],Low[i+1],High[i+1+value2],Low[i+1+value2],Close[i+1+value2]);
	   AvgRange_1=(spread+High[i+1]+Low[i+1])/2.0;
	   if (Close[i+1+value2]<AvgRange_1) {
		   value4_1=2*AvgRange_1-Low[i+1+value2];
		} else {
		   value4_1=2*AvgRange_1-spread+High[i+1+value2];
		}
	   // -----
	   if (MRO1>-1 && Low[i+1]>value4_1) value5=value4_1-value13;
	   if (MRO2>-1 && spread+High[i+1]<value4_1) value6=value4_1+value13;
	   // -----
	   //value11_1=UserFunction("AverageClose",9,i+1);
	   Counter=i;
	   AvgRange=0;
	   for (Counter=i+1; Counter<=i+1+9-1; Counter++) {
		   AvgRange=AvgRange+Close[Counter];
		}
	   value11_1=AvgRange/9.0;
	   // -----
	   //value12_1=UserFunction("AverageClose",value3,i+1);
	   Counter=i;
	   AvgRange=0;
	   for (Counter=i+1; Counter<=i+1+value3-1; Counter++) {
		   AvgRange=AvgRange+Close[Counter];
		}
	   value12_1=AvgRange/value3;
	   // -----
	   if (value11_1<value12_1 && value11>value12) {
		   //value5=UserFunction("TrueLow",i)-value13;
		   if (Close[i+1]<Low[i]) {
			   value5=Close[i+1]-value13;
			} else {
			   value5=Low[i]-value13;
			}
		}
	   if (value11_1>value12_1 && value11<value12) {
		   //value5=UserFunction("TrueHigh",i)+value13;
		   if (Close[i+1]>spread+High[i]) {
			   value5=Close[i+1]+value13;
			} else {
			   value5=spread+High[i]+value13;
			}
		}
	   // -----
	   if (MathAbs(Open[i]-Close[i+1])>=1.618*value13) {
		    if (value11>value12) value5=Low[i]-value13;
		    if (value11<value12) value14=spread+High[i]+value13;
		}
	   // -----
	   //value7=UserFunction("BS105",Low[i],2.40,value13,value9);
	   if (Low[i]-2.40*value13<value9) {
		   value7=value9;
		} else {
		   value7=Low[i]-2.40*value13;
		}
	   // -----
	   //value8=UserFunction("SS105",High[i],2.40,value13,value10);
	   if (spread+High[i]+2.40*value13>value10) {
		   value8=value10;
		} else {
		   value8=spread+High[i]+2.40*value13;
		}
	   // -----
	   //value9=UserFunction("BS0",Low[i],60,value7,RISK,value19);
	   value9=value7;
	   // -----
	   //value10=UserFunction("SS0",High[i],60,value8,RISK,value19);
	   value10=value8;
	   // -----
	   if (Low[i]-value9>value19/Point) value9=Low[i]-(1.50+0.1*Risk)*value13;
	   if (value10-spread+High[i]>value19/Point) value10=spread+High[i]+(1.50+0.1*Risk)*value13;
	   if (value11>=value12 && value5>=value9) value9=value5;
	   if (value11<=value12 && value6<=value10) value10=value6;
	   if (value11<=value12 && value5<=value9) value9=value5;
	   if (value11>=value12 && value6>=value10) value10=value6;
	   // -----
	   Counter=i;
	   TrueCount=0;
	   while (Counter<i+2 && TrueCount<2) {
		   //value11=UserFunction("AverageClose",9,Counter);
		   DCounter=Counter;
		   AvgRange=0;
		   for (DCounter=Counter; DCounter<=Counter+9-1; DCounter++) {
			   AvgRange=AvgRange+Close[DCounter];
			}
		   value11=AvgRange/9.0;
		   //value12=UserFunction("AverageClose",value3,Counter);
		   DCounter=Counter;
		   AvgRange=0;
		   for (DCounter=Counter; DCounter<=Counter+value3-1; DCounter++) {
			   AvgRange=AvgRange+Close[DCounter];
			}
		   value12=AvgRange/value3;
		   if (value11>=value12) TrueCount=TrueCount+1;
		   Counter=Counter+1;
		}
	   if (TrueCount>=2) MRO3=Counter-i-1; else MRO3=-1;
	   // -----
	   Counter=i;
	   TrueCount=0;
	   while (Counter<i+2 && TrueCount<2) {
		   //value11=UserFunction("AverageClose",9,Counter);
		   DCounter=Counter;
		   AvgRange=0;
		   for (DCounter=Counter; DCounter<=Counter+9-1; DCounter++) {
			   AvgRange=AvgRange+Close[DCounter];
			}
		   value11=AvgRange/9.0;
		   //value12=UserFunction("AverageClose",value3,Counter);
		   DCounter=Counter;
		   AvgRange=0;
		   for (DCounter=Counter; DCounter<=Counter+value3-1; DCounter++) {
			   AvgRange=AvgRange+Close[DCounter];
			}
		   value12=AvgRange/value3;
		   if (value11<=value12) TrueCount=TrueCount+1;
		   Counter=Counter+1;
		}
	   if (TrueCount>=2) MRO4=Counter-i-1; else MRO4=-1;
	   // -----
	   if (MRO3>-1 && value9<=value9_1) value9=value9_1;
	   if (MRO4>-1 && value10>=value10_1) value10=value10_1;
	   // -----
	   //value11=UserFunction("AverageClose",9,i);
	   Counter=i;
	   AvgRange=0;
      for (Counter=i; Counter<=i+9-1; Counter++) {
		   AvgRange=AvgRange+Close[Counter];
		}
	   value11=AvgRange/9.0;
	   // -----
	   //value12=UserFunction("AverageClose",value3,i);
	   Counter=i;
	   AvgRange=0;
      for (Counter=i; Counter<=i+value3-1; Counter++) {
		   AvgRange=AvgRange+Close[Counter];
		}
	   value12=AvgRange/value3;
	   // -----
	   val1=0;
	   val2=0;
	   if (value9>0 && value11>=value12 && value9<=spread+High[i]) {
		   val1=value9;
		}
	   if (value10>0 && value10<1000000000 && value11<=value12 && value10>=Low[i]) {
		   val2=value10;
		}
	   // -----
	   value9_1=value9;
	   value10_1=value10;
	   e1[i]=val1; //SetIndexValue(i,val1);
	   e2[i]=val2; //SetIndexValue2(i,val2);
	   // -----
   }
}

