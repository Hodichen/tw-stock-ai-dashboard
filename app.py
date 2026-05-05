# -*- coding: utf-8 -*-
"""
台股 AI 個股分析儀表板（旗艦全景版 + 即時報價 + PDF 導出與分享）
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
import yfinance as yf
import io

# PDF 相關套件
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

st.set_page_config(
    page_title="台股 AI 分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS（米白底 + 深藍/米白卡片 + 高光重點色）
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
.block-container { padding-top: 2rem !important; max-width: 1600px !important; }

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
    align-items: center;
    padding: 4px 0;
    border-bottom: 1px dashed #E5DDD0;
    font-size: 13px;
    min-height: 28px;
}
.kv-row:last-child { border-bottom: none; }
.kv-label { color: #8B7E72; }

/* 數值基礎樣式 */
.kv-value { color: #3D3833; font-weight: 600; }
.kv-value-up { color: #C76A6A; font-weight: 700; }
.kv-value-down { color: #7B9E89; font-weight: 700; }
.kv-value-yellow { color: #B89243; font-weight: 700; }
.kv-value-cyan { color: #5A87A0; font-weight: 700; }

/* --- 🔥 動態放大的 Highlight 樣式 --- */
.val-highlight-up { color: #C76A6A !important; font-size: 18px !important; font-weight: 800 !important; }
.val-highlight-down { color: #7B9E89 !important; font-size: 18px !important; font-weight: 800 !important; }
.val-highlight-neutral { color: #B89243 !important; font-size: 18px !important; font-weight: 800 !important; }

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
# 技術指標與 Highlight 輔助函數
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

def get_highlight_cls(val_type, val):
    if val_type == 'num':
        if val > 0: return "val-highlight-up"
        elif val < 0: return "val-highlight-down"
        else: return "val-highlight-neutral"
    elif val_type == 'trend' or val_type == 'ma':
        if "多頭" in val or "多週期" in val: return "val-highlight-up"
        elif "空頭" in val: return "val-highlight-down"
        else: return "val-highlight-neutral"
    elif val_type == 'macd':
        if "多頭擴張" in val or "空頭縮減" in val: return "val-highlight-up"
        elif "空頭擴張" in val or "多頭縮減" in val: return "val-highlight-down"
        else: return "val-highlight-neutral"
    elif val_type == 'vol':
        if "放大" in val: return "val-highlight-up"
        elif "縮減" in val or "量縮" in val: return "val-highlight-down"
        else: return "val-highlight-neutral"
    elif val_type == 'pv':
        if "齊揚" in val: return "val-highlight-up"
        elif "跌" in val: return "val-highlight-down"
        else: return "val-highlight-neutral"
    elif val_type == 'kd':
        if "高檔" in val or "偏多" in val or "黃金" in val: return "val-highlight-up"
        elif "低檔" in val or "偏空" in val or "死亡" in val: return "val-highlight-down"
        else: return "val-highlight-neutral"
    return "kv-value"

def get_realtime_quote(stock_id):
    """獲取 Yahoo Finance 即時報價 (支援上市 .TW 與上櫃 .TWO)"""
    suffixes = ['.TW', '.TWO']
    for suffix in suffixes:
        try:
            ticker = yf.Ticker(f"{stock_id}{suffix}")
            todays_data = ticker.history(period='1d')
            if not todays_data.empty:
                rt_price = float(todays_data['Close'].iloc[-1])
                rt_vol = int(todays_data['Volume'].iloc[-1] / 1000)
                prev_data = ticker.history(period='5d')
                if len(prev_data) > 1:
                    prev_close = float(prev_data['Close'].iloc[-2])
                    rt_chg = ((rt_price - prev_close) / prev_close) * 100
                else:
                    rt_chg = 0.0
                return rt_price, rt_chg, rt_vol
        except Exception:
            continue
    return None, None, None

# ============================================
# PDF 輸出函數
# ============================================
def create_916_pdf(r):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(360, 640))
    c.setFillColorRGB(0.96, 0.94, 0.92)
    c.rect(0, 0, 360, 640, fill=1, stroke=0)
    
    c.setFillColorRGB(0.36, 0.31, 0.28)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(30, 590, f"{r['name']}")
    c.setFont("Helvetica", 14)
    c.drawString(30, 570, f"Stock ID: {r['id']} | {r['industry']}")
    
    price_color = (0.78, 0.42, 0.42) if r['chg'] >= 0 else (0.48, 0.62, 0.54)
    c.setFillColorRGB(*price_color)
    c.setFont("Helvetica-Bold", 40)
    c.drawString(30, 510, f"{r['close']:.2f}")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(160, 510, f"{r['chg']:+.2f}%")
    
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(30, 480, 330, 480)
    
    c.setFillColorRGB(0.3, 0.3, 0.3)
    y_pos = 450
    data_points = [
        ("Trend Status", f"{r['trend']}"),
        ("Score", f"{r['score']} / 100"),
        ("Volume", f"{r['vol']:,} (Lots)"),
        ("RSI(14)", f"{r['rsi']:.1f}" if r['rsi'] else "N/A"),
        ("MACD", f"{r['macd_status']}"),
        ("Support", f"{r['support_hi']}"),
        ("Resistance", f"{r['resist_hi']}")
    ]
    
    for label, val in data_points:
        c.setFont("Helvetica", 12)
        c.drawString(30, y_pos, label)
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(330, y_pos, val)
        y_pos -= 28
        
    c.setFillColorRGB(0.98, 0.96, 0.94)
    c.rect(30, 100, 300, 120, fill=1, stroke=1)
    c.setFillColorRGB(0.36, 0.31, 0.28)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, 200, "AI Overall Analysis:")
    
    text_obj = c.beginText(40, 180)
    text_obj.setFont("Helvetica", 10)
    text_obj.setLeading(14)
    text_obj.textLine("PDF Export Summary (English Placeholder)")
    text_obj.textLine(f"Trend: {r['trend']}")
    text_obj.textLine(f"Status: {r['status']}")
    c.drawText(text_obj)
    
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(30, 50, f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(30, 40, "Disclaimer: For research only. Not investment advice.")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ============================================
# 主分析邏輯
# ============================================
@st.cache_data(ttl=1800, show_spinner=False)
def analyze(stock_id):
    end = pd.Timestamp.today().strftime("%Y-%m-%d")
    start = (pd.Timestamp.today() - pd.Timedelta(days=200)).strftime("%Y-%m-%d")
    is_etf = stock_id.startswith("00") and len(stock_id) >= 5

    df = dl.taiwan_stock_daily(stock_id=stock_id, start_date=start, end_date=end)
    if df.empty: return None, "找不到此股票，請確認代號"

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
    
    cl_v = safe(df["close"])
    vr_v = safe(df["VRatio"])
    chg = safe(df["Chg%"]) or 0
    vol_v = int(lat["volume"] / 1000) if pd.notna(lat["volume"]) else 0

    macd_v = safe(df["MACD"])
    macd_sig_v = safe(df["MACD_sig"])
    macd_hist_v = safe(df["MACD_hist"])
    macd_hist_prev = safe(df["MACD_hist"], -2)

    # === 即時報價覆蓋邏輯 ===
    rt_price, rt_chg, rt_vol = get_realtime_quote(stock_id)
    if rt_price is not None:
        cl_v = rt_price 
        chg = rt_chg    
        if rt_vol is not None and rt_vol > 0:
            vol_v = rt_vol
            vma5_v = safe(df["VMA5"])
            if vma5_v and vma5_v > 0: vr_v = (rt_vol * 1000) / vma5_v

    # 法人籌碼
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

    # 月營收
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

    # 警示與狀態
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
    if nr >= 2: status = "🔴 過熱"
    elif nr >= 1: status = "🟡 觀察"
    elif ng >= 2: status = "🟢 健康"
    else: status = "⚪ 中性"

    if cl_v and ma20_v: trend = "多頭" if cl_v > ma20_v > (ma60_v or 0) else "空頭" if cl_v < ma20_v else "盤整"
    else: trend = "盤整"

    if macd_hist_v is not None and macd_hist_prev is not None:
        if macd_hist_v > 0 and macd_hist_v > macd_hist_prev: macd_status = "多頭擴張"
        elif macd_hist_v > 0 and macd_hist_v < macd_hist_prev: macd_status = "多頭縮減"
        elif macd_hist_v < 0 and macd_hist_v < macd_hist_prev: macd_status = "空頭擴張"
        elif macd_hist_v < 0 and macd_hist_v > macd_hist_prev: macd_status = "空頭縮減"
        else: macd_status = "中性"
    else: macd_status = "N/A"

    if vr_v: vol_status = "放大" if vr_v > 1.5 else "量縮" if vr_v < 0.7 else "持平"
    else: vol_status = "N/A"

    df_30 = df.tail(30)
    resist_lo = round(df_30["high"].max(), 2)
    resist_hi = round(df["high"].max(), 2)
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

    return {
        "name": name, "id": stock_id, "is_etf": is_etf, "has_rev": has_rev, "industry": industry_category,
        "df": df, "pivot": pivot,
        "close": float(cl_v) if cl_v is not None else float(lat["close"]),
        "chg": chg, "vol": vol_v, "rsi": rsi_v, "k": k_v, "d": d_v,
        "ma5": ma5_v, "ma20": ma20_v, "ma60": ma60_v,
        "macd": macd_v, "macd_sig": macd_sig_v, "macd_hist": macd_hist_v, "macd_status": macd_status,
        "vr": vr_v, "vol_status": vol_status, "trend": trend,
        "ifor": ifor, "itru": itru, "idal": idal, "itot": itot,
        "yoy": yoy, "mom": mom, "rev": rev,
        "status": status, "alerts": alerts, "score": score,
        "resist_lo": resist_lo, "resist_hi": resist_hi,
        "support_lo": support_lo, "support_hi": support_hi,
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
# Gemini API & 圖表函數 (維持不變)
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
    prompt = f"你是台股資深分析師，請根據以下數據對「{stock_name}（{stock_id}）」做深度分析報告。\n【當前數據】\n{data_summary}\n【請依以下結構產出分析報告】\n## 📈 技術面解讀\n## 💼 籌碼面解讀\n## 💡 短線操作建議\n## ⚠️ 風險評估"
    return call_gemini_with_retry(prompt, use_search=False)

@st.cache_data(ttl=1800, show_spinner=False)
def get_news(stock_name, stock_id):
    prompt = f"請幫我搜尋並整理台股「{stock_name}（{stock_id}）」最近 7 天的3-5 則最重要新聞重點。每則新聞格式：\n### 📰 [新聞標題]\n- **重點摘要**：...\n- **影響評估**：..."
    return call_gemini_with_retry(prompt, use_search=True)

MORANDI = {"bg": "#FAF6F0", "grid": "#E5DDD0", "axis": "#8B7E72", "text": "#5C5048", "up": "#C76A6A", "down": "#7B9E89", "ma5": "#CBA365", "ma20": "#6D98AB", "ma60": "#B0889F", "rsi": "#CBA365", "k": "#6D98AB", "d": "#B0889F", "macd_dif": "#6D98AB", "macd_dea": "#CBA365", "foreign": "#6D98AB", "trust": "#C76A6A", "dealer": "#B0889F", "total": "#7B9E89", "price": "#CBA365"}

def plot_kline(df, name, sid, height=620):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.45, 0.13, 0.21, 0.21], subplot_titles=("日 K 線", "成交量", "RSI / KD", "MACD"))
    fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], increasing_line_color=MORANDI["up"], decreasing_line_color=MORANDI["down"], increasing_fillcolor=MORANDI["up"], decreasing_fillcolor=MORANDI["down"], name="K"), row=1, col=1)
    for col, color in [("MA5", MORANDI["ma5"]), ("MA20", MORANDI["ma20"]), ("MA60", MORANDI["ma60"])]: fig.add_trace(go.Scatter(x=df["date"], y=df[col], name=col, line=dict(color=color, width=1.4)), row=1, col=1)
    vc = [MORANDI["up"] if c >= o else MORANDI["down"] for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"], marker_color=vc, name="量", showlegend=False, opacity=0.75), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["RSI"], name="RSI", line=dict(color=MORANDI["rsi"], width=1.6)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["K"], name="K", line=dict(color=MORANDI["k"], width=1.3)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["D"], name="D", line=dict(color=MORANDI["d"], width=1.3)), row=3, col=1)
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
    for col, color in [("外資", MORANDI["foreign"]), ("投信", MORANDI["trust"]), ("自營商", MORANDI["dealer"]), ("合計", MORANDI["total"])]: fig.add_trace(go.Bar(x=rec.index, y=rec[col], name=col, marker_color=color, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=pr["date"], y=pr["close"], name="股價", line=dict(color=MORANDI["price"], width=2.5), marker=dict(size=8), mode="lines+markers"), secondary_y=True)
    fig.update_layout(template="plotly_white", barmode="group", height=340, plot_bgcolor=MORANDI["bg"], paper_bgcolor=MORANDI["bg"], font=dict(color=MORANDI["text"]), margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified")
    return fig

def plot_morandi_gauge(score):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, number={'font': {'size': 36, 'color': '#3D3833'}}, gauge={'axis': {'range': [0, 100], 'visible': False}, 'bar': {'color': "rgba(0,0,0,0)"}, 'steps': [{'range': [0, 40], 'color': "#DBE8E0"}, {'range': [40, 60], 'color': "#F5EFD9"}, {'range': [60, 100], 'color': "#F5DCDC"}]}))
    theta = (1 - score / 100) * np.pi
    r_needle = 0.38
    fig.update_layout(shapes=[dict(type="line", x0=0.5, y0=0.25, x1=0.5 + r_needle * np.cos(theta), y1=0.25 + r_needle * np.sin(theta), line=dict(color="#5C5048", width=5), xref="paper", yref="paper")], height=180, margin=dict(l=15, r=15, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
    return fig

def render_inst_card(label, value):
    cls, sign = ("inst-value-up", "+") if value > 0 else ("inst-value-down", "") if value < 0 else ("inst-value-flat", "")
    return f'<div class="inst-card"><div class="inst-label">{label}</div><div class="{cls}">{sign}{value:,}</div></div>'
def render_pct_card(label, pct, suffix="%"):
    cls = "inst-value-up" if pct > 0 else "inst-value-down" if pct < 0 else "inst-value-flat"
    return f'<div class="inst-card"><div class="inst-label">{label}</div><div class="{cls}">{pct:+.2f}{suffix}</div></div>'

# ============================================
# 主畫面 UI
# ============================================
st.title("📊 台股 AI 個股分析")
st.caption("🤖 整合技術面 / 籌碼面 / 即時新聞 / Gemini AI 解讀 / 9:16 PDF 導出")

ic1, ic2 = st.columns([4, 1])
with ic1: sid = st.text_input("stock_input", placeholder="輸入股票代號，例如 2330", label_visibility="collapsed").strip().upper()
with ic2: go_btn = st.button("🔍 開始分析", type="primary", use_container_width=True)

st.divider()

if not sid:
    st.info("👆 請輸入股票代號，按「開始分析」")
    st.stop()

with st.spinner(f"⚙️ 分析 {sid} 中..."):
    r, err = analyze(sid)

if err or not r:
    st.error(f"❌ {err or '分析失敗'}")
    st.stop()

conclusion_color = "#C76A6A" if r['score'] >= 60 else "#7B9E89" if r['score'] <= 40 else "#5C5048"

# === 🌟 新增：導出與分享功能區塊 ===
st.markdown("### 📤 導出與分享")
c_exp1, c_exp2, c_exp3 = st.columns([1, 1, 2])
with c_exp1:
    pdf_data = create_916_pdf(r)
    st.download_button(label="📱 下載 9:16 PDF", data=pdf_data, file_name=f"{sid}_Report.pdf", mime="application/pdf", use_container_width=True)
with c_exp2:
    share_text = f"【台股AI分析】{r['name']} ({r['id']})\n股價：{r['close']:.2f} ({r['chg']:+.2f}%)\n趨勢：{r['trend']}\n分數：{r['score']}\n結論：{generate_overall_conclusion(r)}"
    st.link_button("💬 分享至 LINE", f"https://line.me/R/msg/text/?{share_text}", use_container_width=True)
with c_exp3:
    if st.button("📋 產生純文字摘要", use_container_width=True):
        st.code(share_text, language="text")
st.divider()

# ============================================
# 模式切換（3個 Tabs 完整恢復）
# ============================================
mode_tab1, mode_tab2, mode_tab3 = st.tabs(["📊 詳細模式", "🎯 7 大重點速覽", "🖥️ 旗艦全景儀表板"])

# --- 模式 1：詳細模式 ---
with mode_tab1:
    st.subheader(f"{r['name']} ({r['id']})  {r['status']}")
    chg_color = "#C76A6A" if r["chg"] >= 0 else "#7B9E89"
    chg_arrow = "▲" if r["chg"] >= 0 else "▼"
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="inst-card"><div class="inst-label">即時收盤價</div><div style="color:#3D3833;font-size:28px;font-weight:700;">{r["close"]:.2f}</div><div style="color:{chg_color};font-size:14px;font-weight:600;">{chg_arrow} {r["chg"]:+.2f}%</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="inst-card"><div class="inst-label">成交量</div><div style="color:#3D3833;font-size:28px;font-weight:700;">{r["vol"]:,}</div><div style="color:#8B7E72;font-size:13px;">張</div></div>', unsafe_allow_html=True)
    with c3:
        rsi_color = "#C76A6A" if r["rsi"] and r["rsi"] > 70 else "#7B9E89" if r["rsi"] and r["rsi"] < 30 else "#3D3833"
        st.markdown(f'<div class="inst-card"><div class="inst-label">RSI(14)</div><div style="color:{rsi_color};font-size:28px;font-weight:700;">{r["rsi"]:.2f}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="inst-card"><div class="inst-label">更新時間</div><div style="color:#3D3833;font-size:22px;font-weight:700;">{datetime.now().strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["📈 技術面", "💼 籌碼面", "📊 基本面", "🤖 AI 智能解讀", "📰 即時新聞"])
    with t1: st.plotly_chart(plot_kline(r["df"], r["name"], r["id"]), use_container_width=True)
    with t2:
        cc = st.columns(4)
        cc[0].markdown(render_inst_card("外資", r["ifor"]), unsafe_allow_html=True)
        cc[1].markdown(render_inst_card("投信", r["itru"]), unsafe_allow_html=True)
        cc[2].markdown(render_inst_card("自營商", r["idal"]), unsafe_allow_html=True)
        cc[3].markdown(render_inst_card("合計", r["itot"]), unsafe_allow_html=True)
        if not r["pivot"].empty: st.plotly_chart(plot_inst(r["pivot"], r["df"]), use_container_width=True)
    with t3:
        if r["has_rev"]:
            bc = st.columns(3)
            with bc[0]: st.markdown(f'<div class="inst-card"><div class="inst-label">最新月營收</div><div style="color:#3D3833;font-size:28px;font-weight:700;">{r["rev"]:.2f} 億</div></div>', unsafe_allow_html=True)
            with bc[1]: st.markdown(render_pct_card("YoY 年增率", r["yoy"]), unsafe_allow_html=True)
            with bc[2]: st.markdown(render_pct_card("MoM 月增率", r["mom"]), unsafe_allow_html=True)
    with t4:
        if st.button("🚀 產生 AI 分析報告", type="primary"):
            with st.spinner("AI 正在思考..."): st.markdown(get_ai_analysis(r["name"], r["id"], f"收盤:{r['close']}, 漲跌:{r['chg']}%, 籌碼:{r['itot']}"))
    with t5:
        if st.button("🔍 搜尋最新新聞", type="primary"):
            with st.spinner("搜尋中..."): st.markdown(get_news(r["name"], r["id"]))

# --- 模式 2：7 大重點速覽 ---
with mode_tab2:
    chg_arrow_top = "▲" if r["chg"] >= 0 else "▼"
    st.markdown(f"""
    <div class="overview-header">
        <div class="overview-title">{r['name']} {r['id']} ｜ 7 大重點速覽</div>
        <div class="overview-pills">
            <span class="overview-pill"><span style="color:#8B7E72;">收盤</span><span style="color:#3D3833;font-weight:700;margin-left:6px;">{r['close']:.2f}</span></span>
            <span class="{'overview-pill-red' if r['chg'] >= 0 else 'overview-pill-green'}">{chg_arrow_top} {r['chg']:+.2f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    row1c1, row1c2, row1c3 = st.columns(3)
    with row1c1: st.markdown(f'<div class="section-card"><div class="section-title">📈 股價表現</div><div class="kv-row"><span class="kv-label">收盤</span><span class="{get_highlight_cls("num", r["chg"])}">{r["close"]:.2f}</span></div></div>', unsafe_allow_html=True)
    with row1c2: st.markdown(f'<div class="section-card"><div class="section-title">📊 趨勢方向</div><div class="kv-row"><span class="kv-label">趨勢</span><span class="{get_highlight_cls("trend", r["trend"])}">{r["trend"]}</span></div></div>', unsafe_allow_html=True)
    with row1c3: st.markdown(f'<div class="section-card"><div class="section-title">👥 籌碼分析</div><div class="kv-row"><span class="kv-label">法人合計</span><span class="{get_highlight_cls("num", r["itot"])}">{r["itot"]:+,} 張</span></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="conclusion-box"><div class="conclusion-title">⭐ 結論</div><div class="conclusion-text" style="color: {conclusion_color};">{generate_overall_conclusion(r)}</div></div>', unsafe_allow_html=True)

# --- 模式 3：旗艦全景儀表板 ---
with mode_tab3:
    top_left, top_right = st.columns([6, 4])
    with top_left: st.plotly_chart(plot_kline(r["df"], r["name"], r["id"], height=580), use_container_width=True)
    with top_right:
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1: st.markdown(f'<div class="section-card"><div class="section-title">📊 技術分析總覽</div><div class="kv-row"><span class="kv-label">↗ 趨勢</span><span class="{get_highlight_cls("trend", r["trend"])}">{r["trend"]}</span></div><div class="kv-row"><span class="kv-label">📶 MACD</span><span class="{get_highlight_cls("macd", r["macd_status"])}">{r["macd_status"]}</span></div></div>', unsafe_allow_html=True)
        with r1_c2: st.markdown(f'<div class="section-card"><div class="section-title">👥 籌碼動向</div><div class="kv-row"><span class="kv-label">外資</span><span class="{get_highlight_cls("num", r["ifor"])}">{r["ifor"]:+,}</span></div><div class="kv-row"><span class="kv-label">投信</span><span class="{get_highlight_cls("num", r["itru"])}">{r["itru"]:+,}</span></div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-card" style="padding:4px;"><div class="section-title">🎯 偏多分數</div>', unsafe_allow_html=True)
        st.plotly_chart(plot_morandi_gauge(r['score']), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    bot_c1, bot_c2 = st.columns([5, 5])
    with bot_c1: st.markdown(f'<div class="section-card"><div class="section-title">🗓 多週期概覽</div><div class="kv-row"><span class="kv-label">中線季線</span><span class="kv-value-cyan">{r["ma60"]:.2f}</span></div></div>', unsafe_allow_html=True)
    with bot_c2: st.markdown(f'<div class="section-card"><div class="section-title">🎯 關鍵價位</div><div class="kv-row"><span class="kv-label">壓力區</span><span class="kv-value-up">{r["resist_hi"]:.2f}</span></div><div class="kv-row"><span class="kv-label">支撐區</span><span class="kv-value-down">{r["support_hi"]:.2f}</span></div></div>', unsafe_allow_html=True)
