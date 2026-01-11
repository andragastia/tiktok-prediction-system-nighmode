"""
Data Preprocessing Page
Convert raw TikTok scraper data into model-ready features
(Updated: Supports 10 Content Categories & Advanced Feature Engineering)
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
from utils.data_processor import get_data_processor

# Page config
st.set_page_config(
    page_title="Preproses Data - Untuk Prediksi Massal",
    page_icon="🔧",
    layout="wide"
)

# Header
st.title("🔧 Preproses Data")
st.markdown("Konversi data mentah dari FreeTikTokScraper menjadi format siap prediksi yang kompatibel dengan Model ML terbaru.")

st.markdown("---")

# Information section (Mempertahankan detail penjelasan asli)
with st.expander("ℹ️ Panduan Preprocessing (Updated)"):
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

    ### Output yang Dihasilkan (Sesuai Model 10 Kategori):
    **Format PROCESSED** dengan fitur lengkap:
    - Engagement metrics: `Suka`, `Komentar`, `Dibagikan`
    - Video properties: `Durasi_Video`, `Jumlah_Hashtag`, `Panjang_Caption`
    - Temporal: `Hari_Upload`, `Jam_Upload`, `Jam_Sejak_Publikasi`, `Is_Weekend`
    - Content type (one-hot): `Kat_Gaming`, `Kat_Fashion`, `Kat_Kuliner`, dll (10 Kategori)
    - Audio type (one-hot): `Audio_Original`, `Audio_Populer`, dll
    - Interaction features: `Interaksi_Gaming_Suka`, `Interaksi_Fashion_Suka`, dll

    ### Proses yang Dilakukan:
    1. ✅ Extract hashtags & hitung panjang caption
    2. ✅ Extract fitur waktu (Jam, Hari, Weekend)
    3. ✅ **Klasifikasi Konten Cerdas** (10 Kategori: Gaming, Fashion, dll)
    4. ✅ **Klasifikasi Audio** (Cek Top 20 Lagu Populer)
    5. ✅ Create interaction features (Perkalian Kategori x Likes)
    6. ✅ One-hot encode semua kategori
    """)

st.markdown("---")

# --- HELPER FUNCTIONS (UPDATED LOGIC, KEEPING STRUCTURE) ---

# Kita gunakan DataProcessor sebagai 'Source of Truth' untuk logika kategori
dp = get_data_processor()

def extract_hashtags(text):
    """Extract hashtags from caption"""
    if pd.isna(text):
        return []
    hashtags = re.findall(r'#\w+', str(text))
    return hashtags

def count_hashtags(text):
    """Count number of hashtags"""
    return len(extract_hashtags(text))

def calculate_hours_since_publish(upload_time, reference_time=None):
    """Calculate hours since publish"""
    from datetime import timezone

    if reference_time is None:
        reference_time = datetime.now(timezone.utc)

    # Ensure both datetimes have compatible timezone information
    if upload_time.tzinfo is not None and reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)
    elif upload_time.tzinfo is None and reference_time.tzinfo is not None:
        upload_time = upload_time.replace(tzinfo=timezone.utc)

    time_diff = reference_time - upload_time
    hours = time_diff.total_seconds() / 3600
    return max(0, hours)

# --- CORE PREPROCESSING FUNCTION (UPDATED) ---
def preprocess_raw_data(df_raw, reference_time=None):
    """
    Preprocess raw TikTok data into model-ready features
    Menggunakan logika DataProcessor agar konsisten dengan Notebook Langkah 4
    """
    df = df_raw.copy()

    # 1. Basic engagement metrics & Rename
    df['Suka'] = df['diggCount']
    df['Komentar'] = df['commentCount']
    df['Dibagikan'] = df['shareCount']
    df['Durasi_Video'] = df['videoMeta.duration']

    # 2. Caption analysis
    df['Jumlah_Hashtag'] = df['text'].apply(count_hashtags)
    df['Panjang_Caption'] = df['text'].apply(lambda x: len(str(x)) if not pd.isna(x) else 0)

    # 3. Temporal features
    df['createTimeISO'] = pd.to_datetime(df['createTimeISO'])
    
    # Timezone handling for hours_since_publish
    if reference_time is None:
        from datetime import timezone
        reference_time = datetime.now(timezone.utc)
    
    # Ensure UTC for calculations
    if df['createTimeISO'].dt.tz is None:
        iso_series = df['createTimeISO'].dt.tz_localize('UTC')
    else:
        iso_series = df['createTimeISO'].dt.tz_convert('UTC')

    df['Jam_Sejak_Publikasi'] = iso_series.apply(
        lambda x: calculate_hours_since_publish(x, reference_time)
    )

    # Fitur Waktu Model
    df['Jam_Posting'] = df['createTimeISO'].dt.hour
    df['Jam_Upload'] = df['Jam_Posting'] # Alias
    df['Hari_Posting'] = df['createTimeISO'].dt.day_name()
    # Is_Weekend (Fitur Baru)
    df['Is_Weekend'] = df['Hari_Posting'].apply(lambda x: 1 if x in ['Saturday', 'Sunday'] else 0)
    # Hari Upload (Numerik 0-6)
    df['Hari_Upload'] = df['createTimeISO'].dt.dayofweek

    # 4. Content & Audio Classification (Using DP Logic for Consistency)
    # Gunakan logika kamus 10 kategori dari DataProcessor
    df['content_type_detected'] = df['text'].apply(dp._classify_content_logic)
    
    # Audio Logic (Load Top 20 if needed)
    if not dp.list_audio_populer and 'musicMeta.musicName' in df.columns:
         dp.list_audio_populer = df['musicMeta.musicName'].value_counts().head(20).index.tolist()
    
    df['audio_type_detected'] = df.apply(dp._classify_audio_logic, axis=1)

    # 5. One-hot Encoding (Dynamic based on Dictionary)
    
    # Kategori (Gaming, Fashion, dll)
    all_categories = list(dp.KAMUS_KATEGORI.keys()) + ['Lainnya']
    for cat in all_categories:
        col_name = f"Kat_{cat}"
        # Buat kolom 1/0
        df[col_name] = (df['content_type_detected'] == cat).astype(int)
        
        # Buat juga alias Tipe_Konten_X jika diperlukan untuk kompatibilitas tampilan
        df[f"Tipe_Konten_{cat}"] = df[col_name]

    # Audio
    all_audios = ['Audio Original', 'Audio Populer', 'Audio Lainnya']
    for audio in all_audios:
        col_name = f"Audio_{audio}"
        df[col_name] = (df['audio_type_detected'] == audio).astype(int)
        # Alias
        df[f"Tipe_Audio_{audio}"] = df[col_name]

    # 6. Interaction Features (Looping)
    # Interaksi = Kat_X * Suka
    for cat in all_categories:
        cat_col = f"Kat_{cat}"
        interaksi_col = f"Interaksi_{cat}_Suka"
        df[interaksi_col] = df[cat_col] * df['Suka']

    # 7. Additional Features (Legacy Support/Trends)
    df['Kekuatan_Tren_Audio'] = df['audio_type_detected'].apply(lambda x: 0.9 if x == 'Audio Populer' else 0.5)
    # Estimasi Tren Hashtag sederhana
    hashtag_engagement = df['Suka'] + df['Komentar'] + df['Dibagikan']
    p75 = hashtag_engagement.quantile(0.75) if not hashtag_engagement.empty else 0
    df['Kekuatan_Tren_Hashtag'] = hashtag_engagement.apply(lambda x: 0.9 if x >= p75 else 0.5)
    
    df['Apakah_Kolaborasi'] = df['text'].apply(lambda x: 1 if any(k in str(x).lower() for k in ['collab', 'ft']) else 0)
    df['Format_Konten_Video'] = 1 # Asumsi Vertical

    # 8. Organize Columns
    # Kita simpan semua kolom hasil engineering
    # Tambahkan ID dan Caption untuk referensi
    if 'Video_ID' not in df.columns:
        df.insert(0, 'Video_ID', range(1, len(df) + 1))
    
    if 'text' in df.columns and 'Caption' not in df.columns:
        df.insert(1, 'Caption', df['text'])

    return df

# --- DOWNLOAD TEMPLATE SECTION ---
st.subheader("📥 Download Template Data Mentah")

col1, col2 = st.columns([1, 3])

with col1:
    # Create raw template (Updated example data)
    raw_template = pd.DataFrame({
        'authorMeta.name': ['septianndt', 'septianndt'],
        'text': ['Main Genshin Impact seru #game #genshin', 'Tutorial masak nasi goreng #masak #resep'],
        'diggCount': [150, 500],
        'shareCount': [10, 30],
        'playCount': [5000, 15000],
        'commentCount': [20, 50],
        'videoMeta.duration': [30, 45],
        'musicMeta.musicName': ['Trending Song', 'original sound'],
        'musicMeta.musicOriginal': [False, True],
        'createTimeISO': ['2024-01-15T14:30:00.000Z', '2024-01-16T10:00:00.000Z'],
        'webVideoUrl': ['https://tiktok.com/v1', 'https://tiktok.com/v2']
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

# --- FILE UPLOAD SECTION ---
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
            'videoMeta.duration', 'musicMeta.musicName', 'createTimeISO'
        ]

        missing_columns = [col for col in required_raw_columns if col not in df_raw.columns]

        if missing_columns:
            st.warning(f"⚠️ Kolom yang hilang: {', '.join(missing_columns)}")
            st.info("Preprocessing akan mencoba berjalan dengan kolom yang tersedia.")
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
                help="Jika dicentang, akan menghitung jam sejak publikasi dari waktu saat ini."
            )

        with col2:
            if not use_current_time:
                from datetime import timezone
                reference_date = st.date_input("Tanggal Referensi", value=datetime.now().date())
                reference_time_input = st.time_input("Waktu Referensi", value=datetime.now().time())
                reference_time = datetime.combine(reference_date, reference_time_input)
                reference_time = reference_time.replace(tzinfo=timezone.utc)
            else:
                reference_time = None

        st.markdown("---")

        # Process button
        if st.button("🔧 Proses Data", use_container_width=True, type="primary"):
            with st.spinner("Sedang memproses data (Klasifikasi Konten & Audio)..."):
                # Preprocess data
                df_processed = preprocess_raw_data(df_raw, reference_time)

                # Store in session state for Batch Prediction
                st.session_state['preprocessed_data'] = df_processed.copy()
                st.session_state['preprocessed_data_ready'] = True

                st.success("✅ Preprocessing selesai!")

                st.markdown("---")

                # Show processing summary (UPDATED FOR NEW CATEGORIES)
                st.header("📊 Hasil Preprocessing")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Video", len(df_processed))

                # Tampilkan top 3 kategori terbanyak
                top_cats = df_processed['content_type_detected'].value_counts().head(3)
                
                if len(top_cats) > 0:
                    with col2: st.metric(f"Top 1: {top_cats.index[0]}", top_cats.iloc[0])
                if len(top_cats) > 1:
                    with col3: st.metric(f"Top 2: {top_cats.index[1]}", top_cats.iloc[1])
                if len(top_cats) > 2:
                    with col4: st.metric(f"Top 3: {top_cats.index[2]}", top_cats.iloc[2])

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
                
                # Show columns of interest
                preview_cols = ['Video_ID', 'Caption', 'content_type_detected', 'Suka', 'Jam_Posting', 'Is_Weekend']
                # Add Interaction columns preview
                preview_cols += [c for c in df_processed.columns if 'Interaksi_' in c][:2] # Show 2 interaksi pertama
                
                st.dataframe(df_processed[[c for c in preview_cols if c in df_processed.columns]].head(10), use_container_width=True)

                st.markdown("---")

                # Feature summary (UPDATED)
                st.subheader("📋 Ringkasan Fitur yang Dihasilkan")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("""
                    **Engagement Metrics:**
                    - ✅ Suka, Komentar, Dibagikan

                    **Video Properties:**
                    - ✅ Durasi_Video, Jumlah_Hashtag, Panjang_Caption

                    **Temporal Features:**
                    - ✅ Hari_Upload, Jam_Upload, Jam_Sejak_Publikasi
                    - ✅ Is_Weekend (Sabtu/Minggu)
                    """)

                with col2:
                    st.markdown("""
                    **Content Type (One-hot):**
                    - ✅ Kat_Gaming, Kat_Fashion, Kat_Kuliner, dll (10 Kategori)

                    **Audio Type (One-hot):**
                    - ✅ Audio_Original, Audio_Populer, Audio_Lainnya

                    **Interaction Features:**
                    - ✅ Interaksi_Gaming_Suka, dll (Perkalian Kategori x Suka)
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

                # CSV Export (Model Ready)
                with col2:
                    # Filter only features needed for model (exclude metadata like URL)
                    exclude_cols = ['webVideoUrl', 'createTimeISO', 'musicMeta.musicName', 'musicMeta.musicOriginal', 'text']
                    model_cols = [c for c in df_processed.columns if c not in exclude_cols]
                    
                    df_for_prediction = df_processed[model_cols].copy()
                    csv_for_prediction = df_for_prediction.to_csv(index=False)

                    st.download_button(
                        label="📥 Unduh CSV (Siap Prediksi)",
                        data=csv_for_prediction,
                        file_name=f"data_ready_for_prediction_{timestamp}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="Hanya features yang diperlukan untuk prediksi"
                    )

                # Excel Export (FIXED: Remove Timezone)
                with col3:
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        # Buat salinan agar tidak merusak dataframe asli di session_state
                        df_excel = df_processed.copy()
                        
                        # --- PERBAIKAN UTAMA: Hapus Zona Waktu ---
                        # Cari kolom datetime yang punya timezone
                        for col in df_excel.select_dtypes(include=['datetime', 'datetimetz']).columns:
                            # Konversi ke string atau hapus timezone
                            df_excel[col] = df_excel[col].dt.tz_localize(None)
                        # -----------------------------------------

                        df_excel.to_excel(writer, index=False, sheet_name='Processed Data')
                        
                        # Summary Sheet
                        summary_df = pd.DataFrame({
                            'Metric': ['Total Data', 'Top Category', 'Top Audio'],
                            'Value': [
                                len(df_processed), 
                                df_processed['content_type_detected'].mode()[0] if not df_processed['content_type_detected'].empty else "-",
                                df_processed['audio_type_detected'].mode()[0] if not df_processed['audio_type_detected'].empty else "-"
                            ]
                        })
                        summary_df.to_excel(writer, index=False, sheet_name='Summary')

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

                # Next steps (Direct Action)
                st.subheader("🎯 Langkah Selanjutnya")

                st.success("""
                **Data Anda sudah siap! Pilih salah satu:**

                **Opsi 1: Langsung Prediksi (Otomatis)**
                - Klik tombol "Langsung ke Batch Prediction" di bawah
                - Data akan otomatis dimuat di halaman Batch Prediction

                **Opsi 2: Download & Upload Manual**
                1. ✅ Download file CSV "Siap Prediksi"
                2. ✅ Buka halaman **Batch Prediction**
                3. ✅ Upload file yang sudah didownload
                """)

                if st.button("📤 Langsung ke Batch Prediction (Auto-load Data)", use_container_width=True, type="primary"):
                    # Set flag to auto-load data in Batch Prediction page
                    st.session_state['auto_load_preprocessed'] = True
                    st.switch_page("pages/4_📤_Prediksi_Massal.py")

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat memproses file: {str(e)}")
        st.exception(e)

else:
    # Show when no file uploaded
    st.info("📁 Silakan upload file CSV dengan data mentah TikTok")

    st.markdown("---")

    # Show example comparison (Mempertahankan contoh visual kode lama)
    st.subheader("📝 Contoh: Data Mentah vs Data Diproses")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Data Mentah (Input):**")
        example_raw = pd.DataFrame({
            'text': ['Main Genshin seru #game'],
            'diggCount': [150],
            'videoMeta.duration': [30],
            'createTimeISO': ['2024-01-15T14:30:00.000Z']
        })
        st.dataframe(example_raw, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Data Diproses (Output):**")
        example_processed = pd.DataFrame({
            'Suka': [150],
            'Durasi_Video': [30],
            'Kat_Gaming': [1], # Kategori baru
            'Is_Weekend': [0], # Fitur baru
            'Interaksi_Gaming_Suka': [150] # Fitur interaksi
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