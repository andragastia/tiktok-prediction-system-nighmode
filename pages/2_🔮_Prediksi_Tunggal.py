"""
Single Prediction Page
Interactive form for predicting individual video performance
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.model_handler import get_model_handler
from utils.data_processor import get_data_processor
from utils.visualizations import create_bar_chart, format_number

# Page config
st.set_page_config(
    page_title="Prediksi Tunggal - Sistem Prediksi TikTok",
    page_icon="🔮",
    layout="wide"
)


# Header
st.title("🔮 Prediksi Performa Video Tunggal")
st.markdown("Prediksi apakah konten Anda berpotensi **Trending** atau **Tidak Trending**")

# Load model and data
@st.cache_resource
def load_model():
    """Load and cache model"""
    return get_model_handler()

@st.cache_data
def load_reference_data():
    """Load reference statistics"""
    dp = get_data_processor()
    return {
        'avg_likes': dp.df['diggCount'].mean(),
        'avg_comments': dp.df['commentCount'].mean(),
        'avg_shares': dp.df['shareCount'].mean(),
        'avg_duration': dp.df['videoMeta.duration'].mean(),
        'trending_threshold': dp.get_trending_threshold(75)
    }

model_handler = load_model()
ref_data = load_reference_data()

st.markdown("---")

# Information section
with st.expander("ℹ️ Panduan Penggunaan"):
    st.markdown("""
    ### Cara Menggunakan:

    1. **Isi semua field** pada form di bawah dengan informasi video Anda
    2. **Klik tombol "🔮 Prediksi Sekarang"** untuk mendapatkan hasil
    3. **Lihat hasil prediksi** beserta confidence score
    4. **Baca rekomendasi** untuk optimasi konten

    ### Tips:
    - Gunakan data dari video serupa sebagai referensi
    - Nilai rata-rata ditampilkan sebagai panduan
    - Semua field wajib diisi untuk prediksi akurat
    """)

st.markdown("---")

# Input Form
st.header("📝 Masukkan Informasi Video")

with st.form("prediction_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📊 Metrik Engagement")

        likes = st.number_input(
            "Jumlah Suka (estimasi)",
            min_value=0,
            value=int(ref_data['avg_likes']),
            help=f"Rata-rata: {ref_data['avg_likes']:,.0f} suka"
        )

        comments = st.number_input(
            "Jumlah Komentar (estimasi)",
            min_value=0,
            value=int(ref_data['avg_comments']),
            help=f"Rata-rata: {ref_data['avg_comments']:,.0f} komentar"
        )

        shares = st.number_input(
            "Jumlah Dibagikan (estimasi)",
            min_value=0,
            value=int(ref_data['avg_shares']),
            help=f"Rata-rata: {ref_data['avg_shares']:,.0f} shares"
        )

    with col2:
        st.subheader("🎬 Detail Video")

        duration = st.number_input(
            "Durasi Video (detik)",
            min_value=1,
            max_value=180,
            value=int(ref_data['avg_duration']),
            help=f"Rata-rata: {ref_data['avg_duration']:.0f} detik"
        )

        hashtag_count = st.number_input(
            "Jumlah Hashtag",
            min_value=0,
            max_value=30,
            value=3,
            help="Jumlah hashtag dalam caption"
        )

        caption_length = st.number_input(
            "Panjang Caption",
            min_value=0,
            max_value=500,
            value=50,
            help="Jumlah karakter dalam caption"
        )

        hours_since_publish = st.number_input(
            "Jam Sejak Publikasi",
            min_value=0,
            max_value=168,
            value=24,
            help="Berapa jam sejak video dipublikasikan (untuk prediksi performa)"
        )

    with col3:
        st.subheader("🎨 Kategori Konten")

        content_type = st.selectbox(
            "Tipe Konten",
            options=["OOTD", "Tutorial", "Vlog", "Lainnya"],
            help="Pilih kategori konten yang paling sesuai"
        )

        audio_type = st.selectbox(
            "Tipe Audio",
            options=["Audio Original", "Audio Populer", "Audio Lainnya"],
            help="Jenis audio yang digunakan"
        )

        upload_day = st.selectbox(
            "Hari Upload",
            options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            index=1,  # Default to Tuesday (best day)
            help="Hari dalam seminggu untuk upload"
        )

        upload_hour = st.slider(
            "Jam Upload (24H)",
            min_value=0,
            max_value=23,
            value=12,
            help="Jam upload dalam format 24 jam"
        )

        is_collaboration = st.checkbox(
            "Apakah Kolaborasi?",
            value=False,
            help="Centang jika video adalah kolaborasi"
        )

    st.markdown("---")

    # Additional settings
    with st.expander("⚙️ Pengaturan Lanjutan (Opsional)"):
        col1, col2 = st.columns(2)

        with col1:
            video_format = st.selectbox(
                "Format Konten Video",
                options=["Vertikal (9:16)", "Horizontal (16:9)", "Persegi (1:1)"],
                help="Format aspek rasio video"
            )

        with col2:
            audio_trend = st.slider(
                "Kekuatan Tren Audio (0-1)",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
                help="Seberapa trending audio yang digunakan (0=tidak trending, 1=sangat trending)"
            )

            hashtag_trend = st.slider(
                "Kekuatan Tren Hashtag (0-1)",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
                help="Seberapa trending hashtag yang digunakan"
            )

    # Submit button
    st.markdown("---")
    submitted = st.form_submit_button("🔮 Prediksi Sekarang", use_container_width=True, type="primary")

# Process prediction
if submitted:
    st.markdown("---")

    with st.spinner("Memproses prediksi..."):
        # Map day to number
        day_mapping = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }

        # Map video format
        format_mapping = {
            "Vertikal (9:16)": 1,
            "Horizontal (16:9)": 2,
            "Persegi (1:1)": 3
        }

        # Prepare features for model
        features = {
            'Suka': likes,
            'Komentar': comments,
            'Dibagikan': shares,
            'Durasi_Video': duration,
            'Jumlah_Hashtag': hashtag_count,
            'Jam_Sejak_Publikasi': hours_since_publish,
            'Panjang_Caption': caption_length,
            'Hari_Upload': day_mapping[upload_day],
            'Jam_Upload': upload_hour,
            'Kekuatan_Tren_Audio': audio_trend,
            'Kekuatan_Tren_Hashtag': hashtag_trend,
            'Apakah_Kolaborasi': 1 if is_collaboration else 0,
            'Format_Konten_Video': format_mapping[video_format],
            'Tipe_Konten_Lainnya': 1 if content_type == 'Lainnya' else 0,
            'Tipe_Konten_OOTD': 1 if content_type == 'OOTD' else 0,
            'Tipe_Konten_Tutorial': 1 if content_type == 'Tutorial' else 0,
            'Tipe_Konten_Vlog': 1 if content_type == 'Vlog' else 0,
            'Tipe_Audio_Audio Lainnya': 1 if audio_type == 'Audio Lainnya' else 0,
            'Tipe_Audio_Audio Original': 1 if audio_type == 'Audio Original' else 0,
            'Tipe_Audio_Audio Populer': 1 if audio_type == 'Audio Populer' else 0,
            'Interaksi_Tutorial_x_Komentar': comments if content_type == 'Tutorial' else 0,
            'Interaksi_OOTD_x_Dibagikan': shares if content_type == 'OOTD' else 0,
        }

        # Make prediction
        prediction, confidence, probabilities = model_handler.predict(features)

    # Display results
    st.header("🎯 Hasil Prediksi")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Prediction result
        if prediction == 1:
            st.success("### 🎉 PREDIKSI: TRENDING!")
            st.markdown("""
            Video Anda diprediksi akan **TRENDING**! 🚀

            Konten ini memiliki potensi tinggi untuk mendapatkan engagement yang baik dan reach yang luas.
            """)
        else:
            st.warning("### ⚠️ PREDIKSI: Tidak Trending")
            st.markdown("""
            Video ini diprediksi **Tidak Trending** berdasarkan parameter yang diberikan.

            Namun, jangan khawatir! Lihat rekomendasi di bawah untuk optimasi.
            """)

    with col2:
        # Confidence score
        st.metric(
            label="Tingkat Keyakinan",
            value=f"{confidence*100:.1f}%",
            delta="Confidence Score"
        )

        # Probability breakdown
        st.markdown("**Probabilitas:**")
        st.progress(probabilities[1], text=f"Trending: {probabilities[1]*100:.1f}%")
        st.progress(probabilities[0], text=f"Tidak Trending: {probabilities[0]*100:.1f}%")

    st.markdown("---")

    # Feature Importance for this prediction
    st.subheader("📊 Faktor Paling Berpengaruh")

    col1, col2 = st.columns([2, 1])

    with col1:
            # Get feature importance from model
            feature_imp = model_handler.get_feature_importance()

            if feature_imp is not None:
                # Display top 10 features
                top_features = feature_imp.head(10).copy() 
               
                rename_fitur = {
                    'Suka': 'Jumlah Suka',
                    'Komentar': 'Jumlah Komentar',
                    'Dibagikan': 'Jumlah Dibagikan',
                    'Durasi_Video': 'Durasi Video',
                    'Jumlah_Hashtag': 'Jumlah Hashtag',
                    'Jam_Sejak_Publikasi': 'Jam Sejak Publikasi',
                    'Panjang_Caption': 'Panjang Caption',
                    'Hari_Upload': 'Hari Upload',
                    'Jam_Upload': 'Jam Upload',
                    'Format_Konten_Video': 'Format Video',
                    'Tipe_Konten_Lainnya': 'Tipe Konten: Lainnya',
                    'Tipe_Konten_OOTD': 'Tipe Konten: OOTD',
                    'Tipe_Konten_Tutorial': 'Tipe Konten: Tutorial',
                    'Tipe_Konten_Vlog': 'Tipe Konten: Vlog',
                    'Tipe_Audio_Audio Lainnya': 'Audio: Lainnya',
                    'Tipe_Audio_Audio Original': 'Audio: Original',
                    'Tipe_Audio_Audio Populer': 'Audio: Populer'
                }

                # Mengganti isi kolom 'feature' menggunakan kamus di atas
                # Jika ada fitur yang tidak ada di kamus, dia akan tetap pakai nama aslinya
                top_features['feature'] = top_features['feature'].map(rename_fitur).fillna(top_features['feature'])
                # ========================================================

                fig_importance = create_bar_chart(
                    top_features,
                    x='feature',
                    y='importance',
                    title="10 Faktor Penentu Utama",
                    xaxis_title="Faktor",
                    yaxis_title="Tingkat Pengaruh",
                    orientation='h'
                )
                st.plotly_chart(fig_importance, use_container_width=True)

    with col2:
        st.markdown("**Insight:**")
        st.markdown(f"""
        Berdasarkan model Random Forest, faktor-faktor berikut paling berpengaruh terhadap prediksi:

        1. **{feature_imp.iloc[0]['feature']}** ({feature_imp.iloc[0]['importance']*100:.1f}%)
        2. **{feature_imp.iloc[1]['feature']}** ({feature_imp.iloc[1]['importance']*100:.1f}%)
        3. **{feature_imp.iloc[2]['feature']}** ({feature_imp.iloc[2]['importance']*100:.1f}%)

        Fokus pada metrik-metrik ini untuk meningkatkan performa!
        """)

    st.markdown("---")

    # Recommendations
    st.subheader("💡 Rekomendasi")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Yang Sudah Baik:")

        recommendations_good = []

        if upload_day == "Tuesday":
            recommendations_good.append("✓ Upload di hari terbaik (Tuesday)")

        if audio_type == "Audio Populer":
            recommendations_good.append("✓ Menggunakan audio populer")

        if hashtag_count >= 3:
            recommendations_good.append("✓ Jumlah hashtag sudah cukup")

        if duration >= 15 and duration <= 60:
            recommendations_good.append("✓ Durasi video optimal (15-60 detik)")

        if likes > ref_data['avg_likes']:
            recommendations_good.append("✓ Target likes di atas rata-rata")

        if len(recommendations_good) > 0:
            for rec in recommendations_good:
                st.success(rec)
        else:
            st.info("Masih ada ruang untuk optimasi")

    with col2:
        st.markdown("### 🔄 Saran Perbaikan:")

        recommendations_improve = []

        if upload_day != "Tuesday":
            recommendations_improve.append("📅 Coba upload di hari Tuesday untuk performa lebih baik")

        if audio_type != "Audio Populer":
            recommendations_improve.append("🎵 Pertimbangkan menggunakan audio yang sedang trending")

        if duration < 15:
            recommendations_improve.append("⏱️ Perpanjang durasi video (minimal 15 detik)")
        elif duration > 60:
            recommendations_improve.append("⏱️ Pertimbangkan durasi lebih pendek (30-60 detik)")

        if hashtag_count < 3:
            recommendations_improve.append("🏷️ Tambahkan lebih banyak hashtag relevan (3-5 hashtag)")

        if likes < ref_data['avg_likes']:
            recommendations_improve.append(f"❤️ Targetkan lebih dari {ref_data['avg_likes']:,.0f} likes")

        if comments < ref_data['avg_comments']:
            recommendations_improve.append("💬 Buat konten yang mendorong komentar (ajukan pertanyaan)")

        if shares < ref_data['avg_shares']:
            recommendations_improve.append("🔄 Buat konten yang shareable (informatif atau menghibur)")

        if len(recommendations_improve) > 0:
            for rec in recommendations_improve:
                st.warning(rec)
        else:
            st.success("Semua parameter sudah optimal! 🎉")

    st.markdown("---")

    # Comparison with average
    st.subheader("📈 Perbandingan dengan Rata-rata")

    comparison_data = pd.DataFrame({
        'Metrik': ['Suka', 'Komentar', 'Dibagikan', 'Durasi (detik)'],
        'Input Anda': [likes, comments, shares, duration],
        'Rata-rata': [ref_data['avg_likes'], ref_data['avg_comments'],
                      ref_data['avg_shares'], ref_data['avg_duration']]
    })

    comparison_data['Selisih (%)'] = ((comparison_data['Input Anda'] - comparison_data['Rata-rata']) /
                                       comparison_data['Rata-rata'] * 100).round(1)

    st.dataframe(
        comparison_data.style.format({
            'Input Anda': '{:,.0f}',
            'Rata-rata': '{:,.0f}',
            'Selisih (%)': '{:+.1f}%'
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # Action items
    st.subheader("🎯 Langkah Selanjutnya")

    if prediction == 1:
        st.success("""
        **Konten Anda berpotensi trending! Pastikan:**
        1. ✅ Upload di waktu yang tepat
        2. ✅ Gunakan thumbnail yang menarik
        3. ✅ Tambahkan caption yang engaging
        4. ✅ Promosikan di platform lain
        5. ✅ Balas komentar untuk meningkatkan engagement
        """)
    else:
        st.info("""
        **Untuk meningkatkan peluang trending:**
        1. 🔄 Review dan terapkan saran perbaikan di atas
        2. 📊 Pelajari video trending serupa
        3. 🎨 Tingkatkan kualitas konten (visual, audio, storytelling)
        4. ⏰ Eksperimen dengan waktu upload yang berbeda
        5. 🏷️ Gunakan hashtag yang sedang trending
        """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>💡 Prediksi berdasarkan Random Forest Model dengan 100 trees dan akurasi tinggi</p>
    <p>Hasil prediksi bersifat estimasi dan dapat bervariasi dengan kondisi aktual</p>
</div>
""", unsafe_allow_html=True)
