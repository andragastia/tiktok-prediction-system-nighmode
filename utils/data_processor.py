"""
Data Processor Module
Handles loading, preprocessing, and optimized classification of TikTok data
SINKRONISASI PENUH DENGAN JUPYTER NOTEBOOK (LANGKAH 4) & STRUKTUR DASHBOARD
(Updated: Force Reload Support to Fix Data Sync Issue)
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

class DataProcessor:
    """Handle data loading and preprocessing"""

    def __init__(self):
        """
        Initialize data processor with robust path handling
        """
        # Gunakan Absolute Path agar file selalu ditemukan (Safety Check)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(os.path.dirname(current_dir), 'data', 'dataset_tiktok.csv')
        
        self.df = None
        self.processed_df = None
        self.list_audio_populer = [] # Akan diisi dinamis saat load_data

        # --- 1. MAPPING HARI (INDONESIA) ---
        self.day_mapping = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu',
            'Sunday': 'Minggu'
        }

        # --- 2. KAMUS KATEGORI LENGKAP (SESUAI NOTEBOOK) ---
        self.KAMUS_KATEGORI = {
            'Gaming': ['game', 'genshin', 'impact', 'honkai', 'star', 'rail', 'mlbb', 'mobile', 'legend', 'esport', 'roblox', 'minecraft', 'valorant', 'win', 'lose', 'victory'],
            'Fashion': ['ootd', 'outfit', 'baju', 'hijab', 'gamis', 'dress', 'style', 'kain', 'batik', 'kebaya', 'jeans', 'haul', 'shopee', 'tas', 'sepatu'],
            'Daily': ['vlog', 'day', 'life', 'hari', 'jalan', 'trip', 'healing', 'cerita', 'kegiatan', 'minivlog', 'daily', 'routine', 'morning', 'kucing'],
            'Edukasi_Karir': ['magang', 'intern', 'kuliah', 'skripsi', 'belajar', 'tips', 'ilmu', 'kerja', 'karir', 'coding', 'tutorial', 'cara', 'kampus', 'mahasiswa'],
            'Religi': ['hijrah', 'kajian', 'islam', 'allah', 'doa', 'sholat', 'ramadan', 'ngaji', 'ustadz', 'dakwah', 'lebaran', 'puasa', 'muslim'],
            'Beauty': ['makeup', 'skincare', 'cantik', 'jerawat', 'lip', 'serum', 'sunscreen', 'foundation', 'bedak', 'glowing', 'acne', 'tutorialmakeup'],
            'Kuliner': ['makan', 'masak', 'resep', 'enak', 'kuliner', 'food', 'minum', 'jajan', 'mukbang', 'cook', 'cafe', 'coffee', 'mie', 'bakso'],
            'Hiburan': ['lucu', 'ngakak', 'komedi', 'prank', 'drama', 'meme', 'viral', 'fyp', 'pov', 'parodi', 'receh', 'ketawa', 'film', 'drakor'],
            'Musik_Konser': ['concert', 'konser', 'tour', 'ticket', 'stage', 'live', 'band', 'singer', 'lagu', 'music', 'musik', 'guitar', 'piano'],
            'Jedag Jedug': ['capcut', 'jedag', 'jedug', 'preset', 'alight', 'motion', 'jj', 'template']
        }

    def load_data(self):
        """
        Load and preprocess dataset from CSV (Sesuai Langkah 4 Notebook)
        [UPDATE] Selalu membaca ulang dari disk untuk menangkap data baru.
        """
        try:
            if not os.path.exists(self.data_path):
                print(f"❌ Error: File tidak ditemukan di {self.data_path}")
                return None

            # [FIX] Selalu baca baru, jangan gunakan cache internal self.df
            self.df = pd.read_csv(self.data_path)

            # A. Parsing Waktu & Fitur Waktu Dasar
            # [FIX] Tambahkan errors='coerce' untuk keamanan jika ada tanggal rusak
            self.df['createTimeISO'] = pd.to_datetime(self.df['createTimeISO'], errors='coerce')
            self.df = self.df.dropna(subset=['createTimeISO']) # Hapus baris jika tanggal gagal diparsing

            self.df['Waktu_Posting'] = self.df['createTimeISO'] # Alias
            self.df['upload_date'] = self.df['createTimeISO'].dt.date
            self.df['upload_hour'] = self.df['createTimeISO'].dt.hour
            self.df['Jam_Posting'] = self.df['createTimeISO'].dt.hour # Alias Notebook
            
            # Mapping Hari
            self.df['upload_day_english'] = self.df['createTimeISO'].dt.day_name()
            self.df['upload_day'] = self.df['upload_day_english'].map(self.day_mapping)
            self.df['Hari_Posting'] = self.df['upload_day_english'] # Alias Notebook
            self.df['upload_year'] = self.df['createTimeISO'].dt.year
            self.df['upload_month'] = self.df['createTimeISO'].dt.month_name()

            # B. Fitur Baru: Is_Weekend (Langkah 4B Notebook)
            self.df['Is_Weekend'] = self.df['Hari_Posting'].apply(lambda x: 1 if x in ['Saturday', 'Sunday'] else 0)

            # C. Fitur Teks (Langkah 4C Notebook)
            self.df['Panjang_Caption'] = self.df['text'].astype(str).apply(len)
            self.df['Jumlah_Hashtag'] = self.df['text'].astype(str).apply(lambda x: len(re.findall(r'#\w+', x)))

            # D. Kategori Konten & Audio Logic (Langkah 4A)
            # Klasifikasi Konten
            self.df['content_type'] = self.df['text'].apply(self._classify_content_logic)
            self.df['Kategori_Konten'] = self.df['content_type'] # Alias

            # Logika Audio Populer (Top 20)
            if 'musicMeta.musicName' in self.df.columns:
                self.list_audio_populer = self.df['musicMeta.musicName'].value_counts().head(20).index.tolist()
            
            self.df['audio_type'] = self.df.apply(self._classify_audio_logic, axis=1)
            self.df['Tipe_Audio'] = self.df['audio_type'] # Alias

            # E. Metrik Engagement (Untuk Dashboard)
            # [FIX] Konversi ke numeric untuk keamanan jika input manual berupa string
            for col in ['diggCount', 'commentCount', 'shareCount', 'playCount']:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)

            self.df['engagement_rate'] = (
                (self.df['diggCount'] + self.df['commentCount'] + self.df['shareCount']) /
                self.df['playCount'].replace(0, 1)
            ) * 100

            return self.df
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return None

    # --- HELPER METHODS (Optimized Logic) ---
    def _classify_content_logic(self, text):
        if pd.isna(text): return 'Lainnya'
        text_lower = str(text).lower()
        for kategori, keywords in self.KAMUS_KATEGORI.items():
            if any(keyword in text_lower for keyword in keywords):
                return kategori
        return 'Lainnya'

    def _classify_audio_logic(self, row):
        # Adaptasi logika notebook ke struktur kolom dataset
        music_name = row.get('musicMeta.musicName', '')
        is_original = row.get('musicMeta.musicOriginal', False)
        
        # Logika: Audio Asli vs Populer (Top 20) vs Lainnya
        if str(is_original).lower() == 'true' or is_original == True:
            return 'Audio Original'
        elif music_name in self.list_audio_populer:
            return 'Audio Populer'
        else:
            return 'Audio Lainnya'

    # --- FUNGSI PENDUKUNG DASHBOARD (TIDAK DIUBAH AGAR FLOW SAMA) ---
    def get_unique_authors(self):
        if self.df is None: self.load_data()
        if self.df is None: return []
        if 'authorMeta.name' in self.df.columns:
            return sorted(self.df['authorMeta.name'].astype(str).unique().tolist())
        return []

    def get_summary_stats(self, df=None):
        target_df = df if df is not None else self.df
        if target_df is None or target_df.empty: return {}
        return {
            'total_videos': len(target_df),
            'total_views': target_df['playCount'].sum(),
            'total_likes': target_df['diggCount'].sum(),
            'total_comments': target_df['commentCount'].sum(),
            'total_shares': target_df['shareCount'].sum(),
            'avg_views': target_df['playCount'].mean(),
            'avg_likes': target_df['diggCount'].mean(),
            'avg_comments': target_df['commentCount'].mean(),
            'avg_shares': target_df['shareCount'].mean(),
            'avg_engagement_rate': target_df['engagement_rate'].mean(),
            'avg_duration': target_df['videoMeta.duration'].mean(),
            'date_range': {'start': target_df['createTimeISO'].min(), 'end': target_df['createTimeISO'].max()}
        }

    def get_leaderboard(self):
        if self.df is None: self.load_data()
        if self.df is None: return pd.DataFrame()
        
        # Ganti 'id' dengan 'webVideoUrl' karena 'id' tidak ada di CSV
        leaderboard = self.df.groupby('authorMeta.name').agg({
            'playCount': 'sum', 'diggCount': 'sum', 'shareCount': 'sum',
            'webVideoUrl': 'count', 'engagement_rate': 'mean'
        }).reset_index()
        
        leaderboard.rename(columns={
            'authorMeta.name': 'Nama Akun', 'webVideoUrl': 'Jml Video',
            'playCount': 'Total Penayangan', 'diggCount': 'Total Suka',
            'shareCount': 'Total Bagikan', 'engagement_rate': 'Rata-rata ER (%)'
        }, inplace=True)
        return leaderboard.sort_values(by='Total Penayangan', ascending=False)

    def get_trending_threshold(self, percentile=75):
        if self.df is None: self.load_data()
        if self.df is None: return 0
        return self.df['playCount'].quantile(percentile / 100)

    # --- VISUALISASI HELPERS ---
    def get_performance_by_day(self, df=None):
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        day_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        return target_df.groupby('upload_day')['playCount'].mean().reindex(day_order)

    def get_performance_by_hour(self, df=None):
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        return target_df.groupby('upload_hour')['playCount'].mean()

    def get_content_type_performance(self, df=None):
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        perf = target_df.groupby('content_type').agg({'playCount': 'mean', 'webVideoUrl': 'count'})
        perf.columns = ['Rata-rata Tayangan', 'Jumlah Video']
        return perf.sort_values(by='Rata-rata Tayangan', ascending=False)

    def get_audio_type_performance(self, df=None):
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        return target_df.groupby('audio_type')['playCount'].mean()

    def get_correlation_matrix(self, df=None):
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        cols = ['playCount', 'diggCount', 'commentCount', 'shareCount', 'videoMeta.duration', 'engagement_rate']
        return target_df[cols].corr()
    
    def get_top_videos(self, df=None, n=10):
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        return target_df.nlargest(n, 'playCount')

    # --- UPDATE UTAMA: PREPARE FEATURES (Sesuai Langkah 4 Notebook) ---
    def prepare_features_for_prediction(self, raw_features):
        """
        Menyiapkan fitur agar SAMA PERSIS dengan format Training .ipynb
        """
        # 1. Ambil Data Mentah
        text_content = raw_features.get('text_content', '')
        detected_category = self._classify_content_logic(text_content)
        
        # Cek Audio (Simulasi logika Top 20 untuk input user)
        user_audio_choice = raw_features.get('audio_type', 'Audio Lainnya') 
        
        # 2. Bangun Dictionary Fitur Dasar (Sesuai Langkah 4B & 4C)
        features = {
            'Jam_Posting': raw_features.get('upload_hour', 12),
            # Is_Weekend: 1 jika Sabtu/Minggu. Input 'upload_day' (0-6) -> 5=Sabtu, 6=Minggu
            'Is_Weekend': 1 if raw_features.get('upload_day', 0) in [5, 6] else 0,
            'Panjang_Caption': raw_features.get('caption_length', 0),
            'Jumlah_Hashtag': raw_features.get('hashtag_count', 0),
            'Suka': raw_features.get('likes', 0), # Penting untuk interaksi
            
            # Jika model butuh fitur lain yg ada di notebook tapi tidak di input form, beri default 0
            # Contoh: 'Durasi_Video' (jika ada di model, meski di Langkah 4 notebook tidak eksplisit disebut direkayasa, biasanya tetap dipakai)
            'Durasi_Video': raw_features.get('duration', 0)
        }

        # 3. One-Hot Encoding (Langkah 4D: Prefix 'Kat_' dan 'Audio_')
        
        # List semua kategori di notebook (termasuk 'Lainnya')
        all_categories = list(self.KAMUS_KATEGORI.keys()) + ['Lainnya']
        for cat in all_categories:
            # Nama kolom harus 'Kat_Gaming', 'Kat_Fashion', dll.
            col_name = f"Kat_{cat}"
            features[col_name] = 1 if detected_category == cat else 0
            
        # List tipe audio
        all_audios = ['Audio Original', 'Audio Populer', 'Audio Lainnya']
        for audio in all_audios:
            # Nama kolom harus 'Audio_Audio Original', dll.
            col_name = f"Audio_{audio}"
            features[col_name] = 1 if user_audio_choice == audio else 0

        # 4. Fitur Interaksi (Langkah 4E: Interaksi_{Kategori}_Suka)
        # Notebook: df_encoded[f'Interaksi_{nama_kat}_Suka'] = df_encoded[col] * df_encoded['Suka']
        
        suka_val = features['Suka']
        
        for cat in all_categories:
            cat_col_name = f"Kat_{cat}" # Kolom One-Hot yg sudah dibuat
            interaksi_col_name = f"Interaksi_{cat}_Suka" # Nama Kolom Interaksi Baru
            
            # Nilai Interaksi = (1 atau 0) * Jumlah Suka
            features[interaksi_col_name] = features[cat_col_name] * suka_val

        return pd.DataFrame([features])

# --- INSTANCE HANDLER (Updated: Support Force Reload) ---
_data_processor = None

def get_data_processor(force_reload=False):
    """
    Get or create data processor instance.
    Args:
        force_reload (bool): If True, discards current instance and reloads from disk.
    """
    global _data_processor
    if _data_processor is None or force_reload:
        _data_processor = DataProcessor()
        _data_processor.load_data()
    return _data_processor