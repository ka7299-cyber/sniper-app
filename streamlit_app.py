import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 頁面基本設定
st.set_page_config(page_title="Sniper X V102", layout="wide")

# 移植大師參數 (來自原生 V75 代碼)
MASTER_PARAMS = {'2330': 17, '2317': 18, '2303': 21, '2454': 29, '2603': 35}

st.title("🚀 Sniper X 戰情室 V102")
st.sidebar.header("控制面板")

# 側邊欄輸入
stock_id = st.sidebar.text_input("請輸入股票代號", value="2330").upper().strip()

def get_data_with_fallback(sid):
    # 優先嘗試上市 (.TW)
    ticker_tw = f"{sid}.TW"
    df = yf.download(ticker_tw, period="1y", progress=False)
    
    # 如果上市抓不到，嘗試上櫃 (.TWO)
    if df.empty:
        ticker_two = f"{sid}.TWO"
        df = yf.download(ticker_two, period="1y", progress=False)
        return df, ticker_two
    return df, ticker_tw

if stock_id:
    with st.spinner(f'正在分析 {stock_id} ...'):
        df, final_ticker = get_data_with_fallback(stock_id)
        
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            ma_days = MASTER_PARAMS.get(stock_id, 20)
            df['MA'] = df['Close'].rolling(window=ma_days).mean()
            
            last_p = float(df['Close'].iloc[-1])
            last_ma = float(df['MA'].iloc[-1])
            status = "🔥 多頭" if last_p > last_ma else "❄️ 空頭"
            
            # 數據面板
            c1, c2, c3 = st.columns(3)
            c1.metric("目前價格", f"{last_p:.2f}")
            c2.metric(f"指標 ({ma_days}MA)", f"{last_ma:.2f}")
            c3.metric("趨勢狀態", status)
            
            # 互動式 Plotly 圖表 (鎖定縮放，保留查線)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'], name='Price', 
                line=dict(color='#1f77b4'),
                hovertemplate='日期: %{x}<br>價格: %{y:.2f}<extra></extra>' # 自訂查線格式
            ))
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MA'], name=f'{ma_days}MA', 
                line=dict(color='#ff7f0e', dash='dash'),
                hovertemplate='均線: %{y:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"{stock_id} ({final_ticker}) 戰情圖表",
                template="plotly_white",
                height=500,
                margin=dict(l=0, r=0, t=50, b=0),
                dragmode=False, # ★關鍵 1：禁用拖動縮放
                hovermode="x unified", # ★關鍵 2：查線時同時顯示價格與均線
                xaxis=dict(fixedrange=True), # ★關鍵 3：禁止 X 軸縮放
                yaxis=dict(fixedrange=True)  # ★關鍵 4：禁止 Y 軸縮放
            )

            # 顯示圖表並設定 config
            st.plotly_chart(fig, use_container_width=True, config={
                'staticPlot': False, 
                'scrollZoom': False, # 禁止滾輪/雙指縮放
                'displayModeBar': False, # 隱藏上方工具列，讓畫面更像 App
                'showAxisDragHandles': False
            })
            
        else:
            st.error(f"❌ 找不到 {stock_id}。")

st.sidebar.info("V102：鎖定視角、優化查線")
