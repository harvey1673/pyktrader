//+------------------------------------------------------------------+
//|                                                 LabTrend1_v1.mq4 |
//|                                  Copyright © 2006, Forex-TSD.com |
//|                         Written by IgorAD,igorad2003@yahoo.co.uk |   
//|            http://finance.groups.yahoo.com/group/TrendLaboratory |                                      
//+------------------------------------------------------------------+
#property copyright "Copyright © 2006, Forex-TSD.com "
#property link      "http://www.forex-tsd.com/"

#property indicator_chart_window
#property indicator_buffers 4
#property indicator_color1 Blue
#property indicator_color2 Red
#property indicator_color3 Blue
#property indicator_color4 Red

//---- input parameters

extern double Risk=3;         //channel narrowing factor (1..10)  
extern int Signal=1;          //Display signals mode
extern int ColorBar=1;        //Display color bars mode: 0-no,1-yes 
extern int TimeFrame=0;       //TimeFrame in min
extern int BarsNumber=1000;
//---- indicator buffers
double UpTrendSignal[];
double DownTrendSignal[];
double UpTrendBar[];
double DownTrendBar[];
double UpTrendBuffer[];
double DownTrendBuffer[];
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
  {
   string short_name;
//---- indicator line
   IndicatorBuffers(6); 
   SetIndexBuffer(0,UpTrendSignal);
   SetIndexBuffer(1,DownTrendSignal);
   SetIndexBuffer(2,UpTrendBar);
   SetIndexBuffer(3,DownTrendBar);
   SetIndexBuffer(4,UpTrendBuffer);
   SetIndexBuffer(5,DownTrendBuffer);
   SetIndexStyle(0,DRAW_ARROW);
   SetIndexStyle(1,DRAW_ARROW);
   SetIndexStyle(2,DRAW_HISTOGRAM,STYLE_SOLID,2);
   SetIndexStyle(3,DRAW_HISTOGRAM,STYLE_SOLID,2);
   SetIndexArrow(0,108);
   SetIndexArrow(1,108);
//---- name for DataWindow and indicator subwindow label
   short_name="LabTrend1("+Risk+")";
   IndicatorShortName(short_name);
   SetIndexLabel(0,"UpTrend Signal");
   SetIndexLabel(1,"DownTrend Signal");
   SetIndexLabel(2,"UpTrend Bar");
   SetIndexLabel(3,"DownTrend Bar");
//----
   SetIndexDrawBegin(0,9);
   SetIndexDrawBegin(1,9);
   SetIndexDrawBegin(2,9);
   SetIndexDrawBegin(3,9);
  
//----
   return(0);
  }
//+------------------------------------------------------------------+
//| LabTrend1_v1                                             |
//+------------------------------------------------------------------+
int start()
  {
   
   datetime TimeArray[];
   int    i,shift,trend,y=0;
   double high, low, price, sum, UpBar,DnBar;
   double smax[25000],smin[25000],bsmax[25000],bsmin[25000];
   double LowArray[],HighArray[];
   
   
   int Line=0;                   //Display line mode: 0-no,1-yes  
   int Length=9;          //Price Channel Period
   
   
   for (shift=BarsNumber-1;shift>=0;shift--)
   {
   UpTrendBuffer[shift]=0.0;
   DownTrendBuffer[shift]=0.0;
   UpTrendSignal[shift]=0.0;
   DownTrendSignal[shift]=0.0;
   UpTrendBar[shift]=0.0;
	DownTrendBar[shift]=0.0;
   }
// Draw price channel boards + calculation : Channel middle, half channel width, 
 
   
   ArrayCopySeries(TimeArray,MODE_TIME,Symbol(),TimeFrame); 
   ArrayCopySeries(LowArray,MODE_LOW,Symbol(),TimeFrame);     
   ArrayCopySeries(HighArray,MODE_HIGH,Symbol(),TimeFrame);  
   
   for(i=0,y=0;i<BarsNumber;i++)
   {
   if (Time[i]<TimeArray[y]) y++;  
   smin[i]=LowArray[Lowest(NULL,TimeFrame,MODE_LOW,Length,y)]; 
   smax[i]=HighArray[Highest(NULL,TimeFrame,MODE_HIGH,Length,y)];       
   
   }  
     
//
   
   for (shift=BarsNumber-Length-1;shift>=0;shift--)
   {	  
// Calculation channel stop values 
              
     bsmax[shift]=smax[shift]-(smax[shift]-smin[shift])*(33.0-Risk)/100.0;
	  bsmin[shift]=smin[shift]+(smax[shift]-smin[shift])*(33.0-Risk)/100.0;

// Signal area : any conditions to trend determination:     
// 1. Price Channel breakout 
    
     
      if(Close[shift]>bsmax[shift])  trend=1; 
      if(Close[shift]<bsmin[shift])  trend=-1;
    
    
// Correction boards values with existing trend	  		



// Drawing area	  
	  UpBar=bsmax[shift];
	  DnBar=bsmin[shift];
	  	  	 
	  if (trend>0) 
	  {
	     if (Signal==1 && UpTrendBuffer[shift+1]==-1.0)
	     {
	        
	        UpTrendSignal[shift]=Low[shift]-0.5*iATR(NULL,TimeFrame,10,shift);
	        	        
	     }
	     else
	     {
	     UpTrendBuffer[shift]=bsmin[shift];
	     UpTrendSignal[shift]=-1;
	     }
	  if(ColorBar>0)
	        {
	           if(Close[shift]>UpBar)
	           {
	              UpTrendBar[shift]=High[shift];
	              DownTrendBar[shift]=Low[shift];
	           }
	           else
	           {
	              UpTrendBar[shift]=EMPTY_VALUE;
	              DownTrendBar[shift]=EMPTY_VALUE;
	           }
	              
	        }   
	  DownTrendBuffer[shift]=-1.0;
	  }
	  
	  if (trend<0) 
	  {
	  if (Signal==1 && DownTrendBuffer[shift+1]==-1.0)
	     {
	     DownTrendSignal[shift]=High[shift]+0.5*iATR(NULL,TimeFrame,10,shift);
	     }
	     else
	     {
	     DownTrendBuffer[shift]=bsmax[shift];
	     DownTrendSignal[shift]=-1;
	     }
	  if(ColorBar>0)
	        {
	           if(Close[shift]<DnBar)
	           {
	              UpTrendBar[shift]=Low[shift];
	              DownTrendBar[shift]=High[shift];
	           }
	           else
	           {
	              UpTrendBar[shift]=EMPTY_VALUE;
	              DownTrendBar[shift]=EMPTY_VALUE;
	           }      
	        }   
	    UpTrendBuffer[shift]=-1.0;
	    }
	  
	 
   }
   return(0);
  }
//+------------------------------------------------------------------+