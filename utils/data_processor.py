"""
Data Processor Module
Handles loading, preprocessing, and optimized classification of TikTok data
(Final Version: Updated Audio Logic Sync with Notebook)
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

class DataProcessor:
    """Handle data loading and preprocessing"""

    def __init__(self):
        # Gunakan Absolute Path untuk keamanan lokasi file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(os.path.dirname(current_dir), 'data', 'dataset_tiktok.csv')
        
        self.df = None
        self.list_audio_populer = [] 

        # Mapping Hari
        self.day_mapping = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu',
            'Sunday': 'Minggu'
        }

        # Kamus 10 Kategori Lengkap
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
        Membaca data dari CSV.
        PENTING: Selalu membaca ulang dari disk (pd.read_csv) untuk menangkap data baru.
        """
        try:
            if not os.path.exists(self.data_path):
                print(f"❌ Error: File tidak ditemukan di {self.data_path}")
                return None

            # [KUNCI PERBAIKAN] Selalu baca baru dari file CSV.
            df = pd.read_csv(self.data_path)

            # --- 1. CLEANING & TYPE CONVERSION ---
            numeric_cols = ['diggCount', 'commentCount', 'shareCount', 'playCount', 'videoMeta.duration']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    df[col] = 0

            # --- 2. CALCULATED METRICS ---
            df['engagement_rate'] = (
                (df['diggCount'] + df['commentCount'] + df['shareCount']) /
                df['playCount'].replace(0, 1)
            ) * 100

            # --- 3. TIME PARSING ---
            df['createTimeISO'] = pd.to_datetime(df['createTimeISO'], errors='coerce')
            df = df.dropna(subset=['createTimeISO']) 

            df['Waktu Posting'] = df['createTimeISO']
            df['upload_date'] = df['createTimeISO'].dt.date
            df['upload_hour'] = df['createTimeISO'].dt.hour
            df['Jam Posting'] = df['createTimeISO'].dt.hour 
            
            df['upload_day_english'] = df['createTimeISO'].dt.day_name()
            df['upload_day'] = df['upload_day_english'].map(self.day_mapping)
            df['Hari Posting'] = df['upload_day_english'] 
            df['upload_year'] = df['createTimeISO'].dt.year
            df['upload_month'] = df['createTimeISO'].dt.month_name()

            df['Is_Weekend'] = df['Hari Posting'].apply(lambda x: 1 if x in ['Saturday', 'Sunday'] else 0)

            # --- 4. TEXT & CATEGORY ---
            df['Panjang Caption'] = df['text'].astype(str).apply(len)
            df['Jumlah Hashtag'] = df['text'].astype(str).apply(lambda x: len(re.findall(r'#\w+', x)))
            
            df['content_type'] = df['text'].apply(self._classify_content_logic)
            df['Kategori Konten'] = df['content_type']

            # --- 5. AUDIO (UPDATED LOGIC) ---
            if 'musicMeta.musicName' in df.columns:
                # Ambil Top 20 Lagu Terpopuler dari data saat ini
                self.list_audio_populer = df['musicMeta.musicName'].value_counts().head(20).index.tolist()
            
            df['audio_type'] = df.apply(self._classify_audio_logic, axis=1)
            df['Tipe Audio'] = df['audio_type']

            # Jika semua berhasil, baru simpan ke variable class
            self.df = df
            print(f"✅ Data loaded successfully: {len(self.df)} records.")
            return self.df

        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            self.df = None
            return None

    # --- HELPER METHODS (Optimized Logic) ---
    def _classify_content_logic(self, text):
        if pd.isna(text): return 'Lainnya'
        text_lower = str(text).lower()
        for kategori, keywords in self.KAMUS_KATEGORI.items():
            if any(keyword in text_lower for keyword in keywords): return kategori
        return 'Lainnya'

    def _classify_audio_logic(self, row):
        """
        Logika Klasifikasi Audio (DIPERBAIKI)
        Prioritas: 
        1. Cek Kosong (NaN/Empty String) -> 'Tanpa Audio'
        2. Cek Original -> 'Audio Original'
        3. Cek Populer -> 'Audio Populer'
        4. Sisanya -> 'Audio Lainnya'
        """
        music_name = row.get('musicMeta.musicName', '')
        
        # 1. HANDLING DATA KOSONG / NULL (Prioritas Tertinggi)
        # Cek jika NaN, None, atau string kosong atau strip
        if pd.isna(music_name) or str(music_name).strip() == '' or str(music_name).strip() == '-':
            return 'Tanpa Audio'
            
        music_name_str = str(music_name)
        music_name_lower = music_name_str.lower()
        
        # Cek literal 'tidak ada musik' atau 'no music'
        if music_name_lower in ['tidak ada musik', 'no music', 'original sound', 'suara asli']:
             # Jika 'original sound' tanpa nama artis, seringkali ini suara asli video (voiceover)
             # Namun bisa juga 'Tanpa Audio' jika videonya hening. 
             # Untuk aman, kita cek is_original flag di bawah.
             pass

        is_original = row.get('musicMeta.musicOriginal', False)
        
        # 2. LOGIKA AUDIO ORIGINAL
        if (str(is_original).lower() == 'true' or is_original == True) or \
           ('original sound' in music_name_lower) or \
           ('suara asli' in music_name_lower):
            return 'Audio Original'
        
        # 3. LOGIKA AUDIO POPULER (Top 20)
        elif music_name_str in self.list_audio_populer:
            return 'Audio Populer'
        
        # 4. SISANYA
        else:
            return 'Audio Lainnya'

    # --- DASHBOARD & STATS ---
    def get_unique_authors(self):
        if self.df is None: self.load_data()
        if self.df is None: return []
        if 'authorMeta.name' in self.df.columns:
            return sorted(self.df['authorMeta.name'].astype(str).unique().tolist())
        return []

    def get_summary_stats(self, df=None):
        target_df = df if df is not None else self.df
        if target_df is None or target_df.empty or 'engagement_rate' not in target_df.columns:
            return {}

        return {
            'total_videos': len(target_df),
            'total_views': target_df['playCount'].sum(),
            'total_likes': target_df['diggCount'].sum(),
            'total_comments': target_df['commentCount'].sum(),
            'total_shares': target_df['shareCount'].sum(),
            'avg_views': target_df['playCount'].mean(),
            'avg_likes': target_df['diggCount'].mean(), 
            'avg_engagement_rate': target_df['engagement_rate'].mean(),
            'avg_duration': target_df['videoMeta.duration'].mean(),
            'date_range': {'start': target_df['createTimeISO'].min(), 'end': target_df['createTimeISO'].max()}
        }

    def get_leaderboard(self):
        if self.df is None: self.load_data()
        if self.df is None: return pd.DataFrame()
        
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
        """
        [FIXED] Mengembalikan DataFrame dengan Mean Views DAN Jumlah Video
        """
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        
        perf = target_df.groupby('audio_type').agg({'playCount': 'mean', 'webVideoUrl': 'count'})
        perf.columns = ['Rata-rata Tayangan', 'Jumlah Video'] # Rename kolom
        
        return perf.sort_values(by='Rata-rata Tayangan', ascending=False)

    def get_correlation_matrix(self, df=None):
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        cols = ['playCount', 'diggCount', 'commentCount', 'shareCount', 'videoMeta.duration', 'engagement_rate']
        return target_df[cols].corr()
    
    def get_top_videos(self, df=None, n=10):
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        return target_df.nlargest(n, 'playCount')

    # --- PREDICTION FEATURES (Sync with Notebook) ---
    def prepare_features_for_prediction(self, raw_features):
        text_content = raw_features.get('text_content', '')
        detected_category = self._classify_content_logic(text_content)
        
        # Audio Classification for Input
        # (Karena kita tidak punya list_audio_populer global dari data user input,
        # kita andalkan input manual 'audio_type' dari form)
        user_audio_choice = raw_features.get('audio_type', 'Audio Lainnya') 
        
        features = {
            'Jam Posting': raw_features.get('upload_hour', 12),
            'Is_Weekend': 1 if raw_features.get('upload_day', 0) in [5, 6] else 0,
            'Panjang Caption': raw_features.get('caption_length', 0),
            'Jumlah Hashtag': raw_features.get('hashtag_count', 0),
            'Suka': raw_features.get('likes', 0),
            'Durasi Video': raw_features.get('duration', 0)
        }

        all_categories = list(self.KAMUS_KATEGORI.keys()) + ['Lainnya']
        for cat in all_categories:
            features[f"Kat_{cat}"] = 1 if detected_category == cat else 0
            
        all_audios = ['Audio Original', 'Audio Populer', 'Audio Lainnya', 'Tanpa Audio']
        for audio in all_audios:
            features[f"Audio_{audio}"] = 1 if user_audio_choice == audio else 0

        suka_val = features['Suka']
        for cat in all_categories:
            features[f"Interaksi_{cat}_Suka"] = features[f"Kat_{cat}"] * suka_val

        return pd.DataFrame([features])

# --- INSTANCE HANDLER (Force Reload Support) ---
_data_processor = None

def get_data_processor(force_reload=False):
    global _data_processor
    if _data_processor is None or force_reload:
        _data_processor = DataProcessor()
        _data_processor.load_data()
    return _data_processor