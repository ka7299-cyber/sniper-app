import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 頁面基本設定
st.set_page_config(page_title="Sniper X V100", layout="wide")

# 移植大師參數 (來自您的 V75 原生代碼)
MASTER_PARAMS = {'2330': 17, '2317': 18, '2303': 21, '2454': 29, '2603': 35}

st.title("🚀 Sniper X 戰情室 V100")
st.markdown("---")

# 側邊欄輸入
stock_id = st.sidebar.text_input("請輸入股票代號", value="2330").upper()

if stock_id:
    # 判斷上市或上櫃
    ticker = f"{stock_id}.TW" if len(stock_id) == 4 else stock_id
    
    with st.spinner(f'正在分析 {stock_id} ...'):
        df = yf.download(ticker, period="1y", progress=False)
        
        if not df.empty:
            # 修正 yfinance 多重索引問題
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
            
            # 互動式 K 線與均線圖 (Plotly)
            fig = go.Figure()
            # 價格線
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', 
                                     line=dict(color='#1f77b4', width=2)))
            # 均線
            fig.add_trace(go.Scatter(x=df.index, y=df['MA'], name=f'{ma_days}MA', 
                                     line=dict(color='#ff7f0e', width=2, dash='dash')))
            
            # 圖表美化
            fig.update_layout(
                title=f"{stock_id} 互動式戰情圖表",
                xaxis_title="日期",
                yaxis_title="價格",
                height=500,
                template="plotly_white",
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error(f"❌ 無法取得 {stock_id} 的資料，請檢查代號是否正確。")

st.sidebar.markdown("---")
st.sidebar.info("本系統使用 Yahoo Finance 即時數據。")
