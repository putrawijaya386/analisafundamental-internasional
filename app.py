import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from io import StringIO

# Konfigurasi halaman
st.set_page_config(
    page_title="Global Stock Fundamental Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan yang lebih menarik
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .country-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: white;
        transition: transform 0.3s;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .country-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .country-flag {
        font-size: 48px;
        margin-bottom: 10px;
    }
    .country-name {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .positive {
        color: #00C853;
        font-weight: bold;
    }
    .negative {
        color: #FF5252;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F0F2F6;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E86AB;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header aplikasi
st.markdown('<h1 class="main-header">🌍 Global Stock Fundamental Analyzer</h1>', unsafe_allow_html=True)
st.markdown("### Monitor fundamental saham seluruh dunia secara real-time")

# Dictionary negara dan bendera (emoji)
countries = {
    "USA": {"name": "Amerika Serikat", "flag": "🇺🇸", "suffix": ""},
    "Indonesia": {"name": "Indonesia", "flag": "🇮🇩", "suffix": ".JK"},
    "UK": {"name": "Inggris", "flag": "🇬🇧", "suffix": ".L"},
    "Japan": {"name": "Jepang", "flag": "🇯🇵", "suffix": ".T"},
    "China": {"name": "China", "flag": "🇨🇳", "suffix": ".SS"},
    "Hong Kong": {"name": "Hong Kong", "flag": "🇭🇰", "suffix": ".HK"},
    "India": {"name": "India", "flag": "🇮🇳", "suffix": ".NS"},
    "Germany": {"name": "Jerman", "flag": "🇩🇪", "suffix": ".DE"},
    "France": {"name": "Prancis", "flag": "🇫🇷", "suffix": ".PA"},
    "Canada": {"name": "Kanada", "flag": "🇨🇦", "suffix": ".TO"},
    "Australia": {"name": "Australia", "flag": "🇦🇺", "suffix": ".AX"},
    "Singapore": {"name": "Singapura", "flag": "🇸🇬", "suffix": ".SI"},
    "South Korea": {"name": "Korea Selatan", "flag": "🇰🇷", "suffix": ".KS"},
    "Brazil": {"name": "Brazil", "flag": "🇧🇷", "suffix": ".SA"},
    "Russia": {"name": "Rusia", "flag": "🇷🇺", "suffix": ".ME"},
}

# Sidebar untuk pencarian saham
with st.sidebar:
    st.markdown("## 🔍 Cari Saham")
    
    # Input kode saham
    stock_input = st.text_input(
        "Masukkan kode saham (contoh: AAPL, BBCA.JK, TSLA):",
        placeholder="AAPL atau BBCA.JK",
        help="Masukkan kode saham sesuai pasar. Untuk Indonesia tambahkan .JK"
    )
    
    st.markdown("---")
    st.markdown("## 🌐 Pilih Negara")
    st.markdown("Klik negara untuk melihat daftar sahamnya")
    
    # Tampilkan bendera negara dalam grid 3 kolom
    cols = st.columns(3)
    selected_country = None
    
    for idx, (country_code, country_info) in enumerate(countries.items()):
        with cols[idx % 3]:
            if st.button(
                f"{country_info['flag']}\n\n{country_info['name']}",
                key=f"country_{country_code}",
                use_container_width=True
            ):
                selected_country = country_code

# Fungsi untuk mendapatkan data saham populer berdasarkan negara
@st.cache_data(ttl=3600)  # Cache untuk 1 jam
def get_popular_stocks(country_code):
    """Mendapatkan daftar saham populer berdasarkan negara"""
    popular_stocks = {
        "USA": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "BRK-B"],
        "Indonesia": ["BBCA.JK", "TLKM.JK", "ASII.JK", "UNVR.JK", "ICBP.JK"],
        "UK": ["HSBA.L", "BP.L", "GSK.L", "RIO.L", "ULVR.L"],
        "Japan": ["7203.T", "9984.T", "6861.T", "9433.T", "8306.T"],
        "China": ["601318.SS", "600519.SS", "601857.SS", "600036.SS"],
        "Hong Kong": ["0700.HK", "0941.HK", "0005.HK", "1299.HK"],
        "India": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"],
        "Germany": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE"],
        "France": ["MC.PA", "SAN.PA", "AIR.PA", "OR.PA"],
        "Canada": ["RY.TO", "TD.TO", "ENB.TO", "CNR.TO"],
        "Australia": ["CBA.AX", "BHP.AX", "WBC.AX", "NAB.AX"],
        "Singapore": ["D05.SI", "U11.SI", "O39.SI", "Z74.SI"],
        "South Korea": ["005930.KS", "000660.KS", "035420.KS", "051910.KS"],
        "Brazil": ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA"],
        "Russia": ["GAZP.ME", "SBER.ME", "LKOH.ME", "ROSN.ME"],
    }
    return popular_stocks.get(country_code, [])

# Fungsi untuk mendapatkan data fundamental
@st.cache_data(ttl=300)  # Cache untuk 5 menit
def get_fundamental_data(ticker_symbol):
    """Mendapatkan data fundamental dari yfinance"""
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # Info dasar perusahaan
        info = stock.info
        
        # Data laporan keuangan
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        
        # Data historis untuk grafik
        history = stock.history(period="5y")
        
        return {
            "info": info,
            "financials": financials,
            "balance_sheet": balance_sheet,
            "cashflow": cashflow,
            "history": history
        }
    except Exception as e:
        st.error(f"Error mendapatkan data untuk {ticker_symbol}: {str(e)}")
        return None

# Fungsi untuk format currency
def format_currency(value):
    """Format nilai menjadi format currency yang mudah dibaca"""
    if pd.isna(value):
        return "N/A"
    
    if abs(value) >= 1e12:
        return f"${value/1e12:.2f}T"
    elif abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"

# Main content
if selected_country:
    st.markdown(f'<h2 class="sub-header">{countries[selected_country]["flag"]} Saham Populer di {countries[selected_country]["name"]}</h2>', unsafe_allow_html=True)
    
    # Tampilkan daftar saham populer untuk negara yang dipilih
    popular_stocks = get_popular_stocks(selected_country)
    
    cols = st.columns(4)
    selected_stock = None
    
    for idx, stock_code in enumerate(popular_stocks):
        with cols[idx % 4]:
            if st.button(stock_code, key=f"stock_{stock_code}", use_container_width=True):
                selected_stock = stock_code
    
    if selected_stock:
        stock_input = selected_stock

# Proses pencarian saham
if stock_input:
    st.markdown(f'<h2 class="sub-header">📊 Analisis Fundamental: {stock_input}</h2>', unsafe_allow_html=True)
    
    with st.spinner("Mengambil data fundamental..."):
        data = get_fundamental_data(stock_input)
    
    if data:
        info = data["info"]
        financials = data["financials"]
        balance_sheet = data["balance_sheet"]
        cashflow = data["cashflow"]
        
        # Tampilkan informasi dasar perusahaan
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📈 Informasi Perusahaan")
            st.write(f"**Nama:** {info.get('longName', 'N/A')}")
            st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
            st.write(f"**Industri:** {info.get('industry', 'N/A')}")
            st.write(f"**Negara:** {info.get('country', 'N/A')}")
        
        with col2:
            st.markdown("### 💰 Market Data")
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            previous_close = info.get('previousClose', 'N/A')
            
            if isinstance(current_price, (int, float)) and isinstance(previous_close, (int, float)):
                change = ((current_price - previous_close) / previous_close) * 100
                change_class = "positive" if change >= 0 else "negative"
                st.write(f"**Harga:** ${current_price:.2f}")
                st.markdown(f"**Perubahan:** <span class='{change_class}'>{change:+.2f}%</span>", unsafe_allow_html=True)
            else:
                st.write(f"**Harga:** {current_price}")
            
            st.write(f"**Market Cap:** {format_currency(info.get('marketCap', 'N/A'))}")
            st.write(f"**Volume:** {format_currency(info.get('volume', 'N/A'))}")
        
        with col3:
            st.markdown("### 🏆 Fundamental")
            st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
            st.write(f"**EPS:** ${info.get('trailingEps', 'N/A')}")
            st.write(f"**Dividend Yield:** {info.get('dividendYield', 'N/A')}")
            st.write(f"**Beta:** {info.get('beta', 'N/A')}")
        
        # Tab untuk laporan keuangan detail
        tabs = st.tabs(["📋 Laporan Laba Rugi", "🏛️ Neraca", "💵 Arus Kas", "📊 Grafik Laba Bersih"])
        
        with tabs[0]:  # Laporan Laba Rugi
            st.markdown("### Laporan Laba Rugi (Income Statement)")
            if not financials.empty:
                # Ambil data 5 tahun terakhir
                recent_years = financials.columns[:5]
                income_df = financials[recent_years].T
                
                # Pilih metrik penting
                important_metrics = [
                    'Total Revenue', 'Gross Profit', 'Operating Income',
                    'Net Income', 'EBITDA', 'Basic EPS'
                ]
                
                # Filter hanya metrik yang tersedia
                available_metrics = [m for m in important_metrics if m in financials.index]
                display_df = financials.loc[available_metrics, recent_years]
                
                # Format nilai
                def format_values(x):
                    try:
                        return format_currency(x)
                    except:
                        return str(x)
                
                styled_df = display_df.applymap(format_values)
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.warning("Data laporan laba rugi tidak tersedia")
        
        with tabs[1]:  # Neraca
            st.markdown("### Neraca (Balance Sheet)")
            if not balance_sheet.empty:
                recent_years = balance_sheet.columns[:5]
                
                # Kelompokkan aset, liabilitas, dan ekuitas
                asset_items = ['Total Assets', 'Current Assets', 'Cash And Cash Equivalents']
                liability_items = ['Total Liabilities Net Minority Interest', 'Current Liabilities', 'Long Term Debt']
                equity_items = ['Stockholders Equity']
                
                all_items = asset_items + liability_items + equity_items
                available_items = [m for m in all_items if m in balance_sheet.index]
                
                if available_items:
                    display_df = balance_sheet.loc[available_items, recent_years]
                    styled_df = display_df.applymap(format_currency)
                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.warning("Item neraca tidak ditemukan")
            else:
                st.warning("Data neraca tidak tersedia")
        
        with tabs[2]:  # Arus Kas
            st.markdown("### Laporan Arus Kas (Cash Flow)")
            if not cashflow.empty:
                recent_years = cashflow.columns[:5]
                
                cashflow_items = [
                    'Operating Cash Flow', 'Investing Cash Flow',
                    'Financing Cash Flow', 'Free Cash Flow'
                ]
                
                available_items = [m for m in cashflow_items if m in cashflow.index]
                
                if available_items:
                    display_df = cashflow.loc[available_items, recent_years]
                    styled_df = display_df.applymap(format_currency)
                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.warning("Item arus kas tidak ditemukan")
            else:
                st.warning("Data arus kas tidak tersedia")
        
        with tabs[3]:  # Grafik Laba Bersih
            st.markdown("### 📊 Grafik Laba Bersih 5 Tahun Terakhir")
            
            if not financials.empty and 'Net Income' in financials.index:
                # Ambil data laba bersih 5 tahun terakhir
                net_income = financials.loc['Net Income']
                
                if len(net_income) > 0:
                    # Konversi index tahun menjadi string
                    years = [str(col.year) if hasattr(col, 'year') else str(col) for col in net_income.index[:5]]
                    values = net_income.values[:5]
                    
                    # Buat grafik batang
                    fig = go.Figure(data=[
                        go.Bar(
                            x=years,
                            y=values,
                            marker_color=['#00C853' if v >= 0 else '#FF5252' for v in values],
                            text=[format_currency(v) for v in values],
                            textposition='auto',
                        )
                    ])
                    
                    fig.update_layout(
                        title='Laba Bersih (Net Income) 5 Tahun Terakhir',
                        xaxis_title='Tahun',
                        yaxis_title='Laba Bersih (USD)',
                        template='plotly_white',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tampilkan analisis trend
                    if len(values) >= 2:
                        trend = "📈 Meningkat" if values[-1] > values[0] else "📉 Menurun"
                        st.info(f"**Trend 5 Tahun:** {trend}")
                else:
                    st.warning("Data laba bersih tidak cukup untuk grafik")
            else:
                st.warning("Data laba bersih tidak tersedia untuk grafik")
        
        # Key Metrics Dashboard
        st.markdown("---")
        st.markdown("### 📊 Dashboard Metrik Kunci")
        
        # Tampilkan metrik penting dalam cards
        metrics_cols = st.columns(4)
        
        metric_data = [
            ("Market Cap", info.get('marketCap'), format_currency),
            ("P/E Ratio", info.get('trailingPE'), lambda x: f"{x:.2f}"),
            ("ROE", info.get('returnOnEquity'), lambda x: f"{x*100:.2f}%"),
            ("Debt to Equity", info.get('debtToEquity'), lambda x: f"{x:.2f}"),
            ("Current Ratio", info.get('currentRatio'), lambda x: f"{x:.2f}"),
            ("Profit Margin", info.get('profitMargins'), lambda x: f"{x*100:.2f}%"),
            ("Revenue Growth", info.get('revenueGrowth'), lambda x: f"{x*100:.2f}%"),
            ("Dividend Yield", info.get('dividendYield'), lambda x: f"{x*100:.2f}%" if x else "N/A"),
        ]
        
        for idx, (name, value, formatter) in enumerate(metric_data[:8]):
            with metrics_cols[idx % 4]:
                if value and not pd.isna(value):
                    try:
                        formatted_value = formatter(value)
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>{name}</h4>
                            <h3>{formatted_value}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    except:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>{name}</h4>
                            <h3>N/A</h3>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{name}</h4>
                        <h3>N/A</h3>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Disclaimer
        st.markdown("---")
        st.markdown("""
        ### ⚠️ Disclaimer
        Data yang ditampilkan diambil dari sumber publik dan mungkin mengalami penundaan.
        Informasi ini hanya untuk tujuan edukasi dan analisis, bukan rekomendasi investasi.
        Selalu lakukan penelitian sendiri sebelum membuat keputusan investasi.
        """)
        
else:
    # Tampilan awal - grid negara
    st.markdown('<h2 class="sub-header">🌐 Pilih Negara untuk Melihat Saham</h2>', unsafe_allow_html=True)
    
    # Tampilkan grid negara dengan bendera
    cols = st.columns(4)
    
    for idx, (country_code, country_info) in enumerate(countries.items()):
        with cols[idx % 4]:
            if st.button(
                f"""
                <div style='text-align: center; padding: 20px;'>
                    <div style='font-size: 48px; margin-bottom: 10px;'>{country_info['flag']}</div>
                    <div style='font-weight: bold; font-size: 16px;'>{country_info['name']}</div>
                </div>
                """,
                key=f"main_country_{country_code}",
                help=f"Klik untuk melihat saham di {country_info['name']}"
            ):
                st.session_state.selected_country = country_code
                st.rerun()
    
    # Informasi cara penggunaan
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Cara Menggunakan:")
        st.markdown("""
        1. **Pilih negara** dari grid di atas
        2. **Pilih saham** dari daftar yang muncul
        3. **Atau langsung ketik** kode saham di sidebar
        4. **Analisis fundamental** akan ditampilkan secara otomatis
        """)
    
    with col2:
        st.markdown("### 📋 Fitur Utama:")
        st.markdown("""
        ✅ **Real-time data** fundamental
        ✅ **Laporan keuangan** lengkap
        ✅ **Grafik laba bersih** 5 tahun
        ✅ **Analisis 15+ negara** global
        ✅ **Tampilan mobile-friendly**
        ✅ **Tanpa login** required
        """)
    
    # Contoh kode saham
    st.markdown("### 💡 Contoh Kode Saham:")
    example_cols = st.columns(5)
    examples = [
        ("🇺🇸 Apple", "AAPL"),
        ("🇮🇩 Bank BCA", "BBCA.JK"),
        ("🇯🇵 Toyota", "7203.T"),
        ("🇭🇰 Tencent", "0700.HK"),
        ("🇬🇧 HSBC", "HSBA.L")
    ]
    
    for idx, (name, code) in enumerate(examples):
        with example_cols[idx]:
            if st.button(
                f"**{name}**\n\n`{code}`",
                key=f"example_{idx}",
                use_container_width=True
            ):
                stock_input = code
                st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>📊 Global Stock Fundamental Analyzer v1.0 • Data update: {}</p>
        <p>⚠️ Informasi ini bukan saran investasi. Lakukan riset mandiri sebelum berinvestasi.</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    unsafe_allow_html=True
)
