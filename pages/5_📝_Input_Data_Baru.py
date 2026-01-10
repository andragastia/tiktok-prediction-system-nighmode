"""
Input Data Baru Page
Menambahkan data video baru ke dataset secara manual
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
dp = get_data_processor()

# Header
st.title("📝 Input Data Video Baru")
st.markdown("Tambahkan data video baru ke dataset. Data akan otomatis muncul di Dashboard.")

st.markdown("---")

# --- FORMULIR INPUT ---
st.subheader("1. Identitas & Konten")

# Pilihan Akun
existing_authors = dp.get_unique_authors()
author_mode = st.radio("Akun Influencer:", ["Pilih Akun Lama", "Akun Baru"], horizontal=True)

if author_mode == "Pilih Akun Lama":
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

# --- LOGIKA PENYIMPANAN (PERBAIKAN UTAMA) ---
if submitted:
    if not author_name or not text_caption:
        st.error("❌ Nama Akun dan Caption wajib diisi!")
    else:
        try:
            # 1. Siapkan Data Baru
            create_time_iso = datetime.combine(upload_date, upload_time).isoformat()
            is_original_audio = True if audio_type == "Audio Original" else False
            
            new_data = {
                'text': text_caption,
                'diggCount': digg_count,
                'shareCount': share_count,
                'playCount': play_count,
                'commentCount': comment_count,
                'videoMeta.duration': duration,
                'musicMeta.musicName': music_name_placeholder,
                'musicMeta.musicOriginal': is_original_audio,
                'createTimeISO': create_time_iso,
                'webVideoUrl': video_url if video_url else f"manual_{int(datetime.now().timestamp())}",
                'authorMeta.name': author_name
            }
            
            # 2. Baca CSV Lama & Gabungkan
            # Kita baca manual pakai pandas untuk memastikan append berhasil
            if os.path.exists(dp.data_path):
                current_df = pd.read_csv(dp.data_path)
                new_row = pd.DataFrame([new_data])
                # Gabung
                updated_df = pd.concat([current_df, new_row], ignore_index=True)
            else:
                updated_df = pd.DataFrame([new_data])
            
            # 3. Simpan ke File (Overwrite file lama)
            updated_df.to_csv(dp.data_path, index=False)
            
            # --- [SOLUSI INTI] BERSIHKAN CACHE & MEMORI ---
            # 1. Hapus cache data Streamlit (agar dashboard membaca file baru)
            st.cache_data.clear()
            
            # 2. Reset instance DataProcessor (agar tidak pegang data lama)
            dp.df = None 
            
            # 3. Set sinyal untuk Dashboard
            st.session_state["data_changed"] = True
            # ----------------------------------------------

            st.success(f"✅ Data berhasil disimpan! (Total Data: {len(updated_df)})")
            
            with st.expander("👁️ Lihat Data Inputan"):
                st.dataframe(pd.DataFrame([new_data]))
            
            st.info("🔄 Cache sistem telah dibersihkan. Dashboard akan memuat data terbaru.")

        except Exception as e:
            st.error(f"Gagal menyimpan: {e}")

st.markdown("---")