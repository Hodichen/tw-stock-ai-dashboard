# -*- coding: utf-8 -*-
"""
台股 AI 個股分析儀表板（旗艦全景版 + 即時報價 + HTML 列印報告 + AI 紙雕圖卡 + 雙引擎備援）
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from FinMind.data import DataLoader
from datetime import datetime
import random
import time
import json
import yfinance as yf
import html as html_lib
import requests
import base64

st.set_page_config(
    page_title="台股 AI 分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS（米白底 + 莫蘭迪色 + 卡片）
# ============================================
st.markdown("""
<style>
.stApp { background: #F5F1EB !important; color: #4A4540 !important; }
.stMarkdown, .stMarkdown p, .stMarkdown li, .stText, [data-testid="stMarkdownContainer"] { color: #4A4540 !important; }
h1, h2, h3, h4, h5, h6 { color: #5C5048 !important; font-weight: 600 !important; }
[data-testid="stCaptionContainer"], .stCaption { color: #8B7E72 !important; }

[data-testid="stMetricLabel"] { color: #8B7E72 !important; font-weight: 500 !important; }
[data-testid="stMetricValue"] { color: #3D3833 !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-weight: 600 !important; }

[data-testid="stMetric"] { background: #FAF6F0; border: 1px solid #E5DDD0; border-radius: 10px; padding: 12px 14px; }
.stTextInput input { background: #FFFFFF !important; border: 1.5px solid #C9BFB1 !important; color: #3D3833 !important; font-size: 16px !important; border-radius: 8px !important; padding: 10px 14px !important; }
.stTextInput input:focus { border-color: #8B9D83 !important; box-shadow: 0 0 0 2px rgba(139, 157, 131, 0.2) !important; }
.stButton button[kind="primary"] { background: #8B9D83 !important; border: 1px solid #6F8169 !important; color: #FFFFFF !important; font-weight: 600 !important; border-radius: 8px !important; }
.stButton button[kind="primary"]:hover { background: #6F8169 !important; border-color: #5A6856 !important; }
.stButton button { background: #FAF6F0 !important; border: 1px solid #D4CABB !important; color: #5C5048 !important; font-weight: 500 !important; border-radius: 8px !important; }
.stButton button:hover { background: #EDE5D5 !important; border-color: #B8AB99 !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
.stTabs [data-baseweb="tab"] { background: #FAF6F0 !important; color: #5C5048 !important; border-radius: 8px 8px 0 0 !important; padding: 10px 18px !important; border: 1px solid #E5DDD0 !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { background: #8B9D83 !important; color: #FFFFFF !important; border-color: #6F8169 !important; }

.inst-card { background: #FAF6F0; border: 1px solid #E5DDD0; border-radius: 10px; padding: 14px; text-align: left; }
.inst-label { color: #8B7E72; font-size: 14px; font-weight: 500; margin-bottom: 6px; }
.inst-value-up { color: #C76A6A; font-size: 28px; font-weight: 700; }
.inst-value-down { color: #7B9E89; font-size: 28px; font-weight: 700; }
.inst-value-flat { color: #8B7E72; font-size: 28px; font-weight: 700; }

.overview-header { background: linear-gradient(135deg, #FAF6F0 0%, #F5EFE5 100%); border: 1px solid #D4CABB; border-radius: 12px; padding: 18px 24px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(120, 108, 90, 0.08); }
.overview-title { color: #5C5048; font-size: 24px; font-weight: 700; margin-bottom: 6px; letter-spacing: 1px; }
.overview-subtitle { color: #8B7E72; font-size: 14px; margin-bottom: 12px; }
.overview-pills { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.overview-pill { background: #FFFFFF; border: 1px solid #D4CABB; color: #5C5048; padding: 6px 14px; border-radius: 16px; font-size: 13px; font-weight: 500; }
.overview-pill-red { background: #FBEDED !important; border: 1px solid #E5BFBF !important; color: #C76A6A !important; padding: 6px 14px; border-radius: 16px; font-size: 14px; font-weight: 600; }
.overview-pill-green { background: #EAF1EC !important; border: 1px solid #B8D0BE !important; color: #5C8169 !important; padding: 6px 14px; border-radius: 16px; font-size: 14px; font-weight: 600; }

.section-card { background: #FAF6F0; border: 1px solid #E5DDD0; border-radius: 8px; padding: 14px; height: 100%; box-shadow: 0 2px 8px rgba(120, 108, 90, 0.04); margin-bottom: 10px; }
.section-title { color: #8B6F47; font-size: 15px; font-weight: 700; border-bottom: 1px solid #E5DDD0; padding-bottom: 6px; margin-bottom: 10px; text-align: center; }
.kv-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px dashed #E5DDD0; font-size: 13px; min-height: 28px; }
.kv-label { color: #8B7E72; }

span.kv-value { color: #3D3833 !important; font-weight: 600 !important; }
span.kv-value-up { color: #C76A6A !important; font-weight: 700 !important; }
span.kv-value-down { color: #7B9E89 !important; font-weight: 700 !important; }
span.kv-value-yellow { color: #B89243 !important; font-weight: 700 !important; }
span.kv-value-cyan { color: #5A87A0 !important; font-weight: 700 !important; }

.conclusion-box { background: linear-gradient(135deg, #F0E9DA 0%, #E8DFCC 100%); border: 2px solid #C9B689; border-radius: 8px; padding: 14px 20px; margin: 10px 0; display: flex; align-items: center; }
.conclusion-title { color: #FAF6F0; background: #8B6F47; padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: 700; margin-right: 16px; white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

# ============================================
# Token 池 + Gemini key 池
# ============================================
def get_finmind_tokens():
    tokens = []
    try: tokens.append(st.secrets["FINMIND_TOKEN"])
    except: pass
    for i in range(2, 5):
        try: tokens.append(st.secrets[f"FINMIND_TOKEN_{i}"])
        except: pass
    return tokens

def get_gemini_keys():
    keys = []
    try: keys.append(st.secrets["GEMINI_API_KEY"])
    except: pass
    try: keys.append(st.secrets["GEMINI_API_KEY_2"])
    except: pass
    return keys

@st.cache_resource
def get_finmind():
    tokens = get_finmind_tokens()
    if not tokens:
        st.error("❌ 未設定 FINMIND_TOKEN")
        st.stop()
    token = random.choice(tokens)
    try:
        dl = DataLoader()
        dl.login_by_token(api_token=token)
        return dl, len(tokens)
    except Exception as e:
        st.error(f"FinMind 登入失敗：{e}")
        st.stop()

def get_gemini_client_for_key(api_key):
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except:
        return None

dl, finmind_token_count = get_finmind()
gemini_keys = get_gemini_keys()

# ============================================
# 技術指標
# ============================================
def sma(s, n): return s.rolling(n, min_periods=1).mean()
def rsi_calc(s, n=14):
    d = s.diff()
    g = d.where(d > 0, 0).ewm(com=n - 1, min_periods=n).mean()
    l = (-d.where(d < 0, 0)).ewm(com=n - 1, min_periods=n).mean()
    return 100 - 100 / (1 + g / l)
def macd_calc(s):
    m = s.ewm(span=12, adjust=False).mean() - s.ewm(span=26, adjust=False).mean()
    sig = m.ewm(span=9, adjust=False).mean()
    return m, sig, m - sig
def kd_calc(hi, lo, cl):
    ll = lo.rolling(9, min_periods=1).min()
    hh = hi.rolling(9, min_periods=1).max()
    rsv = 100 * (cl - ll) / (hh - ll).replace(0, np.nan).fillna(50)
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    return k, d

def safe(s, i=-1):
    try:
        v = s.iloc[i]
        return float(v) if pd.notna(v) else None
    except: return None

# ============================================
# 主分析 (含 FinMind 與 yfinance 雙引擎備援)
# ============================================
@st.cache_data(ttl=1800, show_spinner=False)
def analyze(stock_id):
    end = pd.Timestamp.today().strftime("%Y-%m-%d")
    start = (pd.Timestamp.today() - pd.Timedelta(days=200)).strftime("%Y-%m-%d")
    is_etf = stock_id.startswith("00") and len(stock_id) >= 5

    df = pd.DataFrame()
    
    # 1. 首選：嘗試使用 FinMind 抓取
    try:
        df = dl.taiwan_stock_daily(stock_id=stock_id, start_date=start, end_date=end)
    except Exception:
        pass # 若 FinMind 失敗或超時，進入備援機制

    # 2. 備援：若 FinMind 失敗或回傳空值，啟動 yfinance
    if df is None or df.empty:
        try:
            for suffix in ['.TW', '.TWO']:
                ticker = yf.Ticker(f"{stock_id}{suffix}")
                yf_df = ticker.history(start=start, end=end)
                
                if not yf_df.empty:
                    yf_df = yf_df.reset_index()
                    yf_df = yf_df.rename(columns={
                        "Date": "date", 
                        "Open": "open", 
                        "High": "high", 
                        "Low": "low", 
                        "Close": "close", 
                        "Volume": "volume"
                    })
                    yf_df["date"] = pd.to_datetime(yf_df["date"]).dt.tz_localize(None)
                    df = yf_df[["date", "open", "high", "low", "close", "volume"]]
                    break 
        except Exception:
            pass

    # 3. 最終檢查：若雙引擎皆失敗
    if df is None or df.empty:
        return None, "無法獲取股價資料（FinMind 與 Yahoo Finance 伺服器皆無回應或代號錯誤）。"

    # FinMind 欄位名稱處理
    if "max" in df.columns: 
        df = df.rename(columns={"max": "high", "min": "low", "Trading_Volume": "volume"})

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    industry_category = "未知 / ETF"
    try:
        info = dl.taiwan_stock_info()
        m = info[info["stock_id"] == stock_id]
        name = m["stock_name"].iloc[0] if not m.empty else stock_id
        if "industry_category" in m.columns and not m.empty:
            industry_category = str(m["industry_category"].iloc[0])
    except:
        name = stock_id

    df["MA5"] = sma(df["close"], 5)
    df["MA20"] = sma(df["close"], 20)
    df["MA60"] = sma(df["close"], 60)
    df["std20"] = df["close"].rolling(20, min_periods=1).std()
    df["BB_UB"] = df["MA20"] + 2 * df["std20"]
    df["BB_LB"] = df["MA20"] - 2 * df["std20"]
    df["RSI"] = rsi_calc(df["close"])
    df["MACD"], df["MACD_sig"], df["MACD_hist"] = macd_calc(df["close"])
    df["K"], df["D"] = kd_calc(df["high"], df["low"], df["close"])
    df["VMA5"] = sma(df["volume"], 5)
    df["VMA20"] = sma(df["volume"], 20)
    df["VRatio"] = df["volume"] / df["VMA5"]
    df["Chg%"] = df["close"].pct_change() * 100

    lat = df.iloc[-1]
    rsi_v, k_v, d_v = safe(df["RSI"]), safe(df["K"]), safe(df["D"])
    ma5_v, ma20_v, ma60_v = safe(df["MA5"]), safe(df["MA20"]), safe(df["MA60"])
    bb_ub_v, bb_lb_v = safe(df["BB_UB"]), safe(df["BB_LB"])
    cl_v, vr_v = safe(df["close"]), safe(df["VRatio"])
    chg = safe(df["Chg%"]) or 0
    macd_v = safe(df["MACD"])
    macd_sig_v = safe(df["MACD_sig"])
    macd_hist_v = safe(df["MACD_hist"])
    macd_hist_prev = safe(df["MACD_hist"], -2)
    vma5_v = safe(df["VMA5"])

    # 布林通道狀態
    bb_status = "中性"
    if cl_v and bb_ub_v and bb_lb_v and ma20_v:
        if cl_v >= bb_ub_v: bb_status = "突破上軌"
        elif cl_v <= bb_lb_v: bb_status = "跌破下軌"
        elif cl_v > ma20_v: bb_status = "中軌之上"
        else: bb_status = "中軌之下"

    i_start = (df["date"].max() - pd.Timedelta(days=45)).strftime("%Y-%m-%d")
    pivot = pd.DataFrame()
    try:
        inst = dl.taiwan_stock_institutional_investors(stock_id=stock_id, start_date=i_start, end_date=end)
        if not inst.empty:
            inst["net"] = inst["buy"] - inst["sell"]
            def cls(n):
                if n in ["Foreign_Investor", "Foreign_Dealer_Self"]: return "外資"
                if n == "Investment_Trust": return "投信"
                if n in ["Dealer_self", "Dealer_Hedging"]: return "自營商"
                return "其他"
            inst["類別"] = inst["name"].apply(cls)
            p = inst.pivot_table(index="date", columns="類別", values="net", aggfunc="sum").fillna(0)
            for c in ["外資", "投信", "自營商"]:
                if c not in p.columns: p[c] = 0
            p["合計"] = p["外資"] + p["投信"] + p["自營商"]
            pivot = (p[["外資", "投信", "自營商", "合計"]] / 1000).round().astype(int)
            pivot.index = pd.to_datetime(pivot.index)
            pivot = pivot.sort_index(ascending=False)
    except: pass

    if not pivot.empty:
        ifor, itru, idal, itot = int(pivot["外資"].iloc[0]), int(pivot["投信"].iloc[0]), int(pivot["自營商"].iloc[0]), int(pivot["合計"].iloc[0])
    else: ifor = itru = idal = itot = 0

    yoy = mom = rev = 0
    has_rev = False
    if not is_etf:
        try:
            r_start = (df["date"].max() - pd.Timedelta(days=550)).strftime("%Y-%m-%d")
            rv = dl.taiwan_stock_month_revenue(stock_id=stock_id, start_date=r_start, end_date=end)
            if not rv.empty:
                rv["date"] = pd.to_datetime(rv["date"])
                rv = rv.sort_values("date").reset_index(drop=True)
                rv["MoM"] = rv["revenue"].pct_change(1) * 100
                rv["YoY"] = rv["revenue"].pct_change(12) * 100
                lr = rv.iloc[-1]
                yoy = float(lr["YoY"]) if pd.notna(lr["YoY"]) else 0
                mom = float(lr["MoM"]) if pd.notna(lr["MoM"]) else 0
                rev = float(lr["revenue"]) / 1e8
                has_rev = True
        except: pass

    alerts = {"red": [], "yellow": [], "green": []}
    if rsi_v:
        if rsi_v > 80: alerts["red"].append("RSI 嚴重超買")
        elif rsi_v > 70: alerts["yellow"].append("RSI 接近超買")
        elif rsi_v < 30: alerts["green"].append("RSI 超賣可能反彈")
    if k_v and d_v:
        if k_v > 80 and d_v > 80: alerts["red"].append("KD 高檔鈍化")
        elif k_v < 20 and d_v < 20: alerts["green"].append("KD 低檔鈍化")
    if all(v is not None for v in [ma5_v, ma20_v, ma60_v, cl_v]):
        if cl_v > ma5_v > ma20_v > ma60_v: alerts["green"].append("均線多頭排列")
        elif cl_v < ma5_v < ma20_v < ma60_v: alerts["red"].append("均線空頭排列")
    if vr_v:
        if vr_v > 2: alerts["yellow"].append(f"爆量 ({vr_v:.1f}x)")
        elif vr_v < 0.5: alerts["yellow"].append("量縮警示")
    if chg > 0 and itot < 0: alerts["red"].append("籌碼背離")

    nr, ng = len(alerts["red"]), len(alerts["green"])
    status = "🔴 過熱" if nr >= 2 else "🟡 觀察" if nr >= 1 else "🟢 健康" if ng >= 2 else "⚪ 中性"

    trend = "多頭" if cl_v and ma20_v and cl_v > ma20_v > (ma60_v or 0) else "空頭" if cl_v and ma20_v and cl_v < ma20_v else "盤整"

    if macd_hist_v is not None and macd_hist_prev is not None:
        if macd_hist_v > 0 and macd_hist_v > macd_hist_prev: macd_status = "多頭擴張"
        elif macd_hist_v > 0 and macd_hist_v < macd_hist_prev: macd_status = "多頭縮減"
        elif macd_hist_v < 0 and macd_hist_v < macd_hist_prev: macd_status = "空頭擴張"
        elif macd_hist_v < 0 and macd_hist_v > macd_hist_prev: macd_status = "空頭縮減"
        else: macd_status = "中性"
    else: macd_status = "N/A"

    vol_status = "放大" if vr_v and vr_v > 1.5 else "量縮" if vr_v and vr_v < 0.7 else "持平"

    df_30 = df.tail(30)
    high_30, low_30 = df_30["high"].max(), df_30["low"].min()
    high_recent, low_recent = df["high"].max(), df["low"].min()
    resist_lo, resist_hi = round(high_30, 2), round(high_recent, 2)
    support_lo = round(ma20_v * 0.97, 2) if ma20_v else round(cl_v * 0.95, 2)
    support_hi = round(ma20_v, 2) if ma20_v else round(cl_v * 0.97, 2)

    score = 50
    if trend == "多頭": score += 15
    elif trend == "空頭": score -= 15
    if rsi_v:
        if rsi_v > 70: score -= 10
        elif rsi_v < 30: score += 10
        elif rsi_v > 50: score += 5
    if macd_v and macd_v > 0: score += 10
    if itot > 0: score += 15
    elif itot < 0: score -= 15
    score = max(0, min(100, score))

    # 即時報價覆寫
    vol_v = int(lat["volume"] / 1000) if "max" in df.columns else int(lat["volume"] / 1000)  # yfinance 可能會很大，這裡做個防護
    suffixes = ['.TW', '.TWO']
    for suffix in suffixes:
        try:
            ticker = yf.Ticker(f"{stock_id}{suffix}")
            todays_data = ticker.history(period='1d')
            if not todays_data.empty:
                rt_price = float(todays_data['Close'].iloc[-1])
                rt_vol = int(todays_data['Volume'].iloc[-1] / 1000)
                prev_data = ticker.history(period='5d')
                rt_chg = ((rt_price - float(prev_data['Close'].iloc[-2])) / float(prev_data['Close'].iloc[-2])) * 100 if len(prev_data) > 1 else 0.0
                cl_v, chg = rt_price, rt_chg
                if rt_vol > 0:
                    vol_v = rt_vol
                    if vma5_v and vma5_v > 0: vr_v = (rt_vol * 1000) / vma5_v
                break
        except: continue

    return {
        "name": name, "id": stock_id, "is_etf": is_etf, "has_rev": has_rev, "industry": industry_category,
        "df": df, "pivot": pivot,
        "close": float(cl_v), "chg": chg, "vol": vol_v,
        "rsi": rsi_v, "k": k_v, "d": d_v, "ma5": ma5_v, "ma20": ma20_v, "ma60": ma60_v,
        "bb_ub": bb_ub_v, "bb_lb": bb_lb_v, "bb_mid": ma20_v, "bb_status": bb_status,
        "macd": macd_v, "macd_sig": macd_sig_v, "macd_hist": macd_hist_v, "macd_status": macd_status,
        "vr": vr_v, "vol_status": vol_status, "trend": trend,
        "ifor": ifor, "itru": itru, "idal": idal, "itot": itot,
        "yoy": yoy, "mom": mom, "rev": rev,
        "status": status, "alerts": alerts, "score": score,
        "resist_lo": resist_lo, "resist_hi": resist_hi, "support_lo": support_lo, "support_hi": support_hi,
        "high_30": high_30, "low_30": low_30, "high_recent": high_recent, "low_recent": low_recent,
    }, None

def generate_overall_conclusion(r):
    parts = [f"{r['name']}（{r['id']}）"]
    parts.append("維持多頭趨勢" if r["trend"] == "多頭" else "處於空頭走勢" if r["trend"] == "空頭" else "處於盤整格局")
    parts.append("短線指標偏過熱" if "🔴" in r["status"] else "短線進入觀察區" if "🟡" in r["status"] else "技術面相對健康" if "🟢" in r["status"] else "技術面中性")
    if r["vol_status"] == "放大": parts.append("近期量能放大")
    elif r["vol_status"] == "量縮": parts.append("近期量能縮減")
    if r["itot"] > 1000: parts.append("籌碼面偏多")
    elif r["itot"] < -1000: parts.append("籌碼面偏空")
    if r["trend"] == "多頭" and r["itot"] > 0: parts.append("有利續強")
    elif r["trend"] == "多頭" and "🔴" in r["status"]: parts.append("留意拉回風險")
    elif r["trend"] == "空頭": parts.append("反彈仍偏空")
    else: parts.append("等待方向明確")
    return "，".join(parts) + "。"

# ============================================
# Gemini API
# ============================================
def call_gemini_with_retry(prompt, use_search=False, max_retries=3):
    if not gemini_keys: return "⚠️ 未設定 Gemini API Key"
    for attempt in range(max_retries):
        client = get_gemini_client_for_key(random.choice(gemini_keys))
        if not client: continue
        try:
            from google.genai import types
            if use_search: return client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])).text
            else: return client.models.generate_content(model="gemini-2.5-flash", contents=prompt).text
        except Exception as e:
            if attempt < max_retries - 1: time.sleep(2)
            else: return f"❌ AI 服務繁忙：{str(e)[:200]}"
    return "❌ 發生錯誤"

@st.cache_data(ttl=3600, show_spinner=False)
def get_ai_analysis(stock_name, stock_id, data_summary):
    prompt = f"""你是台股資深分析師，請根據以下數據對「{stock_name}（{stock_id}）」做深度分析報告。
【當前數據】
{data_summary}
【請依以下結構產出分析報告（繁體中文）】
## 📈 技術面解讀
（3-4 句話，分析目前價格動能、均線排列、技術指標訊號）
## 💼 籌碼面解讀
（3-4 句話，分析法人動向、買賣超意義）
## 💡 短線操作建議
（3-5 條具體建議，含進出場點位概念）
## ⚠️ 風險評估
（2-3 條最重要的風險點）
## 🎯 中長線觀察重點
（3-4 條中長線投資人需要追蹤的指標或事件）
請使用繁體中文，保持客觀，提供具體可執行的建議，加上免責聲明結尾。
"""
    return call_gemini_with_retry(prompt, use_search=False)

@st.cache_data(ttl=1800, show_spinner=False)
def get_news(stock_name, stock_id):
    prompt = f"""請幫我搜尋並整理台股「{stock_name}（{stock_id}）」最近 7 天的新聞，產出 3-5 則最重要的新聞重點。
每則新聞請以以下格式呈現：
### 📰 [新聞標題]
- **日期**：YYYY-MM-DD
- **重點摘要**：（2-3 句話）
- **影響評估**：對股價可能的影響（正面/負面/中性）
請使用繁體中文，並按時間排序（最新的在最前面）。
"""
    return call_gemini_with_retry(prompt, use_search=True)

# ============================================
# 🎨 影像生成 API (Imagen 3)
# ============================================
def generate_paper_craft_image(stock_name, stock_id, trend, close_price, chg, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={api_key}"
    
    prompt = f"""
    Create a highly refined 9:16 vertical infographic presentation slide for a stock market report about "{stock_name}" (Stock ID: {stock_id}).
    Key metrics to display: Price {close_price}, Trend: {trend}. Please use Traditional Chinese text if possible.

    ## VISUAL STYLE: Paper Craft / Layered / Shadow
    ### Color Palette
    - Background: Pastel Colored Construction Paper
    - Primary text: Letters looking like paper cutouts
    - Accent color: Complementary color construction paper

    ### Typography
    - Headings: Cutout letters, or Bold Round Font.
    - Body text: Handwritten Style, or Approachable Sans-serif.
    - Structure: A clear hierarchy between headline and body text

    ### Illustration Style
    - Paper Overlapping with Physical Shadow, Paper Cutout, Collage
    - Scissor-cut edges, Layers
    - Roughness of construction paper, Slight thickness
    - Visualize only motifs that belong to the input theme (e.g., upward arrows, stock charts, or subtle financial symbols)

    ### Tone & Voice
    - Warm, Crafty, Fairy-tale, Dimensional
    - Give the page a composed and refined presence
    """
    
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "9:16"}
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if "predictions" in data and len(data["predictions"]) > 0:
            b64_img = data["predictions"][0]["bytesBase64Encoded"]
            return base64.b64decode(b64_img), None
        else:
            return None, f"API Error: {data}"
    except Exception as e:
        return None, str(e)

# ============================================
# 圖表
# ============================================
MORANDI = {"bg": "#FAF6F0", "grid": "#E5DDD0", "axis": "#8B7E72", "text": "#5C5048", "up": "#C76A6A", "down": "#7B9E89", "ma5": "#CBA365", "ma20": "#6D98AB", "ma60": "#B0889F", "rsi": "#CBA365", "k": "#6D98AB", "d": "#B0889F", "macd_dif": "#6D98AB", "macd_dea": "#CBA365", "foreign": "#6D98AB", "trust": "#C76A6A", "dealer": "#B0889F", "total": "#7B9E89", "price": "#CBA365"}

def plot_kline(df, name, sid, height=620):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.45, 0.13, 0.21, 0.21], subplot_titles=("日 K 線 (含布林通道)", "成交量", "RSI / KD", "MACD"))
    if "BB_UB" in df.columns and df["BB_UB"].notna().any():
        fig.add_trace(go.Scatter(x=df["date"], y=df["BB_UB"], name="布林上軌", line=dict(color="rgba(139,126,114,0.4)", width=1, dash='dot'), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=df["BB_LB"], name="布林下軌", line=dict(color="rgba(139,126,114,0.4)", width=1, dash='dot'), fill='tonexty', fillcolor='rgba(139,126,114,0.05)', showlegend=False), row=1, col=1)
    fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], increasing_line_color=MORANDI["up"], decreasing_line_color=MORANDI["down"], increasing_fillcolor=MORANDI["up"], decreasing_fillcolor=MORANDI["down"], name="K"), row=1, col=1)
    for col, color in [("MA5", MORANDI["ma5"]), ("MA20", MORANDI["ma20"]), ("MA60", MORANDI["ma60"])]:
        fig.add_trace(go.Scatter(x=df["date"], y=df[col], name=col, line=dict(color=color, width=1.4)), row=1, col=1)
    vc = [MORANDI["up"] if c >= o else MORANDI["down"] for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"], marker_color=vc, name="量", showlegend=False, opacity=0.75), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["RSI"], name="RSI", line=dict(color=MORANDI["rsi"], width=1.6)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["K"], name="K", line=dict(color=MORANDI["k"], width=1.3)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["D"], name="D", line=dict(color=MORANDI["d"], width=1.3)), row=3, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color=MORANDI["up"], row=3, col=1, line_width=1, opacity=0.5)
    fig.add_hline(y=20, line_dash="dash", line_color=MORANDI["down"], row=3, col=1, line_width=1, opacity=0.5)
    if df["MACD_hist"].notna().any():
        hc = [MORANDI["up"] if v >= 0 else MORANDI["down"] for v in df["MACD_hist"].fillna(0)]
        fig.add_trace(go.Bar(x=df["date"], y=df["MACD_hist"], marker_color=hc, name="MACD柱", showlegend=False, opacity=0.75), row=4, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=df["MACD"], name="DIF", line=dict(color=MORANDI["macd_dif"], width=1.4)), row=4, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=df["MACD_sig"], name="DEA", line=dict(color=MORANDI["macd_dea"], width=1.4)), row=4, col=1)
    fig.update_layout(template="plotly_white", height=height, xaxis_rangeslider_visible=False, hovermode="x unified", plot_bgcolor=MORANDI["bg"], paper_bgcolor=MORANDI["bg"], font=dict(color=MORANDI["text"], family="Arial, 'Noto Sans TC', sans-serif"), margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255,255,255,0.7)"))
    return fig

def plot_inst(pivot, df):
    if pivot.empty: return None
    rec = pivot.head(10).sort_index()
    pr = df[df["date"].isin(pd.to_datetime(rec.index))][["date", "close"]].sort_values("date")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for col, color in [("外資", MORANDI["foreign"]), ("投信", MORANDI["trust"]), ("自營商", MORANDI["dealer"]), ("合計", MORANDI["total"])]:
        fig.add_trace(go.Bar(x=rec.index, y=rec[col], name=col, marker_color=color, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=pr["date"], y=pr["close"], name="股價", line=dict(color=MORANDI["price"], width=2.5), marker=dict(size=8), mode="lines+markers"), secondary_y=True)
    fig.update_layout(template="plotly_white", barmode="group", height=340, plot_bgcolor=MORANDI["bg"], paper_bgcolor=MORANDI["bg"], font=dict(color=MORANDI["text"]), margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified")
    return fig

def plot_morandi_gauge(score):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, number={'font': {'size': 36, 'color': '#3D3833'}}, gauge={'axis': {'range': [0, 100], 'visible': False}, 'bar': {'color': "rgba(0,0,0,0)"}, 'steps': [{'range': [0, 40], 'color': "#DBE8E0"}, {'range': [40, 60], 'color': "#F5EFD9"}, {'range': [60, 100], 'color': "#F5DCDC"}]}))
    theta = (1 - score / 100) * np.pi
    fig.update_layout(shapes=[dict(type="line", x0=0.5, y0=0.25, x1=0.5 + 0.38 * np.cos(theta), y1=0.25 + 0.38 * np.sin(theta), line=dict(color="#5C5048", width=5), xref="paper", yref="paper")], height=180, margin=dict(l=15, r=15, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
    return fig

def render_inst_card(label, value):
    cls, sign = ("inst-value-up", "+") if value > 0 else ("inst-value-down", "") if value < 0 else ("inst-value-flat", "")
    return f'<div class="inst-card"><div class="inst-label">{label}</div><div class="{cls}">{sign}{value:,}</div></div>'

def render_pct_card(label, pct, suffix="%"):
    cls = "inst-value-up" if pct > 0 else "inst-value-down" if pct < 0 else "inst-value-flat"
    return f'<div class="inst-card"><div class="inst-label">{label}</div><div class="{cls}">{pct:+.2f}{suffix}</div></div>'

# ============================================
# HTML 列印報告產生器
# ============================================
def md_to_html(text):
    if not text:
        return ""
    lines = text.split("\n")
    out = []
    in_list = False
    for line in lines:
        line = line.rstrip()
        if not line:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("")
            continue

        import re as _re
        line = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)

        if line.startswith("### "):
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<h3>{html_lib.escape(line[4:])[:].replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')}</h3>")
        elif line.startswith("## "):
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{line[2:]}</li>")
        else:
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<p>{line}</p>")

    if in_list: out.append("</ul>")
    return "\n".join(out)

def build_html_report(r, ai_text, news_text, fig_kline=None, fig_inst=None):
    name = r["name"]
    sid = r["id"]
    industry = r["industry"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    kline_html_str = fig_kline.to_html(full_html=False, include_plotlyjs='cdn') if fig_kline else ""
    inst_html_str = fig_inst.to_html(full_html=False, include_plotlyjs='cdn') if fig_inst else "<p class='hint'>無法人籌碼資料</p>"
    chg_color = "#C76A6A" if r["chg"] >= 0 else "#7B9E89"
    chg_arrow = "▲" if r["chg"] >= 0 else "▼"

    alerts_html = ""
    for a in r["alerts"]["red"]: alerts_html += f'<span class="chip chip-red">🔴 {a}</span>'
    for a in r["alerts"]["yellow"]: alerts_html += f'<span class="chip chip-yellow">🟡 {a}</span>'
    for a in r["alerts"]["green"]: alerts_html += f'<span class="chip chip-green">🟢 {a}</span>'
    if not alerts_html: alerts_html = '<span class="chip">⚪ 目前無特殊警示</span>'

    def fmt_inst(label, v):
        cls = "v-up" if v > 0 else "v-down" if v < 0 else "v-flat"
        sign = "+" if v > 0 else ""
        return f'<div class="cell"><div class="lbl">{label}</div><div class="val {cls}">{sign}{v:,}</div></div>'

    inst_html = fmt_inst("外資(張)", r["ifor"]) + fmt_inst("投信(張)", r["itru"]) + fmt_inst("自營商(張)", r["idal"]) + fmt_inst("合計(張)", r["itot"])

    if r["has_rev"]:
        rev_html = f"""<div class="grid-3">
          <div class="cell"><div class="lbl">最新月營收</div><div class="val">{r['rev']:.2f} 億</div></div>
          <div class="cell"><div class="lbl">YoY 年增率</div><div class="val {'v-up' if r['yoy']>0 else 'v-down'}">{r['yoy']:+.2f}%</div></div>
          <div class="cell"><div class="lbl">MoM 月增率</div><div class="val {'v-up' if r['mom']>0 else 'v-down'}">{r['mom']:+.2f}%</div></div>
        </div>"""
    else:
        rev_html = '<p class="hint">📌 ETF / 興櫃，無月營收資料</p>'

    conclusion = generate_overall_conclusion(r)
    ai_html = md_to_html(ai_text) if ai_text else "<p class='hint'>（未產生 AI 解析）</p>"
    news_html = md_to_html(news_text) if news_text else "<p class='hint'>（未抓取新聞）</p>"

    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>{name}（{sid}）AI 分析報告 - {now}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: "Noto Sans TC", "Microsoft JhengHei", sans-serif; background: #F5F1EB; color: #4A4540; margin: 0; padding: 30px 40px; line-height: 1.7; max-width: 900px; margin: 0 auto; }}
  .toolbar {{ background: #FAF6F0; border: 1px solid #D4CABB; border-radius: 10px; padding: 12px 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }}
  .toolbar-tip {{ color: #8B7E72; font-size: 13px; }}
  .btn {{ background: #8B9D83; color: #fff; border: none; padding: 8px 18px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; font-family: inherit; }}
  .btn:hover {{ background: #6F8169; }}
  .header {{ border-bottom: 3px solid #C9B689; padding-bottom: 14px; margin-bottom: 22px; }}
  .header h1 {{ color: #5C5048; margin: 0; font-size: 26px; }}
  .header .meta {{ color: #8B7E72; font-size: 13px; margin-top: 6px; }}
  h2 {{ color: #8B6F47; border-left: 4px solid #C9B689; padding-left: 12px; margin-top: 28px; margin-bottom: 12px; font-size: 18px; }}
  h3 {{ color: #5C5048; font-size: 15px; margin-top: 18px; margin-bottom: 8px; }}
  p {{ margin: 6px 0; }}
  ul {{ margin: 6px 0 12px 0; padding-left: 22px; }}
  li {{ margin: 3px 0; }}
  strong {{ color: #C76A6A; }}
  .price-row {{ background: linear-gradient(135deg, #FAF6F0, #F5EFE5); border: 1px solid #D4CABB; border-radius: 10px; padding: 16px 22px; margin-bottom: 18px; display: flex; align-items: center; gap: 24px; flex-wrap: wrap; }}
  .price-num {{ font-size: 32px; font-weight: 700; color: #3D3833; }}
  .price-chg {{ font-size: 18px; font-weight: 700; color: {chg_color}; }}
  .price-meta {{ color: #8B7E72; font-size: 13px; }}
  .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
  .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
  .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
  .cell {{ background: #FAF6F0; border: 1px solid #E5DDD0; border-radius: 8px; padding: 12px; text-align: left; }}
  .lbl {{ color: #8B7E72; font-size: 12px; margin-bottom: 6px; }}
  .val {{ font-size: 22px; font-weight: 700; color: #3D3833; }}
  .v-up {{ color: #C76A6A; }}
  .v-down {{ color: #7B9E89; }}
  .v-flat {{ color: #8B7E72; }}
  .chip {{ display: inline-block; padding: 5px 12px; border-radius: 14px; margin: 3px 4px 3px 0; font-size: 13px; background: #F0EDE7; color: #5C5048; border: 1px solid #D4CABB; }}
  .chip-red {{ background: #FBEDED; color: #C76A6A; border-color: #E5BFBF; }}
  .chip-yellow {{ background: #FAF1D8; color: #B89243; border-color: #E5D9A8; }}
  .chip-green {{ background: #EAF1EC; color: #5C8169; border-color: #B8D0BE; }}
  .conclusion {{ background: linear-gradient(135deg, #F0E9DA, #E8DFCC); border: 2px solid #C9B689; border-radius: 10px; padding: 16px 20px; margin: 18px 0; }}
  .conclusion-label {{ background: #8B6F47; color: #fff; padding: 4px 10px; border-radius: 5px; font-size: 13px; font-weight: 700; display: inline-block; margin-bottom: 8px; }}
  .conclusion-text {{ font-size: 15px; color: #5C5048; font-weight: 500; }}
  .chart-container {{ background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #D4CABB; margin-bottom: 20px; width: 100%; overflow: hidden; }}
  .hint {{ color: #8B7E72; font-style: italic; font-size: 13px; }}
  .footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #D4CABB; color: #8B7E72; font-size: 12px; text-align: center; }}
  @media print {{
    body {{ background: #fff; padding: 12mm; max-width: 100%; }}
    .toolbar, .no-print {{ display: none !important; }}
    h2 {{ page-break-after: avoid; }}
    .conclusion, .price-row, .grid-3, .grid-4, .chart-container {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>

  <div class="toolbar no-print">
    <div class="toolbar-tip">💡 按下右側「列印 / 存 PDF」按鈕，或鍵盤 Ctrl + P（Mac: Cmd + P）即可儲存為 PDF</div>
    <button class="btn" onclick="window.print()">🖨️ 列印 / 存 PDF</button>
  </div>

  <div class="header">
    <h1>📊 {name}（{sid}）AI 分析報告</h1>
    <div class="meta">產業：{industry} ｜ 報告生成：{now} ｜ 整體狀態：{r['status']}</div>
  </div>

  <div class="price-row">
    <div>
      <div class="lbl">即時收盤價</div>
      <span class="price-num">{r['close']:.2f}</span>
      <span class="price-chg">{chg_arrow} {r['chg']:+.2f}%</span>
    </div>
    <div>
      <div class="lbl">成交量</div>
      <span class="price-num" style="font-size:24px;">{r['vol']:,}</span>
      <span class="price-meta">張</span>
    </div>
    <div>
      <div class="lbl">偏多分數</div>
      <span class="price-num" style="font-size:24px;color:#B89243;">{r['score']} / 100</span>
    </div>
  </div>

  <h2>🚦 警示燈號</h2>
  <div>{alerts_html}</div>
  
  <h2>📈 趨勢圖表 (日 K 線)</h2>
  <div class="chart-container">
    {kline_html_str}
  </div>

  <h2>📈 技術面總覽</h2>
  <div class="grid-4">
    <div class="cell"><div class="lbl">趨勢方向</div><div class="val v-{('up' if r['trend']=='多頭' else 'down' if r['trend']=='空頭' else 'flat')}">{r['trend']}</div></div>
    <div class="cell"><div class="lbl">RSI(14)</div><div class="val">{f"{r['rsi']:.2f}" if r['rsi'] else 'N/A'}</div></div>
    <div class="cell"><div class="lbl">MACD 狀態</div><div class="val">{r['macd_status']}</div></div>
    <div class="cell"><div class="lbl">量能變化</div><div class="val">{r['vol_status']}</div></div>
  </div>
  <div class="grid-3" style="margin-top:8px;">
    <div class="cell"><div class="lbl">MA5</div><div class="val">{f"{r['ma5']:.2f}" if r['ma5'] else 'N/A'}</div></div>
    <div class="cell"><div class="lbl">MA20</div><div class="val">{f"{r['ma20']:.2f}" if r['ma20'] else 'N/A'}</div></div>
    <div class="cell"><div class="lbl">MA60</div><div class="val">{f"{r['ma60']:.2f}" if r['ma60'] else 'N/A'}</div></div>
  </div>

  <h2>👥 籌碼面動向</h2>
  <div class="grid-4">{inst_html}</div>
  <div class="chart-container" style="margin-top:8px;">
    {inst_html_str}
  </div>

  <h2>📊 基本面</h2>
  {rev_html}

  <h2>🎯 關鍵價位</h2>
  <div class="grid-2">
    <div class="cell"><div class="lbl">壓力區</div><div class="val v-up">{r['resist_lo']:.2f} ~ {r['resist_hi']:.2f}</div></div>
    <div class="cell"><div class="lbl">支撐區</div><div class="val v-down">{r['support_lo']:.2f} ~ {r['support_hi']:.2f}</div></div>
  </div>

  <div class="conclusion">
    <div class="conclusion-label">⭐ 整體結論</div>
    <div class="conclusion-text">{conclusion}</div>
  </div>

  <h2>🤖 AI 智能解析</h2>
  {ai_html}

  <h2>📰 近期重要新聞</h2>
  {news_html}

  <div class="footer">
    📊 資料來源：FinMind / Yahoo Finance ｜ 🤖 AI：Google Gemini 2.5 Flash<br>
    ⚠️ 本報告僅供研究參考，不構成投資建議。投資有風險，操作請審慎評估。
  </div>

</body>
</html>"""
    return html

# ============================================
# 主畫面 UI
# ============================================
st.title("📊 台股 AI 個股分析")
st.caption(f"🤖 整合技術面 / 籌碼面 / 基本面 / Gemini AI 解讀 / 即時新聞 · FinMind {finmind_token_count} token")

ic1, ic2 = st.columns([4, 1])
with ic1:
    sid = st.text_input("stock_input", placeholder="輸入股票代號，例如 2330、0050", label_visibility="collapsed").strip().upper()
with ic2:
    go_btn = st.button("🔍 開始分析", type="primary", use_container_width=True)

st.divider()

if not (go_btn and sid):
    if not sid:
        st.info("👆 請輸入股票代號，按「開始分析」")
        st.stop()

with st.spinner(f"⚙️ 分析 {sid} 中..."):
    r, err = analyze(sid)

if err or not r:
    st.error(f"❌ {err or '分析失敗'}")
    st.stop()

conclusion_color = "#C76A6A" if r['score'] >= 60 else "#7B9E89" if r['score'] <= 40 else "#5C5048"
today_str = datetime.now().strftime("%Y%m%d")

# ============================================
# 📤 導出與分享
# ============================================
st.markdown("### 📤 導出與分享")
c_exp1, c_exp2, c_exp3 = st.columns([1, 1, 2])

with c_exp1:
    if st.button("📝 產生完整 AI 報告", use_container_width=True, key="btn_gen_report"):
        with st.spinner("🔄 正在呼叫 AI 與圖表整合中，請稍候..."):
            summary = f"- 收盤價：{r['close']:.2f}\n- 成交量：{r['vol']:,} 張\n- 技術指標：RSI={r['rsi']}, MACD={r['macd']}\n- 法人籌碼：合計 {r['itot']:+,} 張\n- 狀態：{r['status']}"
            ai_text = get_ai_analysis(r["name"], r["id"], summary)
            news_text = get_news(r["name"], r["id"])
            
            fig_kline_export = plot_kline(r["df"], r["name"], r["id"], height=550)
            fig_inst_export = plot_inst(r["pivot"], r["df"]) if not r["pivot"].empty else None

            html_report = build_html_report(r, ai_text, news_text, fig_kline=fig_kline_export, fig_inst=fig_inst_export)
            st.session_state[f'html_report_{sid}'] = html_report
            st.success("✅ 報告產生完畢！")

    if f'html_report_{sid}' in st.session_state:
        st.download_button(
            label="⬇️ 下載 HTML 報告",
            data=st.session_state[f'html_report_{sid}'].encode("utf-8"),
            file_name=f"{r['name']}({sid})_完整AI解析_{today_str}.html",
            mime="text/html",
            use_container_width=True,
            help="下載後雙擊開啟，按 Ctrl+P 即可存成 PDF"
        )

with c_exp2:
    share_text = f"【台股AI分析】{r['name']} ({r['id']})\n股價：{r['close']:.2f} ({r['chg']:+.2f}%)\n趨勢：{r['trend']}\n分數：{r['score']}\n結論：{generate_overall_conclusion(r)}"
    import urllib.parse
    encoded = urllib.parse.quote(share_text)
    st.link_button("💬 分享至 LINE", f"https://line.me/R/msg/text/?{encoded}", use_container_width=True)

with c_exp3:
    if st.button("📋 產生純文字摘要", use_container_width=True):
        st.code(share_text, language="text")

# 🎨 獨立區域：AI 視覺化圖卡
st.markdown("#### 🎨 AI 視覺化圖卡 (9:16 手機版紙雕風格)")
c_img_btn, c_img_show = st.columns([1, 3])
with c_img_btn:
    if st.button("🖼️ 產生紙雕風格圖卡", use_container_width=True):
        if not gemini_keys:
            st.error("⚠️ 未設定 Gemini API Key")
        else:
            with st.spinner("🎨 AI 畫家正在為您剪紙、拼貼中... (約需 10~15 秒)"):
                api_key = random.choice(gemini_keys)
                img_bytes, img_err = generate_paper_craft_image(r["name"], r["id"], r["trend"], r["close"], r["chg"], api_key)
                if img_bytes:
                    st.session_state[f'paper_img_{sid}'] = img_bytes
                    st.success("✅ 圖卡產生完畢！")
                else:
                    st.error(f"❌ 產生失敗：{img_err}")
    st.caption("註：因圖像生成模型的限制，圖中的中文字體可能會發生變形或錯位，請將其視為背景的風格點綴。")

with c_img_show:
    if f'paper_img_{sid}' in st.session_state:
        st.image(st.session_state[f'paper_img_{sid}'], width=300)
        st.download_button(
            label="⬇️ 下載 9:16 圖卡",
            data=st.session_state[f'paper_img_{sid}'],
            file_name=f"{r['name']}({sid})_紙雕風格圖卡_{today_str}.jpg",
            mime="image/jpeg",
            use_container_width=False
        )

# 顯示報告預覽
if f'html_report_{sid}' in st.session_state:
    with st.expander("👁️ 預覽完整報告（可列印 / 存 PDF）", expanded=True):
        st.markdown("💡 **使用方式**：把報告下載後在瀏覽器開啟 → 按 **Ctrl+P** 即可另存為 PDF（手機選「列印 → 另存 PDF」）")
        components.html(st.session_state[f'html_report_{sid}'], height=800, scrolling=True)

st.divider()

# ============================================
# 模式切換
# ============================================
mode_tab1, mode_tab2, mode_tab3 = st.tabs(["📊 詳細模式", "🎯 7 大重點速覽", "🖥️ 旗艦全景儀表板"])

with mode_tab1:
    st.subheader(f"{r['name']} ({r['id']})  {r['status']}")
    chg_color = "#C76A6A" if r["chg"] >= 0 else "#7B9E89"
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="inst-card"><div class="inst-label">收盤價</div><div style="color:#3D3833;font-size:28px;font-weight:700;">{r["close"]:.2f}</div><div style="color:{chg_color};font-size:14px;font-weight:600;">{"▲" if r["chg"]>=0 else "▼"} {r["chg"]:+.2f}%</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="inst-card"><div class="inst-label">成交量</div><div style="color:#3D3833;font-size:28px;font-weight:700;">{r["vol"]:,}</div><div style="color:#8B7E72;font-size:13px;">張</div></div>', unsafe_allow_html=True)
    with c3:
        rsi_color = "#C76A6A" if r["rsi"] and r["rsi"] > 70 else "#7B9E89" if r["rsi"] and r["rsi"] < 30 else "#3D3833"
        rsi_disp = f"{r['rsi']:.2f}" if r['rsi'] else "N/A"
        st.markdown(f'<div class="inst-card"><div class="inst-label">RSI(14)</div><div style="color:{rsi_color};font-size:28px;font-weight:700;">{rsi_disp}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="inst-card"><div class="inst-label">更新時間</div><div style="color:#3D3833;font-size:22px;font-weight:700;">{datetime.now().strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["📈 技術面", "💼 籌碼面", "📊 基本面", "🤖 AI 智能解讀", "📰 即時新聞"])
    
    with t1: st.plotly_chart(plot_kline(r["df"], r["name"], r["id"]), use_container_width=True, key="kline_tab1")
    with t2:
        cc = st.columns(4)
        cc[0].markdown(render_inst_card("外資", r["ifor"]), unsafe_allow_html=True)
        cc[1].markdown(render_inst_card("投信", r["itru"]), unsafe_allow_html=True)
        cc[2].markdown(render_inst_card("自營商", r["idal"]), unsafe_allow_html=True)
        cc[3].markdown(render_inst_card("合計", r["itot"]), unsafe_allow_html=True)
        if not r["pivot"].empty: st.plotly_chart(plot_inst(r["pivot"], r["df"]), use_container_width=True, key="inst_tab1")
    with t3:
        if r["has_rev"]:
            bc = st.columns(3)
            with bc[0]: st.markdown(f'<div class="inst-card"><div class="inst-label">最新月營收</div><div style="color:#3D3833;font-size:28px;font-weight:700;">{r["rev"]:.2f} 億</div></div>', unsafe_allow_html=True)
            with bc[1]: st.markdown(render_pct_card("YoY 年增率", r["yoy"]), unsafe_allow_html=True)
            with bc[2]: st.markdown(render_pct_card("MoM 月增率", r["mom"]), unsafe_allow_html=True)
    with t4:
        if st.button("🚀 產生 AI 分析報告", type="primary", key="ai_btn_detail"):
            with st.spinner("AI 思考中..."):
                summary = f"收盤:{r['close']}, 漲跌:{r['chg']}%, 籌碼:{r['itot']}, 狀態:{r['status']}"
                st.markdown(get_ai_analysis(r["name"], r["id"], summary))
    with t5:
        if st.button("🔍 搜尋最新新聞", type="primary", key="news_btn_detail"):
            with st.spinner("搜尋中..."): st.markdown(get_news(r["name"], r["id"]))

with mode_tab2:
    st.markdown(f"""
    <div class="overview-header">
        <div class="overview-title">{r['name']} {r['id']} ｜ 7 大重點速覽</div>
        <div class="overview-subtitle">Q版講師帶你看懂：{r['trend']}趨勢、技術指標、籌碼分析</div>
        <div class="overview-pills">
            <span class="overview-pill"><span style="color:#8B7E72;">收盤</span>
                <span style="color:#3D3833;font-weight:700;font-size:16px;margin-left:6px;">{r['close']:.2f}</span></span>
            <span class="{'overview-pill-red' if r['chg'] >= 0 else 'overview-pill-green'}">{'▲' if r['chg']>=0 else '▼'} {r['chg']:+.2f}%</span>
            <span class="overview-pill"><span style="color:#8B7E72;">成交量</span>
                <span style="color:#3D3833;font-weight:700;margin-left:6px;">{r['vol']:,}</span>
                <span style="color:#8B7E72;font-size:11px;margin-left:2px;">張</span></span>
            <span class="overview-pill"><span style="color:#8B7E72;">狀態</span>
                <span style="color:#B89243;font-weight:600;margin-left:6px;">{r['status']}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    row1c1, row1c2, row1c3 = st.columns(3)

    with row1c1:
        high30_pct = ((r['close'] / r['high_30'] - 1) * 100) if r['high_30'] else 0
        if "🔴" in r['status']: st_text = "高檔回落整理"
        elif "🟢" in r['status']: st_text = "穩健上攻中"
        elif "🟡" in r['status']: st_text = "震盪觀察區間"
        else: st_text = "盤整等待方向"
        chg_disp_cls = "kv-value-up" if r['chg'] >= 0 else "kv-value-down"
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">📈 股價表現</div>
            <div class="kv-row"><span class="kv-label">收盤</span><span class="kv-value">{r["close"]:.2f}</span></div>
            <div class="kv-row"><span class="kv-label">漲跌</span><span class="{chg_disp_cls}">{r["chg"]:+.2f}%</span></div>
            <div class="kv-row"><span class="kv-label">近期高點</span><span class="kv-value-yellow">{r["high_recent"]:.2f}</span></div>
            <div class="kv-row"><span class="kv-label">近期低點</span><span class="kv-value-cyan">{r["low_recent"]:.2f}</span></div>
            <div class="kv-row"><span class="kv-label">距高點</span><span class="kv-value">{high30_pct:+.1f}%</span></div>
            <div style="margin-top:10px;padding-top:8px;border-top:1px solid #E5DDD0;">
                <div style="color:#4A4540;font-size:13px;padding-left:16px;position:relative;">
                    <span style="position:absolute;left:0;color:#B89243;font-size:9px;top:6px;">●</span>{st_text}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with row1c2:
        ma5 = f"{r['ma5']:.2f}" if r['ma5'] else "N/A"
        ma20 = f"{r['ma20']:.2f}" if r['ma20'] else "N/A"
        ma60 = f"{r['ma60']:.2f}" if r['ma60'] else "N/A"
        if r['trend'] == "多頭":
            trend_color = "kv-value-up"
            trend_text = "均線多頭排列（5 > 20 > 60）"
        elif r['trend'] == "空頭":
            trend_color = "kv-value-down"
            trend_text = "均線空頭排列（5 < 20 < 60）"
        else:
            trend_color = "kv-value-yellow"
            trend_text = "均線糾結，趨勢不明"
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">📊 趨勢與均線</div>
            <div class="kv-row"><span class="kv-label">趨勢方向</span><span class="{trend_color}">{r["trend"]}</span></div>
            <div class="kv-row"><span class="kv-label">MA5</span><span class="kv-value-yellow">{ma5}</span></div>
            <div class="kv-row"><span class="kv-label">MA20</span><span class="kv-value-cyan">{ma20}</span></div>
            <div class="kv-row"><span class="kv-label">MA60</span><span class="kv-value" style="color:#8B5F7A;">{ma60}</span></div>
            <div style="margin-top:10px;padding-top:8px;border-top:1px solid #E5DDD0;">
                <div style="color:#4A4540;font-size:13px;padding-left:16px;position:relative;">
                    <span style="position:absolute;left:0;color:#B89243;font-size:9px;top:6px;">●</span>{trend_text}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with row1c3:
        rsi_disp = f"{r['rsi']:.1f}" if r['rsi'] else "N/A"
        k_disp = f"{r['k']:.1f}" if r['k'] else "N/A"
        d_disp = f"{r['d']:.1f}" if r['d'] else "N/A"
        macd_disp = f"{r['macd']:.2f}" if r['macd'] else "N/A"
        rsi_cls = "kv-value-up" if r['rsi'] and r['rsi'] > 70 else "kv-value-down" if r['rsi'] and r['rsi'] < 30 else "kv-value"
        kd_cls = "kv-value-up" if r['k'] and r['k'] > 80 else "kv-value-down" if r['k'] and r['k'] < 20 else "kv-value"
        macd_cls = "kv-value-up" if "多頭" in r['macd_status'] else "kv-value-down" if "空頭" in r['macd_status'] else "kv-value"
        if r['rsi'] and r['rsi'] > 80: tech_summary = "RSI 嚴重超買，留意拉回"
        elif r['rsi'] and r['rsi'] > 70: tech_summary = "RSI 偏高，技術過熱"
        elif r['rsi'] and r['rsi'] < 30: tech_summary = "RSI 偏低，可能反彈"
        elif r['k'] and r['d'] and r['k'] > r['d']: tech_summary = "KD 多頭排列，續強機率高"
        else: tech_summary = "技術指標中性區間"
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">💹 技術指標</div>
            <div class="kv-row"><span class="kv-label">RSI(14)</span><span class="{rsi_cls}">{rsi_disp}</span></div>
            <div class="kv-row"><span class="kv-label">K / D</span><span class="{kd_cls}">{k_disp} / {d_disp}</span></div>
            <div class="kv-row"><span class="kv-label">MACD</span><span class="{macd_cls}">{macd_disp}</span></div>
            <div class="kv-row"><span class="kv-label">MACD 狀態</span><span class="{macd_cls}">{r['macd_status']}</span></div>
            <div style="margin-top:10px;padding-top:8px;border-top:1px solid #E5DDD0;">
                <div style="color:#4A4540;font-size:13px;padding-left:16px;position:relative;">
                    <span style="position:absolute;left:0;color:#B89243;font-size:9px;top:6px;">●</span>{tech_summary}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    row2c1, row2c2, row2c3 = st.columns(3)

    with row2c1:
        if r['vol_status'] == "放大":
            vol_text = f"量能放大（量比 {r['vr']:.2f}x）"
            vol_cls = "kv-value-up"
        elif r['vol_status'] == "量縮":
            vol_text = f"量能縮減（量比 {r['vr']:.2f}x）"
            vol_cls = "kv-value-down"
        else:
            vol_text = f"量能持平（量比 {r['vr']:.2f}x）"
            vol_cls = "kv-value"
        if "🔴" in r['status'] and r['vol_status'] == "放大": type_text = "高檔放量警示"
        elif r['trend'] == "多頭" and r['vol_status'] == "量縮": type_text = "量縮觀察"
        elif r['trend'] == "空頭" and r['vol_status'] == "放大": type_text = "放量下跌注意"
        else: type_text = "中性無明顯型態"
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">📦 量能與型態</div>
            <div class="kv-row"><span class="kv-label">成交量</span><span class="kv-value">{r["vol"]:,} 張</span></div>
            <div class="kv-row"><span class="kv-label">量比</span><span class="{vol_cls}">{r["vr"]:.2f}x</span></div>
            <div class="kv-row"><span class="kv-label">量能變化</span><span class="{vol_cls}">{r["vol_status"]}</span></div>
            <div class="kv-row"><span class="kv-label">型態研判</span><span class="kv-value-yellow">{type_text}</span></div>
            <div style="margin-top:10px;padding-top:8px;border-top:1px solid #E5DDD0;">
                <div style="color:#4A4540;font-size:13px;padding-left:16px;position:relative;">
                    <span style="position:absolute;left:0;color:#B89243;font-size:9px;top:6px;">●</span>{vol_text}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with row2c2:
        ifor_cls = "kv-value-up" if r['ifor'] > 0 else "kv-value-down" if r['ifor'] < 0 else "kv-value"
        itru_cls = "kv-value-up" if r['itru'] > 0 else "kv-value-down" if r['itru'] < 0 else "kv-value"
        idal_cls = "kv-value-up" if r['idal'] > 0 else "kv-value-down" if r['idal'] < 0 else "kv-value"
        itot_cls = "kv-value-up" if r['itot'] > 0 else "kv-value-down" if r['itot'] < 0 else "kv-value"
        if r['itot'] > 1000: chip_text = "法人合計大買，籌碼面偏多"
        elif r['itot'] < -1000: chip_text = "法人合計大賣，籌碼面偏空"
        elif r['ifor'] > 0 and r['itru'] > 0: chip_text = "外資投信同步買超"
        elif r['ifor'] < 0 and r['itru'] < 0: chip_text = "外資投信同步賣超"
        else: chip_text = "法人籌碼分歧，觀察為宜"
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">👥 籌碼分析</div>
            <div class="kv-row"><span class="kv-label">外資</span><span class="{ifor_cls}">{r["ifor"]:+,} 張</span></div>
            <div class="kv-row"><span class="kv-label">投信</span><span class="{itru_cls}">{r["itru"]:+,} 張</span></div>
            <div class="kv-row"><span class="kv-label">自營商</span><span class="{idal_cls}">{r["idal"]:+,} 張</span></div>
            <div class="kv-row"><span class="kv-label">合計</span><span class="{itot_cls}">{r["itot"]:+,} 張</span></div>
            <div style="margin-top:10px;padding-top:8px;border-top:1px solid #E5DDD0;">
                <div style="color:#4A4540;font-size:13px;padding-left:16px;position:relative;">
                    <span style="position:absolute;left:0;color:#B89243;font-size:9px;top:6px;">●</span>{chip_text}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with row2c3:
        if "🔴" in r['status']:
            ops = ["短線追高風險高", "建議逢高分批減碼", "等待回測支撐再進場"]
        elif r['trend'] == "多頭" and "🟢" in r['status']:
            ops = ["技術面健康可佈局", "建議分批承接", "支撐區是加碼點"]
        elif r['trend'] == "空頭":
            ops = ["趨勢偏空建議觀望", "若反彈偏空操作", "破支撐應停損出場"]
        else:
            ops = ["盤整待方向", "區間操作為主", "突破再追進"]
        ops_html = "".join([f'<div style="color:#4A4540;font-size:13px;padding:3px 0 3px 16px;position:relative;line-height:1.6;"><span style="position:absolute;left:0;color:#B89243;font-size:9px;top:8px;">●</span>{op}</div>' for op in ops])
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🎯 關鍵價位與策略</div>
            <div class="kv-row"><span class="kv-label">壓力區</span><span class="kv-value-up">{r["resist_lo"]:.2f} ~ {r["resist_hi"]:.2f}</span></div>
            <div class="kv-row"><span class="kv-label">支撐區</span><span class="kv-value-down">{r["support_lo"]:.2f} ~ {r["support_hi"]:.2f}</span></div>
            <div class="kv-row"><span class="kv-label">短線觀察</span><span class="kv-value-yellow">20 日線附近</span></div>
            <div style="margin-top:10px;padding-top:8px;border-top:1px solid #E5DDD0;">
                <div style="color:#8B6F47;font-size:13px;font-weight:600;margin-bottom:4px;">💡 操作建議</div>
                {ops_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="conclusion-box"><div class="conclusion-title">⭐ 整體結論</div><div class="conclusion-text" style="color: {conclusion_color};">{generate_overall_conclusion(r)}</div></div>', unsafe_allow_html=True)


with mode_tab3:
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid #E5DDD0; padding-bottom:8px; margin-bottom:12px;">
        <div>
            <span style="font-size:24px; font-weight:700; color:#5C5048;">{r['name']} ({r['id']})</span>
            <span style="background:#F0E9DA; color:#8B6F47; padding:3px 10px; border-radius:12px; font-size:12px; margin-left:10px; font-weight:600;">{r['industry']}</span>
        </div>
        <div style="text-align:right;">
            <span style="font-size:14px; color:#8B7E72; margin-right:8px;">日 K 線</span>
            <span style="font-size:28px; font-weight:800; color:{chg_color};">{r['close']:.2f}</span>
            <span style="font-size:16px; font-weight:700; color:{chg_color}; margin-left:8px;">{r['chg']:+.2f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    top_left, top_right = st.columns([6, 4])

    with top_left:
        st.plotly_chart(plot_kline(r["df"], r["name"], r["id"], height=620), use_container_width=True, key="kline_tab3")

    with top_right:
        rsi_disp = f"{r['rsi']:.1f}" if r['rsi'] else "N/A"
        k_disp = f"{r['k']:.1f}" if r['k'] else "N/A"
        d_disp = f"{r['d']:.1f}" if r['d'] else "N/A"
        macd_disp = f"{r['macd']:.2f}" if r['macd'] else "N/A"

        if r['ma5'] and r['ma20'] and r['ma60']:
            if r['close'] > r['ma5'] > r['ma20'] > r['ma60']: ma_state = "均線多頭"
            elif r['close'] < r['ma5'] < r['ma20'] < r['ma60']: ma_state = "均線空頭"
            else: ma_state = "均線糾結"
        else: ma_state = "N/A"

        if r['k'] and r['d']:
            if r['k'] > r['d']: kd_state = "黃金交叉" if r['k'] < 60 else "偏多走勢"
            else: kd_state = "死亡交叉" if r['k'] > 40 else "偏空走勢"
        else: kd_state = "N/A"

        if r['chg'] > 0 and r['vol_status'] == "放大": pv_state = "價漲量增"
        elif r['chg'] > 0 and r['vol_status'] == "量縮": pv_state = "價漲量縮"
        elif r['chg'] < 0 and r['vol_status'] == "放大": pv_state = "價跌量增"
        elif r['chg'] < 0 and r['vol_status'] == "量縮": pv_state = "價跌量縮"
        else: pv_state = "中性"

        ma_cls = "kv-value-up" if "多頭" in ma_state else "kv-value-down" if "空頭" in ma_state else "kv-value-yellow"
        kd_cls_3 = "kv-value-up" if "黃金" in kd_state or "偏多" in kd_state else "kv-value-down" if "死亡" in kd_state or "偏空" in kd_state else "kv-value-yellow"
        macd_cls_3 = "kv-value-up" if "多頭擴張" in r['macd_status'] else "kv-value-down" if "空頭擴張" in r['macd_status'] else "kv-value-yellow"
        vol_cls_3 = "kv-value-up" if r['vol_status'] == "放大" else "kv-value-down" if r['vol_status'] == "量縮" else "kv-value-yellow"
        pv_cls = "kv-value-up" if "漲" in pv_state and "量增" in pv_state else "kv-value-down" if "跌" in pv_state else "kv-value-yellow"
        trend_cls_3 = "kv-value-up" if r['trend'] == "多頭" else "kv-value-down" if r['trend'] == "空頭" else "kv-value-yellow"

        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">📊 技術分析總覽</div>
            <div class="kv-row"><span class="kv-label">↗ 趨勢方向</span><span class="{trend_cls_3}">{r['trend']}</span></div>
            <div class="kv-row"><span class="kv-label">⭐ MA 狀態</span><span class="{ma_cls}">{ma_state}</span></div>
            <div class="kv-row"><span class="kv-label">~ KD 指標</span><span class="{kd_cls_3}">{kd_state}</span></div>
            <div class="kv-row"><span class="kv-label">📊 MACD</span><span class="{macd_cls_3}">{r['macd_status']}</span></div>
            <div class="kv-row"><span class="kv-label">📦 成交量</span><span class="{vol_cls_3}">{r['vol_status']}</span></div>
            <div class="kv-row"><span class="kv-label">⚡ 量價關係</span><span class="{pv_cls}">{pv_state}</span></div>
        </div>
        """, unsafe_allow_html=True)

        if r['has_rev']:
            yoy_cls = "kv-value-up" if r['yoy'] > 0 else "kv-value-down"
            rev_block = (
                f'<div class="kv-row"><span class="kv-label">所屬產業</span><span class="kv-value">{r["industry"]}</span></div>'
                f'<div class="kv-row"><span class="kv-label">單月營收</span><span class="kv-value">{r["rev"]:.2f} 億</span></div>'
                f'<div class="kv-row"><span class="kv-label">營收年增</span><span class="{yoy_cls}">{r["yoy"]:+.2f}%</span></div>'
            )
        else:
            rev_block = (
                f'<div class="kv-row"><span class="kv-label">所屬產業</span><span class="kv-value">{r["industry"]}</span></div>'
                '<div class="kv-row"><span class="kv-label">類型</span><span class="kv-value-yellow">ETF / 興櫃</span></div>'
                '<div class="kv-row"><span class="kv-label">營收資料</span><span class="kv-value">無</span></div>'
            )

        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">📋 基本概況</div>
            {rev_block}
        </div>
        """, unsafe_allow_html=True)

        bb_ub_disp = f"{r['bb_ub']:.2f}" if r['bb_ub'] else "N/A"
        bb_mid_disp = f"{r['bb_mid']:.2f}" if r['bb_mid'] else "N/A"
        bb_lb_disp = f"{r['bb_lb']:.2f}" if r['bb_lb'] else "N/A"
        bb_state_cls = "kv-value-up" if "上軌" in r['bb_status'] or "中軌之上" in r['bb_status'] else "kv-value-down" if "下軌" in r['bb_status'] or "中軌之下" in r['bb_status'] else "kv-value-yellow"
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🌊 布林通道 (20,2)</div>
            <div class="kv-row"><span class="kv-label">上軌 (壓力)</span><span class="kv-value-up">{bb_ub_disp}</span></div>
            <div class="kv-row"><span class="kv-label">中軌 (月線)</span><span class="kv-value-yellow">{bb_mid_disp}</span></div>
            <div class="kv-row"><span class="kv-label">下軌 (支撐)</span><span class="kv-value-down">{bb_lb_disp}</span></div>
            <div class="kv-row"><span class="kv-label">通道狀態</span><span class="{bb_state_cls}">{r['bb_status']}</span></div>
        </div>
        """, unsafe_allow_html=True)

    bot_c1, bot_c2, bot_c3 = st.columns(3)

    with bot_c1:
        if "🔴" in r['status']: risk_html = '<div style="text-align:center;padding:18px 0;"><div style="font-size:48px;">🔴</div><div style="color:#C76A6A;font-weight:700;margin-top:8px;">高風險</div></div>'
        elif "🟡" in r['status']: risk_html = '<div style="text-align:center;padding:18px 0;"><div style="font-size:48px;">🟡</div><div style="color:#B89243;font-weight:700;margin-top:8px;">需觀察</div></div>'
        elif "🟢" in r['status']: risk_html = '<div style="text-align:center;padding:18px 0;"><div style="font-size:48px;">🟢</div><div style="color:#7B9E89;font-weight:700;margin-top:8px;">低風險</div></div>'
        else: risk_html = '<div style="text-align:center;padding:18px 0;"><div style="font-size:48px;">⚪</div><div style="color:#8B7E72;font-weight:700;margin-top:8px;">中性</div></div>'

        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🚦 短線風險</div>
            {risk_html}
        </div>
        """, unsafe_allow_html=True)

    with bot_c2:
        st.markdown('<div class="section-card" style="padding:8px;"><div class="section-title">🎯 偏多分數</div>', unsafe_allow_html=True)
        st.plotly_chart(plot_morandi_gauge(r['score']), use_container_width=True, config={"displayModeBar": False}, key="gauge_tab3")
        st.markdown('</div>', unsafe_allow_html=True)

    with bot_c3:
        itot_cls_big = "kv-value-up" if r['itot'] > 0 else "kv-value-down" if r['itot'] < 0 else "kv-value"
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🎯 關鍵價位</div>
            <div class="kv-row"><span class="kv-label">壓力區</span><span class="kv-value-up">{r['resist_hi']:.2f}</span></div>
            <div class="kv-row"><span class="kv-label">支撐區</span><span class="kv-value-down">{r['support_hi']:.2f}</span></div>
            <div class="kv-row"><span class="kv-label">合計買賣</span><span class="{itot_cls_big}">{r['itot']:+,} 張</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="conclusion-box"><div class="conclusion-title">⭐ 整體結論</div><div class="conclusion-text" style="color: {conclusion_color};">{generate_overall_conclusion(r)}</div></div>', unsafe_allow_html=True)

st.divider()
st.caption(f"📊 資料來源：FinMind / Yahoo Finance · 🤖 AI：Google Gemini 2.5 Flash / Imagen 3 · 最後分析：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("⚠️ 本網站僅供研究參考，不構成投資建議。投資有風險，操作請審慎評估。")
