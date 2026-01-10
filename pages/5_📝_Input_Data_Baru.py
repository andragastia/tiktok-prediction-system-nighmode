import streamlit as st
import pandas as pd
from datetime import datetime
from utils.input_handler import save_new_data_to_csv # Import fungsi yang baru kita buat

st.set_page_config(page_title="Input Data Baru", page_icon="📝")

st.title("📝 Input Data Video Baru")
st.markdown("""
Halaman ini berfungsi untuk **menambahkan data latih baru** ke dalam sistem. 
Data yang disimpan akan otomatis masuk ke `dataset_tiktok.csv` dan langsung terbaca di **Dashboard Analitik**.
""")

with st.form("input_form"):
    st.subheader("1. Informasi Konten")
    text_content = st.text_area("Caption / Deskripsi Video", placeholder="Tulis caption lengkap video di sini...")
    
    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input("Durasi Video (detik)", min_value=1, value=60)
        is_original_music = st.checkbox("Menggunakan Musik Original?", value=True)
    with col2:
        music_name = st.text_input("Nama Musik (Opsional)", value="Original Sound")
        music_author = st.text_input("Pembuat Musik (Opsional)", value="-")

    st.subheader("2. Statistik Performa (Data Historis)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        play_count = st.number_input("Jumlah Views (Play)", min_value=0, step=100)
    with c2:
        digg_count = st.number_input("Jumlah Likes (Digg)", min_value=0, step=10)
    with c3:
        share_count = st.number_input("Jumlah Shares", min_value=0, step=1)
    with c4:
        comment_count = st.number_input("Jumlah Comments", min_value=0, step=1)

    st.subheader("3. Waktu Upload")
    d_date = st.date_input("Tanggal Upload", datetime.now())
    d_time = st.time_input("Jam Upload", datetime.now().time())

    # Tombol Submit
    submitted = st.form_submit_button("💾 Simpan ke Database")

    if submitted:
        if not text_content:
            st.error("Caption video tidak boleh kosong!")
        else:
            # Gabungkan Tanggal & Waktu jadi format ISO 8601 (Sesuai dataset TikTok)
            # Contoh target: 2023-08-22T14:00:34.000Z
            full_datetime = datetime.combine(d_date, d_time)
            create_time_iso = full_datetime.strftime('%Y-%m-%dT%H:%M:%S.000Z')

            # Mapping input ke nama kolom dataset_tiktok.csv
            input_data = {
                'text': text_content,
                'videoMeta.duration': duration,
                'musicMeta.musicOriginal': is_original_music,
                'musicMeta.musicName': music_name,
                'musicMeta.musicAuthor': music_author,
                
                # Statistik
                'playCount': play_count,
                'diggCount': digg_count,
                'shareCount': share_count,
                'commentCount': comment_count,
                
                # Waktu
                'createTimeISO': create_time_iso
            }

            # Eksekusi Penyimpanan
            success, message = save_new_data_to_csv(input_data)
            
            if success:
                st.success(message)
                
                # UPDATE BAGIAN INI:
                st.cache_data.clear() 
                st.session_state["data_changed"] = True  # Kirim sinyal ke Dashboard
                
                st.info("Cache dibersihkan. Silakan buka Dashboard untuk melihat data baru.")
            else:
                st.error(message)