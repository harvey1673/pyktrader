
#property copyright "Copyright © 2006, TrendLaboratory Ltd."
#property link      "http://finance.groups.yahoo.com/group/TrendLaboratory"

#property indicator_chart_window
#property indicator_buffers 6
#property indicator_color1 Blue
#property indicator_color2 Red
#property indicator_color3 White
#property indicator_color4 Gold
#property indicator_color5 Blue
#property indicator_color6 Red

extern int Length = 5;
extern int Deviation = 1;
extern double MoneyRisk = 1.0;
extern int Signal = 1;
extern int Line = 1;
extern int Nbars = 1000;
double g_ibuf_104[];
double g_ibuf_108[];
double g_ibuf_112[];
double g_ibuf_116[];
double g_ibuf_120[];
double g_ibuf_124[];
extern bool SoundON = TRUE;
bool gi_132 = FALSE;
bool gi_136 = FALSE;

int init() {
   SetIndexBuffer(0, g_ibuf_104);
   SetIndexBuffer(1, g_ibuf_108);
   SetIndexBuffer(2, g_ibuf_112);
   SetIndexBuffer(3, g_ibuf_116);
   SetIndexBuffer(4, g_ibuf_120);
   SetIndexBuffer(5, g_ibuf_124);
   SetIndexStyle(0, DRAW_ARROW, STYLE_SOLID, 1);
   SetIndexStyle(1, DRAW_ARROW, STYLE_SOLID, 1);
   SetIndexStyle(2, DRAW_ARROW, STYLE_SOLID, 1);
   SetIndexStyle(3, DRAW_ARROW, STYLE_SOLID, 1);
   SetIndexStyle(4, DRAW_LINE);
   SetIndexStyle(5, DRAW_LINE);
   SetIndexArrow(0, 159);
   SetIndexArrow(1, 159);
   SetIndexArrow(2, 108);
   SetIndexArrow(3, 108);
   IndicatorDigits(MarketInfo(Symbol(), MODE_DIGITS));
   string ls_0 = "BBands Stop(" + Length + "," + Deviation + ")";
   IndicatorShortName(ls_0);
   SetIndexLabel(0, "UpTrend Stop");
   SetIndexLabel(1, "DownTrend Stop");
   SetIndexLabel(2, "UpTrend Signal");
   SetIndexLabel(3, "DownTrend Signal");
   SetIndexLabel(4, "UpTrend Line");
   SetIndexLabel(5, "DownTrend Line");
   SetIndexDrawBegin(0, Length);
   SetIndexDrawBegin(1, Length);
   SetIndexDrawBegin(2, Length);
   SetIndexDrawBegin(3, Length);
   SetIndexDrawBegin(4, Length);
   SetIndexDrawBegin(5, Length);
   return (0);
}

int start() {
   int li_8;
   double lda_12[25000];
   double lda_16[25000];
   double lda_20[25000];
   double lda_24[25000];
   for (int l_shift_4 = Nbars; l_shift_4 >= 0; l_shift_4--) {
      g_ibuf_104[l_shift_4] = 0;
      g_ibuf_108[l_shift_4] = 0;
      g_ibuf_112[l_shift_4] = 0;
      g_ibuf_116[l_shift_4] = 0;
      g_ibuf_120[l_shift_4] = EMPTY_VALUE;
      g_ibuf_124[l_shift_4] = EMPTY_VALUE;
   }
   for (l_shift_4 = Nbars - Length - 1; l_shift_4 >= 0; l_shift_4--) {
      lda_12[l_shift_4] = iBands(NULL, 0, Length, Deviation, 0, PRICE_CLOSE, MODE_UPPER, l_shift_4);
      lda_16[l_shift_4] = iBands(NULL, 0, Length, Deviation, 0, PRICE_CLOSE, MODE_LOWER, l_shift_4);
      if (Close[l_shift_4] > lda_12[l_shift_4 + 1]) li_8 = 1;
      if (Close[l_shift_4] < lda_16[l_shift_4 + 1]) li_8 = -1;
      if (li_8 > 0 && lda_16[l_shift_4] < lda_16[l_shift_4 + 1]) lda_16[l_shift_4] = lda_16[l_shift_4 + 1];
      if (li_8 < 0 && lda_12[l_shift_4] > lda_12[l_shift_4 + 1]) lda_12[l_shift_4] = lda_12[l_shift_4 + 1];
      lda_20[l_shift_4] = lda_12[l_shift_4] + (MoneyRisk - 1.0) / 2.0 * (lda_12[l_shift_4] - lda_16[l_shift_4]);
      lda_24[l_shift_4] = lda_16[l_shift_4] - (MoneyRisk - 1.0) / 2.0 * (lda_12[l_shift_4] - lda_16[l_shift_4]);
      if (li_8 > 0 && lda_24[l_shift_4] < lda_24[l_shift_4 + 1]) lda_24[l_shift_4] = lda_24[l_shift_4 + 1];
      if (li_8 < 0 && lda_20[l_shift_4] > lda_20[l_shift_4 + 1]) lda_20[l_shift_4] = lda_20[l_shift_4 + 1];
      if (li_8 > 0) {
         if (Signal > 0 && g_ibuf_104[l_shift_4 + 1] == -1.0) {
            g_ibuf_112[l_shift_4] = lda_24[l_shift_4];
            g_ibuf_104[l_shift_4] = lda_24[l_shift_4];
            if (Line > 0) g_ibuf_120[l_shift_4] = lda_24[l_shift_4];
            if (SoundON == TRUE && l_shift_4 == 0 && !gi_132) {
                Alert("BERUBAH", Symbol(), Period());
                gi_132 = TRUE;
               gi_136 = FALSE;
            }
         } else {
            g_ibuf_104[l_shift_4] = lda_24[l_shift_4];
            if (Line > 0) g_ibuf_120[l_shift_4] = lda_24[l_shift_4];
            g_ibuf_112[l_shift_4] = -1;
         }
         if (Signal == 2) g_ibuf_104[l_shift_4] = 0;
         g_ibuf_116[l_shift_4] = -1;
         g_ibuf_108[l_shift_4] = -1.0;
         g_ibuf_124[l_shift_4] = EMPTY_VALUE;
      }
      if (li_8 < 0) {
         if (Signal > 0 && g_ibuf_108[l_shift_4 + 1] == -1.0) {
            g_ibuf_116[l_shift_4] = lda_20[l_shift_4];
            g_ibuf_108[l_shift_4] = lda_20[l_shift_4];
            if (Line > 0) g_ibuf_124[l_shift_4] = lda_20[l_shift_4];
            if (SoundON == TRUE && l_shift_4 == 0 && !gi_136) {
               Alert("BERUBAH", Symbol(), Period());
               gi_136 = TRUE;
               gi_132 = FALSE;
            }
         } else {
            g_ibuf_108[l_shift_4] = lda_20[l_shift_4];
            if (Line > 0) g_ibuf_124[l_shift_4] = lda_20[l_shift_4];
            g_ibuf_116[l_shift_4] = -1;
         }
         if (Signal == 2) g_ibuf_108[l_shift_4] = 0;
         g_ibuf_112[l_shift_4] = -1;
         g_ibuf_104[l_shift_4] = -1.0;
         g_ibuf_120[l_shift_4] = EMPTY_VALUE;
      }
   }
   return (0);
}