"""
Analytics Dashboard Page
Comprehensive analytics and insights for TikTok content performance
(Updated: Multi-Influencer Support & Leaderboard & Auto-Reload)
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# --- MEKANISME RELOAD OTOMATIS (UPDATE PENTING) ---
# Kode ini mendeteksi sinyal dari halaman Input Data Baru
if "data_changed" in st.session_state and st.session_state["data_changed"]:
    st.cache_data.clear()  # Hapus cache memori agar data baru terbaca
    st.session_state["data_changed"] = False # Reset sinyal
    st.rerun() # Refresh halaman

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_processor import get_data_processor
from utils.visualizations import *

# Page config
st.set_page_config(
    page_title="Dashboard Analitik - Sistem Prediksi TikTok",
    page_icon="📊",
    layout="wide"
)

# --- DEBUGGING MODE (Bisa dihapus nanti) ---
# st.warning("⚠️ DEBUG MODE: Menampilkan 5 Data Terakhir di Database")
# try:
#     df_debug = pd.read_csv('data/dataset_tiktok.csv')
#     st.dataframe(df_debug.tail(5)) 
# except Exception as e:
#     st.error(f"Gagal membaca file: {e}")
# -------------------------------------------

# Load data
@st.cache_data(ttl=0) # TTL=0 agar tidak cache terlalu lama (UPDATE)
def load_all_data():
    """Load and cache all data"""
    dp = get_data_processor()
    dp.load_data() # Paksa baca ulang CSV terbaru
    
    return {
        'dp_instance': dp, # Kita butuh objek ini untuk akses fungsi helper
        'raw_data': dp.df,
        'stats': dp.get_summary_stats(),
        'perf_by_day': dp.get_performance_by_day(),
        'perf_by_hour': dp.get_performance_by_hour(),
        'content_type_perf': dp.get_content_type_performance(),
        'audio_type_perf': dp.get_audio_type_performance(),
        'top_videos': dp.get_top_videos(n=10),
        'correlation': dp.get_correlation_matrix()
    }

with st.spinner("Memuat data terbaru..."):
    data = load_all_data()

# Ambil instance DataProcessor untuk akses helper functions
dp = data['dp_instance']

# Validasi Data Kosong agar tidak crash
if dp.df is None or dp.df.empty:
    st.error("❌ Data tidak ditemukan atau kosong. Silakan input data terlebih dahulu.")
    st.stop()

# --- SIDEBAR FILTERS (UPDATE: INFLUENCER FILTER) ---
st.sidebar.header("🔧 Filter Data")

# [FITUR BARU] 1. Filter Influencer
unique_authors = dp.get_unique_authors()
selected_author = st.sidebar.selectbox(
    "Pilih Akun Influencer:",
    ["Semua Influencer"] + unique_authors
)

# Header Dinamis
st.title("📊 Dashboard Analitik Performa Konten")
if selected_author == "Semua Influencer":
    st.markdown("Analisis mendalam performa konten **Semua Influencer**")
else:
    st.markdown(f"Analisis mendalam performa konten akun **@{selected_author}**")


# [UPDATE LOGIKA DATA]
# Kita filter data mentah (raw_data) DULUAN sebelum masuk ke filter tanggal
if selected_author != "Semua Influencer":
    base_df = data['raw_data'][data['raw_data']['authorMeta.name'] == selected_author].copy()
else:
    base_df = data['raw_data'].copy()


# 2. Filter Tanggal (Bekerja di atas base_df yang sudah difilter author)
base_df['createTimeISO'] = pd.to_datetime(base_df['createTimeISO'])

if not base_df.empty:
    min_date = base_df['createTimeISO'].min().date()
    max_date = base_df['createTimeISO'].max().date()
else:
    min_date, max_date = pd.Timestamp.now().date(), pd.Timestamp.now().date()

# Pilihan Mode Filter Waktu
filter_mode = st.sidebar.radio(
    "Mode Filter Waktu:",
    ["Semua Waktu", "Rentang Tanggal", "Bulan Tertentu", "Tahun Tertentu"]
)

# 3. Logika Filter Akhir (filtered_df)
filtered_df = base_df.copy()

if not filtered_df.empty:
    if filter_mode == "Rentang Tanggal":
        date_range = st.sidebar.date_input(
            "Pilih Rentang Tanggal",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['createTimeISO'].dt.date >= start_date) &
                (filtered_df['createTimeISO'].dt.date <= end_date)
            ]

    elif filter_mode == "Bulan Tertentu":
        available_years = sorted(filtered_df['createTimeISO'].dt.year.unique())
        selected_year = st.sidebar.selectbox("Pilih Tahun", available_years)
        
        months_in_year = filtered_df[filtered_df['createTimeISO'].dt.year == selected_year]['createTimeISO'].dt.month_name().unique()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        sorted_months = sorted(months_in_year, key=lambda x: month_order.index(x) if x in month_order else 99)
        
        selected_month = st.sidebar.selectbox("Pilih Bulan", sorted_months)
        
        filtered_df = filtered_df[
            (filtered_df['createTimeISO'].dt.year == selected_year) &
            (filtered_df['createTimeISO'].dt.month_name() == selected_month)
        ]

    elif filter_mode == "Tahun Tertentu":
        available_years = sorted(filtered_df['createTimeISO'].dt.year.unique())
        selected_year = st.sidebar.selectbox("Pilih Tahun", available_years)
        filtered_df = filtered_df[filtered_df['createTimeISO'].dt.year == selected_year]

st.sidebar.info(f"Menampilkan **{len(filtered_df)}** video")


# ==================== OVERVIEW METRICS ====================
st.header("📈 Ringkasan Performa")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Video",
        value=f"{len(filtered_df)}",
    )

with col2:
    total_views = filtered_df['playCount'].sum()
    st.metric(
        label="Total Tayangan",
        value=format_number(total_views),
    )

with col3:
    total_likes = filtered_df['diggCount'].sum()
    st.metric(
        label="Total Suka",
        value=format_number(total_likes),
    )

with col4:
    total_comments = filtered_df['commentCount'].sum()
    st.metric(
        label="Total Komentar",
        value=format_number(total_comments),
    )

with col5:
    avg_engagement = filtered_df['engagement_rate'].mean() if not filtered_df.empty else 0
    st.metric(
        label="Avg. Engagement",
        value=f"{avg_engagement:.2f}%",
    )

# Additional metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_views = filtered_df['playCount'].mean() if not filtered_df.empty else 0
    st.metric(
        label="Rata-rata Tayangan",
        value=format_number(avg_views)
    )

with col2:
    median_views = filtered_df['playCount'].median() if not filtered_df.empty else 0
    st.metric(
        label="Median Tayangan",
        value=format_number(median_views)
    )

with col3:
    best_video_views = filtered_df['playCount'].max() if not filtered_df.empty else 0
    st.metric(
        label="Video Terbaik",
        value=format_number(best_video_views)
    )

with col4:
    avg_duration = filtered_df['videoMeta.duration'].mean() if not filtered_df.empty else 0
    st.metric(
        label="Durasi Rata-rata",
        value=f"{avg_duration:.0f} detik"
    )

st.markdown("---")

# ==================== [FITUR BARU] LEADERBOARD ====================
# Hanya muncul jika memilih "Semua Influencer"
if selected_author == "Semua Influencer":
    st.header("🏆 Peringkat Influencer (Leaderboard)")
    st.info("Membandingkan performa influencer berdasarkan total tayangan.")
    
    # Ambil leaderboard dari DataProcessor
    leaderboard_df = dp.get_leaderboard()
    
    # Tampilkan dengan formatting yang rapi
    tampilan_leaderboard = leaderboard_df.copy()
    
    # Format angka agar ada koma ribuan
    for col in ['Total Penayangan', 'Total Suka', 'Total Bagikan']:
        if col in tampilan_leaderboard.columns:
            tampilan_leaderboard[col] = tampilan_leaderboard[col].apply(lambda x: f"{x:,.0f}")
            
    if 'Rata-rata ER (%)' in tampilan_leaderboard.columns:
        tampilan_leaderboard['Rata-rata ER (%)'] = tampilan_leaderboard['Rata-rata ER (%)'].apply(lambda x: f"{x:.2f}%")
        
    st.dataframe(
        tampilan_leaderboard, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "Nama Akun": st.column_config.TextColumn("Nama Akun", width="medium"),
            "Total Penayangan": st.column_config.ProgressColumn(
                "Total Tayangan",
                format="%s",
                min_value=0,
                max_value=int(leaderboard_df['Total Penayangan'].max()) if not leaderboard_df.empty else 100
            ),
        }
    )
    st.markdown("---")

# ==================== PERFORMANCE OVER TIME ====================
st.header("⏰ Performa Berdasarkan Waktu")

if not filtered_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Performa per Hari")
        # Hitung ulang berdasarkan filtered_df
        day_perf = dp.get_performance_by_day(filtered_df).reset_index()
        day_perf = day_perf.rename(columns={'upload_day': 'Hari Upload', 'playCount': 'Rata-rata Tayangan'})

        fig_day = create_bar_chart(day_perf, x='Hari Upload', y='Rata-rata Tayangan', title="Rerata Tayangan per Hari", xaxis_title="Hari", yaxis_title="Views")
        st.plotly_chart(fig_day, use_container_width=True)
        
        # Insight
        if not day_perf.empty:
            best_day = day_perf.loc[day_perf['Rata-rata Tayangan'].idxmax(), 'Hari Upload']
            st.info(f"📌 **Hari Terbaik**: {best_day}")

    with col2:
        st.subheader("🕐 Performa per Jam")
        hour_perf = dp.get_performance_by_hour(filtered_df).reset_index()
        hour_perf = hour_perf.rename(columns={'upload_hour': 'Jam Upload', 'playCount': 'Rata-rata Tayangan'})

        fig_hour = create_line_chart(hour_perf, x='Jam Upload', y='Rata-rata Tayangan', title="Rerata Tayangan per Jam", xaxis_title="Jam", yaxis_title="Views")
        st.plotly_chart(fig_hour, use_container_width=True)
        
        if not hour_perf.empty:
            best_hour = hour_perf.loc[hour_perf['Rata-rata Tayangan'].idxmax(), 'Jam Upload']
            st.info(f"📌 **Jam Terbaik**: Pukul {best_hour}:00")

    # Time series view
    st.subheader("📈 Tren Tayangan Sepanjang Waktu")
    time_series_df = filtered_df.sort_values('createTimeISO')[['createTimeISO', 'playCount']]
    time_series_df = time_series_df.rename(columns={'createTimeISO': 'Tanggal Upload', 'playCount': 'Jumlah Tayangan'})

    fig_timeline = create_time_series_chart(time_series_df, date_col='Tanggal Upload', value_col='Jumlah Tayangan', title="Tren Video", yaxis_title="Tayangan")
    st.plotly_chart(fig_timeline, use_container_width=True)

else:
    st.warning("Tidak ada data yang cocok dengan filter.")

st.markdown("---")

# ==================== CONTENT TYPE ANALYSIS ====================
st.header("🎨 Analisis Tipe Konten")

# Hitung ulang berdasarkan filtered_df
content_type_perf = dp.get_content_type_performance(filtered_df)

if not content_type_perf.empty:
    content_dist = content_type_perf.reset_index().rename(columns={
        'content_type': 'Tipe Konten', 
        'video_count': 'Jumlah Video', 
        'playCount_mean': 'Rata-rata Tayangan'
    })

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Distribusi Tipe Konten")
        fig_content_pie = create_pie_chart(values=content_dist['Jumlah Video'], names=content_dist['Tipe Konten'], title="Proporsi Video", hole=0.4)
        st.plotly_chart(fig_content_pie, use_container_width=True)

    with col2:
        st.subheader("⭐ Performa per Tipe Konten")
        fig_content_bar = create_bar_chart(content_dist, x='Tipe Konten', y='Rata-rata Tayangan', title="Rerata Tayangan per Tipe", xaxis_title="Kategori", yaxis_title="Views")
        st.plotly_chart(fig_content_bar, use_container_width=True)

    # Insight
    if not content_dist.empty:
        best_content = content_dist.loc[content_dist['Rata-rata Tayangan'].idxmax(), 'Tipe Konten']
        best_content_views = content_dist['Rata-rata Tayangan'].max()
        st.info(f"📌 **Tipe Konten Juara**: {best_content} (Avg. {format_number(best_content_views)} tayangan)")

    # Tabel Detail
    st.subheader("📋 Detail Performa Tipe Konten")
    content_table = content_dist[['Tipe Konten', 'Jumlah Video', 'Rata-rata Tayangan']].copy()
    content_table['Rata-rata Tayangan'] = content_table['Rata-rata Tayangan'].apply(lambda x: f"{x:,.0f}")
    st.dataframe(content_table, use_container_width=True, hide_index=True)

else:
    st.warning("Data tipe konten tidak tersedia.")

st.markdown("---")

# ==================== AUDIO TYPE ANALYSIS ====================
st.header("🎵 Analisis Tipe Audio")

# Hitung ulang berdasarkan filtered_df
audio_type_perf = dp.get_audio_type_performance(filtered_df)

if not audio_type_perf.empty:
    audio_dist = audio_type_perf.reset_index().rename(columns={
        'audio_type': 'Jenis Audio', 
        'video_count': 'Jumlah Video', 
        'playCount_mean': 'Rata-rata Tayangan'
    })

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Distribusi Penggunaan Audio")
        fig_audio_pie = create_pie_chart(values=audio_dist['Jumlah Video'], names=audio_dist['Jenis Audio'], title="Proporsi Audio", hole=0.4)
        st.plotly_chart(fig_audio_pie, use_container_width=True)

    with col2:
        st.subheader("⭐ Performa per Jenis Audio")
        fig_audio_bar = create_bar_chart(audio_dist, x='Jenis Audio', y='Rata-rata Tayangan', title="Efektivitas Audio", xaxis_title="Jenis", yaxis_title="Views")
        st.plotly_chart(fig_audio_bar, use_container_width=True)
    
    if not audio_dist.empty:
        best_audio = audio_dist.loc[audio_dist['Rata-rata Tayangan'].idxmax(), 'Jenis Audio']
        st.info(f"📌 **Audio Paling Efektif**: {best_audio}")
else:
    st.warning("Data audio tidak tersedia.")

st.markdown("---")

# ==================== TOP PERFORMERS ====================
st.header("🏆 Video dengan Performa Terbaik")

tab1, tab2, tab3 = st.tabs(["📈 Top by Views", "❤️ Top by Likes", "💬 Top by Comments"])

if not filtered_df.empty:
    with tab1:
        st.subheader("Top 10 Video Berdasarkan Tayangan")
        top_views = filtered_df.nlargest(10, 'playCount')[['text', 'playCount', 'diggCount', 'engagement_rate']].copy()
        top_views.columns = ['Caption', 'Tayangan', 'Suka', 'ER (%)']
        top_views['Tayangan'] = top_views['Tayangan'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(top_views, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Top 10 Video Berdasarkan Suka")
        top_likes = filtered_df.nlargest(10, 'diggCount')[['text', 'playCount', 'diggCount']].copy()
        top_likes.columns = ['Caption', 'Tayangan', 'Suka']
        st.dataframe(top_likes, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Top 10 Video Berdasarkan Komentar")
        top_comments = filtered_df.nlargest(10, 'commentCount')[['text', 'playCount', 'diggCount', 'commentCount']].copy()
        top_comments.columns = ['Caption', 'Tayangan', 'Suka', 'Komentar']
        st.dataframe(top_comments, use_container_width=True, hide_index=True)

st.markdown("---")

# ==================== ENGAGEMENT PATTERNS ====================
st.header("🔗 Pola Engagement")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Korelasi Metrik")
    # Hitung korelasi berdasarkan data yang difilter
    corr_df = dp.get_correlation_matrix(filtered_df)
    
    rename_map = {
        'playCount': 'Tayangan', 'diggCount': 'Suka', 
        'commentCount': 'Komentar', 'shareCount': 'Dibagikan', 
        'videoMeta.duration': 'Durasi', 'engagement_rate': 'Engagement'
    }
    corr_df = corr_df.rename(columns=rename_map, index=rename_map)
    
    fig_corr = create_correlation_heatmap(corr_df, title="Matriks Hubungan")
    st.plotly_chart(fig_corr, use_container_width=True)

with col2:
        st.subheader("📈 Distribusi Engagement Rate")
        hist_df = filtered_df.copy().rename(columns={'engagement_rate': 'Engagement Rate (%)'})
        
        # FIX: Tambahkan parameter 'xaxis_title' yang wajib diminta oleh fungsi
        fig_hist = create_histogram(
            hist_df, 
            x='Engagement Rate (%)', 
            title="Sebaran Engagement", 
            xaxis_title="Persentase Engagement (%)", # <-- TAMBAHAN WAJIB INI
            nbins=30
        )
        st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# ==================== KEY INSIGHTS (LOGIKA DINAMIS) ====================
st.header("💡 Insight Utama")

# Hitung insight berdasarkan data filtered_df
if not filtered_df.empty and not content_type_perf.empty:
    # Ambil rekomendasi dinamis
    rec_day = best_day if 'best_day' in locals() else "-"
    rec_hour = best_hour if 'best_hour' in locals() else "-"
    rec_content = best_content if 'best_content' in locals() else "-"
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Rekomendasi Strategis")
        st.markdown(f"""
        1. **Waktu Upload**: Hari **{rec_day}**, Pukul **{rec_hour}:00**
        2. **Konten**: Fokus pada tipe **{rec_content}**
        3. **Audio**: Gunakan **{best_audio if 'best_audio' in locals() else "-"}**
        """)
        
    with col2:
        st.subheader("📊 Ringkasan")
        st.info(f"Analisis ini didasarkan pada **{len(filtered_df)}** video terpilih.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>📊 Dashboard Analitik TikTok - Dikembangkan oleh Nayandra Agastia Putra</p>
</div>
""", unsafe_allow_html=True)