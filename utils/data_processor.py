"""
Data Processor Module
Handles loading, preprocessing, and optimized classification of TikTok data
Tanpa dependensi berat (Sastrawi/Stopwords) untuk performa Streamlit yang cepat.
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re

class DataProcessor:
    """Handle data loading and preprocessing"""

    def __init__(self, data_path="data/dataset_tiktok.csv"):
        """
        Initialize data processor
        Args:
            data_path (str): Path to the dataset file
        """
        self.data_path = data_path
        self.df = None
        self.processed_df = None
        
        # --- 1. MAPPING HARI (INDONESIA) ---
        self.day_mapping = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu',
            'Sunday': 'Minggu'
        }

        # --- 2. KAMUS KATEGORI LENGKAP (DATABASE KATA KUNCI) ---
        # Digunakan untuk deteksi konten menggunakan 'Substring Matching' (Cepat & Ringan)
        self.KAMUS_KATEGORI = {
            'Gaming': [
                'game', 'genshin', 'impact', 'honkai', 'star', 'rail', 'abyss', 'mobile', 'legend', 'rank', 
                'ditusiofficial', 'ditusigaming', 'spiralabyss', 'ditusi', 'seele', 'kafka', 'blade', 'gameplay', 
                'gacha', 'esport', 'roblox', 'minecraft', 'valorant', 'mlbb', 'push', 'win', 'lose', 'victory'
            ],
            'Fashion': [
                'ootd', 'outfit', 'baju', 'hijab', 'gamis', 'dress', 'style', 'kain', 'batik', 'kebaya', 
                'jeans', 'denim', 'blouse', 'kulot', 'pashmina', 'scarf', 'look', 'styling', 'shopee', 'haul', 
                'unboxing', 'racun', 'rekomendasi', 'tas', 'bag', 'sepatu', 'mixmatch', 'wardrobe', 'cewebumi'
            ],
            'Daily': [
                'vlog', 'day', 'life', 'hari', 'jalan', 'trip', 'healing', 'cerita', 'kegiatan', 'minivlog',
                'story', 'diary', 'daily', 'routine', 'morning', 'activity', 'random', 'dump', 'recap', 'date', 
                'family', 'vibes', 'moment', 'liburan', 'staycation', 'pulang', 'mudik', 'roomtour', 'kucing'
            ],
            'Edukasi_Karir': [
                'magang', 'intern', 'kuliah', 'skripsi', 'belajar', 'tips', 'ilmu', 'kerja', 'karir', 'coding', 
                'developer', 'python', 'tutorial', 'cara', 'how', 'linkedin', 'loker', 'cv', 'interview', 
                'kampus', 'mahasiswa', 'wisuda', 'sidang', 'sekolah', 'guru', 'dosen', 'presentasi', 'study'
            ],
            'Religi': [
                'hijrah', 'kajian', 'islam', 'allah', 'doa', 'sholat', 'ramadan', 'ngaji', 'ustadz', 'dakwah',
                'lebaran', 'puasa', 'bukber', 'sahur', 'bismillah', 'alhamdulillah', 'masyaallah', 'muslim', 
                'mukena', 'sajadah', 'iman', 'alquran', 'hadist', 'ibadah', 'pahala', 'surga', 'taubat'
            ],
            'Beauty': [
                'makeup', 'skincare', 'cantik', 'jerawat', 'lip', 'serum', 'sunscreen', 'cushion', 'foundation', 
                'bedak', 'alis', 'mascara', 'glowing', 'acne', 'facial', 'toner', 'moisturizer', 'wardah', 
                'emina', 'somethinc', 'avoskin', 'bodycare', 'shampoo', 'parfum', 'liptint', 'tutorialmakeup'
            ],
            'Kuliner': [
                'makan', 'masak', 'resep', 'enak', 'kuliner', 'food', 'minum', 'jajan', 'pedas', 'mukbang', 
                'bikin', 'cook', 'cafe', 'coffee', 'kopi', 'snack', 'mie', 'bakso', 'nasi', 'sarapan', 
                'lunch', 'dinner', 'roti', 'ayam', 'daging', 'sambal', 'manis', 'gurih'
            ],
            'Hiburan': [
                'lucu', 'ngakak', 'komedi', 'prank', 'drama', 'meme', 'viral', 'fyp', 'dance', 'challenge', 
                'pov', 'parodi', 'receh', 'ketawa', 'funny', 'nonton', 'film', 'drakor', 'kpop', 'anime', 
                'wibu', 'cosplay'
            ],
            'Musik_Konser': [
                'concert', 'konser', 'tour', 'ticket', 'stage', 'live', 'band', 'singer', 'nyanyi', 'lirik', 
                'lagu', 'music', 'musik', 'guitar', 'piano', 'taylor', 'coldplay', 'tulus', 'mahalini', 
                'idol', 'playlist', 'spotify'
            ],
            'Jedag Jedug': [
                'capcut', 'jedag', 'jedug', 'preset', 'alight', 'motion', 'am', 'xml', 'jj', 'template'
            ]
        }

    def load_data(self):
        """
        Load the dataset from CSV
        Returns:
            pd.DataFrame: Loaded dataset
        """
        try:
            self.df = pd.read_csv(self.data_path)

            # Convert createTimeISO to datetime
            self.df['createTimeISO'] = pd.to_datetime(self.df['createTimeISO'])

            # Extract datetime features (UPDATE: Bahasa Indonesia)
            self.df['upload_date'] = self.df['createTimeISO'].dt.date
            self.df['upload_hour'] = self.df['createTimeISO'].dt.hour
            
            # Mapping Hari ke Bahasa Indonesia
            self.df['upload_day_english'] = self.df['createTimeISO'].dt.day_name()
            self.df['upload_day'] = self.df['upload_day_english'].map(self.day_mapping)
            
            self.df['upload_month'] = self.df['createTimeISO'].dt.month_name()
            self.df['upload_year'] = self.df['createTimeISO'].dt.year

            # Calculate engagement rate
            self.df['engagement_rate'] = (
                (self.df['diggCount'] + self.df['commentCount'] + self.df['shareCount']) /
                self.df['playCount'].replace(0, 1)
            ) * 100

            # --- UPDATE: Panggil Helper Function untuk Klasifikasi Cepat ---
            self.df['content_type'] = self.df['text'].apply(self._classify_content_logic)
            self.df['audio_type'] = self.df.apply(self._classify_audio_logic, axis=1)

            return self.df
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None

    # --- HELPER METHODS (Optimized Logic) ---
    def _classify_content_logic(self, text):
        """
        Logika klasifikasi konten TEROPTIMASI.
        Menggantikan Stemming/Stopwords dengan pencarian substring langsung.
        Jauh lebih cepat untuk Dashboard real-time.
        """
        if pd.isna(text): return 'Lainnya'
        text_lower = str(text).lower()
        
        # Loop dictionary: Jika ada keyword yang 'nyangkut' di teks, langsung return kategorinya
        for kategori, keywords in self.KAMUS_KATEGORI.items():
            if any(keyword in text_lower for keyword in keywords):
                return kategori
        return 'Lainnya'

    def _classify_audio_logic(self, row):
        """Logika klasifikasi audio"""
        if pd.isna(row['musicMeta.musicName']) or row['musicMeta.musicName'] == '':
            return 'Tanpa Audio'
        elif row['musicMeta.musicOriginal']:
            return 'Audio Original'
        else:
            return 'Audio Populer'

    def get_unique_authors(self):
        """[BARU] Ambil list unique author untuk dropdown filter"""
        if self.df is None: self.load_data()
        if 'authorMeta.name' in self.df.columns:
            return sorted(self.df['authorMeta.name'].astype(str).unique().tolist())
        return []

    # --- FUNGSI STATISTIK (Dengan Filter df=None) ---

    def get_summary_stats(self, df=None):
        """Get summary statistics of the dataset"""
        target_df = df if df is not None else self.df
        if target_df is None or target_df.empty: return {}

        stats = {
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
            'date_range': {
                'start': target_df['createTimeISO'].min(),
                'end': target_df['createTimeISO'].max()
            }
        }
        return stats

    def get_best_video(self, df=None, metric='playCount'):
        """Get the best performing video by metric"""
        target_df = df if df is not None else self.df
        if target_df is None or target_df.empty: return None
        return target_df.nlargest(1, metric).iloc[0]

    def get_top_videos(self, df=None, n=10, metric='playCount'):
        """Get top N videos by metric"""
        target_df = df if df is not None else self.df
        if target_df is None or target_df.empty: return pd.DataFrame()
        return target_df.nlargest(n, metric)

    def get_performance_by_day(self, df=None):
        """Get average performance by day of week"""
        target_df = df if df is not None else self.df
        if target_df is None or target_df.empty: return pd.DataFrame()

        # Update: Urutan Hari Indonesia
        day_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']

        perf = target_df.groupby('upload_day').agg({
            'playCount': 'mean',
            'diggCount': 'mean',
            'commentCount': 'mean',
            'shareCount': 'mean',
            'engagement_rate': 'mean',
            'webVideoUrl': 'count'
        }).rename(columns={'webVideoUrl': 'video_count'})

        # Reorder by day of week
        perf = perf.reindex([day for day in day_order if day in perf.index])

        return perf

    def get_performance_by_hour(self, df=None):
        """Get average performance by hour of day"""
        target_df = df if df is not None else self.df
        if target_df is None or target_df.empty: return pd.DataFrame()

        perf = target_df.groupby('upload_hour').agg({
            'playCount': 'mean',
            'diggCount': 'mean',
            'commentCount': 'mean',
            'shareCount': 'mean',
            'engagement_rate': 'mean',
            'webVideoUrl': 'count'
        }).rename(columns={'webVideoUrl': 'video_count'})

        return perf

    def get_content_type_performance(self, df=None):
        """Analyze performance by content type"""
        target_df = df if df is not None else self.df
        if target_df is None or target_df.empty: return pd.DataFrame()

        # Klasifikasi sudah dilakukan di load_data, kita tinggal group
        perf = target_df.groupby('content_type').agg({
            'playCount': ['mean', 'sum'],
            'diggCount': ['mean', 'sum'],
            'commentCount': ['mean', 'sum'],
            'shareCount': ['mean', 'sum'],
            'engagement_rate': 'mean',
            'webVideoUrl': 'count'
        })

        perf.columns = ['_'.join(col).strip() for col in perf.columns.values]
        perf = perf.rename(columns={'webVideoUrl_count': 'video_count'})
        return perf.sort_values(by='playCount_mean', ascending=False)

    def get_audio_type_performance(self, df=None):
        """Analyze performance by audio type"""
        target_df = df if df is not None else self.df
        if target_df is None or target_df.empty: return pd.DataFrame()

        # Klasifikasi sudah dilakukan di load_data
        perf = target_df.groupby('audio_type').agg({
            'playCount': ['mean', 'sum'],
            'diggCount': ['mean', 'sum'],
            'commentCount': ['mean', 'sum'],
            'shareCount': ['mean', 'sum'],
            'engagement_rate': 'mean',
            'webVideoUrl': 'count'
        })

        perf.columns = ['_'.join(col).strip() for col in perf.columns.values]
        perf = perf.rename(columns={'webVideoUrl_count': 'video_count'})
        return perf

    def get_leaderboard(self):
        """
        [BARU] Membuat tabel peringkat antar influencer (Leaderboard)
        """
        if self.df is None: self.load_data()
            
        leaderboard = self.df.groupby('authorMeta.name').agg({
            'playCount': 'sum',
            'diggCount': 'sum',
            'shareCount': 'sum',
            'id': 'count', # Jumlah Video
            'engagement_rate': 'mean'
        }).reset_index()
        
        # Rename kolom agar bahasa Indonesia
        leaderboard.rename(columns={
            'authorMeta.name': 'Nama Akun',
            'id': 'Jml Video',
            'playCount': 'Total Penayangan',
            'diggCount': 'Total Suka',
            'shareCount': 'Total Bagikan',
            'engagement_rate': 'Rata-rata ER (%)'
        }, inplace=True)
        
        return leaderboard.sort_values(by='Total Penayangan', ascending=False)

    def get_trending_threshold(self, percentile=75):
        """Calculate trending threshold based on percentile"""
        if self.df is None: self.load_data()
        return self.df['playCount'].quantile(percentile / 100)

    def get_correlation_matrix(self, df=None):
        """Get correlation matrix for numeric features"""
        target_df = df if df is not None else self.df
        if target_df is None: return pd.DataFrame()
        
        numeric_cols = ['playCount', 'diggCount', 'commentCount', 'shareCount', 'videoMeta.duration', 'engagement_rate']
        return target_df[numeric_cols].corr()

    def prepare_features_for_prediction(self, raw_features):
        """
        Prepare raw features for model prediction.
        Mapping 14 Kategori Baru -> 4 Kategori Model Lama (agar tidak error)
        """
        # Deteksi kategori dari text input user menggunakan Kamus
        text_content = raw_features.get('text_content', '')
        detected_category = self._classify_content_logic(text_content)
        
        features = {
            'Suka': raw_features.get('likes', 0),
            'Komentar': raw_features.get('comments', 0),
            'Dibagikan': raw_features.get('shares', 0),
            'Durasi_Video': raw_features.get('duration', 30),
            'Jumlah_Hashtag': raw_features.get('hashtag_count', 3),
            'Jam_Sejak_Publikasi': raw_features.get('hours_since_publish', 24),
            'Panjang_Caption': raw_features.get('caption_length', 50),
            'Hari_Upload': raw_features.get('upload_day', 0),
            'Jam_Upload': raw_features.get('upload_hour', 12),
            
            'Format_Konten_Video': raw_features.get('video_format', 1),
            
            # --- MAPPING STRATEGIS (Agar Model Lama Tetap Bisa Dipakai) ---
            # Model hanya dilatih dengan: Lainnya, OOTD, Tutorial, Vlog.
            
            # 1. Fashion & Beauty -> Masuk ke OOTD (karena mirip secara visual/audiens)
            'Tipe_Konten_OOTD': 1 if detected_category in ['Fashion', 'Beauty'] else 0,
            
            # 2. Edukasi_Karir -> Masuk ke Tutorial (karena sifatnya instruksional)
            'Tipe_Konten_Tutorial': 1 if detected_category == 'Edukasi_Karir' else 0,
            
            # 3. Daily -> Masuk ke Vlog (karena sifatnya kegiatan harian)
            'Tipe_Konten_Vlog': 1 if detected_category == 'Daily' else 0,

            # 4. Sisanya (Gaming, Kuliner, Hiburan, dll) -> Masuk ke Lainnya
            'Tipe_Konten_Lainnya': 1 if detected_category not in ['Fashion', 'Edukasi_Karir', 'Daily', 'Beauty'] else 0,
            
            'Tipe_Audio_Audio Lainnya': 1 if raw_features.get('audio_type') == 'Audio Lainnya' else 0,
            'Tipe_Audio_Audio Original': 1 if raw_features.get('audio_type') == 'Audio Original' else 0,
            'Tipe_Audio_Audio Populer': 1 if raw_features.get('audio_type') == 'Audio Populer' else 0,
        }

        return pd.DataFrame([features])


# Singleton instance
_data_processor = None

def get_data_processor():
    """Get or create data processor instance"""
    global _data_processor
    if _data_processor is None:
        _data_processor = DataProcessor()
        _data_processor.load_data()
    return _data_processor