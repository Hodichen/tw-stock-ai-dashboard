# -*- coding: utf-8 -*-
"""
台股 AI 個股分析儀表板（三模式：詳細 / 7大重點速覽 / 旗艦全景儀表板）
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from FinMind.data import DataLoader
from datetime import datetime
import random
import time
import json

st.set_page_config(
    page_title="台股 AI 分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS（米白底 + 深藍/米白卡片）
# ============================================
st.markdown("""
<style>
.stApp { background: #F5F1EB !important; color: #4A4540 !important; }
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
.stText, [data-testid="stMarkdownContainer"] { color: #4A4540 !important; }
h1, h2, h3, h4, h5, h6 { color: #5C5048 !important; font-weight: 600 !important; }
[data-testid="stCaptionContainer"], .stCaption { color: #8B7E72 !important; }

[data-testid="stMetricLabel"] { color: #8B7E72 !important; font-weight: 500 !important; }
[data-testid="stMetricValue"] { color: #3D3833 !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-weight: 600 !important; }

[data-testid="stMetric"] {
    background: #FAF6F0;
    border: 1px solid #E5DDD0;
    border-radius: 10px;
    padding: 12px 14px;
}

.stTextInput input {
    background: #FFFFFF !important;
    border: 1.5px solid #C9BFB1 !important;
    color: #3D3833 !important;
    font-size: 16px !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus {
    border-color: #8B9D83 !important;
    box-shadow: 0 0 0 2px rgba(139, 157, 131, 0.2) !important;
}

.stButton button[kind="primary"] {
    background: #8B9D83 !important;
    border: 1px solid #6F8169 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
.stButton button[kind="primary"]:hover {
    background: #6F8169 !important;
    border-color: #5A6856 !important;
}
.stButton button {
    background: #FAF6F0 !important;
    border: 1px solid #D4CABB !important;
    color: #5C5048 !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}
.stButton button:hover {
    background: #EDE5D5 !important;
    border-color: #B8AB99 !important;
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: #FAF6F0 !important;
    color: #5C5048 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 18px !important;
    border: 1px solid #E5DDD0 !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: #8B9D83 !important;
    color: #FFFFFF !important;
    border-color: #6F8169 !important;
}

.stAlert { border-radius: 10px !important; border: 1px solid !important; }
hr, [data-testid="stDivider"] { border-color: #D4CABB !important; background: #D4CABB !important; }
.stDataFrame { background: #FAF6F0; border: 1px solid #E5DDD0; border-radius: 8px; }
.stSpinner > div { border-top-color: #8B9D83 !important; }
.js-plotly-plot { background: #FAF6F0 !important; border-radius: 8px; padding: 6px; }
header[data-testid="stHeader"] { background: #F5F1EB !important; }
.block-container { padding-top: 2rem !important; max-width: 1600px !important; } /* 寬度放寬以適應儀表板 */

/* 詳細模式 - 法人卡片 */
.inst-card {
    background: #FAF6F0;
    border: 1px solid #E5DDD0;
    border-radius: 10px;
    padding: 14px;
    text-align: left;
}
.inst-label { color: #8B7E72; font-size: 14px; font-weight: 500; margin-bottom: 6px; }
.inst-value-up { color: #C76A6A; font-size: 28px; font-weight: 700; }
.inst-value-down { color: #7B9E89; font-size: 28px; font-weight: 700; }
.inst-value-flat { color: #8B7E72; font-size: 28px; font-weight: 700; }

/* === 重點速覽 / 戰情室卡片 === */
.overview-header {
    background: linear-gradient(135deg, #FAF6F0 0%, #F5EFE5 100%);
    border: 1px solid #D4CABB;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(120, 108, 90, 0.08);
}
.overview-title {
    color: #5C5048;
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 6px;
    letter-spacing: 1px;
}
.overview-subtitle {
    color: #8B7E72;
    font-size: 14px;
    margin-bottom: 12px;
}
.overview-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
}
.overview-pill {
    background: #FFFFFF;
    border: 1px solid #D4CABB;
    color: #5C5048;
    padding: 6px 14px;
    border-radius: 16px;
    font-size: 13px;
    font-weight: 500;
}
.overview-pill-red {
    background: #FBEDED;
    border: 1px solid #E5BFBF;
    color: #C76A6A;
    padding: 6px 14px;
    border-radius: 16px;
    font-size: 14px;
    font-weight: 600;
}
.overview-pill-green {
    background: #EAF1EC;
    border: 1px solid #B8D0BE;
    color: #5C8169;
    padding: 6px 14px;
    border-radius: 16px;
    font-size: 14px;
    font-weight: 600;
}

.section-card {
    background: #FAF6F0;
    border: 1px solid #E5DDD0;
    border-radius: 8px;
    padding: 14px;
    height: 100%;
    box-shadow: 0 2px 8px rgba(120, 108, 90, 0.04);
    margin-bottom: 10px;
}
.section-title {
    color: #8B6F47;
    font-size: 15px;
    font-weight: 700;
    border-bottom: 1px solid #E5DDD0;
    padding-bottom: 6px;
    margin-bottom: 10px;
    letter-spacing: 0.5px;
    text-align: center;
}
.kv-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px dashed #E5DDD0;
    font-size: 13px;
}
.kv-row:last-child { border-bottom: none; }
.kv-label { color: #8B7E72; }
.kv-value { color: #3D3833; font-weight: 600; }
.kv-value-up { color: #C76A6A; font-weight: 700; }
.kv-value-down { color: #7B9E89; font-weight: 700; }
.kv-value-yellow { color: #B89243; font-weight: 700; }
.kv-value-cyan { color: #5A87A0; font-weight: 700; }

.bullet-item {
    color: #4A4540;
    font-size: 13px;
    padding: 4px 0 4px 16px;
    position: relative;
    line-height: 1.6;
}
.bullet-item::before {
    content: "●";
    color: #B89243;
    position: absolute;
    left: 0;
    font-size: 9px;
    top: 7px;
}

.conclusion-box {
    background: linear-gradient(135deg, #F0E9DA 0%, #E8DFCC 100%);
    border: 2px solid #C9B689;
    border-radius: 8px;
    padding: 14px 20px;
    margin: 10px 0;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 8px rgba(184, 146, 67, 0.1);
}
.conclusion-title {
    color: #FAF6F0;
    background: #8B6F47;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 700;
    margin-right: 16px;
    white-space: nowrap;
}
.conclusion-text {
    color: #5C5048;
    font-size: 15px;
    font-weight: 600;
    line-height: 1.6;
}

/* 劇本小卡 */
.scenario-box {
    border: 1px solid #D4CABB;
    border-radius: 6px;
    padding: 8px;
    text-align: center;
    background: #FFFFFF;
}
.scenario-title {
    font-weight: 700;
    padding: 4px 0;
    border-radius: 4px;
    margin-bottom: 6px;
    font-size: 14px;
}
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
    except:
        return None


# ============================================
# 主分析
# ============================================
@st.cache_data(ttl=1800, show_spinner=False)
def analyze(stock_id):
    end = pd.Timestamp.today().strftime("%Y-%m-%d")
    start = (pd.Timestamp.today() - pd.Timedelta(days=200)).strftime("%Y-%m-%d")
    is_etf = stock_id.startswith("00") and len(stock_id) >= 5

    df = dl.taiwan_stock_daily(stock_id=stock_id, start_date=start, end_date=end)
    if df.empty:
        return None, "找不到此股票，請確認代號"

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
    cl_v, vr_v = safe(df["close"]), safe(df["VRatio"])
    chg = safe(df["Chg%"]) or 0
    macd_v = safe(df["MACD"])
    macd_sig_v = safe(df["MACD_sig"])
    macd_hist_v = safe(df["MACD_hist"])
    macd_hist_prev = safe(df["MACD_hist"], -2)

    # 法人
    i_start = (df["date"].max() - pd.Timedelta(days=45)).strftime("%Y-%m-%d")
    pivot = pd.DataFrame()
    try:
        inst = dl.taiwan_stock_institutional_investors(
            stock_id=stock_id, start_date=i_start, end_date=end
        )
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
                if c not in p.columns:
                    p[c] = 0
            p["合計"] = p["外資"] + p["投信"] + p["自營商"]
            pivot = (p[["外資", "投信", "自營商", "合計"]] / 1000).round().astype(int)
            pivot.index = pd.to_datetime(pivot.index)
            pivot = pivot.sort_index(ascending=False)
    except:
        pass

    if not pivot.empty:
        ifor = int(pivot["外資"].iloc[0])
        itru = int(pivot["投信"].iloc[0])
        idal = int(pivot["自營商"].iloc[0])
        itot = int(pivot["合計"].iloc[0])
    else:
        ifor = itru = idal = itot = 0

    # 月營收
    yoy = mom = rev = 0
    has_rev = False
    if not is_etf:
        try:
            r_start = (df["date"].max() - pd.Timedelta(days=550)).strftime("%Y-%m-%d")
            rv = dl.taiwan_stock_month_revenue(
                stock_id=stock_id, start_date=r_start, end_date=end
            )
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
        except:
            pass

    # 警示
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
    if has_rev:
        if yoy > 30: alerts["green"].append(f"營收 YoY +{yoy:.0f}%")
        elif yoy < -10: alerts["red"].append(f"營收 YoY {yoy:.0f}%")

    nr, ng = len(alerts["red"]), len(alerts["green"])
    if nr >= 2: status = "🔴 過熱"
    elif nr >= 1: status = "🟡 觀察"
    elif ng >= 2: status = "🟢 健康"
    else: status = "⚪ 中性"

    # 趨勢方向
    if cl_v and ma20_v:
        if cl_v > ma20_v > (ma60_v or 0): trend = "多頭"
        elif cl_v < ma20_v: trend = "空頭"
        else: trend = "盤整"
    else:
        trend = "盤整"

    # MACD 狀態
    if macd_hist_v is not None and macd_hist_prev is not None:
        if macd_hist_v > 0 and macd_hist_v > macd_hist_prev: macd_status = "多頭擴張"
        elif macd_hist_v > 0 and macd_hist_v < macd_hist_prev: macd_status = "多頭縮減"
        elif macd_hist_v < 0 and macd_hist_v < macd_hist_prev: macd_status = "空頭擴張"
        elif macd_hist_v < 0 and macd_hist_v > macd_hist_prev: macd_status = "空頭縮減"
        else: macd_status = "中性"
    else:
        macd_status = "N/A"

    # 量能變化
    vma5_v = safe(df["VMA5"])
    vma20_v = safe(df["VMA20"])
    if vr_v:
        if vr_v > 1.5: vol_status = "放大"
        elif vr_v < 0.7: vol_status = "量縮"
        else: vol_status = "持平"
    else:
        vol_status = "N/A"

    df_30 = df.tail(30)
    high_30 = df_30["high"].max()
    low_30 = df_30["low"].min()
    high_recent = df["high"].max()
    low_recent = df["low"].min()

    resist_lo = round(high_30, 2)
    resist_hi = round(high_recent, 2)
    support_lo = round(ma20_v * 0.97, 2) if ma20_v else round(cl_v * 0.95, 2)
    support_hi = round(ma20_v, 2) if ma20_v else round(cl_v * 0.97, 2)
    
    # 計算短線勝率 / 偏多分數 (供儀表板使用)
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

    return {
        "name": name, "id": stock_id, "is_etf": is_etf, "has_rev": has_rev, "industry": industry_category,
        "df": df, "pivot": pivot,
        "close": float(lat["close"]), "chg": chg,
        "vol": int(lat["volume"] / 1000),
        "rsi": rsi_v, "k": k_v, "d": d_v,
        "ma5": ma5_v, "ma20": ma20_v, "ma60": ma60_v,
        "macd": macd_v, "macd_sig": macd_sig_v, "macd_hist": macd_hist_v,
        "macd_status": macd_status,
        "vr": vr_v, "vol_status": vol_status,
        "trend": trend,
        "ifor": ifor, "itru": itru, "idal": idal, "itot": itot,
        "yoy": yoy, "mom": mom, "rev": rev,
        "status": status, "alerts": alerts, "score": score,
        "high_30": high_30, "low_30": low_30,
        "high_recent": high_recent, "low_recent": low_recent,
        "resist_lo": resist_lo, "resist_hi": resist_hi,
        "support_lo": support_lo, "support_hi": support_hi,
    }, None

def generate_overall_conclusion(r):
    parts = []
    parts.append(f"{r['name']}（{r['id']}）")
    if r["trend"] == "多頭": parts.append("維持多頭趨勢")
    elif r["trend"] == "空頭": parts.append("處於空頭走勢")
    else: parts.append("處於盤整格局")

    if "🔴 過熱" in r["status"]: parts.append("短線指標偏過熱")
    elif "🟡" in r["status"]: parts.append("短線進入觀察區")
    elif "🟢" in r["status"]: parts.append("技術面相對健康")
    else: parts.append("技術面中性")

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
    models_to_try = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
    last_error = None

    for attempt in range(max_retries):
        api_key = random.choice(gemini_keys)
        client = get_gemini_client_for_key(api_key)
        if client is None: continue

        model = models_to_try[0] if attempt < 2 else models_to_try[1]
        try:
            from google.genai import types
            if use_search:
                response = client.models.generate_content(
                    model=model, contents=prompt,
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]),
                )
            else:
                response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            err_msg = str(e)
            last_error = err_msg
            if any(x in err_msg for x in ["503", "429", "UNAVAILABLE", "overloaded", "RESOURCE_EXHAUSTED"]):
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            else: return f"❌ AI 暫時無法使用：{err_msg[:200]}"

    return f"❌ AI 服務暫時繁忙（已重試 {max_retries} 次）\n\n錯誤訊息：{str(last_error)[:200]}"

@st.cache_data(ttl=3600, show_spinner=False)
def get_ai_analysis(stock_name, stock_id, data_summary):
    prompt = f"""你是台股資深分析師，請根據以下數據對「{stock_name}（{stock_id}）」做深度分析報告。
【當前數據】\n{data_summary}\n
【請依以下結構產出分析報告（繁體中文）】
## 📈 技術面解讀
## 💼 籌碼面解讀
## 💡 短線操作建議
## ⚠️ 風險評估
## 🎯 中長線觀察重點
請使用繁體中文，保持客觀，提供具體可執行的建議，加上免責聲明結尾。"""
    return call_gemini_with_retry(prompt, use_search=False)

@st.cache_data(ttl=1800, show_spinner=False)
def get_news(stock_name, stock_id):
    prompt = f"""請幫我搜尋並整理台股「{stock_name}（{stock_id}）」最近 7 天的新聞，產出 3-5 則最重要的新聞重點。
每則新聞格式：\n### 📰 [新聞標題]\n- **日期**：YYYY-MM-DD\n- **重點摘要**：...\n- **影響評估**：...
請使用繁體中文，按時間排序。"""
    return call_gemini_with_retry(prompt, use_search=True)


# ============================================
# 圖表與儀表組件
# ============================================
MORANDI = {
    "bg": "#FAF6F0", "grid": "#E5DDD0", "axis": "#8B7E72", "text": "#5C5048",
    "up": "#C76A6A", "down": "#7B9E89",
    "ma5": "#CBA365", "ma20": "#6D98AB", "ma60": "#B0889F",
    "rsi": "#CBA365", "k": "#6D98AB", "d": "#B0889F",
    "macd_dif": "#6D98AB", "macd_dea": "#CBA365",
    "foreign": "#6D98AB", "trust": "#C76A6A", "dealer": "#B0889F",
    "total": "#7B9E89", "price": "#CBA365",
}

def plot_kline(df, name, sid, height=620):
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.04,
        row_heights=[0.45, 0.13, 0.21, 0.21],
        subplot_titles=("日 K 線", "成交量", "RSI / KD", "MACD")
    )
    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color=MORANDI["up"], decreasing_line_color=MORANDI["down"],
        increasing_fillcolor=MORANDI["up"], decreasing_fillcolor=MORANDI["down"], name="K"
    ), row=1, col=1)
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
    
    fig.update_layout(
        template="plotly_white", height=height, xaxis_rangeslider_visible=False, hovermode="x unified",
        plot_bgcolor=MORANDI["bg"], paper_bgcolor=MORANDI["bg"],
        font=dict(color=MORANDI["text"], family="Arial, 'Noto Sans TC', sans-serif"),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255,255,255,0.7)")
    )
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])], gridcolor=MORANDI["grid"], showgrid=True, linecolor=MORANDI["axis"], color=MORANDI["text"])
    fig.update_yaxes(gridcolor=MORANDI["grid"], showgrid=True, linecolor=MORANDI["axis"], color=MORANDI["text"])
    return fig

def plot_inst(pivot, df):
    if pivot.empty: return None
    rec = pivot.head(10).sort_index()
    pr = df[df["date"].isin(pd.to_datetime(rec.index))][["date", "close"]].sort_values("date")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for col, color in [("外資", MORANDI["foreign"]), ("投信", MORANDI["trust"]), ("自營商", MORANDI["dealer"]), ("合計", MORANDI["total"])]:
        fig.add_trace(go.Bar(x=rec.index, y=rec[col], name=col, marker_color=color, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=pr["date"], y=pr["close"], name="股價", line=dict(color=MORANDI["price"], width=2.5), marker=dict(size=8), mode="lines+markers"), secondary_y=True)
    fig.update_layout(
        template="plotly_white", barmode="group", height=340, plot_bgcolor=MORANDI["bg"], paper_bgcolor=MORANDI["bg"],
        font=dict(color=MORANDI["text"], family="Arial, 'Noto Sans TC', sans-serif"),
        margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255,255,255,0.7)")
    )
    fig.update_yaxes(title_text="法人(張)", secondary_y=False, gridcolor=MORANDI["grid"], color=MORANDI["text"])
    fig.update_yaxes(title_text="股價(元)", secondary_y=True, gridcolor=MORANDI["grid"], color=MORANDI["text"])
    fig.update_xaxes(gridcolor=MORANDI["grid"], color=MORANDI["text"])
    return fig

def plot_morandi_gauge(score):
    """產出儀表板的測速儀圖表"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        number = {'font': {'size': 32, 'color': '#3D3833'}},
        gauge = {
            'axis': {'range': [None, 100], 'visible': False},
            'bar': {'color': "#5C5048", 'thickness': 0.15},
            'steps': [
                {'range': [0, 40], 'color': "#DBE8E0"},  # 綠色 (偏弱)
                {'range': [40, 70], 'color': "#F5EFD9"}, # 黃色 (中性)
                {'range': [70, 100], 'color': "#F5DCDC"} # 紅色 (偏多)
            ],
        }
    ))
    fig.update_layout(
        height=180, 
        margin=dict(l=15, r=15, t=10, b=0), 
        paper_bgcolor="rgba(0,0,0,0)", 
        font=dict(family="Arial, 'Noto Sans TC'")
    )
    return fig

def render_inst_card(label, value):
    cls, sign = ("inst-value-up", "+") if value > 0 else ("inst-value-down", "") if value < 0 else ("inst-value-flat", "")
    return f'<div class="inst-card"><div class="inst-label">{label}</div><div class="{cls}">{sign}{value:,}</div></div>'

def render_pct_card(label, pct, suffix="%"):
    cls = "inst-value-up" if pct > 0 else "inst-value-down" if pct < 0 else "inst-value-flat"
    return f'<div class="inst-card"><div class="inst-label">{label}</div><div class="{cls}">{pct:+.2f}{suffix}</div></div>'


# ============================================
# 主畫面
# ============================================
st.title("📊 台股 AI 個股分析")
st.caption(f"🤖 整合技術面 / 籌碼面 / 基本面 / Gemini AI 解讀 / 即時新聞 · FinMind {finmind_token_count} token / Gemini {len(gemini_keys)} key")

ic1, ic2 = st.columns([4, 1])
with ic1:
    sid = st.text_input("stock_input", placeholder="輸入股票代號，例如 2330、0050", label_visibility="collapsed", key="stock_input")
with ic2:
    go_btn = st.button("🔍 開始分析", type="primary", use_container_width=True)

st.divider()

if not (go_btn and sid.strip()):
    if not sid.strip():
        st.info("👆 請輸入股票代號，按「開始分析」")
        st.markdown("""
        ### 🎯 三種顯示模式
        - 📊 **詳細模式**：完整數據表格 + K 線圖 + 法人柱狀圖（適合深入研究）
        - 🎯 **7 大重點速覽**：6 區塊重點圖卡 + 整體結論（適合快速判讀）
        - 🖥️ **旗艦全景儀表板**：參考專業看盤軟體的高密度戰情室（看盤必備）
        """)
        st.stop()

if not sid.strip():
    st.warning("請輸入股票代號")
    st.stop()

sid = sid.strip().upper()

with st.spinner(f"⚙️ 分析 {sid} 中..."):
    r, err = analyze(sid)

if err or r is None:
    st.error(f"❌ {err or '分析失敗'}")
    st.stop()

# ============================================
# 模式切換（3個 Tabs）
# ============================================
mode_tab1, mode_tab2, mode_tab3 = st.tabs(["📊 詳細模式", "🎯 7 大重點速覽", "🖥️ 旗艦全景儀表板"])

# --------------------------------------------
# 模式 1：詳細模式
# --------------------------------------------
with mode_tab1:
    st.subheader(f"{r['name']} ({r['id']})  {r['status']}")
    chg_color = "#C76A6A" if r["chg"] >= 0 else "#7B9E89"
    chg_arrow = "▲" if r["chg"] >= 0 else "▼"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="inst-card"><div class="inst-label">收盤價</div><div style="color:#3D3833;font-size:28px;font-weight:700;">{r["close"]:.2f}</div><div style="color:{chg_color};font-size:14px;font-weight:600;margin-top:4px;">{chg_arrow} {r["chg"]:+.2f}%</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="inst-card"><div class="inst-label">成交量</div><div style="color:#3D3833;font-size:28px;font-weight:700;">{r["vol"]:,}</div><div style="color:#8B7E72;font-size:13px;margin-top:4px;">張</div></div>', unsafe_allow_html=True)
    with c3:
        rsi_color = "#C76A6A" if r["rsi"] and r["rsi"] > 70 else "#7B9E89" if r["rsi"] and r["rsi"] < 30 else "#3D3833"
        rsi_label = "(超買)" if r["rsi"] and r["rsi"] > 70 else "(超賣)" if r["rsi"] and r["rsi"] < 30 else ""
        rsi_disp = f"{r['rsi']:.2f}" if r["rsi"] else "N/A"
        st.markdown(f'<div class="inst-card"><div class="inst-label">RSI(14)</div><div style="color:{rsi_color};font-size:28px;font-weight:700;">{rsi_disp}</div><div style="color:{rsi_color};font-size:13px;margin-top:4px;">{rsi_label}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="inst-card"><div class="inst-label">更新時間</div><div style="color:#3D3833;font-size:22px;font-weight:700;margin-top:6px;">{datetime.now().strftime("%m/%d %H:%M")}</div></div>', unsafe_allow_html=True)

    all_alerts = [("red", a) for a in r["alerts"]["red"]] + [("yellow", a) for a in r["alerts"]["yellow"]] + [("green", a) for a in r["alerts"]["green"]]
    if all_alerts:
        chips_html = "".join([f'<span style="display:inline-block;background:{("#F5DCDC" if t=="red" else "#F5EFD9" if t=="yellow" else "#DBE8E0")};color:{("#C76A6A" if t=="red" else "#A88838" if t=="yellow" else "#5C8169")};padding:6px 14px;border-radius:16px;margin:3px 5px 3px 0;font-size:13px;font-weight:500;">{"🔴" if t=="red" else "🟡" if t=="yellow" else "🟢"} {txt}</span>' for t, txt in all_alerts])
        st.markdown(f"<div style='margin-top:14px;'>{chips_html}</div>", unsafe_allow_html=True)

    st.divider()
    t1, t2, t3, t4, t5 = st.tabs(["📈 技術面", "💼 籌碼面", "📊 基本面", "🤖 AI 智能解讀", "📰 即時新聞"])

    with t1:
        st.markdown("### 完整 K 線圖")
        st.plotly_chart(plot_kline(r["df"], r["name"], r["id"]), use_container_width=True, config={"displayModeBar": False})
    with t2:
        cc = st.columns(4)
        cc[0].markdown(render_inst_card("外資", r["ifor"]), unsafe_allow_html=True)
        cc[1].markdown(render_inst_card("投信", r["itru"]), unsafe_allow_html=True)
        cc[2].markdown(render_inst_card("自營商", r["idal"]), unsafe_allow_html=True)
        cc[3].markdown(render_inst_card("合計", r["itot"]), unsafe_allow_html=True)
        if not r["pivot"].empty:
            st.plotly_chart(plot_inst(r["pivot"], r["df"]), use_container_width=True, config={"displayModeBar": False})
    with t3:
        if r["has_rev"]:
            bc = st.columns(3)
            with bc[0]: st.markdown(f'<div class="inst-card"><div class="inst-label">最新月營收</div><div style="color:#3D3833;font-size:28px;font-weight:700;">{r["rev"]:.2f}</div><div style="color:#8B7E72;font-size:13px;margin-top:4px;">億元</div></div>', unsafe_allow_html=True)
            with bc[1]: st.markdown(render_pct_card("YoY 年增率", r["yoy"]), unsafe_allow_html=True)
            with bc[2]: st.markdown(render_pct_card("MoM 月增率", r["mom"]), unsafe_allow_html=True)
        else: st.info("📌 此標的為 ETF 或興櫃，無月營收資料")
    with t4:
        if st.button("🚀 產生 AI 分析報告", type="primary", key="ai_btn_detail"):
            with st.spinner("AI 正在思考中..."):
                summary = f"- 收盤價：{r['close']:.2f}\n- 成交量：{r['vol']:,} 張\n- 技術指標：RSI={r['rsi']}, MACD={r['macd']}\n- 法人籌碼：合計 {r['itot']:+,} 張\n- 狀態：{r['status']}"
                st.markdown(get_ai_analysis(r["name"], r["id"], summary))
    with t5:
        if st.button("🔍 搜尋最新新聞", type="primary", key="news_btn_detail"):
            with st.spinner("正在搜尋新聞..."): st.markdown(get_news(r["name"], r["id"]))


# --------------------------------------------
# 模式 2：7 大重點速覽
# --------------------------------------------
with mode_tab2:
    chg_arrow_top = "▲" if r["chg"] >= 0 else "▼"
    st.markdown(f"""
    <div class="overview-header">
        <div class="overview-title">{r['name']} {r['id']} ｜ 7 大重點速覽</div>
        <div class="overview-subtitle">Q版講師帶你看懂：{r['trend']}趨勢、技術指標、籌碼分析</div>
        <div class="overview-pills">
            <span class="overview-pill"><span style="color:#8B7E72;">收盤</span><span style="color:#3D3833;font-weight:700;font-size:16px;margin-left:6px;">{r['close']:.2f}</span></span>
            <span class="{'overview-pill-red' if r['chg'] >= 0 else 'overview-pill-green'}">{chg_arrow_top} {r['chg']:+.2f}%</span>
            <span class="overview-pill"><span style="color:#8B7E72;">成交量</span><span style="color:#3D3833;font-weight:700;margin-left:6px;">{r['vol']:,}</span><span style="color:#8B7E72;font-size:11px;margin-left:2px;">張</span></span>
            <span class="overview-pill"><span style="color:#8B7E72;">狀態</span><span style="color:#B89243;font-weight:600;margin-left:6px;">{r['status']}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    row1c1, row1c2, row1c3 = st.columns(3)
    with row1c1:
        st.markdown(f"""<div class="section-card"><div class="section-title">📈 股價表現</div>
        <div class="kv-row"><span class="kv-label">收盤</span><span class="kv-value">{r["close"]:.2f}</span></div>
        <div class="kv-row"><span class="kv-label">漲跌</span><span class="{'kv-value-up' if r['chg'] >= 0 else 'kv-value-down'}">{r["chg"]:+.2f}%</span></div>
        </div>""", unsafe_allow_html=True)
    with row1c2:
        st.markdown(f"""<div class="section-card"><div class="section-title">📊 趨勢與均線</div>
        <div class="kv-row"><span class="kv-label">趨勢方向</span><span class="{'kv-value-up' if r['trend'] == '多頭' else 'kv-value-down' if r['trend'] == '空頭' else 'kv-value-yellow'}">{r["trend"]}</span></div>
        </div>""", unsafe_allow_html=True)
    with row1c3:
        rsi_disp_tab2 = f"{r['rsi']:.1f}" if r['rsi'] else "N/A"
        st.markdown(f"""<div class="section-card"><div class="section-title">💹 技術指標</div>
        <div class="kv-row"><span class="kv-label">RSI(14)</span><span class="kv-value">{rsi_disp_tab2}</span></div>
        <div class="kv-row"><span class="kv-label">MACD 狀態</span><span class="kv-value">{r["macd_status"]}</span></div>
        </div>""", unsafe_allow_html=True)

    row2c1, row2c2, row2c3 = st.columns(3)
    with row2c1:
        st.markdown(f"""<div class="section-card"><div class="section-title">📦 量能與型態</div>
        <div class="kv-row"><span class="kv-label">量比</span><span class="kv-value">{r["vr"]:.2f}x</span></div>
        <div class="kv-row"><span class="kv-label">量能變化</span><span class="kv-value">{r["vol_status"]}</span></div>
        </div>""", unsafe_allow_html=True)
    with row2c2:
        st.markdown(f"""<div class="section-card"><div class="section-title">👥 籌碼分析</div>
        <div class="kv-row"><span class="kv-label">法人合計</span><span class="{'kv-value-up' if r['itot'] > 0 else 'kv-value-down' if r['itot'] < 0 else 'kv-value'}">{r["itot"]:+,} 張</span></div>
        </div>""", unsafe_allow_html=True)
    with row2c3:
        st.markdown(f"""<div class="section-card"><div class="section-title">🎯 關鍵價位</div>
        <div class="kv-row"><span class="kv-label">壓力區</span><span class="kv-value-up">{r["resist_lo"]:.2f} ~ {r["resist_hi"]:.2f}</span></div>
        <div class="kv-row"><span class="kv-label">支撐區</span><span class="kv-value-down">{r["support_lo"]:.2f} ~ {r["support_hi"]:.2f}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="conclusion-box"><div class="conclusion-title">⭐ 整體結論</div><div class="conclusion-text">{generate_overall_conclusion(r)}</div></div>', unsafe_allow_html=True)


# --------------------------------------------
# 模式 3：🖥️ 旗艦全景儀表板 (致敬專業看盤軟體)
# --------------------------------------------
with mode_tab3:
    # --- 頂端資訊條 ---
    chg_color = '#C76A6A' if r['chg'] >= 0 else '#7B9E89'
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid #E5DDD0; padding-bottom:8px; margin-bottom:12px;">
        <div>
            <span style="font-size:24px; font-weight:700; color:#5C5048; letter-spacing:1px;">{r['name']} ({r['id']})</span>
            <span style="font-size:13px; font-weight:600; background:#FAF6F0; color:#8B6F47; padding:4px 8px; border-radius:4px; margin-left:12px; border:1px solid #D4CABB;">{r['industry']}</span>
        </div>
        <div style="text-align:right;">
            <span style="font-size:14px; font-weight:600; color:#8B7E72; margin-right:8px;">日 K 線</span>
            <span style="font-size:28px; font-weight:800; color:{chg_color};">{r['close']:.2f}</span>
            <span style="font-size:16px; font-weight:700; color:{chg_color}; margin-left:8px;">{r['chg']:+.2f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- 排版：上半部 (圖表 60% | 資訊面板 40%) ---
    top_left, top_right = st.columns([6, 4])
    
    with top_left:
        st.plotly_chart(plot_kline(r["df"], r["name"], r["id"], height=580), use_container_width=True, config={"displayModeBar": False})

    with top_right:
        # 右上：總覽與概況 (2欄)
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            # 預處理變數，避免 f-string 衝突
            trend_val = f"<span class='{'kv-value-up' if r['trend']=='多頭' else 'kv-value-down' if r['trend']=='空頭' else 'kv-value-yellow'}'>{r['trend']}</span>"
            kd_str = "高檔鈍化" if (r['k'] and r['k']>80) else "低檔鈍化" if (r['k'] and r['k']<20) else "中性區間"
            macd_str = r['macd_status']
            vol_str = r['vol_status']
            pv_str = "價量齊揚" if (r['chg']>0 and r['vr'] and r['vr']>1) else "價跌量縮" if (r['chg']<0 and r['vr'] and r['vr']<1) else "中性"
            
            st.markdown(f"""
            <div class="section-card">
                <div class="section-title">📊 技術分析總覽</div>
                <div class="kv-row"><span class="kv-label">↗ 趨勢方向</span>{trend_val}</div>
                <div class="kv-row"><span class="kv-label">★ MA 狀態</span><span class="kv-value-yellow">多週期排列</span></div>
                <div class="kv-row"><span class="kv-label">∿ KD 指標</span><span class="kv-value">{kd_str}</span></div>
                <div class="kv-row"><span class="kv-label">📶 MACD</span><span class="kv-value">{macd_str}</span></div>
                <div class="kv-row"><span class="kv-label">📦 成交量</span><span class="kv-value">{vol_str}</span></div>
                <div class="kv-row"><span class="kv-label">⚖ 量價關係</span><span class="kv-value">{pv_str}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        with r1_c2:
            # 營收與概況
            rev_str = f"{r['yoy']:+.2f}%" if r['has_rev'] else "N/A"
            rev_cls = "kv-value-up" if (r['has_rev'] and r['yoy']>0) else "kv-value-down"
            
            st.markdown(f"""
            <div class="section-card" style="margin-bottom:10px;">
                <div class="section-title">🏢 基本概況</div>
                <div class="kv-row"><span class="kv-label">所屬產業</span><span class="kv-value">{r['industry']}</span></div>
                <div class="kv-row"><span class="kv-label">單月營收</span><span class="kv-value">{r['rev']:.2f} 億</span></div>
                <div class="kv-row"><span class="kv-label">營收年增</span><span class="{rev_cls}">{rev_str}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            # 籌碼分析
            itot_cls = "kv-value-up" if r['itot']>0 else "kv-value-down" if r['itot']<0 else "kv-value"
            st.markdown(f"""
            <div class="section-card">
                <div class="section-title">👥 籌碼分析</div>
                <div class="kv-row"><span class="kv-label">外資動向</span><span class="{'kv-value-up' if r['ifor']>0 else 'kv-value-down'}">{r["ifor"]:+,} 張</span></div>
                <div class="kv-row"><span class="kv-label">投信動向</span><span class="{'kv-value-up' if r['itru']>0 else 'kv-value-down'}">{r["itru"]:+,} 張</span></div>
                <div class="kv-row" style="background:#F5EFD9; padding:4px; border-radius:4px;"><span class="kv-label" style="color:#A88838;font-weight:600;">合計買賣</span><span class="{itot_cls}">{r["itot"]:+,} 張</span></div>
            </div>
            """, unsafe_allow_html=True)

        # 右中：燈號、勝率儀表板、價位
        r2_c1, r2_c2, r2_c3 = st.columns([1, 1.2, 1])
        with r2_c1:
            risk = "high" if "🔴" in r['status'] else "mid" if "🟡" in r['status'] else "low"
            op_h = 1 if risk=="high" else 0.2
            op_m = 1 if risk=="mid" else 0.2
            op_l = 1 if risk=="low" else 0.2
            st.markdown(f"""
            <div class="section-card" style="text-align:center;">
                <div class="section-title">🚦 短線風險</div>
                <div style="opacity:{op_h}; color:#C76A6A; font-weight:700; padding:4px 0;">🔴 高風險</div>
                <div style="opacity:{op_m}; color:#B89243; font-weight:700; padding:4px 0;">🟡 需觀察</div>
                <div style="opacity:{op_l}; color:#5C8169; font-weight:700; padding:4px 0;">🟢 低風險</div>
            </div>
            """, unsafe_allow_html=True)
        with r2_c2:
            st.markdown('<div class="section-card" style="padding:4px;"><div class="section-title" style="margin-bottom:0;">🎯 偏多分數</div>', unsafe_allow_html=True)
            st.plotly_chart(plot_morandi_gauge(r['score']), use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with r2_c3:
            st.markdown(f"""
            <div class="section-card">
                <div class="section-title">🎯 關鍵價位</div>
                <div style="text-align:center; padding-bottom:8px; border-bottom:1px solid #E5DDD0;">
                    <div style="color:#C76A6A; font-size:12px;">壓力區</div>
                    <div style="font-weight:700; font-size:18px;">{r['resist_hi']:.2f}</div>
                </div>
                <div style="text-align:center; padding-top:8px;">
                    <div style="color:#7B9E89; font-size:12px;">支撐區</div>
                    <div style="font-weight:700; font-size:18px;">{r['support_hi']:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- 排版：下半部 (劇本區與型態) ---
    bot_c1, bot_c2, bot_c3 = st.columns([2.5, 2.5, 5])
    
    with bot_c1:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🔎 型態與訊號</div>
            <div class="bullet-item">MA均線：{'多頭' if r['ma5'] and r['ma20'] and r['ma5']>r['ma20'] else '偏空'}排列</div>
            <div class="bullet-item">RSI狀態：{'超買' if r['rsi'] and r['rsi']>70 else '超賣' if r['rsi'] and r['rsi']<30 else '中立'}</div>
            <div class="bullet-item">MACD柱：{r['macd_status']}</div>
            <div class="bullet-item">法人籌碼：{'偏多' if r['itot']>0 else '偏空'}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with bot_c2:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🗓 多週期概覽 (MA)</div>
            <div class="kv-row"><span class="kv-label">日 K 級別</span><span class="{'kv-value-up' if r['trend']=='多頭' else 'kv-value-down'}">{r['trend']}</span></div>
            <div class="kv-row"><span class="kv-label">短線位階</span><span class="kv-value-yellow">觀望 20 日線</span></div>
            <div class="kv-row"><span class="kv-label">中線位階</span><span class="kv-value-cyan">季線 {r['ma60']:.2f}</span></div>
            <div class="kv-row"><span style="color:#8B7E72; font-size:12px; margin-top:4px;">*位階依 MA 均線判定</span></div>
        </div>
        """, unsafe_allow_html=True)

    with bot_c3:
        # 隔日操作劇本推算
        c = r['close']
        res = r['resist_hi']
        sup = r['support_hi']
        st.markdown(f"""
        <div class="section-card" style="background: #F5EFE5; border: 1px solid #D4CABB;">
            <div class="section-title" style="margin-bottom:8px;">📝 隔日操作劇本 (程式推演僅供參考)</div>
            <div style="display:flex; gap:10px;">
                <div class="scenario-box" style="flex:1;">
                    <div class="scenario-title" style="background:#FBEDED; color:#C76A6A;">① 開高 (強勢)</div>
                    <div style="font-size:13px; line-height:1.6; color:#5C5048;">
                        進場：{(c*1.01):.2f}<br>停損：{(c*0.99):.2f}<br>目標：{res:.2f}
                    </div>
                </div>
                <div class="scenario-box" style="flex:1;">
                    <div class="scenario-title" style="background:#F5EFD9; color:#A88838;">② 震盪 (盤整)</div>
                    <div style="font-size:13px; line-height:1.6; color:#5C5048;">
                        進場：{c:.2f}<br>停損：{sup:.2f}<br>目標：{res:.2f}
                    </div>
                </div>
                <div class="scenario-box" style="flex:1;">
                    <div class="scenario-title" style="background:#EAF1EC; color:#5C8169;">③ 開低 (弱勢)</div>
                    <div style="font-size:13px; line-height:1.6; color:#5C5048;">
                        進場：{(c*0.98):.2f}<br>停損：{(sup*0.98):.2f}<br>目標：{c:.2f}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- 底部結論區 ---
    st.markdown(f"""
    <div class="conclusion-box">
        <div class="conclusion-title">整體結論</div>
        <div class="conclusion-text">{generate_overall_conclusion(r)}</div>
    </div>
    """, unsafe_allow_html=True)


st.divider()
st.caption(f"📊 資料來源：FinMind · 🤖 AI：Google Gemini 2.5 Flash · 最後分析：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("⚠️ 本網站僅供研究參考，不構成投資建議。投資有風險，操作請審慎評估。")
