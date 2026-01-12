"""
Input Data Baru Page
Menambahkan data video baru ke dataset secara manual
(Final Fix: Safe Append Mode & Robust Column Alignment)
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_processor import get_data_processor

# Page config
st.set_page_config(
    page_title="Input Data Baru - Sistem Prediksi TikTok",
    page_icon="📝",
    layout="wide"
)

# Load Data Processor
# (Hanya load instance, tidak perlu force reload di awal)
dp = get_data_processor()

# Header
st.title("📝 Input Data Video Baru")
st.markdown("Tambahkan data video baru ke dataset. Data akan otomatis disesuaikan dengan struktur database.")

st.markdown("---")

# --- FORMULIR INPUT ---
st.subheader("1. Identitas & Konten")

# Pilihan Akun
# Gunakan try-except untuk handle jika dp.df masih kosong
try:
    existing_authors = dp.get_unique_authors()
except:
    existing_authors = []

author_mode = st.radio("Akun Influencer:", ["Pilih Akun Lama", "Akun Baru"], horizontal=True)

if author_mode == "Pilih Akun Lama" and existing_authors:
    author_name = st.selectbox("Nama Akun", options=existing_authors)
else:
    author_name = st.text_input("Nama Akun Baru (tanpa @)", placeholder="contoh: tiktok_creator")

with st.form("input_data_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        text_caption = st.text_area("Caption / Deskripsi", placeholder="#fyp #viral...", help="Wajib diisi untuk deteksi kategori")
        video_url = st.text_input("Link Video (URL)")
        audio_type = st.selectbox("Tipe Audio", ["Audio Original", "Audio Populer", "Audio Lainnya"])
        music_name_placeholder = f"Manual Input ({audio_type})" 

    with col2:
        st.markdown("**Metrik Performa**")
        play_count = st.number_input("Views", min_value=0, step=100)
        digg_count = st.number_input("Likes", min_value=0, step=10)
        comment_count = st.number_input("Comments", min_value=0, step=1)
        share_count = st.number_input("Shares", min_value=0, step=1)
        duration = st.number_input("Durasi (detik)", min_value=1, value=15)

    st.markdown("**Waktu Upload**")
    c1, c2 = st.columns(2)
    with c1: upload_date = st.date_input("Tanggal", value=datetime.now())
    with c2: upload_time = st.time_input("Jam", value=datetime.now().time())

    st.markdown("---")
    submitted = st.form_submit_button("💾 Simpan Data", type="primary", use_container_width=True)

# --- LOGIKA PENYIMPANAN AMAN (CORE FIX) ---
if submitted:
    if not author_name or not text_caption:
        st.error("❌ Nama Akun dan Caption wajib diisi!")
    else:
        try:
            # 1. Format Tanggal Standard (YYYY-MM-DD HH:MM:SS)
            # Format string ini sangat aman dan mudah dibaca oleh Pandas
            dt_obj = datetime.combine(upload_date, upload_time)
            create_time_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S") 
            
            is_original_audio = True if audio_type == "Audio Original" else False
            
            # 2. Pastikan File Ada & Baca Header
            # Kita hanya butuh header (baris pertama) untuk menyamakan kolom
            if os.path.exists(dp.data_path):
                # Baca 1 baris saja untuk efisiensi
                df_header = pd.read_csv(dp.data_path, nrows=1)
                existing_columns = df_header.columns.tolist()
            else:
                st.error("Database (dataset_tiktok.csv) tidak ditemukan!")
                st.stop()

            # 3. Buat DataFrame Baru dengan Struktur Kolom yang SAMA PERSIS
            # Ini mencegah kolom bergeser atau hilang
            new_row = pd.DataFrame(columns=existing_columns)
            new_row.loc[0] = np.nan # Inisialisasi baris kosong

            # 4. Mapping Data Input ke Kolom CSV
            data_map = {
                'text': text_caption,
                'diggCount': digg_count,
                'shareCount': share_count,
                'playCount': play_count,
                'commentCount': comment_count,
                'videoMeta.duration': duration,
                'musicMeta.musicName': music_name_placeholder,
                'musicMeta.musicOriginal': is_original_audio,
                'createTimeISO': create_time_str, # Format tanggal aman
                'webVideoUrl': video_url if video_url else f"manual_{int(datetime.now().timestamp())}",
                'authorMeta.name': author_name,
                
                # Isi kolom pelengkap agar tidak NaN (Penting!)
                'authorMeta.nickName': author_name,
                'authorMeta.verified': False,
                'musicMeta.musicAuthor': 'Unknown',
                'secretID': 'manual_input',
                'videoMeta.height': 0,
                'videoMeta.width': 0
            }

            # Masukkan data ke dalam kolom yang sesuai
            for col, val in data_map.items():
                if col in new_row.columns:
                    new_row.at[0, col] = val

            # Isi kolom lain yang kosong dengan nilai default aman (0)
            # Agar tidak dianggap baris rusak oleh DataProcessor
            new_row = new_row.fillna(0) 

            # 5. SIMPAN KE CSV (MODE APPEND)
            # mode='a' : Tambahkan ke bawah
            # header=False : Jangan tulis nama kolom lagi
            new_row.to_csv(dp.data_path, mode='a', header=False, index=False)
            
            # 6. FORCE RELOAD & CLEAR CACHE
            # Ini wajib agar Dashboard menyadari ada data baru
            st.cache_data.clear()
            get_data_processor(force_reload=True) # Reset instance global
            st.session_state["data_changed"] = True # Sinyal ke Dashboard
            
            st.success("✅ Berhasil! Data baru telah ditambahkan ke database.")
            
            with st.expander("👁️ Lihat Data yang Masuk"):
                st.dataframe(new_row)
                
            st.info("🔄 Cache sistem telah dibersihkan. Dashboard akan memuat data terbaru.")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat menyimpan: {e}")