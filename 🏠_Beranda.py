"""
Sistem Prediksi Performa Konten TikTok
Titik masuk utama untuk aplikasi Streamlit
"""
import streamlit as st
from utils.data_processor import get_data_processor
# Catatan: utils.model_handler mungkin tidak digunakan langsung di sini jika hanya menampilkan statistik data
# tapi tetap kita import untuk konsistensi jika nanti dibutuhkan inisialisasi awal.
from utils.model_handler import get_model_handler 

# Konfigurasi Halaman
st.set_page_config(
    page_title="Beranda", 
    page_icon="🏠",       
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Data Processor (Singleton)
# Ini memastikan data terbaru termuat saat aplikasi dibuka
dp = get_data_processor()
dp.load_data() 

# --- HEADER UTAMA ---
st.title("🎯 Sistem Prediksi Performa Konten TikTok")
st.markdown('<div class="sub-header">Platform Analitik dan Prediksi untuk Kreator Konten (Multi-Influencer)</div>', unsafe_allow_html=True)

st.markdown("---")

# --- PENDAHULUAN ---
col1, col2 = st.columns([2, 1])

with col1:
    st.header("👋 Selamat Datang!")

    st.markdown("""
    Sistem ini membantu Anda menganalisis dan memprediksi performa konten TikTok menggunakan:
    - **Machine Learning**: *Random Forest Classifier*
    - **Analisis Data**: Analisis mendalam dari kumpulan data video TikTok
    - **Prediksi *Real-time***: Prediksi potensi *trending* untuk konten baru

    ### 🎨 Fitur Utama:

    **1. 📊 Dasbor Analitik (*Analytics Dashboard*)**
    - Analisis performa konten secara komprehensif dari berbagai *influencer*.
    - Visualisasi pola keterlibatan (*engagement*) dan tren.
    - Peringkat performa (*Leaderboard*) kreator konten.

    **2. 🔮 Prediksi Tunggal**
    - Formulir interaktif untuk prediksi satu video.
    - Skor kepercayaan (*confidence score*) dan analisis kepentingan fitur.
    - Rekomendasi strategi konten berdasarkan hasil prediksi.

    **3. 📝 Input Data Baru**
    - Tambahkan data video baru secara manual untuk memperkaya basis data.
    - Pembaruan sistem secara langsung (*real-time*).

    **4. 🔧 Pra-pemrosesan Data (*Data Preprocessing*)** - Konversi otomatis data mentah.
    - Ekstraksi fitur untuk model *Machine Learning*.
    - Unduh data siap pakai.

    **5. 📤 Prediksi Massal**
    - Unggah CSV untuk prediksi banyak video sekaligus.
    - Perbandingan hasil prediksi vs aktual.
    """)

with col2:
    st.info("""
    **💡 Mulai Cepat (*Quick Start*)**

    **Ingin Menambah Data?**
    1. 📝 **Input Data Baru** - Masukkan data manual
    2. 🔧 **Pra-pemrosesan** - Jika punya data mentah

    **Ingin Menganalisis?**
    1. 📊 **Dasbor Analitik** - Lihat wawasan data
    2. 🔮 **Prediksi Tunggal** - Cek potensi video
    3. 📤 **Prediksi Massal** - Analisis *batch*

    ---

    **📊 Info Dataset Saat Ini**
    Data diambil secara *real-time* dari sistem:
    """)
    
    # Menampilkan info dataset dinamis
    total_influencers = len(dp.get_unique_authors())
    total_vids = len(dp.df) if dp.df is not None else 0
    st.write(f"- **Total Video:** {total_vids}")
    st.write(f"- **Total Influencer:** {total_influencers}")

# --- STATISTIK CEPAT ---
st.markdown("---")
st.subheader("📈 Statistik Cepat")

# Mengambil statistik terbaru dari Data Processor
stats = dp.get_summary_stats()

if stats:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Video",
            value=f"{stats.get('total_videos', 0)}"
        )

    with col2:
        st.metric(
            label="Total Tayangan",
            value=f"{stats.get('total_views', 0):,.0f}"
        )

    with col3:
        st.metric(
            label="Total Suka",
            value=f"{stats.get('total_likes', 0):,.0f}"
        )

    with col4:
        st.metric(
            label="Total Komentar",
            value=f"{stats.get('total_comments', 0):,.0f}"
        )

    with col5:
        avg_er = stats.get('avg_engagement_rate', 0)
        st.metric(
            label="Rerata *Engagement*",
            value=f"{avg_er:.2f}%"
        )
else:
    st.error("Gagal memuat statistik. Pastikan dataset tersedia.")

st.markdown("---")

# --- PANDUAN NAVIGASI ---
st.subheader("🧭 Panduan Navigasi")

# Baris 1: Analitik & Prediksi
c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    ### 📊 Dasbor Analitik
    Jelajahi wawasan mendalam tentang:
    - Performa konten berdasarkan waktu & kategori
    - Perbandingan antar *influencer*
    - Pola keterlibatan (*engagement*)
    """)
    # Perbaiki path sesuai struktur folder Anda (gunakan nama file yang benar)
    if st.button("🚀 Buka Dasbor", key="nav_dashboard"):
        st.switch_page("pages/1_📊_Dashboard_Analitik.py") 

with c2:
    st.markdown("""
    ### 🔮 Prediksi Tunggal
    Prediksi performa untuk satu konten:
    - Input manual fitur video
    - Dapatkan prediksi *Trending* / Tidak
    - Lihat faktor penentu
    """)
    if st.button("🎯 Mulai Prediksi", key="nav_prediction"):
        st.switch_page("pages/2_🔮_Prediksi_Tunggal.py")

# Baris 2: Input & Tools
c3, c4 = st.columns(2)

with c3:
    st.markdown("""
    ### 📝 Input Data Baru
    Tambahkan data manual:
    - Isi formulir data video
    - Simpan ke basis data
    - Perbarui analitik otomatis
    """)
    # Pastikan file pages/5_📝_Input_Data_Baru.py sudah dibuat sesuai sesi sebelumnya
    if st.button("✍️ Input Data", key="nav_input"):
        st.switch_page("pages/5_📝_Input_Data_Baru.py")

with c4:
    st.markdown("""
    ### 🔧 & 📤 Fitur Lanjutan
    Alat bantu pengolahan data:
    - **Pra-pemrosesan Data**: Bersihkan data mentah
    - **Prediksi Massal**: Unggah CSV untuk analisis banyak
    """)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔧 Preproses", key="nav_preprocessing"):
            st.switch_page("pages/3_🔧_Preproses_Data.py")
    with col_b:
        if st.button("📥 Massal", key="nav_batch"):
            st.switch_page("pages/4_📤_Prediksi_Massal.py")

st.markdown("---")

# --- FOOTER ---
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Sistem Prediksi Performa Konten TikTok</strong></p>
    <p>Tugas Akhir Skripsi - UPN Veteran Jakarta</p>
    <p>Dikembangkan dengan Streamlit • Didukung oleh <em>Random Forest Classifier</em></p>
    <p>© 2025 Nayandra Agastia Putra</p>
</div>
""", unsafe_allow_html=True)