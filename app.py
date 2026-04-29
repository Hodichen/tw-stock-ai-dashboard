# -*- coding: utf-8 -*-
"""
台股 AI 個股分析儀表板（莫蘭迪色系 / 護眼米白底）
功能：技術面 + 籌碼面 + 基本面 + Gemini AI 解讀 + 個股新聞
特色：FinMind 4 token 輪替 + Gemini 2 token 輪替 + AI 自動重試
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

# ============================================
# 頁面設定
# ============================================
st.set_page_config(
    page_title="台股 AI 分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 莫蘭迪米白護眼配色
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
.block-container { padding-top: 2rem !important; max-width: 1400px !important; }

/* 自訂法人卡片（取代 metric，可控紅綠色） */
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
</style>
""", unsafe_allow_html=True)


# ============================================
# Token 池輪替機制
# ============================================
def get_finmind_tokens():
    tokens = []
    try:
        tokens.append(st.secrets["FINMIND_TOKEN"])
    except Exception:
        pass
    for i in range(2, 5):
        try:
            tokens.append(st.secrets[f"FINMIND_TOKEN_{i}"])
        except Exception:
            pass
    return tokens


def get_gemini_keys():
    keys = []
    try:
        keys.append(st.secrets["GEMINI_API_KEY"])
    except Exception:
        pass
    try:
        keys.append(st.secrets["GEMINI_API_KEY_2"])
    except Exception:
        pass
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
    """為特定 key 建立 client"""
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception:
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

    try:
        info = dl.taiwan_stock_info()
        m = info[info["stock_id"] == stock_id]
        name = m["stock_name"].iloc[0] if not m.empty else stock_id
    except:
        name = stock_id

    df["MA5"] = sma(df["close"], 5)
    df["MA20"] = sma(df["close"], 20)
    df["MA60"] = sma(df["close"], 60)
    df["RSI"] = rsi_calc(df["close"])
    df["MACD"], df["MACD_sig"], df["MACD_hist"] = macd_calc(df["close"])
    df["K"], df["D"] = kd_calc(df["high"], df["low"], df["close"])
    df["VMA5"] = sma(df["volume"], 5)
    df["VRatio"] = df["volume"] / df["VMA5"]
    df["Chg%"] = df["close"].pct_change() * 100

    lat = df.iloc[-1]
    rsi_v, k_v, d_v = safe(df["RSI"]), safe(df["K"]), safe(df["D"])
    ma5_v, ma20_v, ma60_v = safe(df["MA5"]), safe(df["MA20"]), safe(df["MA60"])
    cl_v, vr_v = safe(df["close"]), safe(df["VRatio"])
    chg = safe(df["Chg%"]) or 0

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

    return {
        "name": name, "id": stock_id, "is_etf": is_etf, "has_rev": has_rev,
        "df": df, "pivot": pivot,
        "close": float(lat["close"]), "chg": chg,
        "vol": int(lat["volume"] / 1000),
        "rsi": rsi_v, "k": k_v, "d": d_v,
        "ma5": ma5_v, "ma20": ma20_v, "ma60": ma60_v,
        "macd": safe(df["MACD"]), "macd_sig": safe(df["MACD_sig"]),
        "vr": vr_v,
        "ifor": ifor, "itru": itru, "idal": idal, "itot": itot,
        "yoy": yoy, "mom": mom, "rev": rev,
        "status": status, "alerts": alerts,
        "high_recent": df["high"].max(), "low_recent": df["low"].min(),
    }, None


# ============================================
# Gemini API（自動重試 + 模型 fallback + key 輪替）
# ============================================
def call_gemini_with_retry(prompt, use_search=False, max_retries=3):
    """智能呼叫 Gemini API：
    - 隨機選 key
    - 503 過載自動換 key 或換模型重試
    - 最多重試 3 次
    """
    if not gemini_keys:
        return "⚠️ 未設定 Gemini API Key"

    # 嘗試的模型順序：先用 flash，過載就降到 flash-lite
    models_to_try = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

    last_error = None
    for attempt in range(max_retries):
        # 隨機選 key（每次重試都重新選）
        api_key = random.choice(gemini_keys)
        client = get_gemini_client_for_key(api_key)
        if client is None:
            last_error = "Gemini client 初始化失敗"
            continue

        # 選模型（前 2 次用 flash，第 3 次用 flash-lite）
        model = models_to_try[0] if attempt < 2 else models_to_try[1]

        try:
            from google.genai import types
            if use_search:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    ),
                )
            else:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
            return response.text
        except Exception as e:
            err_msg = str(e)
            last_error = err_msg
            # 503 / 429 / 過載 → 立刻換 key 重試
            if any(x in err_msg for x in ["503", "429", "UNAVAILABLE", "overloaded", "RESOURCE_EXHAUSTED"]):
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等 2 秒再試
                    continue
            else:
                # 其他錯誤直接回傳
                return f"❌ AI 暫時無法使用：{err_msg[:200]}"

    return (f"❌ AI 服務暫時繁忙（已重試 {max_retries} 次）\n\n"
            f"建議：請等待 1-2 分鐘後再試，或改用其他股票測試。\n\n"
            f"錯誤訊息：{str(last_error)[:200]}")


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

請務必：
- 使用繁體中文
- 不要過度樂觀或悲觀，保持客觀
- 提供具體可執行的建議
- 加上免責聲明結尾
"""
    return call_gemini_with_retry(prompt, use_search=False)


@st.cache_data(ttl=1800, show_spinner=False)
def get_news(stock_name, stock_id):
    prompt = f"""請幫我搜尋並整理台股「{stock_name}（{stock_id}）」最近 7 天的新聞，
產出 3-5 則最重要的新聞重點。

每則新聞請以以下格式呈現：

### 📰 [新聞標題]
- **日期**：YYYY-MM-DD
- **重點摘要**：（2-3 句話）
- **影響評估**：對股價可能的影響（正面/負面/中性）

請使用繁體中文，並按時間排序（最新的在最前面）。
若沒有相關新聞，請說明。
"""
    return call_gemini_with_retry(prompt, use_search=True)


# ============================================
# 圖表（莫蘭迪色系，台股紅漲綠跌）
# ============================================
MORANDI = {
    "bg": "#FAF6F0",
    "grid": "#E5DDD0",
    "axis": "#8B7E72",
    "text": "#5C5048",
    "up": "#C76A6A",
    "down": "#7B9E89",
    "ma5": "#CBA365",
    "ma20": "#6D98AB",
    "ma60": "#B0889F",
    "rsi": "#CBA365",
    "k": "#6D98AB",
    "d": "#B0889F",
    "macd_dif": "#6D98AB",
    "macd_dea": "#CBA365",
    "foreign": "#6D98AB",
    "trust": "#C76A6A",
    "dealer": "#B0889F",
    "total": "#7B9E89",
    "price": "#CBA365",
}


def plot_kline(df, name, sid):
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.04,
        row_heights=[0.45, 0.13, 0.21, 0.21],
        subplot_titles=("日 K 線", "成交量", "RSI / KD", "MACD")
    )

    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        increasing_line_color=MORANDI["up"], decreasing_line_color=MORANDI["down"],
        increasing_fillcolor=MORANDI["up"], decreasing_fillcolor=MORANDI["down"],
        name="K"
    ), row=1, col=1)

    for col, color in [("MA5", MORANDI["ma5"]), ("MA20", MORANDI["ma20"]), ("MA60", MORANDI["ma60"])]:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df[col], name=col,
            line=dict(color=color, width=1.4)
        ), row=1, col=1)

    vc = [MORANDI["up"] if c >= o else MORANDI["down"] for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"], marker_color=vc,
                         name="量", showlegend=False, opacity=0.75), row=2, col=1)

    fig.add_trace(go.Scatter(x=df["date"], y=df["RSI"], name="RSI",
                             line=dict(color=MORANDI["rsi"], width=1.6)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["K"], name="K",
                             line=dict(color=MORANDI["k"], width=1.3)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["D"], name="D",
                             line=dict(color=MORANDI["d"], width=1.3)), row=3, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color=MORANDI["up"], row=3, col=1, line_width=1, opacity=0.5)
    fig.add_hline(y=20, line_dash="dash", line_color=MORANDI["down"], row=3, col=1, line_width=1, opacity=0.5)

    if df["MACD_hist"].notna().any():
        hc = [MORANDI["up"] if v >= 0 else MORANDI["down"] for v in df["MACD_hist"].fillna(0)]
        fig.add_trace(go.Bar(x=df["date"], y=df["MACD_hist"], marker_color=hc,
                             name="MACD柱", showlegend=False, opacity=0.75), row=4, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=df["MACD"], name="DIF",
                                 line=dict(color=MORANDI["macd_dif"], width=1.4)), row=4, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=df["MACD_sig"], name="DEA",
                                 line=dict(color=MORANDI["macd_dea"], width=1.4)), row=4, col=1)

    fig.update_layout(
        template="plotly_white", height=620,
        xaxis_rangeslider_visible=False, hovermode="x unified",
        plot_bgcolor=MORANDI["bg"], paper_bgcolor=MORANDI["bg"],
        font=dict(color=MORANDI["text"], family="Arial, 'Noto Sans TC', sans-serif"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(255,255,255,0.7)")
    )
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])],
                     gridcolor=MORANDI["grid"], showgrid=True,
                     linecolor=MORANDI["axis"], color=MORANDI["text"])
    fig.update_yaxes(gridcolor=MORANDI["grid"], showgrid=True,
                     linecolor=MORANDI["axis"], color=MORANDI["text"])
    return fig


def plot_inst(pivot, df):
    if pivot.empty:
        return None
    rec = pivot.head(10).sort_index()
    pr = df[df["date"].isin(pd.to_datetime(rec.index))][["date", "close"]].sort_values("date")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for col, color in [("外資", MORANDI["foreign"]), ("投信", MORANDI["trust"]),
                       ("自營商", MORANDI["dealer"]), ("合計", MORANDI["total"])]:
        fig.add_trace(go.Bar(x=rec.index, y=rec[col], name=col,
                             marker_color=color, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=pr["date"], y=pr["close"], name="股價",
        line=dict(color=MORANDI["price"], width=2.5),
        marker=dict(size=8), mode="lines+markers"
    ), secondary_y=True)
    fig.update_layout(
        template="plotly_white", barmode="group", height=340,
        plot_bgcolor=MORANDI["bg"], paper_bgcolor=MORANDI["bg"],
        font=dict(color=MORANDI["text"], family="Arial, 'Noto Sans TC', sans-serif"),
        margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(255,255,255,0.7)")
    )
    fig.update_yaxes(title_text="法人(張)", secondary_y=False,
                     gridcolor=MORANDI["grid"], color=MORANDI["text"])
    fig.update_yaxes(title_text="股價(元)", secondary_y=True,
                     gridcolor=MORANDI["grid"], color=MORANDI["text"])
    fig.update_xaxes(gridcolor=MORANDI["grid"], color=MORANDI["text"])
    return fig


# ============================================
# 紅綠數值卡片（取代 metric，讓 ± 可控色）
# ============================================
def render_inst_card(label, value):
    """法人卡片：正數紅、負數綠、零灰"""
    if value > 0:
        color_class = "inst-value-up"
        sign = "+"
    elif value < 0:
        color_class = "inst-value-down"
        sign = ""  # 負號自帶
    else:
        color_class = "inst-value-flat"
        sign = ""
    formatted = f"{sign}{value:,}"
    return f"""
    <div class="inst-card">
        <div class="inst-label">{label}</div>
        <div class="{color_class}">{formatted}</div>
    </div>
    """


def render_pct_card(label, pct, suffix="%"):
    """百分比卡片：正數紅、負數綠"""
    if pct > 0:
        color_class = "inst-value-up"
    elif pct < 0:
        color_class = "inst-value-down"
    else:
        color_class = "inst-value-flat"
    return f"""
    <div class="inst-card">
        <div class="inst-label">{label}</div>
        <div class="{color_class}">{pct:+.2f}{suffix}</div>
    </div>
    """


def style_alert_text(text):
    """讓警示燈字串裡的 +X% / -X% 套色"""
    return text


# ============================================
# 主畫面
# ============================================
st.title("📊 台股 AI 個股分析")
st.caption(f"🤖 整合技術面 / 籌碼面 / 基本面 / Gemini AI 解讀 / 即時新聞 · "
           f"FinMind {finmind_token_count} token / Gemini {len(gemini_keys)} key")

ic1, ic2 = st.columns([4, 1])
with ic1:
    sid = st.text_input(
        "stock_input",
        placeholder="輸入股票代號，例如 2330、0050、6849、00981A",
        label_visibility="collapsed",
        key="stock_input"
    )
with ic2:
    go_btn = st.button("🔍 開始分析", type="primary", use_container_width=True)

st.divider()

if not (go_btn and sid.strip()):
    if not sid.strip():
        st.info("👆 請輸入股票代號，按「開始分析」")
        st.markdown("""
        ### 🎯 本系統提供
        - 📈 **技術面分析**：RSI / MACD / KD / 均線
        - 💼 **籌碼面分析**：三大法人買賣超
        - 📊 **基本面分析**：月營收 YoY / MoM
        - 🤖 **Gemini AI 智能解讀**：分析師等級的深度報告
        - 📰 **即時個股新聞**：最近 7 天重要新聞整理
        - 🚦 **多指標警示燈**：紅黃綠三色預警

        ### ✅ 支援
        上市、上櫃、ETF、興櫃股票

        ### 🎨 配色說明（台股慣例）
        - 🔴 紅色 = 上漲 / 正數 / 買進
        - 🟢 綠色 = 下跌 / 負數 / 賣出
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


# ── 標題列 ──
st.subheader(f"{r['name']} ({r['id']})  {r['status']}")

# 收盤價漲跌：用自訂 HTML 控色
chg_color = "#C76A6A" if r["chg"] >= 0 else "#7B9E89"
chg_arrow = "▲" if r["chg"] >= 0 else "▼"

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="inst-card">
        <div class="inst-label">收盤價</div>
        <div style="color:#3D3833;font-size:28px;font-weight:700;">{r['close']:.2f}</div>
        <div style="color:{chg_color};font-size:14px;font-weight:600;margin-top:4px;">
            {chg_arrow} {r['chg']:+.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="inst-card">
        <div class="inst-label">成交量</div>
        <div style="color:#3D3833;font-size:28px;font-weight:700;">{r['vol']:,}</div>
        <div style="color:#8B7E72;font-size:13px;margin-top:4px;">張</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    rsi_color = "#C76A6A" if r["rsi"] and r["rsi"] > 70 else "#7B9E89" if r["rsi"] and r["rsi"] < 30 else "#3D3833"
    rsi_label = "(超買)" if r["rsi"] and r["rsi"] > 70 else "(超賣)" if r["rsi"] and r["rsi"] < 30 else ""
    st.markdown(f"""
    <div class="inst-card">
        <div class="inst-label">RSI(14)</div>
        <div style="color:{rsi_color};font-size:28px;font-weight:700;">{f"{r['rsi']:.2f}" if r['rsi'] else "N/A"}</div>
        <div style="color:{rsi_color};font-size:13px;margin-top:4px;">{rsi_label}</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="inst-card">
        <div class="inst-label">更新時間</div>
        <div style="color:#3D3833;font-size:22px;font-weight:700;margin-top:6px;">
            {datetime.now().strftime("%m/%d %H:%M")}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── 警示燈：每個訊號獨立一個 chip，不再用 · 連起來 ──
all_alerts = []
for a in r["alerts"]["red"]:
    all_alerts.append(("red", a))
for a in r["alerts"]["yellow"]:
    all_alerts.append(("yellow", a))
for a in r["alerts"]["green"]:
    all_alerts.append(("green", a))

if all_alerts:
    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    chips_html = ""
    for atype, atext in all_alerts:
        if atype == "red":
            chips_html += (
                f'<span style="display:inline-block;background:#F5DCDC;color:#C76A6A;'
                f'padding:6px 14px;border-radius:16px;margin:3px 5px 3px 0;font-size:13px;'
                f'font-weight:500;border:1px solid #E5BFBF;">🔴 {atext}</span>'
            )
        elif atype == "yellow":
            chips_html += (
                f'<span style="display:inline-block;background:#F5EFD9;color:#A88838;'
                f'padding:6px 14px;border-radius:16px;margin:3px 5px 3px 0;font-size:13px;'
                f'font-weight:500;border:1px solid #E5D9A8;">🟡 {atext}</span>'
            )
        else:
            chips_html += (
                f'<span style="display:inline-block;background:#DBE8E0;color:#5C8169;'
                f'padding:6px 14px;border-radius:16px;margin:3px 5px 3px 0;font-size:13px;'
                f'font-weight:500;border:1px solid #B8D0BE;">🟢 {atext}</span>'
            )
    st.markdown(chips_html, unsafe_allow_html=True)

st.divider()


# ── 5 個分頁 ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 技術面",
    "💼 籌碼面",
    "📊 基本面",
    "🤖 AI 智能解讀",
    "📰 即時新聞"
])

with tab1:
    st.markdown("### 技術指標總覽")
    tc = st.columns(4)
    tc[0].metric("MA5", f"{r['ma5']:.2f}" if r['ma5'] else "N/A")
    tc[1].metric("MA20", f"{r['ma20']:.2f}" if r['ma20'] else "N/A")
    tc[2].metric("MA60", f"{r['ma60']:.2f}" if r['ma60'] else "N/A")
    tc[3].metric("近期高/低", f"{r['high_recent']:.1f} / {r['low_recent']:.1f}")

    tc2 = st.columns(4)
    tc2[0].metric("K", f"{r['k']:.2f}" if r['k'] else "N/A")
    tc2[1].metric("D", f"{r['d']:.2f}" if r['d'] else "N/A")
    tc2[2].metric("MACD", f"{r['macd']:.2f}" if r['macd'] else "N/A")
    tc2[3].metric("量比", f"{r['vr']:.2f}x" if r['vr'] else "N/A")

    st.markdown("### 完整 K 線圖")
    st.plotly_chart(plot_kline(r["df"], r["name"], r["id"]),
                    use_container_width=True, config={"displayModeBar": False})

with tab2:
    st.markdown("### 三大法人最新買賣超（張）")
    cc = st.columns(4)
    cc[0].markdown(render_inst_card("外資", r["ifor"]), unsafe_allow_html=True)
    cc[1].markdown(render_inst_card("投信", r["itru"]), unsafe_allow_html=True)
    cc[2].markdown(render_inst_card("自營商", r["idal"]), unsafe_allow_html=True)
    cc[3].markdown(render_inst_card("合計", r["itot"]), unsafe_allow_html=True)

    if not r["pivot"].empty:
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        fig = plot_inst(r["pivot"], r["df"])
        if fig:
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})

        st.markdown("### 📋 近 10 日法人明細（張）")
        disp = r["pivot"].head(10).copy()
        disp.index = disp.index.strftime("%Y-%m-%d")
        st.dataframe(disp, use_container_width=True)
    else:
        st.info("無法人資料（可能為興櫃股或新上市股）")

with tab3:
    st.markdown("### 基本面數據")
    if r["has_rev"]:
        bc = st.columns(3)
        with bc[0]:
            st.markdown(f"""
            <div class="inst-card">
                <div class="inst-label">最新月營收</div>
                <div style="color:#3D3833;font-size:28px;font-weight:700;">{r['rev']:.2f}</div>
                <div style="color:#8B7E72;font-size:13px;margin-top:4px;">億元</div>
            </div>
            """, unsafe_allow_html=True)
        with bc[1]:
            st.markdown(render_pct_card("YoY 年增率", r["yoy"]), unsafe_allow_html=True)
        with bc[2]:
            st.markdown(render_pct_card("MoM 月增率", r["mom"]), unsafe_allow_html=True)

        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

        if r["yoy"] > 30:
            st.success(f"🚀 營收高速成長：YoY +{r['yoy']:.1f}%，基本面強勁")
        elif r["yoy"] > 10:
            st.success(f"✅ 營收穩健成長：YoY +{r['yoy']:.1f}%")
        elif r["yoy"] > 0:
            st.info(f"📊 營收溫和成長：YoY +{r['yoy']:.1f}%")
        elif r["yoy"] > -10:
            st.warning(f"⚠️ 營收略微衰退：YoY {r['yoy']:.1f}%")
        else:
            st.error(f"🔴 營收明顯衰退：YoY {r['yoy']:.1f}%")
    else:
        st.info("📌 此標的為 ETF 或興櫃，無月營收資料")

with tab4:
    st.markdown("### 🤖 Gemini AI 智能解讀")
    st.caption("由 Google Gemini 2.5 Flash 模型產生的深度分析報告（自動重試 + 模型降級）")

    if st.button("🚀 產生 AI 分析報告", type="primary", key="ai_btn"):
        with st.spinner("AI 正在思考中（含自動重試），請稍候 10-30 秒..."):
            ma5_str = f"{r['ma5']:.1f}" if r['ma5'] else "N/A"
            ma20_str = f"{r['ma20']:.1f}" if r['ma20'] else "N/A"
            ma60_str = f"{r['ma60']:.1f}" if r['ma60'] else "N/A"
            rsi_str = f"{r['rsi']:.1f}" if r['rsi'] else "N/A"
            k_str = f"{r['k']:.1f}" if r['k'] else "N/A"
            d_str = f"{r['d']:.1f}" if r['d'] else "N/A"
            macd_str = f"{r['macd']:.2f}" if r['macd'] else "N/A"
            rev_block = f"月營收：{r['rev']:.2f} 億, YoY {r['yoy']:+.1f}%, MoM {r['mom']:+.1f}%" if r['has_rev'] else "ETF 或興櫃，無月營收資料"

            data_summary = f"""
- 收盤價：{r['close']:.2f}（漲跌 {r['chg']:+.2f}%）
- 成交量：{r['vol']:,} 張
- 均線：MA5={ma5_str}, MA20={ma20_str}, MA60={ma60_str}
- 技術指標：RSI={rsi_str}, K={k_str}, D={d_str}, MACD={macd_str}
- 法人籌碼：外資 {r['ifor']:+,} 張, 投信 {r['itru']:+,} 張, 自營商 {r['idal']:+,} 張
- {rev_block}
- 警示燈：紅燈 {len(r['alerts']['red'])} 個, 黃燈 {len(r['alerts']['yellow'])} 個, 綠燈 {len(r['alerts']['green'])} 個
- 整體狀態：{r['status']}
"""
            ai_report = get_ai_analysis(r["name"], r["id"], data_summary)
            st.markdown(ai_report)
            st.divider()
            st.caption("⚠️ 本分析由 AI 產生，僅供參考。投資決策請依個人判斷與風險承受能力。")
    else:
        st.info("👆 點上方按鈕開始 AI 分析（自動重試 3 次，含模型降級機制）")

with tab5:
    st.markdown("### 📰 個股最新新聞")
    st.caption("由 Gemini Google Search 即時搜尋最近 7 天相關新聞")

    if st.button("🔍 搜尋最新新聞", type="primary", key="news_btn"):
        with st.spinner("正在搜尋新聞，請稍候 10-30 秒..."):
            news = get_news(r["name"], r["id"])
            st.markdown(news)
            st.divider()
            st.caption("📌 新聞來源：Google Search · 由 Gemini AI 整理摘要")
    else:
        st.info("👆 點上方按鈕搜尋最新新聞")

st.divider()
st.caption(f"📊 資料來源：FinMind · 🤖 AI：Google Gemini 2.5 Flash · 最後分析：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("⚠️ 本網站僅供研究參考，不構成投資建議。投資有風險，操作請審慎評估。")
