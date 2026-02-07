import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 頁面基本設定
st.set_page_config(page_title="Sniper X V101", layout="wide")

# 移植大師參數 (來自原生 V75 代碼)
MASTER_PARAMS = {'2330': 17, '2317': 18, '2303': 21, '2454': 29, '2603': 35}

st.title("🚀 Sniper X 戰情室 V101")
st.sidebar.header("控制面板")

# 側邊欄輸入
stock_id = st.sidebar.text_input("請輸入股票代號", value="2330").upper().strip()

def get_data_with_fallback(sid):
    """
    自動修復上櫃股票無法讀取的問題
    """
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
            # 處理多重索引問題
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # 自動選擇參數：大師或 AI 預設 (20MA)
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
            
            # 互動式 Plotly 圖表
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#1f77b4')))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA'], name=f'{ma_days}MA', line=dict(color='#ff7f0e', dash='dash')))
            
            fig.update_layout(
                title=f"{stock_id} ({final_ticker}) 戰情圖表",
                template="plotly_white",
                height=500,
                margin=dict(l=0, r=0, t=50, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error(f"❌ 依然找不到 {stock_id} 的資料。請確認代號是否正確。")

st.sidebar.info(f"當前模式：智慧後綴補位 (TW/TWO)")
