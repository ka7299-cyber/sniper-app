import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 頁面基本設定
st.set_page_config(page_title="Sniper X V103", layout="wide")

# 移植大師參數
MASTER_PARAMS = {'2330': 17, '2317': 18, '2303': 21, '2454': 29, '2603': 35}

st.title("🚀 Sniper X 戰情室 V103")

# --- 側邊欄控制 ---
st.sidebar.header("控制面板")
stock_id = st.sidebar.text_input("輸入股票代號", value="2330").upper().strip()

# ★ 新增功能：讓使用者選擇顯示區間
# 這樣直屏時可以選擇「3個月」，圖表就不會那麼擠
range_options = {"3個月": 60, "半年": 120, "1年": 240}
selected_range = st.sidebar.selectbox("顯示時間區間", list(range_options.keys()), index=1)
days_to_show = range_options[selected_range]

def get_data_with_fallback(sid):
    ticker_tw = f"{sid}.TW"
    df = yf.download(ticker_tw, period="2y", progress=False) # 抓長一點確保均線正確
    if df.empty:
        ticker_two = f"{sid}.TWO"
        df = yf.download(ticker_two, period="2y", progress=False)
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
            
            # 數據面板 (Metric)
            c1, c2, c3 = st.columns(3)
            c1.metric("目前價格", f"{last_p:.1f}")
            c2.metric(f"{ma_days}MA", f"{last_ma:.1f}")
            c3.metric("狀態", status)
            
            # 僅擷取使用者選擇的顯示區間
            plot_df = df.tail(days_to_show)
            
            # --- 繪圖優化 ---
            fig = go.Figure()
            
            # 加入多空填色，讓直屏看趨勢更直覺
            fig.add_trace(go.Scatter(
                x=plot_df.index, y=plot_df['Close'], name='價格',
                line=dict(color='#1f77b4', width=2),
                hovertemplate='%{y:.1f}<extra>價格</extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=plot_df.index, y=plot_df['MA'], name='均線',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                hovertemplate='%{y:.1f}<extra>均線</extra>'
            ))
            
            fig.update_layout(
                title=f"{stock_id} ({selected_range})",
                template="plotly_white",
                height=450, # 稍微降低高度，避免手機需要滑很久
                margin=dict(l=10, r=10, t=50, b=10),
                dragmode=False,
                hovermode="x unified",
                # ★ 強制顯示較少的日期標籤，避免重疊亂掉
                xaxis=dict(fixedrange=True, nticks=6), 
                yaxis=dict(fixedrange=True, side="right"), # 價格改在右邊，手機看更直覺
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        else:
            st.error(f"❌ 找不到 {stock_id}")
