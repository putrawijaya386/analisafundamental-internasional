import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.title("📈 Simple Stock Analyzer")

# Input saham
ticker = st.text_input("Masukkan kode saham (contoh: AAPL, BBCA.JK):", "AAPL")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Informasi Perusahaan")
            st.write(f"Nama: {info.get('longName', 'N/A')}")
            st.write(f"Sektor: {info.get('sector', 'N/A')}")
            st.write(f"Harga: ${info.get('currentPrice', 'N/A')}")
            
        with col2:
            st.subheader("Fundamental")
            st.write(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")
            st.write(f"Market Cap: ${info.get('marketCap', 'N/A'):,}")
            st.write(f"Dividend Yield: {info.get('dividendYield', 'N/A')}")
        
        st.success("Data berhasil diambil!")
        
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Coba kode saham yang berbeda")
