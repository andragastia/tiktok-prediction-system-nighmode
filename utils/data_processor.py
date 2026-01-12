"""
Data Processor Module
Handles loading, preprocessing, and optimized classification of TikTok data
(Final Robust Version: Singleton Destruction Mechanism)
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

class DataProcessor:
    """Handle data loading and preprocessing"""

    def __init__(self):
        # TEKNIK JANGKAR: Cari file relatif terhadap folder 'utils' ini berada
        # 1. Cari folder dimana script ini (data_processor.py) berada
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Naik satu level ke folder root project (keluar dari folder 'utils')
        root_project_dir = os.path.dirname(current_file_dir)
        
        # 3. Masuk ke folder 'data' dan cari filenya
        self.data_path = os.path.join(root_project_dir, 'data', 'dataset_tiktok.csv')
        
        # [DEBUG] Print ke terminal agar Anda bisa lihat path pastinya
        print(f"🔗 [SYSTEM PATH] Data Processor menggunakan file: {self.data_path}")
        
        self.df = None
        # ... (sisanya sama) ...        
        # Print path ke terminal (agar bisa dicek di layar hitam cmd/terminal)
        print(f"DEBUG PATH: {self.data_path}")
        
        self.df = None
        self.list_audio_populer = [] 

        # Mapping Hari
        self.day_mapping = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu',
            'Sunday': 'Minggu'
        }

        # Kamus 10 Kategori
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
        try:
            if not os.path.exists(self.data_path):
                print(f"❌ Error: File tidak ditemukan di {self.data_path}")
                return None

            # [DEBUG] Baca Raw Data
            df = pd.read_csv(self.data_path)
            total_awal = len(df)
            print(f"📊 [DEBUG] Total baris mentah di CSV: {total_awal}")

            # --- 1. CLEANING ---
            numeric_cols = ['diggCount', 'commentCount', 'shareCount', 'playCount', 'videoMeta.duration']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    df[col] = 0

            # --- 2. METRICS ---
            df['engagement_rate'] = (
                (df['diggCount'] + df['commentCount'] + df['shareCount']) /
                df['playCount'].replace(0, 1)
            ) * 100

            # --- 3. TIME PARSING (TITIK KRITIS) ---
            # Kita konversi tanggal. Yang gagal jadi NaT (Not a Time)
            df['createTimeISO'] = pd.to_datetime(df['createTimeISO'], errors='coerce')
            
            # [DEBUG] Cek berapa yang NaT (Rusak)
            baris_rusak = df[df['createTimeISO'].isna()]
            if not baris_rusak.empty:
                print(f"⚠️ [WARNING] Ada {len(baris_rusak)} baris dengan tanggal rusak/kosong yang akan DIHAPUS!")
                # Tampilkan contoh data yang rusak di Terminal
                print("   Contoh data rusak:")
                print(baris_rusak.head(1).to_string())

            # Hapus yang rusak
            df = df.dropna(subset=['createTimeISO']) 

            # ... (Sisa kode sama: Waktu_Posting, Upload Day, dll) ...
            df['Waktu_Posting'] = df['createTimeISO']
            df['upload_date'] = df['createTimeISO'].dt.date
            df['upload_hour'] = df['createTimeISO'].dt.hour
            df['Jam_Posting'] = df['createTimeISO'].dt.hour 
            
            df['upload_day_english'] = df['createTimeISO'].dt.day_name()
            df['upload_day'] = df['upload_day_english'].map(self.day_mapping)
            df['Hari_Posting'] = df['upload_day_english'] 
            df['upload_year'] = df['createTimeISO'].dt.year
            df['upload_month'] = df['createTimeISO'].dt.month_name()
            df['Is_Weekend'] = df['Hari_Posting'].apply(lambda x: 1 if x in ['Saturday', 'Sunday'] else 0)
            
            # --- 4. TEXT & CATEGORY ---
            df['Panjang_Caption'] = df['text'].astype(str).apply(len)
            df['Jumlah_Hashtag'] = df['text'].astype(str).apply(lambda x: len(re.findall(r'#\w+', x)))
            df['content_type'] = df['text'].apply(self._classify_content_logic)
            df['Kategori_Konten'] = df['content_type']

            # --- 5. AUDIO ---
            if 'musicMeta.musicName' in df.columns:
                self.list_audio_populer = df['musicMeta.musicName'].value_counts().head(20).index.tolist()
            
            df['audio_type'] = df.apply(self._classify_audio_logic, axis=1)
            df['Tipe_Audio'] = df['audio_type']

            self.df = df
            print(f"✅ [SUCCESS] Data bersih yang dimuat: {len(self.df)} baris. (Selisih: {total_awal - len(self.df)})")
            return self.df

        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            self.df = None
            return None
        
    # --- HELPER METHODS ---
    def _classify_content_logic(self, text):
        if pd.isna(text): return 'Lainnya'
        text_lower = str(text).lower()
        for kategori, keywords in self.KAMUS_KATEGORI.items():
            if any(keyword in text_lower for keyword in keywords): return kategori
        return 'Lainnya'

    def _classify_audio_logic(self, row):
        music_name = row.get('musicMeta.musicName', '')
        
        # 1. HANDLING KOSONG (Prioritas)
        if pd.isna(music_name) or str(music_name).strip() in ['', '-', 'nan']:
            return 'Tanpa Audio'
            
        music_name_str = str(music_name)
        music_name_lower = music_name_str.lower()
        
        if music_name_lower in ['tidak ada musik', 'no music']:
             return 'Tanpa Audio'

        is_original = row.get('musicMeta.musicOriginal', False)
        
        # 2. ORIGINAL
        if (str(is_original).lower() == 'true' or is_original == True) or \
           ('original sound' in music_name_lower) or \
           ('suara asli' in music_name_lower):
            return 'Audio Original'
        
        # 3. POPULER
        elif music_name_str in self.list_audio_populer:
            return 'Audio Populer'
        
        # 4. LAINNYA
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
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        perf = target_df.groupby('audio_type').agg({'playCount': 'mean', 'webVideoUrl': 'count'})
        perf.columns = ['Rata-rata Tayangan', 'Jumlah Video'] 
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

    # --- PREDICTION FEATURES ---
    def prepare_features_for_prediction(self, raw_features):
        text_content = raw_features.get('text_content', '')
        detected_category = self._classify_content_logic(text_content)
        user_audio_choice = raw_features.get('audio_type', 'Audio Lainnya') 
        
        features = {
            'Jam_Posting': raw_features.get('upload_hour', 12),
            'Is_Weekend': 1 if raw_features.get('upload_day', 0) in [5, 6] else 0,
            'Panjang_Caption': raw_features.get('caption_length', 0),
            'Jumlah_Hashtag': raw_features.get('hashtag_count', 0),
            'Suka': raw_features.get('likes', 0),
            'Durasi_Video': raw_features.get('duration', 0)
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

# --- GLOBAL INSTANCE MANAGEMENT (CRITICAL FIX) ---
# Variable global ini menyimpan instance DataProcessor
_data_processor_instance = None

def get_data_processor(force_reload=False):
    """
    Mengambil atau membuat ulang DataProcessor.
    Args:
        force_reload (bool): Jika True, HANCURKAN instance lama dan buat baru.
                             Ini WAJIB dipanggil setelah menyimpan data baru.
    """
    global _data_processor_instance
    
    if _data_processor_instance is None or force_reload:
        print("🔄 [SYSTEM] Membuat Instance DataProcessor Baru...")
        _data_processor_instance = DataProcessor()
        _data_processor_instance.load_data()
    
    return _data_processor_instance