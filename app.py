def plot_morandi_gauge(score):
    """產出帶有真實指針箭頭的儀表板 (修復 Plotly 雲端版本衝突)"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        number = {'font': {'size': 36, 'color': '#3D3833'}},
        gauge = {
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': "rgba(0,0,0,0)"}, # 隱藏預設填滿，改用真實指針
            'steps': [
                {'range': [0, 40], 'color': "#DBE8E0"},  # 綠色 (偏弱)
                {'range': [40, 60], 'color': "#F5EFD9"}, # 黃色 (中性)
                {'range': [60, 100], 'color': "#F5DCDC"} # 紅色 (偏多)
            ],
        }
    ))
    
    # 透過三角函數計算指針末端位置
    theta = (1 - score / 100) * np.pi
    r_needle = 0.38 # 指針長度
    x_head = 0.5 + r_needle * np.cos(theta)
    y_head = 0.25 + r_needle * np.sin(theta)
    
    # 改用 shapes (幾何直線) 來畫出儀表板指針，完美避開 annotation 報錯
    fig.update_layout(
        shapes=[
            dict(
                type="line",
                x0=0.5, y0=0.25,
                x1=x_head, y1=y_head,
                line=dict(color="#5C5048", width=5),
                xref="paper", yref="paper"
            )
        ],
        height=180, 
        margin=dict(l=15, r=15, t=10, b=10), 
        paper_bgcolor="rgba(0,0,0,0)", 
        font=dict(family="Arial, 'Noto Sans TC'")
    )
    return fig
