import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime

# Tambahkan path root agar bisa import utils
sys.path.append(str(Path(__file__).parent.parent))

# Import fungsi asli yang terbukti WORKS
from utils.input_handler import save_new_data_to_csv 
# Import data processor HANYA untuk mengambil daftar akun (Read Only)
from utils.data_processor import get_data_processor

st.set_page_config(page_title="Input Data Baru", page_icon="📝")

st.title("📝 Input Data Video Baru")
st.markdown("""
Halaman ini berfungsi untuk **menambahkan data latih baru** ke dalam sistem. 
Data yang disimpan akan otomatis masuk ke `dataset_tiktok.csv` dan langsung terbaca di **Dashboard Analitik**.
""")

# --- [BAGIAN TAMBAHAN 1] FITUR PILIH AKUN ---
# Ambil daftar akun yang sudah ada dari DataProcessor
dp = get_data_processor()
try:
    # Coba ambil list akun, jika gagal list kosong
    existing_authors = dp.get_unique_authors()
except:
    existing_authors = []

st.subheader("1. Identitas Akun")
author_mode = st.radio("Mode Akun:", ["Pilih Akun Lama", "Input Akun Baru"], horizontal=True)

if author_mode == "Pilih Akun Lama" and existing_authors:
    selected_author = st.selectbox("Nama Akun", options=existing_authors)
else:
    selected_author = st.text_input("Nama Akun Baru (tanpa @)", placeholder="contoh: tiktok_creator")

# --- FORMULIR ASLI (DENGAN SEDIKIT UPDATE UI) ---
with st.form("input_form"):
    st.subheader("2. Informasi Konten")
    text_content = st.text_area("Caption / Deskripsi Video", placeholder="Tulis caption lengkap video di sini...")
    
    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input("Durasi Video (detik)", min_value=1, value=60)
        
        # [BAGIAN TAMBAHAN 2] UI Audio yang lebih detail
        audio_type_opt = st.selectbox("Jenis Audio", ["Audio Original", "Audio Lainnya", "Audio Populer", "Tanpa Audio"])
        is_original_music = True if audio_type_opt == "Audio Original" else False
        
    with col2:
        # Auto-fill nama musik jika Original
        default_music_name = f"original sound - {selected_author}" if is_original_music else ""
        music_name = st.text_input("Nama Musik (Opsional)", value=default_music_name, placeholder="Judul lagu...")
        music_author = st.text_input("Pembuat Musik (Opsional)", value="-")

    st.subheader("3. Statistik Performa (Data Historis)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: play_count = st.number_input("Jumlah Views (Play)", min_value=0, step=100)
    with c2: digg_count = st.number_input("Jumlah Likes (Digg)", min_value=0, step=10)
    with c3: share_count = st.number_input("Jumlah Shares", min_value=0, step=1)
    with c4: comment_count = st.number_input("Jumlah Comments", min_value=0, step=1)

    st.subheader("4. Waktu Upload")
    d_date = st.date_input("Tanggal Upload", datetime.now())
    d_time = st.time_input("Jam Upload", datetime.now().time())

    # Tombol Submit
    submitted = st.form_submit_button("💾 Simpan ke Database", type="primary")

    if submitted:
        # Validasi sederhana
        if not text_content:
            st.error("❌ Caption video tidak boleh kosong!")
        elif not selected_author:
            st.error("❌ Nama akun tidak boleh kosong!")
        else:
            # Format Waktu ISO 8601 (Sesuai dataset TikTok)
            full_datetime = datetime.combine(d_date, d_time)
            create_time_iso = full_datetime.strftime('%Y-%m-%dT%H:%M:%S.000Z')

            # Mapping input ke nama kolom dataset_tiktok.csv
            input_data = {
                # [DATA BARU] Masukkan Akun yang Dipilih
                'authorMeta.name': selected_author,
                'authorMeta.nickName': selected_author, 
                'authorMeta.verified': False, # Default
                
                # Data Konten
                'text': text_content,
                'videoMeta.duration': duration,
                'musicMeta.musicOriginal': is_original_music,
                'musicMeta.musicName': music_name if music_name else f"Sound ({audio_type_opt})",
                'musicMeta.musicAuthor': music_author,
                
                # Statistik
                'playCount': play_count,
                'diggCount': digg_count,
                'shareCount': share_count,
                'commentCount': comment_count,
                
                # Waktu
                'createTimeISO': create_time_iso,
                
                # Data Teknis Tambahan (Agar tidak error saat dibaca Dashboard)
                'webVideoUrl': 'manual_input',
                'videoMeta.height': 1920,
                'videoMeta.width': 1080,
                'id': f"manual_{int(datetime.now().timestamp())}"
            }

            # --- EKSEKUSI PENYIMPANAN (MENGGUNAKAN FUNGSI ASLI ANDA) ---
            # Kita mengirim dictionary yang LEBIH LENGKAP ke fungsi lama
            success, message = save_new_data_to_csv(input_data)
            
            if success:
                st.success(f"✅ {message}")
                
                # --- UPDATE DASHBOARD AGAR TERBACA ---
                st.cache_data.clear() # 1. Hapus cache view
                
                # 2. Paksa DataProcessor baca ulang file CSV dari disk
                # (Ini penting agar dashboard tidak pakai data lama di RAM)
                get_data_processor(force_reload=True) 
                
                # 3. Trigger rerun dashboard
                st.session_state["data_changed"] = True 
                
                st.info("🔄 Cache dibersihkan. Data baru siap ditampilkan di Dashboard.")
                
                # Tampilkan preview data yang disimpan
                with st.expander("Lihat Data Tersimpan"):
                    st.json(input_data)
            else:
                st.error(f"❌ Gagal: {message}")