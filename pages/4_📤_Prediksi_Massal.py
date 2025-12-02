"""
Batch Prediction Page
CSV upload interface for bulk predictions
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime
from io import BytesIO

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.model_handler import get_model_handler
from utils.data_processor import get_data_processor
from utils.visualizations import create_pie_chart, create_bar_chart, create_heatmap

# Page config
st.set_page_config(
    page_title="Prediksi Massal - Sistem Prediksi TikTok",
    page_icon="📤",
    layout="wide"
)


# Header
st.title("📤 Prediksi Massal (Batch Prediction)")
st.markdown("Upload file CSV untuk memprediksi banyak video sekaligus")

# Load model
@st.cache_resource
def load_model():
    """Load and cache model"""
    return get_model_handler()

model_handler = load_model()

st.markdown("---")

# Information section
with st.expander("ℹ️ Panduan Penggunaan"):
    st.markdown("""
    ### Cara Menggunakan:

    1. **Download template CSV** menggunakan tombol di bawah
    2. **Isi template** dengan data video Anda
    3. **Upload file CSV** yang sudah diisi
    4. **Klik "Jalankan Prediksi"** untuk memproses
    5. **Download hasil** dalam format CSV atau Excel

    ### Format CSV:
    File CSV harus memiliki kolom-kolom berikut (sesuai dengan 22 features model):
    - `Suka`, `Komentar`, `Dibagikan`, `Durasi_Video`, `Jumlah_Hashtag`
    - `Jam_Sejak_Publikasi`, `Panjang_Caption`, `Hari_Upload`, `Jam_Upload`
    - `Kekuatan_Tren_Audio`, `Kekuatan_Tren_Hashtag`, `Apakah_Kolaborasi`
    - `Format_Konten_Video`, dan kolom tipe konten/audio (one-hot encoded)

    ### Kolom Opsional:
    - `Actual`: Label aktual untuk perbandingan (0=Tidak Trending, 1=Trending)
    - `Video_ID`: ID unik untuk identifikasi video
    - `Caption`: Caption video untuk referensi
    """)

st.markdown("---")

# Template download
st.subheader("📥 Download Template CSV")

# Create template DataFrame
template_data = {
    'Video_ID': [1, 2, 3],
    'Caption': ['Contoh video 1', 'Contoh video 2', 'Contoh video 3'],
    'Suka': [100, 500, 1000],
    'Komentar': [10, 50, 100],
    'Dibagikan': [5, 25, 50],
    'Durasi_Video': [30, 45, 60],
    'Jumlah_Hashtag': [3, 5, 4],
    'Jam_Sejak_Publikasi': [24, 48, 72],
    'Panjang_Caption': [50, 80, 100],
    'Hari_Upload': [1, 2, 5],  # 0=Monday, 1=Tuesday, etc.
    'Jam_Upload': [12, 15, 18],
    'Kekuatan_Tren_Audio': [0.5, 0.7, 0.9],
    'Kekuatan_Tren_Hashtag': [0.6, 0.8, 0.7],
    'Apakah_Kolaborasi': [0, 0, 1],
    'Format_Konten_Video': [1, 1, 2],  # 1=Vertical, 2=Horizontal, 3=Square
    'Tipe_Konten_Lainnya': [0, 0, 0],
    'Tipe_Konten_OOTD': [1, 0, 0],
    'Tipe_Konten_Tutorial': [0, 1, 0],
    'Tipe_Konten_Vlog': [0, 0, 1],
    'Tipe_Audio_Audio Lainnya': [0, 0, 0],
    'Tipe_Audio_Audio Original': [1, 0, 0],
    'Tipe_Audio_Audio Populer': [0, 1, 1],
    'Interaksi_Tutorial_x_Komentar': [0, 50, 0],
    'Interaksi_OOTD_x_Dibagikan': [5, 0, 0],
    'Actual': [0, 1, 1]  # Optional: actual labels for comparison
}

template_df = pd.DataFrame(template_data)

# Convert to CSV
csv_template = template_df.to_csv(index=False)

col1, col2 = st.columns([1, 3])
with col1:
    st.download_button(
        label="📥 Unduh Template CSV",
        data=csv_template,
        file_name="template_prediksi_tiktok.csv",
        mime="text/csv",
        use_container_width=True
    )
with col2:
    st.info("💡 Template berisi 3 contoh data. Hapus baris contoh dan isi dengan data Anda sendiri.")

st.markdown("---")

# File upload
st.subheader("📁 Upload File CSV")

# Check if there's preprocessed data from Data Preprocessing page
uploaded_file = None
df = None

if st.session_state.get('auto_load_preprocessed', False) and st.session_state.get('preprocessed_data_ready', False):
    # Auto-load preprocessed data
    df = st.session_state.get('preprocessed_data')
    if df is not None:
        st.info("ℹ️ Data otomatis dimuat dari halaman Data Preprocessing")
        st.success(f"✅ Data berhasil dimuat! Total baris: {len(df)}")

        # Show preview
        with st.expander("👁️ Preview Data (5 baris pertama)"):
            st.dataframe(df.head(), use_container_width=True)

        # Clear the auto-load flag so it doesn't auto-load on refresh
        st.session_state['auto_load_preprocessed'] = False

if df is None:
    # Show file uploader if no auto-loaded data
    uploaded_file = st.file_uploader(
        "Pilih file CSV untuk diprediksi",
        type=['csv'],
        help="Upload file CSV yang sudah diisi dengan data video"
    )

if uploaded_file is not None:
    try:
        # Load CSV
        df = pd.read_csv(uploaded_file)

        st.success(f"✅ File berhasil diunggah! Total baris: {len(df)}")

        # Show preview
        with st.expander("👁️ Preview Data (5 baris pertama)"):
            st.dataframe(df.head(), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Gagal membaca file: {str(e)}")
        st.stop()

# Process data if available (either from upload or auto-load)
if df is not None:
    try:
        # Get required features from model
        required_features = model_handler.feature_names

        # Check for required columns
        missing_columns = set(required_features) - set(df.columns)

        if missing_columns:
            st.error(f"❌ Kolom yang hilang: {', '.join(missing_columns)}")
            st.warning("Pastikan file CSV memiliki semua kolom yang diperlukan. Download template untuk referensi.")
            st.stop()

        st.success("✅ Semua kolom yang diperlukan tersedia!")

        # Check for 'Actual' column
        has_actual = 'Actual' in df.columns

        if has_actual:
            st.info("📊 Kolom 'Actual' ditemukan. Analisis perbandingan akan tersedia setelah prediksi.")

        st.markdown("---")

        # Prediction button
        if st.button("🚀 Jalankan Prediksi", use_container_width=True, type="primary"):
            with st.spinner("Sedang memproses prediksi..."):
                # Extract features
                X = df[required_features]

                # Make predictions
                predictions, probabilities = model_handler.predict_batch(X)

                if predictions is not None:
                    # Add predictions to dataframe
                    df['Prediksi'] = predictions
                    df['Prediksi_Label'] = df['Prediksi'].map({
                        0: 'Tidak Trending',
                        1: 'Trending'
                    })
                    df['Confidence'] = probabilities.max(axis=1)
                    df['Prob_Tidak_Trending'] = probabilities[:, 0]
                    df['Prob_Trending'] = probabilities[:, 1]

                    st.success("✅ Prediksi berhasil dilakukan!")

                    st.markdown("---")

                    # Display results
                    st.header("📊 Hasil Prediksi")

                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            label="Total Video",
                            value=len(df)
                        )

                    with col2:
                        trending_count = (df['Prediksi'] == 1).sum()
                        st.metric(
                            label="Diprediksi Trending",
                            value=trending_count,
                            delta=f"{trending_count/len(df)*100:.1f}%"
                        )

                    with col3:
                        not_trending_count = (df['Prediksi'] == 0).sum()
                        st.metric(
                            label="Tidak Trending",
                            value=not_trending_count,
                            delta=f"{not_trending_count/len(df)*100:.1f}%"
                        )

                    with col4:
                        avg_confidence = df['Confidence'].mean()
                        st.metric(
                            label="Avg. Confidence",
                            value=f"{avg_confidence*100:.1f}%"
                        )

                    st.markdown("---")

                    # Visualizations
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("📊 Distribusi Prediksi")

                        # Pie chart
                        prediction_counts = df['Prediksi_Label'].value_counts()
                        fig_pie = create_pie_chart(
                            values=prediction_counts.values,
                            names=prediction_counts.index,
                            title="Distribusi Hasil Prediksi",
                            hole=0.4
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)

                    with col2:
                        st.subheader("📈 Distribusi Confidence Score")

                        # Histogram of confidence
                        conf_dist = df.groupby(pd.cut(df['Confidence'], bins=10)).size().reset_index()
                        conf_dist.columns = ['Range', 'Count']
                        conf_dist['Range'] = conf_dist['Range'].astype(str)

                        fig_conf = create_bar_chart(
                            conf_dist,
                            x='Range',
                            y='Count',
                            title="Distribusi Confidence Score",
                            xaxis_title="Confidence Range",
                            yaxis_title="Jumlah Video"
                        )
                        st.plotly_chart(fig_conf, use_container_width=True)

                    st.markdown("---")

                    # Comparison Analysis (if actual labels available)
                    if has_actual:
                        st.header("🔍 Analisis Perbandingan")

                        from sklearn.metrics import (
                            confusion_matrix,
                            accuracy_score,
                            precision_score,
                            recall_score,
                            f1_score,
                            classification_report
                        )

                        y_true = df['Actual']
                        y_pred = df['Prediksi']

                        # Metrics
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            accuracy = accuracy_score(y_true, y_pred)
                            st.metric("Akurasi", f"{accuracy*100:.1f}%")

                        with col2:
                            precision = precision_score(y_true, y_pred, zero_division=0)
                            st.metric("Presisi", f"{precision*100:.1f}%")

                        with col3:
                            recall = recall_score(y_true, y_pred, zero_division=0)
                            st.metric("Recall", f"{recall*100:.1f}%")

                        with col4:
                            f1 = f1_score(y_true, y_pred, zero_division=0)
                            st.metric("F1-Score", f"{f1*100:.1f}%")

                        st.markdown("---")

                        # Confusion Matrix
                        col1, col2 = st.columns([1, 1])

                        with col1:
                            st.subheader("📊 Confusion Matrix")

                            cm = confusion_matrix(y_true, y_pred)

                            # Create heatmap
                            fig_cm = create_heatmap(
                                data=cm,
                                x_labels=['Tidak Trending', 'Trending'],
                                y_labels=['Tidak Trending', 'Trending'],
                                title="Confusion Matrix",
                                colorscale='Blues'
                            )
                            st.plotly_chart(fig_cm, use_container_width=True)

                        with col2:
                            st.subheader("📋 Classification Report")

                            # Classification report
                            report = classification_report(
                                y_true,
                                y_pred,
                                target_names=['Tidak Trending', 'Trending'],
                                output_dict=True
                            )

                            report_df = pd.DataFrame(report).transpose()
                            report_df = report_df[['precision', 'recall', 'f1-score', 'support']]
                            report_df = report_df.round(3)

                            st.dataframe(report_df, use_container_width=True)

                        # Misclassified videos
                        misclassified = df[df['Actual'] != df['Prediksi']]

                        if len(misclassified) > 0:
                            st.markdown("---")
                            st.subheader("❌ Video yang Salah Diprediksi")

                            st.warning(f"Total video yang salah diprediksi: {len(misclassified)} dari {len(df)} ({len(misclassified)/len(df)*100:.1f}%)")

                            # Show misclassified videos
                            display_cols = ['Video_ID', 'Caption', 'Actual', 'Prediksi_Label', 'Confidence']
                            display_cols = [col for col in display_cols if col in misclassified.columns]

                            if len(display_cols) > 0:
                                st.dataframe(
                                    misclassified[display_cols].head(10),
                                    use_container_width=True,
                                    hide_index=True
                                )
                        else:
                            st.success("✅ Semua prediksi benar! Akurasi 100%")

                    st.markdown("---")

                    # Results table
                    st.subheader("📋 Detail Hasil Prediksi")

                    # Select columns to display
                    display_columns = ['Video_ID', 'Caption'] if 'Video_ID' in df.columns and 'Caption' in df.columns else []
                    display_columns += ['Prediksi_Label', 'Confidence', 'Prob_Trending', 'Prob_Tidak_Trending']

                    if has_actual:
                        display_columns.insert(2, 'Actual')

                    # Filter columns that exist
                    display_columns = [col for col in display_columns if col in df.columns]

                    # Format and display
                    result_df = df[display_columns].copy()

                    if 'Confidence' in result_df.columns:
                        result_df['Confidence'] = result_df['Confidence'].apply(lambda x: f"{x*100:.1f}%")
                    if 'Prob_Trending' in result_df.columns:
                        result_df['Prob_Trending'] = result_df['Prob_Trending'].apply(lambda x: f"{x*100:.1f}%")
                    if 'Prob_Tidak_Trending' in result_df.columns:
                        result_df['Prob_Tidak_Trending'] = result_df['Prob_Tidak_Trending'].apply(lambda x: f"{x*100:.1f}%")

                    st.dataframe(result_df, use_container_width=True, hide_index=True)

                    st.markdown("---")

                    # Export section
                    st.subheader("💾 Ekspor Hasil")

                    col1, col2, col3 = st.columns(3)

                    # CSV Export
                    with col1:
                        csv_data = df.to_csv(index=False)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                        st.download_button(
                            label="📥 Unduh CSV",
                            data=csv_data,
                            file_name=f"hasil_prediksi_{timestamp}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                    # Excel Export
                    with col2:
                        buffer = BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='Prediksi')

                        excel_data = buffer.getvalue()

                        st.download_button(
                            label="📥 Unduh Excel",
                            data=excel_data,
                            file_name=f"hasil_prediksi_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

                    # Summary Export (predictions only)
                    with col3:
                        summary_cols = display_columns
                        summary_df = df[summary_cols]
                        summary_csv = summary_df.to_csv(index=False)

                        st.download_button(
                            label="📥 Unduh Ringkasan",
                            data=summary_csv,
                            file_name=f"ringkasan_prediksi_{timestamp}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                else:
                    st.error("❌ Terjadi kesalahan saat melakukan prediksi. Silakan cek format data Anda.")

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat memproses data: {str(e)}")
        st.exception(e)

# Show placeholder when no data available
if df is None and not st.session_state.get('preprocessed_data_ready', False):
    st.info("📁 Silakan upload file CSV atau gunakan fitur Data Preprocessing untuk memulai prediksi batch")

    # Show example
    st.markdown("---")
    st.subheader("📝 Contoh Format Data")

    example_df = pd.DataFrame({
        'Video_ID': [1, 2, 3],
        'Suka': [150, 500, 2000],
        'Komentar': [15, 50, 200],
        'Dibagikan': [8, 25, 100],
        'Durasi_Video': [30, 45, 60],
        'Jumlah_Hashtag': [3, 5, 4],
        '...': ['...', '...', '...']
    })

    st.dataframe(example_df, use_container_width=True, hide_index=True)
    st.caption("💡 Download template lengkap menggunakan tombol di atas")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>📤 Batch Prediction - Prediksi massal untuk analisis performa konten</p>
    <p>Mendukung format CSV dan Excel untuk ekspor hasil</p>
</div>
""", unsafe_allow_html=True)
