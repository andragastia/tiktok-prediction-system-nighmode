"""
Analytics Dashboard Page
Comprehensive analytics and insights for TikTok content performance
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

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


# Header
st.title("📊 Dashboard Analitik Performa Konten")
st.markdown("Analisis mendalam tentang performa konten TikTok @septianndt")

# Load data
@st.cache_data
def load_all_data():
    """Load and cache all data"""
    dp = get_data_processor()
    return {
        'raw_data': dp.df,
        'stats': dp.get_summary_stats(),
        'perf_by_day': dp.get_performance_by_day(),
        'perf_by_hour': dp.get_performance_by_hour(),
        'content_type_perf': dp.get_content_type_performance(),
        'audio_type_perf': dp.get_audio_type_performance(),
        'top_videos': dp.get_top_videos(n=10),
        'correlation': dp.get_correlation_matrix()
    }

with st.spinner("Memuat data..."):
    data = load_all_data()

st.success("✅ Data berhasil dimuat!")

# Sidebar filters
st.sidebar.header("🔧 Filter Data")

# 1. Pastikan kolom tanggal bertipe datetime
data['raw_data']['createTimeISO'] = pd.to_datetime(data['raw_data']['createTimeISO'])
min_date = data['raw_data']['createTimeISO'].min().date()
max_date = data['raw_data']['createTimeISO'].max().date()

# 2. Pilihan Mode Filter
filter_mode = st.sidebar.radio(
    "Mode Filter Waktu:",
    ["Semua Waktu", "Rentang Tanggal", "Bulan Tertentu", "Tahun Tertentu"]
)

# 3. Logika Filter
filtered_df = data['raw_data'].copy()

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
    # Ambil daftar tahun dan bulan yang tersedia di data
    available_years = sorted(filtered_df['createTimeISO'].dt.year.unique())
    selected_year = st.sidebar.selectbox("Pilih Tahun", available_years)
    
    # Filter bulan berdasarkan tahun yang dipilih
    months_in_year = filtered_df[filtered_df['createTimeISO'].dt.year == selected_year]['createTimeISO'].dt.month_name().unique()
    # Urutkan bulan secara kronologis (bukan alfabetis)
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

# Tampilkan info filter aktif
st.sidebar.info(f"Menampilkan **{len(filtered_df)}** video")

# --- (Sisa kode di bawah st.markdown("---") tetap sama) ---
# ==================== OVERVIEW METRICS ====================
st.header("📈 Ringkasan Performa")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Video",
        value=f"{len(filtered_df)}",
        delta=None
    )

with col2:
    total_views = filtered_df['playCount'].sum()
    st.metric(
        label="Total Tayangan",
        value=format_number(total_views),
        delta=None
    )

with col3:
    total_likes = filtered_df['diggCount'].sum()
    st.metric(
        label="Total Suka",
        value=format_number(total_likes),
        delta=None
    )

with col4:
    total_comments = filtered_df['commentCount'].sum()
    st.metric(
        label="Total Komentar",
        value=format_number(total_comments),
        delta=None
    )

with col5:
    avg_engagement = filtered_df['engagement_rate'].mean()
    st.metric(
        label="Avg. Engagement",
        value=f"{avg_engagement:.2f}%",
        delta=None
    )

# Additional metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_views = filtered_df['playCount'].mean()
    st.metric(
        label="Rata-rata Tayangan",
        value=format_number(avg_views)
    )

with col2:
    median_views = filtered_df['playCount'].median()
    st.metric(
        label="Median Tayangan",
        value=format_number(median_views)
    )

with col3:
    best_video_views = filtered_df['playCount'].max()
    st.metric(
        label="Video Terbaik",
        value=format_number(best_video_views)
    )

with col4:
    avg_duration = filtered_df['videoMeta.duration'].mean()
    st.metric(
        label="Durasi Rata-rata",
        value=f"{avg_duration:.0f} detik"
    )

st.markdown("---")

# ==================== PERFORMANCE OVER TIME ====================
st.header("⏰ Performa Berdasarkan Waktu")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Performa per Hari")

    # Prepare data for day performance
    day_perf = data['perf_by_day'].reset_index()
    fig_day = create_bar_chart(
        day_perf,
        x='upload_day',
        y='playCount',
        title="Rata-rata Tayangan per Hari dalam Seminggu",
        xaxis_title="Hari",
        yaxis_title="Rata-rata Tayangan"
    )
    st.plotly_chart(fig_day, use_container_width=True)

    # Best day insight
    best_day = day_perf.loc[day_perf['playCount'].idxmax(), 'upload_day']
    best_day_views = day_perf['playCount'].max()
    st.info(f"📌 **Hari Terbaik**: {best_day} dengan rata-rata {format_number(best_day_views)} tayangan")

with col2:
    st.subheader("🕐 Performa per Jam")

    # Prepare data for hour performance
    hour_perf = data['perf_by_hour'].reset_index()
    fig_hour = create_line_chart(
        hour_perf,
        x='upload_hour',
        y='playCount',
        title="Rata-rata Tayangan per Jam Upload",
        xaxis_title="Jam (24H)",
        yaxis_title="Rata-rata Tayangan"
    )
    st.plotly_chart(fig_hour, use_container_width=True)

    # Best hour insight
    best_hour = hour_perf.loc[hour_perf['playCount'].idxmax(), 'upload_hour']
    best_hour_views = hour_perf['playCount'].max()
    st.info(f"📌 **Jam Terbaik**: {best_hour}:00 dengan rata-rata {format_number(best_hour_views)} tayangan")

# Time series view
st.subheader("📈 Tren Tayangan Sepanjang Waktu")
time_series_df = filtered_df.sort_values('createTimeISO')[['createTimeISO', 'playCount']]
fig_timeline = create_time_series_chart(
    time_series_df,
    date_col='createTimeISO',
    value_col='playCount',
    title="Tayangan Video Sepanjang Waktu",
    yaxis_title="Jumlah Tayangan"
)
st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown("---")

# ==================== CONTENT TYPE ANALYSIS ====================
st.header("🎨 Analisis Tipe Konten")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribusi Tipe Konten")

    # Content type distribution
    content_dist = data['content_type_perf'].reset_index()
    fig_content_pie = create_pie_chart(
        values=content_dist['video_count'],
        names=content_dist['content_type'],
        title="Distribusi Tipe Konten",
        hole=0.4
    )
    st.plotly_chart(fig_content_pie, use_container_width=True)

with col2:
    st.subheader("⭐ Performa per Tipe Konten")

    # Content type performance
    fig_content_bar = create_bar_chart(
        content_dist,
        x='content_type',
        y='playCount_mean',
        title="Rata-rata Tayangan per Tipe Konten",
        xaxis_title="Tipe Konten",
        yaxis_title="Rata-rata Tayangan"
    )
    st.plotly_chart(fig_content_bar, use_container_width=True)

# Best content type insight
best_content = content_dist.loc[content_dist['playCount_mean'].idxmax(), 'content_type']
best_content_views = content_dist['playCount_mean'].max()
st.info(f"📌 **Tipe Konten Terbaik**: {best_content} dengan rata-rata {format_number(best_content_views)} tayangan")

# Detailed content type table
st.subheader("📋 Detail Performa Tipe Konten")
content_table = content_dist[['content_type', 'video_count', 'playCount_mean', 'diggCount_mean', 'commentCount_mean']].copy()
content_table.columns = ['Tipe Konten', 'Jumlah Video', 'Avg. Tayangan', 'Avg. Suka', 'Avg. Komentar']
content_table['Avg. Tayangan'] = content_table['Avg. Tayangan'].apply(lambda x: f"{x:,.0f}")
content_table['Avg. Suka'] = content_table['Avg. Suka'].apply(lambda x: f"{x:,.0f}")
content_table['Avg. Komentar'] = content_table['Avg. Komentar'].apply(lambda x: f"{x:,.0f}")
st.dataframe(content_table, use_container_width=True, hide_index=True)

st.markdown("---")

# ==================== AUDIO TYPE ANALYSIS ====================
st.header("🎵 Analisis Tipe Audio")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribusi Tipe Audio")

    # Audio type distribution
    audio_dist = data['audio_type_perf'].reset_index()
    fig_audio_pie = create_pie_chart(
        values=audio_dist['video_count'],
        names=audio_dist['audio_type'],
        title="Distribusi Tipe Audio",
        hole=0.4
    )
    st.plotly_chart(fig_audio_pie, use_container_width=True)

with col2:
    st.subheader("⭐ Performa per Tipe Audio")

    # Audio type performance
    fig_audio_bar = create_bar_chart(
        audio_dist,
        x='audio_type',
        y='playCount_mean',
        title="Rata-rata Tayangan per Tipe Audio",
        xaxis_title="Tipe Audio",
        yaxis_title="Rata-rata Tayangan"
    )
    st.plotly_chart(fig_audio_bar, use_container_width=True)

# Best audio type insight
best_audio = audio_dist.loc[audio_dist['playCount_mean'].idxmax(), 'audio_type']
best_audio_views = audio_dist['playCount_mean'].max()
st.info(f"📌 **Tipe Audio Terbaik**: {best_audio} dengan rata-rata {format_number(best_audio_views)} tayangan")

st.markdown("---")

# ==================== TOP PERFORMERS ====================
st.header("🏆 Video dengan Performa Terbaik")

tab1, tab2, tab3 = st.tabs(["📈 Top by Views", "❤️ Top by Likes", "💬 Top by Comments"])

with tab1:
    st.subheader("Top 10 Video Berdasarkan Tayangan")
    top_by_views = data['top_videos'][['text', 'playCount', 'diggCount', 'commentCount', 'shareCount', 'engagement_rate']].copy()
    top_by_views.columns = ['Caption', 'Tayangan', 'Suka', 'Komentar', 'Dibagikan', 'Engagement Rate']
    top_by_views['Tayangan'] = top_by_views['Tayangan'].apply(lambda x: f"{x:,}")
    top_by_views['Suka'] = top_by_views['Suka'].apply(lambda x: f"{x:,}")
    top_by_views['Komentar'] = top_by_views['Komentar'].apply(lambda x: f"{x:,}")
    top_by_views['Dibagikan'] = top_by_views['Dibagikan'].apply(lambda x: f"{x:,}")
    top_by_views['Engagement Rate'] = top_by_views['Engagement Rate'].apply(lambda x: f"{x:.2f}%")
    st.dataframe(top_by_views, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Top 10 Video Berdasarkan Suka")
    top_by_likes = filtered_df.nlargest(10, 'diggCount')[['text', 'playCount', 'diggCount', 'commentCount', 'shareCount']].copy()
    top_by_likes.columns = ['Caption', 'Tayangan', 'Suka', 'Komentar', 'Dibagikan']
    top_by_likes['Tayangan'] = top_by_likes['Tayangan'].apply(lambda x: f"{x:,}")
    top_by_likes['Suka'] = top_by_likes['Suka'].apply(lambda x: f"{x:,}")
    top_by_likes['Komentar'] = top_by_likes['Komentar'].apply(lambda x: f"{x:,}")
    top_by_likes['Dibagikan'] = top_by_likes['Dibagikan'].apply(lambda x: f"{x:,}")
    st.dataframe(top_by_likes, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Top 10 Video Berdasarkan Komentar")
    top_by_comments = filtered_df.nlargest(10, 'commentCount')[['text', 'playCount', 'diggCount', 'commentCount', 'shareCount']].copy()
    top_by_comments.columns = ['Caption', 'Tayangan', 'Suka', 'Komentar', 'Dibagikan']
    top_by_comments['Tayangan'] = top_by_comments['Tayangan'].apply(lambda x: f"{x:,}")
    top_by_comments['Suka'] = top_by_comments['Suka'].apply(lambda x: f"{x:,}")
    top_by_comments['Komentar'] = top_by_comments['Komentar'].apply(lambda x: f"{x:,}")
    top_by_comments['Dibagikan'] = top_by_comments['Dibagikan'].apply(lambda x: f"{x:,}")
    st.dataframe(top_by_comments, use_container_width=True, hide_index=True)

st.markdown("---")

# ==================== ENGAGEMENT PATTERNS ====================
st.header("🔗 Pola Engagement")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Korelasi Metrik")

    # Correlation heatmap
    fig_corr = create_correlation_heatmap(
        data['correlation'],
        title="Matriks Korelasi Metrik Performa"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

with col2:
    st.subheader("📈 Distribusi Engagement Rate")

    # Engagement rate histogram
    fig_engagement_hist = create_histogram(
        filtered_df,
        x='engagement_rate',
        title="Distribusi Engagement Rate",
        xaxis_title="Engagement Rate (%)",
        nbins=30
    )
    st.plotly_chart(fig_engagement_hist, use_container_width=True)

    # Engagement stats
    st.metric("Median Engagement", f"{filtered_df['engagement_rate'].median():.2f}%")
    st.metric("Max Engagement", f"{filtered_df['engagement_rate'].max():.2f}%")

# Scatter plot: Views vs Likes
st.subheader("🎯 Tayangan vs Suka")
fig_scatter = create_scatter_plot(
    filtered_df,
    x='playCount',
    y='diggCount',
    title="Hubungan antara Tayangan dan Suka",
    xaxis_title="Jumlah Tayangan",
    yaxis_title="Jumlah Suka",
    size='engagement_rate'
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ==================== KEY INSIGHTS ====================
st.header("💡 Insight Utama")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ Rekomendasi")
    st.markdown(f"""
    Berdasarkan analisis data, berikut rekomendasi untuk meningkatkan performa:

    1. **Waktu Upload Optimal**
       - Hari terbaik: **{best_day}**
       - Jam terbaik: **{best_hour}:00**

    2. **Tipe Konten**
       - Fokus pada: **{best_content}**
       - Konten ini menghasilkan performa terbaik

    3. **Strategi Audio**
       - Gunakan: **{best_audio}**
       - Terbukti meningkatkan engagement

    4. **Target Engagement**
       - Rata-rata saat ini: **{avg_engagement:.2f}%**
       - Target: **{avg_engagement * 1.5:.2f}%** (peningkatan 50%)
    """)

with col2:
    st.subheader("📊 Statistik Penting")
    st.markdown(f"""
    **Performa Keseluruhan:**
    - Total video dianalisis: **{len(filtered_df)}**
    - Total tayangan: **{format_number(total_views)}**
    - Video terbaik: **{format_number(best_video_views)}** tayangan

    **Rata-rata Metrik:**
    - Tayangan per video: **{format_number(avg_views)}**
    - Suka per video: **{format_number(filtered_df['diggCount'].mean())}**
    - Komentar per video: **{format_number(filtered_df['commentCount'].mean())}**

    **Engagement:**
    - Engagement rate rata-rata: **{avg_engagement:.2f}%**
    - Video dengan engagement tertinggi: **{filtered_df['engagement_rate'].max():.2f}%**
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>📊 Dashboard Analitik TikTok - Data diperbarui secara real-time</p>
</div>
""", unsafe_allow_html=True)
