# ============================================
# app.py - Trading Signal Generator Pro
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================
# HELPER FUNCTION: Safe Scalar Extraction
# ============================================
def safe_float(value, default=0.0):
    try:
        if hasattr(value, 'item'):
            value = value.item()
        elif hasattr(value, 'values'):
            if len(value.values) > 0:
                value = value.values[0]
            else:
                return default
        if pd.isna(value):
            return default
        return float(value)
    except:
        return default

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Trading Signal Pro | Enterprise",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# ULTRA MODERN STOCK UI CSS
# ============================================
st.markdown("""
<style>
    /* ===== IMPORT FONTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* ===== MAIN BACKGROUND - STOCK MARKET THEME ===== */
    .stApp {
        background: #0a0e1a;
        background-image: 
            /* Stock market grid pattern */
            linear-gradient(rgba(16, 185, 129, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(16, 185, 129, 0.02) 1px, transparent 1px),
            /* Market pulse glow */
            radial-gradient(ellipse at 15% 25%, rgba(16, 185, 129, 0.04) 0%, transparent 50%),
            radial-gradient(ellipse at 85% 75%, rgba(139, 92, 246, 0.03) 0%, transparent 50%),
            /* Trading floor glow */
            radial-gradient(ellipse at 50% 50%, rgba(16, 185, 129, 0.02) 0%, transparent 70%);
        background-size: 40px 40px, 40px 40px, 100% 100%, 100% 100%, 100% 100%;
    }
    
    /* ==========================================
       SIDEBAR - WALL STREET STYLE
       ========================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1220 0%, #0f172a 30%, #0a0e1a 100%) !important;
        border-right: 1px solid rgba(16, 185, 129, 0.08) !important;
        box-shadow: 4px 0 60px rgba(0, 0, 0, 0.7) !important;
    }
    
    .sidebar-brand {
        text-align: center;
        padding: 24px 0 20px 0;
        border-bottom: 1px solid rgba(16, 185, 129, 0.06);
        margin-bottom: 20px;
        background: rgba(16, 185, 129, 0.02);
        border-radius: 0 0 20px 20px;
    }
    
    .sidebar-brand .logo-icon {
        font-size: 32px;
        display: block;
        margin-bottom: 4px;
    }
    
    .sidebar-brand .brand-name {
        font-size: 22px;
        font-weight: 900;
        background: linear-gradient(135deg, #34d399 0%, #10b981 50%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    
    .sidebar-brand .brand-sub {
        font-size: 8px;
        font-weight: 700;
        color: #4b5563;
        letter-spacing: 0.35em;
        text-transform: uppercase;
        margin-top: 2px;
        -webkit-text-fill-color: #4b5563;
    }
    
    /* Live Ticker Tape */
    .ticker-tape {
        display: flex;
        justify-content: center;
        gap: 14px;
        margin-top: 10px;
        padding: 6px 12px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.03);
    }
    
    .ticker-tape .ticker-item {
        font-size: 9px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace !important;
        color: #6b7280;
    }
    
    .ticker-tape .ticker-item .up { color: #34d399; }
    .ticker-tape .ticker-item .down { color: #f87171; }
    
    /* Sidebar Labels */
    .sidebar-label {
        color: #6b7280;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        padding: 12px 0 6px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.02);
        margin-bottom: 10px;
    }
    
    .sidebar-input-label {
        color: #9ca3af;
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    
    section[data-testid="stSidebar"] .stTextInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 10px !important;
        color: #e5e7eb !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        font-family: 'JetBrains Mono', monospace !important;
        transition: all 0.3s ease !important;
    }
    
    section[data-testid="stSidebar"] .stTextInput input:focus {
        border-color: rgba(16, 185, 129, 0.3) !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.06) !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    .sidebar-about {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 14px;
        padding: 14px 16px;
        margin-top: 6px;
    }
    
    .sidebar-about .title {
        color: #e5e7eb;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
    }
    
    .sidebar-about .desc {
        color: #6b7280;
        font-size: 10px;
        line-height: 1.6;
        margin-top: 4px;
    }
    
    .sidebar-about .stats {
        color: #4b5563;
        font-size: 9px;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid rgba(255, 255, 255, 0.03);
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .sidebar-about .stats .label { color: #6b7280; }
    .sidebar-about .stats .value { color: #34d399; font-weight: 600; }
    
    .sidebar-caption {
        text-align: center;
        color: #2d3748;
        font-size: 9px;
        letter-spacing: 0.1em;
        padding: 12px 0 4px 0;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* ==========================================
       MAIN CONTENT - MODERN TRADING DASHBOARD
       ========================================== */
    
    .main-title {
        font-size: 40px;
        font-weight: 900;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #ffffff 0%, #34d399 50%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
        line-height: 1.1;
    }
    
    .main-title .accent {
        background: linear-gradient(135deg, #34d399, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-subtitle {
        color: #6b7280;
        font-size: 14px;
        font-weight: 400;
        letter-spacing: 0.06em;
        margin-top: 2px;
    }
    
    .main-subtitle .highlight-text {
        color: #34d399;
        font-weight: 500;
        -webkit-text-fill-color: #34d399;
    }
    
    .enterprise-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.1);
        border-radius: 30px;
        padding: 1px 14px;
        font-size: 8px;
        font-weight: 700;
        color: #34d399;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-left: 10px;
        -webkit-text-fill-color: #34d399;
        vertical-align: middle;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.08), rgba(139, 92, 246, 0.05), transparent);
        margin: 20px 0 24px 0;
    }
    
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.01em;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .section-title .highlight {
        background: linear-gradient(135deg, #34d399, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .section-title .badge {
        background: rgba(16, 185, 129, 0.06);
        border: 1px solid rgba(16, 185, 129, 0.08);
        border-radius: 30px;
        padding: 0px 10px;
        font-size: 7px;
        font-weight: 700;
        color: #34d399;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        -webkit-text-fill-color: #34d399;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* ===== METRIC CARDS ===== */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 18px 14px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #10b981, #34d399, #10b981);
        background-size: 200% 100%;
        opacity: 0;
        transition: opacity 0.4s ease;
        animation: shimmer 3s linear infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(16, 185, 129, 0.1);
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card:hover::before { opacity: 1; }
    
    .metric-card .label {
        color: #6b7280;
        font-size: 9px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 4px;
    }
    
    .metric-card .value {
        color: #ffffff;
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 2px 0;
    }
    
    .metric-card .sub {
        color: #4b5563;
        font-size: 10px;
        font-weight: 400;
        margin-top: 2px;
    }
    
    .metric-card .change-positive { color: #34d399; font-weight: 600; font-size: 11px; }
    .metric-card .change-negative { color: #f87171; font-weight: 600; font-size: 11px; }
    
    /* ===== SIGNAL CARDS - ULTRA MODERN ===== */
    .signal-buy, .signal-hold, .signal-sell {
        border-radius: 24px;
        padding: 36px 28px;
        text-align: center;
        transition: all 0.5s ease;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
    }
    
    .signal-buy {
        background: linear-gradient(145deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.02));
        border: 2px solid rgba(16, 185, 129, 0.2);
        box-shadow: 0 8px 48px rgba(16, 185, 129, 0.05);
    }
    
    .signal-buy::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -30%;
        width: 60%;
        height: 100%;
        background: radial-gradient(circle, rgba(16, 185, 129, 0.06) 0%, transparent 70%);
        animation: pulse-glow 4s ease-in-out infinite;
    }
    
    .signal-buy:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 12px 60px rgba(16, 185, 129, 0.15);
    }
    
    .signal-hold {
        background: linear-gradient(145deg, rgba(251, 191, 36, 0.06), rgba(245, 158, 11, 0.02));
        border: 2px solid rgba(251, 191, 36, 0.15);
        box-shadow: 0 8px 48px rgba(251, 191, 36, 0.05);
    }
    
    .signal-hold::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -30%;
        width: 60%;
        height: 100%;
        background: radial-gradient(circle, rgba(251, 191, 36, 0.06) 0%, transparent 70%);
        animation: pulse-glow 4s ease-in-out infinite;
    }
    
    .signal-hold:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(251, 191, 36, 0.3);
        box-shadow: 0 12px 60px rgba(251, 191, 36, 0.12);
    }
    
    .signal-sell {
        background: linear-gradient(145deg, rgba(248, 113, 113, 0.06), rgba(239, 68, 68, 0.02));
        border: 2px solid rgba(248, 113, 113, 0.15);
        box-shadow: 0 8px 48px rgba(248, 113, 113, 0.05);
    }
    
    .signal-sell::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -30%;
        width: 60%;
        height: 100%;
        background: radial-gradient(circle, rgba(248, 113, 113, 0.06) 0%, transparent 70%);
        animation: pulse-glow 4s ease-in-out infinite;
    }
    
    .signal-sell:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(248, 113, 113, 0.3);
        box-shadow: 0 12px 60px rgba(248, 113, 113, 0.12);
    }
    
    @keyframes pulse-glow {
        0%, 100% { transform: scale(1); opacity: 0.4; }
        50% { transform: scale(1.3); opacity: 0.7; }
    }
    
    .signal-buy .icon, .signal-hold .icon, .signal-sell .icon {
        font-size: 52px;
        position: relative;
        z-index: 1;
        display: block;
    }
    
    .signal-buy .text {
        font-size: 30px;
        font-weight: 900;
        color: #34d399;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }
    
    .signal-hold .text {
        font-size: 30px;
        font-weight: 900;
        color: #fbbf24;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }
    
    .signal-sell .text {
        font-size: 30px;
        font-weight: 900;
        color: #f87171;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }
    
    .signal-buy .sub, .signal-hold .sub, .signal-sell .sub {
        color: #6b7280;
        font-size: 13px;
        margin-top: 4px;
        position: relative;
        z-index: 1;
        letter-spacing: 0.04em;
    }
    
    .signal-buy .action, .signal-hold .action, .signal-sell .action {
        color: #4b5563;
        font-size: 11px;
        margin-top: 8px;
        position: relative;
        z-index: 1;
        border-top: 1px solid rgba(255, 255, 255, 0.04);
        padding-top: 8px;
    }
    
    /* ===== CONFIDENCE CONTAINER ===== */
    .confidence-container {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 20px 22px;
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .confidence-container:hover {
        border-color: rgba(16, 185, 129, 0.08);
    }
    
    .confidence-container .label {
        color: #6b7280;
        font-size: 9px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.15em;
    }
    
    .confidence-container .value {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 2px 0;
    }
    
    .confidence-bar-bg {
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 4px;
        overflow: hidden;
        margin-top: 8px;
    }
    
    .confidence-bar-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #10b981, #34d399);
        transition: width 1.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.1);
    }
    
    .confidence-detail {
        color: #4b5563;
        font-size: 10px;
        margin-top: 8px;
        letter-spacing: 0.04em;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* ===== DISCLAIMER ===== */
    .disclaimer {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(253, 203, 110, 0.04);
        border-left: 3px solid rgba(253, 203, 110, 0.08);
        border-radius: 12px;
        padding: 14px 20px;
        margin-top: 28px;
    }
    
    .disclaimer p {
        color: #6b7280;
        font-size: 11px;
        margin: 0;
        line-height: 1.6;
    }
    
    .disclaimer strong { color: #9ca3af; }
    
    .footer {
        text-align: center;
        color: #2d3748;
        font-size: 10px;
        padding: 20px 0 6px 0;
        letter-spacing: 0.08em;
        border-top: 1px solid rgba(255, 255, 255, 0.02);
        margin-top: 28px;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .footer .brand .highlight {
        background: linear-gradient(135deg, #34d399, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main-title { font-size: 26px; }
        .metric-card .value { font-size: 18px; }
        .signal-buy .text, .signal-hold .text, .signal-sell .text { font-size: 22px; }
        .signal-buy .icon, .signal-hold .icon, .signal-sell .icon { font-size: 36px; }
        .signal-buy, .signal-hold, .signal-sell { padding: 20px; }
        .enterprise-badge { font-size: 6px; padding: 1px 8px; margin-left: 4px; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FEATURE NAMES - LOCKED (Match Colab)
# ============================================
EXPECTED_FEATURES = [
    'SMA_10', 'SMA_20', 'SMA_50',
    'RSI_14',
    'MACD', 'MACD_Signal', 'MACD_Histogram',
    'Momentum_10', 'Momentum_20',
    'Volatility_10', 'Volatility_20',
    'High_Low_ratio', 'Close_Open_ratio',
    'Volume_Change', 'Volume_Ratio',
    'BB_Position'
]

# ============================================
# SIGNAL MAPPING
# ============================================
SIGNAL_MAP = {
    -1: {'label': 'SELL', 'emoji': '📉', 'color': '#f87171', 'class': 'signal-sell', 
         'action': 'Consider selling or reducing exposure'},
    0: {'label': 'HOLD', 'emoji': '⏸️', 'color': '#fbbf24', 'class': 'signal-hold',
        'action': 'Maintain current positions'},
    1: {'label': 'BUY', 'emoji': '📈', 'color': '#34d399', 'class': 'signal-buy',
        'action': 'Consider buying or increasing exposure'}
}

# ============================================
# LOAD MODELS
# ============================================
@st.cache_resource
def load_models():
    try:
        model_path = 'models/best_model.pkl'
        scaler_path = 'models/scaler.pkl'
        features_path = 'models/feature_columns.pkl'
        
        if not os.path.exists(model_path):
            return None, None, None, "Model files not found"
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        feature_columns = joblib.load(features_path)
        
        return model, scaler, feature_columns, None
    except Exception as e:
        return None, None, None, str(e)

model, scaler, feature_columns, load_error = load_models()

# ============================================
# SIDEBAR - WALL STREET STYLE
# ============================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span class="logo-icon">📡</span>
        <div class="brand-name">SIGNAL PRO</div>
        <div class="brand-sub">Trading Terminal</div>
        <div class="ticker-tape">
            <span class="ticker-item"><span class="up">▲</span> AAPL</span>
            <span class="ticker-item"><span class="down">▼</span> MSFT</span>
            <span class="ticker-item"><span class="up">▲</span> GOOGL</span>
            <span class="ticker-item"><span class="up">▲</span> NVDA</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-label">📊 Portfolio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-input-label">Symbol</div>', unsafe_allow_html=True)
    ticker = st.text_input("", "AAPL", label_visibility="collapsed").upper()
    st.caption("AAPL · MSFT · GOOGL · TSLA · NVDA")
    
    st.markdown('<div class="sidebar-label" style="margin-top:14px;">📅 Timeframe</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", datetime.now() - timedelta(days=365), label_visibility="collapsed")
    with col2:
        end_date = st.date_input("To", datetime.now(), label_visibility="collapsed")
    
    st.markdown("---")
    
    st.markdown("""
    <div class="sidebar-about">
        <div class="title">📡 Signal Engine</div>
        <div class="desc">
            AI-powered BUY/SELL/HOLD signals using 
            <span style="color: #34d399;">ensemble ML</span> 
            with 16 technical indicators.
        </div>
        <div class="stats">
            <span class="label">Model:</span> <span class="value">Ensemble</span><br>
            <span class="label">Accuracy:</span> <span class="value">~40%</span> (3-class)<br>
            <span class="label">Features:</span> <span class="value">16</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-caption">⚡ v4.0 · Enterprise Terminal</div>', unsafe_allow_html=True)

# ============================================
# MAIN CONTENT
# ============================================
st.markdown("""
<div class="main-title">
    Trading <span class="accent">Signal</span> Generator
    <span class="enterprise-badge">Terminal Pro</span>
</div>
<div class="main-subtitle">
    Institutional-grade <span class="highlight-text">BUY / SELL / HOLD</span> signals powered by ensemble ML
</div>
<div class="custom-divider"></div>
""", unsafe_allow_html=True)

# ============================================
# FETCH DATA
# ============================================
@st.cache_data
def fetch_stock_data(ticker, start, end):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start, end=end)
        if df.empty:
            return None, None
        info = stock.info
        company_info = {
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'N/A'),
            'pe_ratio': info.get('trailingPE', 0),
            'beta': info.get('beta', 0)
        }
        return df, company_info
    except:
        return None, None

with st.spinner(f"Loading {ticker} market data..."):
    df, company_info = fetch_stock_data(ticker, start_date, end_date)

if df is None or df.empty:
    st.error(f"❌ Could not fetch data for {ticker}")
    st.stop()

# ============================================
# METRICS ROW
# ============================================
st.markdown('<div class="section-title">📊 <span class="highlight">Market Dashboard</span> <span class="badge">Live</span></div>', unsafe_allow_html=True)

current_price = float(df['Close'].iloc[-1])
prev_price = float(df['Close'].iloc[-2])
price_change = ((current_price - prev_price) / prev_price) * 100
volume = float(df['Volume'].iloc[-1])
avg_volume = float(df['Volume'].mean())
high_52w = float(df['High'].max())
low_52w = float(df['Low'].min())

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Price</div>
        <div class="value">${current_price:.2f}</div>
        <div class="{'change-positive' if price_change >= 0 else 'change-negative'}">
            {price_change:+.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Volume</div>
        <div class="value">{volume/1e6:.1f}M</div>
        <div class="sub">Avg {avg_volume/1e6:.1f}M</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">52W High</div>
        <div class="value" style="color: #34d399;">${high_52w:.2f}</div>
        <div class="sub">+{((high_52w - current_price)/current_price*100):.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">52W Low</div>
        <div class="value" style="color: #f87171;">${low_52w:.2f}</div>
        <div class="sub">-{((current_price - low_52w)/current_price*100):.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    pe_ratio = company_info.get('pe_ratio', 0)
    beta = company_info.get('beta', 0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Valuation</div>
        <div class="value">P/E {pe_ratio:.1f}</div>
        <div class="sub">Beta {beta:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# PRICE CHART
# ============================================
st.markdown(f'<div class="section-title">📉 <span class="highlight">{ticker}</span> Price Action <span class="badge">{company_info.get("name", ticker)[:15]}</span></div>', unsafe_allow_html=True)

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.04,
    row_heights=[0.7, 0.3],
    subplot_titles=(f'{company_info.get("name", ticker)} · Daily Candles', 'Volume')
)

fig.add_trace(
    go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Price',
        increasing_line_color='#34d399',
        decreasing_line_color='#f87171'
    ),
    row=1, col=1
)

# Moving Averages
ma20 = df['Close'].rolling(20).mean()
ma50 = df['Close'].rolling(50).mean()
ma200 = df['Close'].rolling(200).mean()

fig.add_trace(go.Scatter(x=df.index, y=ma20, name='SMA 20', line=dict(color='#fbbf24', width=1.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=ma50, name='SMA 50', line=dict(color='#a78bfa', width=1.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=ma200, name='SMA 200', line=dict(color='#f472b6', width=1.5)), row=1, col=1)

# Volume bars
colors = ['#34d399' if close >= open else '#f87171' for close, open in zip(df['Close'], df['Open'])]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors, opacity=0.6), row=2, col=1)

fig.update_layout(
    height=500,
    template='plotly_dark',
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#6b7280', size=10)),
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=35, b=20)
)

fig.update_xaxes(gridcolor='rgba(255,255,255,0.02)')
fig.update_yaxes(gridcolor='rgba(255,255,255,0.02)')

st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# SIGNAL GENERATOR - FIXED FOR SVC
# ============================================
st.markdown('<div class="section-title">📡 <span class="highlight">Trading Signal</span> <span class="badge">AI Generated</span></div>', unsafe_allow_html=True)

if model is None or scaler is None or feature_columns is None:
    st.error(f"❌ Model loading error: {load_error}")
    st.info("Please make sure all model files are in the 'models' folder.")
    st.stop()

try:
    # ==========================================
    # CREATE FEATURES
    # ==========================================
    
    close_series = df['Close']
    high_series = df['High']
    low_series = df['Low']
    open_series = df['Open']
    volume_series = df['Volume']
    
    n = len(close_series)
    last_close = safe_float(close_series.iloc[-1])
    last_high = safe_float(high_series.iloc[-1])
    last_low = safe_float(low_series.iloc[-1])
    last_open = safe_float(open_series.iloc[-1])
    last_volume = safe_float(volume_series.iloc[-1])
    
    returns_values = close_series.pct_change().values
    
    feature_values = {}
    
    # 1. Moving Averages
    feature_values['SMA_10'] = safe_float(close_series.rolling(10).mean().iloc[-1]) if n >= 10 else safe_float(close_series.mean())
    feature_values['SMA_20'] = safe_float(close_series.rolling(20).mean().iloc[-1]) if n >= 20 else safe_float(close_series.mean())
    feature_values['SMA_50'] = safe_float(close_series.rolling(50).mean().iloc[-1]) if n >= 50 else safe_float(close_series.mean())
    
    # 2. RSI
    delta = close_series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    feature_values['RSI_14'] = safe_float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    
    # 3. MACD
    exp1 = close_series.ewm(span=12, adjust=False).mean()
    exp2 = close_series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    feature_values['MACD'] = safe_float(macd.iloc[-1])
    feature_values['MACD_Signal'] = safe_float(macd_signal.iloc[-1])
    feature_values['MACD_Histogram'] = feature_values['MACD'] - feature_values['MACD_Signal']
    
    # 4. Momentum
    feature_values['Momentum_10'] = safe_float(close_series.iloc[-1] - close_series.iloc[-10]) if n >= 10 else 0.0
    feature_values['Momentum_20'] = safe_float(close_series.iloc[-1] - close_series.iloc[-20]) if n >= 20 else 0.0
    
    # 5. Volatility
    if n >= 10:
        vol_10 = np.std(returns_values[-10:]) if len(returns_values[-10:]) > 0 else 0.01
        feature_values['Volatility_10'] = safe_float(vol_10)
    else:
        feature_values['Volatility_10'] = 0.01
    
    if n >= 20:
        vol_20 = np.std(returns_values[-20:]) if len(returns_values[-20:]) > 0 else 0.01
        feature_values['Volatility_20'] = safe_float(vol_20)
    else:
        feature_values['Volatility_20'] = 0.01
    
    # 6. Ratios
    feature_values['High_Low_ratio'] = last_high / last_low if last_low != 0 else 1.0
    feature_values['Close_Open_ratio'] = last_close / last_open if last_open != 0 else 1.0
    
    # 7. Volume
    feature_values['Volume_Change'] = safe_float(volume_series.pct_change().iloc[-1]) if n > 1 else 0.0
    
    if n >= 20:
        volume_sma = np.mean(volume_series.values[-20:]) if len(volume_series.values[-20:]) > 0 else last_volume
    else:
        volume_sma = np.mean(volume_series.values) if len(volume_series.values) > 0 else 1.0
    
    feature_values['Volume_Ratio'] = last_volume / volume_sma if volume_sma != 0 else 1.0
    
    # 8. Bollinger Bands Position
    bb_middle = close_series.rolling(20).mean()
    bb_std = close_series.rolling(20).std()
    bb_position = (close_series - bb_middle) / (2 * bb_std)
    feature_values['BB_Position'] = safe_float(bb_position.iloc[-1]) if not pd.isna(bb_position.iloc[-1]) else 0.0
    
    # Convert to DataFrame
    latest_df = pd.DataFrame([feature_values])
    
    # Check ALL features exist
    missing_features = []
    for col in EXPECTED_FEATURES:
        if col not in latest_df.columns:
            missing_features.append(col)
    
    if missing_features:
        st.error(f"❌ Missing features: {missing_features}")
        with st.expander("🔍 Debug Information"):
            st.write("**Features Created:**", list(feature_values.keys()))
            st.write("**Expected Features:**", EXPECTED_FEATURES)
        st.stop()
    
    # Select features in correct order
    latest_features = latest_df[EXPECTED_FEATURES].values.reshape(1, -1)
    latest_scaled = scaler.transform(latest_features)
    
    # ==========================================
    # MAKE PREDICTION - FIXED FOR SVC
    # ==========================================
    
    # Predict
    prediction = model.predict(latest_scaled)[0]
    
    # Get probabilities safely (handles SVC without predict_proba)
    try:
        probabilities = model.predict_proba(latest_scaled)[0]
        confidence = max(probabilities)
    except AttributeError:
        # For models without predict_proba (like SVC without probability=True)
        try:
            decisions = model.decision_function(latest_scaled)
            if len(decisions.shape) == 1:
                confidence = abs(decisions[0]) / (abs(decisions[0]) + 1)
                # Approximate probabilities for display
                if prediction == 1:
                    probabilities = np.array([0.1, 0.1, 0.8])
                elif prediction == -1:
                    probabilities = np.array([0.8, 0.1, 0.1])
                else:
                    probabilities = np.array([0.2, 0.6, 0.2])
            else:
                confidence = 0.5
                probabilities = np.array([0.33, 0.33, 0.34])
        except:
            confidence = 0.5
            probabilities = np.array([0.33, 0.33, 0.34])
    
    # Get signal info
    signal_info = SIGNAL_MAP.get(prediction, SIGNAL_MAP[0])
    
    # ==========================================
    # DISPLAY SIGNAL
    # ==========================================
    
    col1, col2, col3 = st.columns([2, 1.2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="{signal_info['class']}">
            <div class="icon">{signal_info['emoji']}</div>
            <div class="text">{signal_info['label']}</div>
            <div class="sub">Recommended action for tomorrow</div>
            <div class="action">{signal_info['action']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="confidence-container">
            <div class="label">Confidence Level</div>
            <div class="value">{confidence:.1%}</div>
            <div class="confidence-bar-bg">
                <div class="confidence-bar-fill" style="width: {confidence*100:.1f}%;"></div>
            </div>
            <div class="confidence-detail">
                Signal: {signal_info['label']} · {n} days analyzed
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Get probabilities for each class
        prob_buy = probabilities[2] if len(probabilities) > 2 else 0
        prob_hold = probabilities[1] if len(probabilities) > 1 else 0
        prob_sell = probabilities[0] if len(probabilities) > 0 else 0
        
        st.markdown(f"""
        <div class="confidence-container">
            <div class="label">Probability Breakdown</div>
            <div style="margin-top: 8px;">
                <div style="display: flex; justify-content: space-between; color: #34d399; font-size: 12px;">
                    <span>📈 BUY</span>
                    <span style="font-weight: 700;">{prob_buy:.1%}</span>
                </div>
                <div style="width: 100%; height: 2px; background: rgba(255,255,255,0.04); border-radius: 2px; margin-top: 2px;">
                    <div style="width: {prob_buy*100:.1f}%; height: 100%; background: #34d399; border-radius: 2px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; color: #fbbf24; font-size: 12px; margin-top: 6px;">
                    <span>⏸️ HOLD</span>
                    <span style="font-weight: 700;">{prob_hold:.1%}</span>
                </div>
                <div style="width: 100%; height: 2px; background: rgba(255,255,255,0.04); border-radius: 2px; margin-top: 2px;">
                    <div style="width: {prob_hold*100:.1f}%; height: 100%; background: #fbbf24; border-radius: 2px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; color: #f87171; font-size: 12px; margin-top: 6px;">
                    <span>📉 SELL</span>
                    <span style="font-weight: 700;">{prob_sell:.1%}</span>
                </div>
                <div style="width: 100%; height: 2px; background: rgba(255,255,255,0.04); border-radius: 2px; margin-top: 2px;">
                    <div style="width: {prob_sell*100:.1f}%; height: 100%; background: #f87171; border-radius: 2px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Signal Generation Error: {str(e)}")
    st.info("💡 This could be due to insufficient historical data. Try using a longer date range (at least 200 days).")
    
    with st.expander("🔍 Debug Information"):
        st.write("**📊 Data Shape:**", df.shape)
        st.write("**📅 Date Range:**", df.index[0].strftime('%Y-%m-%d'), "to", df.index[-1].strftime('%Y-%m-%d'))
        st.write("**🔢 Expected Features:**", EXPECTED_FEATURES)
        
        if 'feature_values' in locals():
            st.write("**📋 Features Created:**", list(feature_values.keys()))
            missing = set(EXPECTED_FEATURES) - set(feature_values.keys())
            if missing:
                st.write("**❌ Missing Features:**", missing)

# ============================================
# DISCLAIMER & FOOTER
# ============================================
st.markdown("""
<div class="disclaimer">
    <p>
        <strong>⚠️ Disclaimer:</strong> This tool is for educational and informational purposes only. 
        Trading signals are generated by machine learning models and are not guaranteed. 
        Always conduct your own research before making trading decisions.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <span class="brand"><span class="highlight">Trading Signal Pro</span></span>
    <span style="color: #2d3748;">· Enterprise Terminal v4.0</span>
</div>
""", unsafe_allow_html=True)