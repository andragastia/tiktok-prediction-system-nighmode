"""
Data Preprocessing Page
Convert raw TikTok scraper data into model-ready features
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime
import re
from io import BytesIO

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.model_handler import get_model_handler

# Page config
st.set_page_config(
    page_title="Data Preprocessing - Sistem Prediksi TikTok",
    page_icon="🔧",
    layout="wide"
)


# Header
st.title("🔧 Preprocessing Data TikTok")
st.markdown("Konversi data mentah dari FreeTikTokScraper menjadi format siap prediksi")

st.markdown("---")

# Information section
with st.expander("ℹ️ Panduan Preprocessing"):
    st.markdown("""
    ### Apa itu Preprocessing?

    Preprocessing adalah proses mengubah data mentah dari TikTok menjadi format yang dapat dipahami oleh model machine learning.

    ### Input yang Diterima:
    **Format RAW (dari FreeTikTokScraper)** dengan kolom:
    - `text` - Caption video
    - `diggCount` - Jumlah likes
    - `shareCount` - Jumlah shares
    - `playCount` - Jumlah views
    - `commentCount` - Jumlah comments
    - `videoMeta.duration` - Durasi video
    - `musicMeta.musicName` - Nama musik
    - `musicMeta.musicOriginal` - Is original audio
    - `createTimeISO` - Timestamp upload
    - `webVideoUrl` - URL video

    ### Output yang Dihasilkan:
    **Format PROCESSED** dengan 22 features:
    - Engagement metrics: `Suka`, `Komentar`, `Dibagikan`
    - Video properties: `Durasi_Video`, `Jumlah_Hashtag`, `Panjang_Caption`
    - Temporal: `Hari_Upload`, `Jam_Upload`, `Jam_Sejak_Publikasi`
    - Content type (one-hot): `Tipe_Konten_OOTD`, `Tipe_Konten_Tutorial`, dll
    - Audio type (one-hot): `Tipe_Audio_Audio Original`, dll
    - Interaction features: `Interaksi_Tutorial_x_Komentar`, dll

    ### Proses yang Dilakukan:
    1. ✅ Extract hashtags dari caption
    2. ✅ Calculate caption length
    3. ✅ Extract temporal features (day, hour)
    4. ✅ Classify content type (OOTD, Tutorial, Vlog, etc.)
    5. ✅ Classify audio type (Original, Popular, Other)
    6. ✅ Create interaction features
    7. ✅ Calculate hours since publish
    8. ✅ One-hot encode categorical features
    """)

st.markdown("---")

# Helper functions for preprocessing
def extract_hashtags(text):
    """Extract hashtags from caption"""
    if pd.isna(text):
        return []
    hashtags = re.findall(r'#\w+', str(text))
    return hashtags

def count_hashtags(text):
    """Count number of hashtags"""
    return len(extract_hashtags(text))

def classify_content_type(text):
    """Classify content type based on caption keywords"""
    if pd.isna(text):
        return 'Lainnya'

    text_lower = str(text).lower()

    # Check for OOTD
    if any(keyword in text_lower for keyword in ['ootd', 'outfit', 'look', 'fashion', 'style']):
        return 'OOTD'
    # Check for Tutorial
    elif any(keyword in text_lower for keyword in ['tutorial', 'how to', 'cara', 'tips', 'belajar']):
        return 'Tutorial'
    # Check for Vlog
    elif any(keyword in text_lower for keyword in ['vlog', 'day in', 'diary', 'daily', 'routine']):
        return 'Vlog'
    # Check for Educational
    elif any(keyword in text_lower for keyword in ['teacher', 'guru', 'mengajar', 'pkm', 'sekolah', 'kelas']):
        return 'Tutorial'  # Educational content is similar to Tutorial
    else:
        return 'Lainnya'

def classify_audio_type(music_name, is_original):
    """Classify audio type"""
    if pd.isna(music_name) or music_name == '':
        return 'Audio Lainnya'
    elif is_original:
        return 'Audio Original'
    else:
        return 'Audio Populer'

def calculate_hours_since_publish(upload_time, reference_time=None):
    """Calculate hours since publish"""
    from datetime import timezone

    if reference_time is None:
        reference_time = datetime.now(timezone.utc)

    # Ensure both datetimes have compatible timezone information
    if upload_time.tzinfo is not None and reference_time.tzinfo is None:
        # Make reference_time timezone-aware (UTC)
        reference_time = reference_time.replace(tzinfo=timezone.utc)
    elif upload_time.tzinfo is None and reference_time.tzinfo is not None:
        # Make upload_time timezone-aware (assume UTC)
        upload_time = upload_time.replace(tzinfo=timezone.utc)

    time_diff = reference_time - upload_time
    hours = time_diff.total_seconds() / 3600
    return max(0, hours)  # Ensure non-negative

def estimate_trend_strength(value, percentile_75, percentile_90):
    """Estimate trend strength based on value percentiles"""
    if value >= percentile_90:
        return 0.9
    elif value >= percentile_75:
        return 0.7
    else:
        return 0.5

def preprocess_raw_data(df_raw, reference_time=None):
    """
    Preprocess raw TikTok data into model-ready features

    Args:
        df_raw: DataFrame with raw TikTok data
        reference_time: Reference datetime for calculating hours since publish

    Returns:
        DataFrame with 22 model features
    """
    df = df_raw.copy()

    # 1. Basic engagement metrics
    df['Suka'] = df['diggCount']
    df['Komentar'] = df['commentCount']
    df['Dibagikan'] = df['shareCount']
    df['Durasi_Video'] = df['videoMeta.duration']

    # 2. Caption analysis
    df['Jumlah_Hashtag'] = df['text'].apply(count_hashtags)
    df['Panjang_Caption'] = df['text'].apply(lambda x: len(str(x)) if not pd.isna(x) else 0)

    # 3. Temporal features
    df['createTimeISO'] = pd.to_datetime(df['createTimeISO'])
    df['Hari_Upload'] = df['createTimeISO'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['Jam_Upload'] = df['createTimeISO'].dt.hour

    # Calculate hours since publish
    if reference_time is None:
        reference_time = datetime.now()
    df['Jam_Sejak_Publikasi'] = df['createTimeISO'].apply(
        lambda x: calculate_hours_since_publish(x, reference_time)
    )

    # 4. Content type classification
    df['content_type'] = df['text'].apply(classify_content_type)

    # 5. Audio type classification
    df['audio_type'] = df.apply(
        lambda row: classify_audio_type(row['musicMeta.musicName'], row['musicMeta.musicOriginal']),
        axis=1
    )

    # 6. Trend strength estimation (based on engagement percentiles)
    # For audio trend: based on whether it's popular music
    df['Kekuatan_Tren_Audio'] = df.apply(
        lambda row: 0.9 if row['audio_type'] == 'Audio Populer'
                    else 0.8 if row['audio_type'] == 'Audio Original'
                    else 0.5,
        axis=1
    )

    # For hashtag trend: estimate based on engagement
    hashtag_engagement = df['Suka'] + df['Komentar'] + df['Dibagikan']
    p75 = hashtag_engagement.quantile(0.75)
    p90 = hashtag_engagement.quantile(0.90)
    df['Kekuatan_Tren_Hashtag'] = hashtag_engagement.apply(
        lambda x: estimate_trend_strength(x, p75, p90)
    )

    # 7. Collaboration detection (simple heuristic)
    df['Apakah_Kolaborasi'] = df['text'].apply(
        lambda x: 1 if any(keyword in str(x).lower() for keyword in ['collab', 'ft', 'with', 'bersama']) else 0
    )

    # 8. Video format (assume vertical for TikTok)
    df['Format_Konten_Video'] = 1  # 1 = Vertical (9:16)

    # 9. One-hot encode content type
    df['Tipe_Konten_Lainnya'] = (df['content_type'] == 'Lainnya').astype(int)
    df['Tipe_Konten_OOTD'] = (df['content_type'] == 'OOTD').astype(int)
    df['Tipe_Konten_Tutorial'] = (df['content_type'] == 'Tutorial').astype(int)
    df['Tipe_Konten_Vlog'] = (df['content_type'] == 'Vlog').astype(int)

    # 10. One-hot encode audio type
    df['Tipe_Audio_Audio Lainnya'] = (df['audio_type'] == 'Audio Lainnya').astype(int)
    df['Tipe_Audio_Audio Original'] = (df['audio_type'] == 'Audio Original').astype(int)
    df['Tipe_Audio_Audio Populer'] = (df['audio_type'] == 'Audio Populer').astype(int)

    # 11. Interaction features
    df['Interaksi_Tutorial_x_Komentar'] = df['Komentar'] * df['Tipe_Konten_Tutorial']
    df['Interaksi_OOTD_x_Dibagikan'] = df['Dibagikan'] * df['Tipe_Konten_OOTD']

    # Select final 22 features in correct order
    feature_columns = [
        'Suka', 'Komentar', 'Dibagikan', 'Durasi_Video', 'Jumlah_Hashtag',
        'Jam_Sejak_Publikasi', 'Panjang_Caption', 'Hari_Upload', 'Jam_Upload',
        'Kekuatan_Tren_Audio', 'Kekuatan_Tren_Hashtag', 'Apakah_Kolaborasi',
        'Format_Konten_Video', 'Tipe_Konten_Lainnya', 'Tipe_Konten_OOTD',
        'Tipe_Konten_Tutorial', 'Tipe_Konten_Vlog', 'Tipe_Audio_Audio Lainnya',
        'Tipe_Audio_Audio Original', 'Tipe_Audio_Audio Populer',
        'Interaksi_Tutorial_x_Komentar', 'Interaksi_OOTD_x_Dibagikan'
    ]

    df_processed = df[feature_columns].copy()

    # Keep some metadata for reference
    metadata_columns = []
    if 'webVideoUrl' in df.columns:
        metadata_columns.append('webVideoUrl')
    if 'text' in df.columns:
        metadata_columns.append('text')

    # Add Video_ID if not present
    if 'Video_ID' not in df.columns:
        df_processed.insert(0, 'Video_ID', range(1, len(df_processed) + 1))

    # Add Caption for reference
    if 'text' in df.columns:
        df_processed.insert(1, 'Caption', df['text'])

    # Add content and audio type for reference
    df_processed.insert(2, 'content_type_detected', df['content_type'])
    df_processed.insert(3, 'audio_type_detected', df['audio_type'])

    return df_processed

# Download raw template
st.subheader("📥 Download Template Data Mentah")

col1, col2 = st.columns([1, 3])

with col1:
    # Create raw template
    raw_template = pd.DataFrame({
        'authorMeta.name': ['septianndt', 'septianndt'],
        'text': ['OOTD hari ini #ootd #fashion', 'Tutorial makeup natural #tutorial #beauty'],
        'diggCount': [150, 500],
        'shareCount': [10, 30],
        'playCount': [5000, 15000],
        'commentCount': [20, 50],
        'videoMeta.duration': [30, 45],
        'musicMeta.musicName': ['Trending Song', 'original sound'],
        'musicMeta.musicOriginal': [False, True],
        'createTimeISO': ['2024-01-15T14:30:00.000Z', '2024-01-16T10:00:00.000Z'],
        'webVideoUrl': ['https://www.tiktok.com/@septianndt/video/1', 'https://www.tiktok.com/@septianndt/video/2']
    })

    csv_raw_template = raw_template.to_csv(index=False)

    st.download_button(
        label="📥 Unduh Template RAW",
        data=csv_raw_template,
        file_name="template_raw_tiktok.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    st.info("💡 Template berisi format data mentah dari FreeTikTokScraper. Isi dengan data Anda sendiri.")

st.markdown("---")

# File upload
st.subheader("📁 Upload Data Mentah")

uploaded_file = st.file_uploader(
    "Pilih file CSV dengan data mentah TikTok",
    type=['csv'],
    help="Upload file CSV dari FreeTikTokScraper atau format serupa"
)

if uploaded_file is not None:
    try:
        # Load raw data
        df_raw = pd.read_csv(uploaded_file)

        st.success(f"✅ File berhasil diunggah! Total baris: {len(df_raw)}")

        # Show raw data preview
        with st.expander("👁️ Preview Data Mentah (5 baris pertama)"):
            st.dataframe(df_raw.head(), use_container_width=True)

        # Check required columns
        required_raw_columns = [
            'text', 'diggCount', 'shareCount', 'playCount', 'commentCount',
            'videoMeta.duration', 'musicMeta.musicName', 'musicMeta.musicOriginal',
            'createTimeISO', 'webVideoUrl'
        ]

        missing_columns = [col for col in required_raw_columns if col not in df_raw.columns]

        if missing_columns:
            st.warning(f"⚠️ Kolom yang hilang: {', '.join(missing_columns)}")
            st.info("Preprocessing akan tetap dilakukan dengan kolom yang tersedia.")
        else:
            st.success("✅ Semua kolom yang diperlukan tersedia!")

        st.markdown("---")

        # Preprocessing options
        st.subheader("⚙️ Pengaturan Preprocessing")

        col1, col2 = st.columns(2)

        with col1:
            use_current_time = st.checkbox(
                "Gunakan waktu saat ini untuk 'Jam Sejak Publikasi'",
                value=True,
                help="Jika dicentang, akan menghitung jam sejak publikasi dari waktu saat ini. Jika tidak, gunakan waktu kustom."
            )

        with col2:
            if not use_current_time:
                from datetime import timezone
                reference_date = st.date_input(
                    "Tanggal Referensi",
                    value=datetime.now().date()
                )
                reference_time_input = st.time_input(
                    "Waktu Referensi",
                    value=datetime.now().time()
                )
                reference_time = datetime.combine(reference_date, reference_time_input)
                # Make timezone-aware (UTC)
                reference_time = reference_time.replace(tzinfo=timezone.utc)
            else:
                reference_time = None

        st.markdown("---")

        # Process button
        if st.button("🔧 Proses Data", use_container_width=True, type="primary"):
            with st.spinner("Sedang memproses data..."):
                # Preprocess data
                df_processed = preprocess_raw_data(df_raw, reference_time)

                # Store in session state for potential use in Batch Prediction
                st.session_state['preprocessed_data'] = df_processed.copy()
                st.session_state['preprocessed_data_ready'] = True

                st.success("✅ Preprocessing selesai!")

                st.markdown("---")

                # Show processing summary
                st.header("📊 Hasil Preprocessing")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Video", len(df_processed))

                with col2:
                    ootd_count = df_processed['Tipe_Konten_OOTD'].sum()
                    st.metric("OOTD Videos", ootd_count)

                with col3:
                    tutorial_count = df_processed['Tipe_Konten_Tutorial'].sum()
                    st.metric("Tutorial Videos", tutorial_count)

                with col4:
                    vlog_count = df_processed['Tipe_Konten_Vlog'].sum()
                    st.metric("Vlog Videos", vlog_count)

                st.markdown("---")

                # Show content type distribution
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📊 Distribusi Tipe Konten")
                    content_dist = df_processed['content_type_detected'].value_counts()
                    st.bar_chart(content_dist)

                with col2:
                    st.subheader("🎵 Distribusi Tipe Audio")
                    audio_dist = df_processed['audio_type_detected'].value_counts()
                    st.bar_chart(audio_dist)

                st.markdown("---")

                # Show processed data preview
                st.subheader("👁️ Preview Data yang Sudah Diproses")

                # Show first 10 rows with all features
                st.dataframe(df_processed.head(10), use_container_width=True)

                st.markdown("---")

                # Feature summary
                st.subheader("📋 Ringkasan Fitur yang Dihasilkan")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("""
                    **Engagement Metrics:**
                    - ✅ Suka (Likes)
                    - ✅ Komentar (Comments)
                    - ✅ Dibagikan (Shares)

                    **Video Properties:**
                    - ✅ Durasi_Video
                    - ✅ Jumlah_Hashtag
                    - ✅ Panjang_Caption
                    - ✅ Format_Konten_Video

                    **Temporal Features:**
                    - ✅ Hari_Upload (0-6)
                    - ✅ Jam_Upload (0-23)
                    - ✅ Jam_Sejak_Publikasi
                    """)

                with col2:
                    st.markdown("""
                    **Trend Strength:**
                    - ✅ Kekuatan_Tren_Audio
                    - ✅ Kekuatan_Tren_Hashtag

                    **Content Type (One-hot):**
                    - ✅ Tipe_Konten_Lainnya
                    - ✅ Tipe_Konten_OOTD
                    - ✅ Tipe_Konten_Tutorial
                    - ✅ Tipe_Konten_Vlog

                    **Audio Type (One-hot):**
                    - ✅ Tipe_Audio_Audio Lainnya
                    - ✅ Tipe_Audio_Audio Original
                    - ✅ Tipe_Audio_Audio Populer

                    **Interaction Features:**
                    - ✅ Interaksi_Tutorial_x_Komentar
                    - ✅ Interaksi_OOTD_x_Dibagikan
                    """)

                st.markdown("---")

                # Export section
                st.subheader("💾 Ekspor Data yang Sudah Diproses")

                st.info("💡 File yang dihasilkan sudah siap untuk digunakan di halaman **Batch Prediction**")

                col1, col2, col3 = st.columns(3)

                # CSV Export (all features)
                with col1:
                    csv_processed = df_processed.to_csv(index=False)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                    st.download_button(
                        label="📥 Unduh CSV (Lengkap)",
                        data=csv_processed,
                        file_name=f"data_processed_{timestamp}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="Semua kolom termasuk metadata"
                    )

                # CSV Export (features only, ready for prediction)
                with col2:
                    # Get model features
                    model_handler = get_model_handler()
                    feature_columns = model_handler.feature_names

                    df_for_prediction = df_processed[['Video_ID', 'Caption'] + feature_columns].copy()
                    csv_for_prediction = df_for_prediction.to_csv(index=False)

                    st.download_button(
                        label="📥 Unduh CSV (Siap Prediksi)",
                        data=csv_for_prediction,
                        file_name=f"data_ready_for_prediction_{timestamp}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="Hanya features yang diperlukan untuk prediksi"
                    )

                # Excel Export
                with col3:
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df_processed.to_excel(writer, index=False, sheet_name='Processed Data')

                        # Add summary sheet
                        summary_data = {
                            'Metric': ['Total Videos', 'OOTD', 'Tutorial', 'Vlog', 'Lainnya',
                                      'Audio Original', 'Audio Populer', 'Audio Lainnya'],
                            'Count': [
                                len(df_processed),
                                df_processed['Tipe_Konten_OOTD'].sum(),
                                df_processed['Tipe_Konten_Tutorial'].sum(),
                                df_processed['Tipe_Konten_Vlog'].sum(),
                                df_processed['Tipe_Konten_Lainnya'].sum(),
                                df_processed['Tipe_Audio_Audio Original'].sum(),
                                df_processed['Tipe_Audio_Audio Populer'].sum(),
                                df_processed['Tipe_Audio_Audio Lainnya'].sum()
                            ]
                        }
                        pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name='Summary')

                    excel_data = buffer.getvalue()

                    st.download_button(
                        label="📥 Unduh Excel",
                        data=excel_data,
                        file_name=f"data_processed_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        help="Termasuk sheet summary"
                    )

                st.markdown("---")

                # Next steps
                st.subheader("🎯 Langkah Selanjutnya")

                st.success("""
                **Data Anda sudah siap! Pilih salah satu:**

                **Opsi 1: Langsung Prediksi (Otomatis)**
                - Klik tombol "Langsung ke Batch Prediction" di bawah
                - Data akan otomatis dimuat di halaman Batch Prediction
                - Langsung klik "Jalankan Prediksi"

                **Opsi 2: Download & Upload Manual**
                1. ✅ Download file CSV "Siap Prediksi"
                2. ✅ Buka halaman **Batch Prediction**
                3. ✅ Upload file yang sudah didownload
                4. ✅ Jalankan prediksi
                """)

                if st.button("📤 Langsung ke Batch Prediction (Auto-load Data)", use_container_width=True, type="primary"):
                    # Set flag to auto-load data in Batch Prediction page
                    st.session_state['auto_load_preprocessed'] = True
                    st.switch_page("pages/3_📤_Batch_Prediction.py")

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat memproses file: {str(e)}")
        st.exception(e)

else:
    # Show when no file uploaded
    st.info("📁 Silakan upload file CSV dengan data mentah TikTok")

    st.markdown("---")

    # Show example of raw vs processed
    st.subheader("📝 Contoh: Data Mentah vs Data Diproses")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Data Mentah (Input):**")
        example_raw = pd.DataFrame({
            'text': ['OOTD hari ini #ootd #fashion'],
            'diggCount': [150],
            'commentCount': [20],
            'shareCount': [10],
            'videoMeta.duration': [30],
            'createTimeISO': ['2024-01-15T14:30:00.000Z']
        })
        st.dataframe(example_raw, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Data Diproses (Output):**")
        example_processed = pd.DataFrame({
            'Suka': [150],
            'Komentar': [20],
            'Dibagikan': [10],
            'Durasi_Video': [30],
            'Jumlah_Hashtag': [2],
            'Tipe_Konten_OOTD': [1],
            'Hari_Upload': [0],  # Monday
            'Jam_Upload': [14]
        })
        st.dataframe(example_processed, use_container_width=True, hide_index=True)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>🔧 Data Preprocessing - Konversi otomatis data mentah ke format model</p>
    <p>Mendukung format FreeTikTokScraper dan format serupa</p>
</div>
""", unsafe_allow_html=True)
