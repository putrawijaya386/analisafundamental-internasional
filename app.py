import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Saham Global",
    page_icon="📈",
    layout="wide"
)

# Judul Aplikasi
st.title("📊 ANALISIS FUNDAMENTAL SAHAM GLOBAL")
st.markdown("**Monitor saham seluruh dunia secara real-time**")

# Daftar negara dan kode saham contoh
countries = {
    "🇺🇸 USA": ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN"],
    "🇮🇩 Indonesia": ["BBCA.JK", "TLKM.JK", "ASII.JK", "UNVR.JK"],
    "🇯🇵 Jepang": ["7203.T", "9984.T", "9433.T"],
    "🇨🇳 China": ["0700.HK", "BABA", "JD"],
    "🇸🇬 Singapura": ["D05.SI", "U11.SI"],
    "🇦🇺 Australia": ["CBA.AX", "BHP.AX"],
    "🇰🇷 Korea": ["005930.KS", "000660.KS"],
}

# SIDEBAR - PENCARIAN
with st.sidebar:
    st.header("🔍 CARI SAHAM")
    
    # Pilihan cepat
    st.subheader("🌎 PILIH NEGARA")
    selected_country = st.selectbox(
        "Pilih negara:",
        list(countries.keys())
    )
    
    if selected_country:
        stocks_list = countries[selected_country]
        selected_stock = st.selectbox(
            "Pilih saham:",
            stocks_list
        )
    
    st.subheader("🔤 MASUKKAN KODE SAHAM")
    custom_stock = st.text_input(
        "Atau ketik kode saham manual:",
        placeholder="Contoh: AAPL, BBCA.JK"
    )
    
    st.markdown("---")
    st.markdown("**💡 Contoh kode saham:**")
    st.code("AAPL = Apple Inc (USA)\nBBCA.JK = Bank BCA (Indonesia)\n7203.T = Toyota (Jepang)")
    
    st.markdown("---")
    st.markdown("**📱 Dibuat dengan Streamlit**")

# Tentukan saham yang akan dianalisis
stock_to_analyze = None
if custom_stock:
    stock_to_analyze = custom_stock.upper()
elif 'selected_stock' in locals():
    stock_to_analyze = selected_stock

# JIKA ADA SAHAM YANG DIPILIH
if stock_to_analyze:
    st.header(f"📈 ANALISIS: {stock_to_analyze}")
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Ambil data
        status_text.text("🔍 Mengambil data saham...")
        progress_bar.progress(25)
        
        stock = yf.Ticker(stock_to_analyze)
        
        # Step 2: Info perusahaan
        status_text.text("📋 Memuat info perusahaan...")
        progress_bar.progress(50)
        
        info = stock.info
        
        # Tampilkan data dasar
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏢 INFO PERUSAHAAN")
            st.write(f"**Nama:** {info.get('longName', info.get('shortName', 'Tidak Tersedia'))}")
            st.write(f"**Sektor:** {info.get('sector', 'Tidak Tersedia')}")
            st.write(f"**Industri:** {info.get('industry', 'Tidak Tersedia')}")
            st.write(f"**Negara:** {info.get('country', 'Tidak Tersedia')}")
            
            # Market data
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            if isinstance(current_price, (int, float)):
                st.metric("💰 **Harga Saat Ini**", f"${current_price:.2f}")
        
        with col2:
            st.subheader("📊 FUNDAMENTAL")
            
            # Data fundamental
            pe_ratio = info.get('trailingPE', 'N/A')
            market_cap = info.get('marketCap', 'N/A')
            
            if isinstance(market_cap, (int, float)):
                if market_cap >= 1e12:
                    market_cap_display = f"${market_cap/1e12:.2f} T"
                elif market_cap >= 1e9:
                    market_cap_display = f"${market_cap/1e9:.2f} B"
                elif market_cap >= 1e6:
                    market_cap_display = f"${market_cap/1e6:.2f} M"
                else:
                    market_cap_display = f"${market_cap:,.2f}"
            else:
                market_cap_display = "N/A"
            
            st.metric("🏦 **Market Cap**", market_cap_display)
            st.metric("📐 **P/E Ratio**", f"{pe_ratio}" if isinstance(pe_ratio, (int, float)) else "N/A")
            
            # Dividend Yield
            div_yield = info.get('dividendYield', 'N/A')
            if isinstance(div_yield, (int, float)):
                st.metric("🎯 **Dividend Yield**", f"{div_yield*100:.2f}%")
            else:
                st.metric("🎯 **Dividend Yield**", "N/A")
        
        # Step 3: Data keuangan
        status_text.text("💵 Memuat laporan keuangan...")
        progress_bar.progress(75)
        
        # Buat tabs untuk laporan keuangan
        tab1, tab2, tab3 = st.tabs(["📋 LAPORAN LABA RUGI", "🏛️ NERACA", "📊 GRAFIK"])
        
        with tab1:
            st.subheader("Laporan Laba Rugi")
            try:
                financials = stock.financials
                if not financials.empty:
                    # Ambil metrik penting
                    metrics = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income']
                    
                    # Filter yang tersedia
                    available_metrics = [m for m in metrics if m in financials.index]
                    
                    if available_metrics:
                        # Ambil 3 tahun terakhir
                        years_to_show = min(3, len(financials.columns))
                        display_data = financials.loc[available_metrics, :years_to_show]
                        
                        # Format angka
                        def format_num(x):
                            if isinstance(x, (int, float)):
                                if abs(x) >= 1e9:
                                    return f"${x/1e9:.2f}B"
                                elif abs(x) >= 1e6:
                                    return f"${x/1e6:.2f}M"
                                else:
                                    return f"${x:,.2f}"
                            return "N/A"
                        
                        formatted_df = display_data.applymap(format_num)
                        st.dataframe(formatted_df)
                    else:
                        st.info("Data laba rugi terbatas")
                else:
                    st.warning("Data laba rugi tidak tersedia")
            except:
                st.warning("Tidak dapat memuat data laba rugi")
        
        with tab2:
            st.subheader("Neraca Keuangan")
            try:
                balance_sheet = stock.balance_sheet
                if not balance_sheet.empty:
                    # Ambil metrik penting
                    metrics = ['Total Assets', 'Total Liabilities Net Minority Interest', 'Total Equity Gross Minority Interest']
                    
                    available_metrics = [m for m in metrics if m in balance_sheet.index]
                    
                    if available_metrics:
                        years_to_show = min(3, len(balance_sheet.columns))
                        display_data = balance_sheet.loc[available_metrics, :years_to_show]
                        
                        def format_num(x):
                            if isinstance(x, (int, float)):
                                if abs(x) >= 1e9:
                                    return f"${x/1e9:.2f}B"
                                elif abs(x) >= 1e6:
                                    return f"${x/1e6:.2f}M"
                                else:
                                    return f"${x:,.2f}"
                            return "N/A"
                        
                        formatted_df = display_data.applymap(format_num)
                        st.dataframe(formatted_df)
                    else:
                        st.info("Data neraca terbatas")
                else:
                    st.warning("Data neraca tidak tersedia")
            except:
                st.warning("Tidak dapat memuat data neraca")
        
        with tab3:
            st.subheader("Grafik Harga 1 Tahun")
            try:
                # Ambil data historis
                hist_data = stock.history(period="1y")
                
                if not hist_data.empty and 'Close' in hist_data.columns:
                    # Buat grafik
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['Close'],
                        mode='lines',
                        name='Harga',
                        line=dict(color='#2E86AB', width=2)
                    ))
                    
                    fig.update_layout(
                        title=f'Perjalanan Harga {stock_to_analyze} (1 Tahun)',
                        xaxis_title='Tanggal',
                        yaxis_title='Harga (USD)',
                        template='plotly_white',
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tampilkan data statistik
                    if len(hist_data) > 0:
                        current_price = hist_data['Close'].iloc[-1]
                        min_price = hist_data['Close'].min()
                        max_price = hist_data['Close'].max()
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("💰 Harga Sekarang", f"${current_price:.2f}")
                        col2.metric("📉 Terendah", f"${min_price:.2f}")
                        col3.metric("📈 Tertinggi", f"${max_price:.2f}")
                else:
                    st.warning("Data historis tidak tersedia")
            except:
                st.warning("Tidak dapat membuat grafik")
        
        # Step 4: Selesai
        status_text.text("✅ Analisis selesai!")
        progress_bar.progress(100)
        
        # INFO PERINGATAN
        st.markdown("---")
        st.info("""
        **⚠️ PERHATIAN:**
        - Data mungkin delay 15-20 menit
        - Informasi ini untuk edukasi, bukan rekomendasi investasi
        - Selalu lakukan riset mandiri sebelum investasi
        """)
        
        # Tombol refresh
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
    except Exception as e:
        st.error(f"❌ ERROR: {str(e)}")
        st.info("""
        **Solusi masalah:**
        1. Pastikan kode saham benar (contoh: AAPL, BBCA.JK)
        2. Periksa koneksi internet
        3. Coba saham dari negara lain
        4. Refresh halaman
        """)
        
        # Tombol untuk kembali
        if st.button("🔙 Kembali ke Pencarian"):
            st.rerun()

# JIKA BELUM ADA SAHAM YANG DIPILIH
else:
    st.header("🎯 CARA MENGGUNAKAN")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📱 **Langkah-langkah:**
        1. **Pilih negara** di sidebar
        2. **Pilih saham** dari daftar
        3. **Atau ketik** kode saham manual
        4. **Lihat analisis** yang muncul
        
        ### 🌍 **Negara Tersedia:**
        - Amerika Serikat 🇺🇸
        - Indonesia 🇮🇩
        - Jepang 🇯🇵
        - China 🇨🇳
        - Singapura 🇸🇬
        - Australia 🇦🇺
        - Korea Selatan 🇰🇷
        """)
    
    with col2:
        st.markdown("""
        ### 📊 **Data yang Disediakan:**
        - ✅ Info perusahaan
        - ✅ Harga saham real-time
        - ✅ Market cap & P/E ratio
        - ✅ Laporan laba rugi
        - ✅ Neraca keuangan
        - ✅ Grafik harga 1 tahun
        
        ### ⚡ **Fitur:**
        - Real-time data
        - Mobile-friendly
        - Tanpa login
        - Gratis 100%
        """)
    
    st.markdown("---")
    
    # Contoh analisis cepat
    st.subheader("🚀 CONTOH ANALISIS CEPAT")
    
    quick_cols = st.columns(4)
    example_stocks = [
        ("AAPL", "Apple Inc"),
        ("GOOGL", "Google"),
        ("BBCA.JK", "Bank BCA"),
        ("TLKM.JK", "Telkom Indonesia")
    ]
    
    for idx, (code, name) in enumerate(example_stocks):
        with quick_cols[idx]:
            if st.button(f"**{code}**\n{name}", use_container_width=True):
                stock_to_analyze = code
                st.rerun()
    
    st.markdown("---")
    
    # Statistik aplikasi
    st.markdown(f"""
    **📅 Terakhir update:** {datetime.now().strftime("%d %B %Y %H:%M")}
    **🌐 Status:** Online
    **📈 Jumlah negara:** {len(countries)}
    **💼 Contoh saham:** {sum(len(v) for v in countries.values())}
    """)

# FOOTER
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>📊 <b>Global Stock Analyzer</b> | Dibuat dengan Streamlit & Python</p>
    <p>⚠️ Data dari Yahoo Finance | Bukan saran investasi</p>
    </div>
    """,
    unsafe_allow_html=True
            )
