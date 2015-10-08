//+------------------------------------------------------------------+
//|                                              NRTR_color_line.mq4 |
//+------------------------------------------------------------------+

#property indicator_chart_window
#property indicator_buffers 2
#property indicator_color1 Blue
#property indicator_color2 Red
//---- input parameters
extern int ATRPeriod=14;
extern double Coefficient=4.0;
extern int StartBar=1000;

//---- buffers
double value1[];
double value2[];

bool TrendUP;
double Extremum,TR,ATR,Values[100],ChannelWidth;
int J,Head,Weight,Curr;

int init() {

//---- indicator line
   IndicatorBuffers(2);
   SetIndexStyle(0,DRAW_LINE);
   SetIndexArrow(0,167);
   SetIndexEmptyValue(0,0);
   SetIndexEmptyValue(1,0);
   SetIndexStyle(1,DRAW_LINE);
   SetIndexArrow(1,167);
   SetIndexBuffer(0,value1);
   SetIndexBuffer(1,value2);
   return(0);
}

int start() {
   int Shift;
   
   if (Close[StartBar-2] > Close[StartBar-1]) TrendUP = true;
   else TrendUP = false;
   Extremum = Close[ StartBar - 2 ];

   for (Shift = StartBar - 3; Shift>=0; Shift--) {
	   TR = High[Shift] - Low[Shift];
	   if ( MathAbs( High[ Shift ] - Close[ Shift + 1 ]) > TR ) TR = MathAbs( High[ Shift ] - Close[ Shift + 1 ]);
	   if ( MathAbs( Low[ Shift ] - Close[ Shift + 1 ]) > TR )  TR = MathAbs( Low[ Shift ] - Close[ Shift + 1 ]);
	   if (Shift == StartBar - 3) 
		   for (J = 0; J<ATRPeriod; J++) {
			   Values[J] = TR;
		   }
	   Values[ Head ] = TR;
	   ATR = 0;
	   Weight = ATRPeriod;
	   Curr = Head;
	   for (J = 0; J<ATRPeriod; J++) {
		   ATR += Values[ Curr ] * Weight;
		   Weight -= 1;
		   Curr -= 1;
		   if ( Curr == -1 ) Curr = ATRPeriod - 1;
	   }
	   ATR = ( 2.0 * ATR ) / ( ATRPeriod * ( ATRPeriod + 1.0 ));
	   Head += 1;
	   if (Head == ATRPeriod) Head = 0;
	   ChannelWidth = Coefficient * ATR;
	   if (TrendUP && ( Low[ Shift ] < ( Extremum - ChannelWidth ) ) )  {
		   TrendUP = false;
		   Extremum = High[ Shift ];
	   }
	   if ( !TrendUP && ( High[ Shift ] > ( Extremum + ChannelWidth) ) ) {
		   TrendUP = true;
		   Extremum = Low[ Shift ];
	   }
	
	   if ( TrendUP && ( Low[Shift] > Extremum ) ) Extremum = Low[ Shift ];
	   if ( !TrendUP && ( High[ Shift ] < Extremum ) ) Extremum = High[ Shift ];
	
	   if (TrendUP) {
		   value1[Shift]=Extremum - ChannelWidth;
		   value2[Shift]=0;
	   } else {
		   value1[Shift]=0;
		   value2[Shift]=Extremum + ChannelWidth;
	   }
	}
}

