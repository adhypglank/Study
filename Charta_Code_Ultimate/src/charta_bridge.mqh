//+------------------------------------------------------------------+
//|                                       Charta bridge for MT5      |
//|                        Hak Cipta © 2026 Adi Putra (Adhyp Glank)  |
//+------------------------------------------------------------------+
#property copyright "Adi Putra (Adhyp Glank)"
#property strict

// Add http://127.0.0.1:15555 to MetaTrader 5 -> Tools -> Options -> Expert Advisors -> Allow WebRequest for listed URL.
input string ChartaBridgeUrl = "http://127.0.0.1:15555";
input int    ChartaTimeout   = 1000;

//+------------------------------------------------------------------+
//| Request the current Charta signal from the Python HTTP bridge.   |
//+------------------------------------------------------------------+
string ChartaRequest(string topic)
{
   char data[], result[];
   string headers;
   string url = ChartaBridgeUrl + "/signal?topic=" + topic;
   int res = WebRequest("GET", url, headers, ChartaTimeout, data, result, headers);
   if(res != 200)
   {
      Print("[CHARTA BRIDGE] request failed, http=", res);
      return "";
   }
   return CharArrayToString(result, 0, ArraySize(result), CP_UTF8);
}

//+------------------------------------------------------------------+
//| Process a single Charta signal if it matches the expected AG id. |
//+------------------------------------------------------------------+
void ProcessChartaSignal(string json, string expected_id)
{
   if(StringFind(json, "\"id\":\"" + expected_id + "\"") == -1)
      return;

   string key = "\"spok\":\"";
   int start  = StringFind(json, key);
   if(start == -1)
      return;
   start += StringLen(key);

   int end_ = StringFind(json, "\"", start);
   if(end_ == -1)
      return;

   string spok = StringSubstr(json, start, end_ - start);
   Print("[CHARTA] ", expected_id, " -> ", spok);

   char data[], result[];
   string headers;
   string ack_url = ChartaBridgeUrl + "/ack?id=" + expected_id;
   WebRequest("POST", ack_url, headers, ChartaTimeout, data, result, headers);
}
