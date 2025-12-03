"""
TikTok Content Performance Prediction System
Main entry point for the Streamlit application
"""
import streamlit as st
from utils.data_processor import get_data_processor
from utils.model_handler import get_model_handler

# Page configuration
st.set_page_config(
    page_title="Beranda", 
    page_icon="🏠",       
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main header
st.title("🎯 Sistem Prediksi Performa Konten TikTok")
st.markdown('<div class="sub-header">Platform Analitik dan Prediksi untuk Content Creator @septianndt</div>', unsafe_allow_html=True)

st.markdown("---")

# Introduction
col1, col2 = st.columns([2, 1])

with col1:
    st.header("👋 Selamat Datang!")

    st.markdown("""
    Sistem ini membantu Anda menganalisis dan memprediksi performa konten TikTok menggunakan:
    - **Machine Learning**: Random Forest Classifier dengan 100 trees
    - **Data Analytics**: Analisis mendalam dari 166 video
    - **Prediksi Real-time**: Prediksi potensi trending untuk konten baru

    ### 🎨 Fitur Utama:

    **1. 📊 Dashboard Analitik**
    - Analisis performa konten secara komprehensif
    - Visualisasi pola engagement dan trending
    - Identifikasi waktu terbaik untuk posting

    **2. 🔮 Prediksi Tunggal**
    - Form input interaktif untuk prediksi individual
    - Confidence score dan analisis feature importance
    - Rekomendasi strategi konten

    **3. 🔧 Data Preprocessing** 
    - Konversi otomatis data mentah dari FreeTikTokScraper
    - Extract 22 features untuk model ML
    - Download file siap prediksi
    - Mendukung upload RAW data

    **4. 📤 Prediksi Massal**
    - Upload CSV untuk batch prediction
    - Perbandingan hasil prediksi vs aktual
    - Export hasil dalam format CSV/Excel
    """)

with col2:
    st.info("""
    **💡 Quick Start**

    **Punya data mentah?**
    1. 🔧 **Preprocessing** - Konversi data RAW
    2. 📤 **Batch Prediction** - Prediksi massal

    **Sudah punya data processed?**
    1. 📊 **Dashboard** - Lihat insights
    2. 🔮 **Prediksi Tunggal** - Test individual
    3. 📤 **Prediksi Massal** - Bulk analysis

    ---

    **📊 Dataset Info**
    - Total Video: 166
    - Periode: 2023-2024
    - Creator: @septianndt
    """)

# Load data for quick stats
@st.cache_data
def load_quick_stats():
    """Load and cache quick statistics"""
    data_processor = get_data_processor()
    return data_processor.get_summary_stats()

try:
    stats = load_quick_stats()

    st.markdown("---")
    st.subheader("📈 Statistik Cepat")

    # Display key metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Video",
            value=f"{stats['total_videos']}"
        )

    with col2:
        st.metric(
            label="Total Tayangan",
            value=f"{stats['total_views']:,.0f}"
        )

    with col3:
        st.metric(
            label="Total Suka",
            value=f"{stats['total_likes']:,.0f}"
        )

    with col4:
        st.metric(
            label="Total Komentar",
            value=f"{stats['total_comments']:,.0f}"
        )

    with col5:
        st.metric(
            label="Avg. Engagement",
            value=f"{stats['avg_engagement_rate']:.2f}%"
        )

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat data: {str(e)}")

st.markdown("---")

# Navigation guide
st.subheader("🧭 Panduan Navigasi")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📊 Analytics Dashboard
    Jelajahi insights mendalam tentang:
    - Performa konten berdasarkan waktu
    - Tipe konten terbaik
    - Pola engagement
    - Top performing videos
    """)
    if st.button("🚀 Buka Dashboard", key="nav_dashboard"):
        st.switch_page("pages/1_📊_Analytics_Dashboard.py")

with col2:
    st.markdown("""
    ### 🔧 Data Preprocessing
    Konversi data mentah TikTok:
    - Upload data dari FreeTikTokScraper
    - Otomatis extract features
    - Download file siap prediksi
    - Langsung ke batch prediction
    """)
    if st.button("🔧 Proses Data", key="nav_preprocessing"):
        st.switch_page("pages/4_🔧_Data_Preprocessing.py")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔮 Prediksi Tunggal
    Prediksi performa untuk satu konten:
    - Input manual fitur video
    - Dapatkan prediksi trending
    - Lihat confidence score
    - Terima rekomendasi
    """)
    if st.button("🎯 Mulai Prediksi", key="nav_prediction"):
        st.switch_page("pages/2_🔮_Prediction.py")

with col2:
    st.markdown("""
    ### 📤 Prediksi Massal
    Upload CSV untuk prediksi batch:
    - Prediksi banyak video sekaligus
    - Bandingkan hasil
    - Download report
    - Analisis performa
    """)
    if st.button("📥 Upload CSV", key="nav_batch"):
        st.switch_page("pages/3_📤_Batch_Prediction.py")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>TikTok Content Performance Prediction System</strong></p>
    <p>Tugas Akhir Skripsi - UPN Veteran Jakarta</p>
    <p>Developed with Streamlit • Powered by Random Forest Classifier</p>
</div>
""", unsafe_allow_html=True)
