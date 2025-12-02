"""
Data Processor Module
Handles loading and preprocessing of TikTok data
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

            # Extract datetime features
            self.df['upload_date'] = self.df['createTimeISO'].dt.date
            self.df['upload_hour'] = self.df['createTimeISO'].dt.hour
            self.df['upload_day'] = self.df['createTimeISO'].dt.day_name()
            self.df['upload_month'] = self.df['createTimeISO'].dt.month_name()
            self.df['upload_year'] = self.df['createTimeISO'].dt.year

            # Calculate engagement rate
            self.df['engagement_rate'] = (
                (self.df['diggCount'] + self.df['commentCount'] + self.df['shareCount']) /
                self.df['playCount'].replace(0, 1)
            ) * 100

            return self.df
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None

    def get_summary_stats(self):
        """
        Get summary statistics of the dataset

        Returns:
            dict: Summary statistics
        """
        if self.df is None:
            self.load_data()

        stats = {
            'total_videos': len(self.df),
            'total_views': self.df['playCount'].sum(),
            'total_likes': self.df['diggCount'].sum(),
            'total_comments': self.df['commentCount'].sum(),
            'total_shares': self.df['shareCount'].sum(),
            'avg_views': self.df['playCount'].mean(),
            'avg_likes': self.df['diggCount'].mean(),
            'avg_comments': self.df['commentCount'].mean(),
            'avg_shares': self.df['shareCount'].mean(),
            'avg_engagement_rate': self.df['engagement_rate'].mean(),
            'avg_duration': self.df['videoMeta.duration'].mean(),
            'date_range': {
                'start': self.df['createTimeISO'].min(),
                'end': self.df['createTimeISO'].max()
            }
        }

        return stats

    def get_best_video(self, metric='playCount'):
        """
        Get the best performing video by metric

        Args:
            metric (str): Metric to sort by (playCount, diggCount, etc.)

        Returns:
            pd.Series: Best video row
        """
        if self.df is None:
            self.load_data()

        return self.df.nlargest(1, metric).iloc[0]

    def get_top_videos(self, n=10, metric='playCount'):
        """
        Get top N videos by metric

        Args:
            n (int): Number of videos
            metric (str): Metric to sort by

        Returns:
            pd.DataFrame: Top videos
        """
        if self.df is None:
            self.load_data()

        return self.df.nlargest(n, metric)

    def get_performance_by_day(self):
        """
        Get average performance by day of week

        Returns:
            pd.DataFrame: Performance by day
        """
        if self.df is None:
            self.load_data()

        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        perf = self.df.groupby('upload_day').agg({
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

    def get_performance_by_hour(self):
        """
        Get average performance by hour of day

        Returns:
            pd.DataFrame: Performance by hour
        """
        if self.df is None:
            self.load_data()

        perf = self.df.groupby('upload_hour').agg({
            'playCount': 'mean',
            'diggCount': 'mean',
            'commentCount': 'mean',
            'shareCount': 'mean',
            'engagement_rate': 'mean',
            'webVideoUrl': 'count'
        }).rename(columns={'webVideoUrl': 'video_count'})

        return perf

    def get_content_type_performance(self):
        """
        Analyze performance by content type (based on caption analysis)

        Returns:
            pd.DataFrame: Performance by content type
        """
        if self.df is None:
            self.load_data()

        # Simple content type classification based on keywords
        def classify_content(text):
            text_lower = str(text).lower()

            if any(keyword in text_lower for keyword in ['ootd', 'outfit', 'look']):
                return 'OOTD'
            elif any(keyword in text_lower for keyword in ['tutorial', 'how to', 'cara', 'tips']):
                return 'Tutorial'
            elif any(keyword in text_lower for keyword in ['vlog', 'day in', 'diary', 'daily']):
                return 'Vlog'
            elif any(keyword in text_lower for keyword in ['teacher', 'guru', 'mengajar', 'pkm']):
                return 'Educational'
            else:
                return 'Lainnya'

        self.df['content_type'] = self.df['text'].apply(classify_content)

        perf = self.df.groupby('content_type').agg({
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

    def get_audio_type_performance(self):
        """
        Analyze performance by audio type

        Returns:
            pd.DataFrame: Performance by audio type
        """
        if self.df is None:
            self.load_data()

        def classify_audio(row):
            if pd.isna(row['musicMeta.musicName']) or row['musicMeta.musicName'] == '':
                return 'Tanpa Audio'
            elif row['musicMeta.musicOriginal']:
                return 'Audio Original'
            else:
                return 'Audio Populer'

        self.df['audio_type'] = self.df.apply(classify_audio, axis=1)

        perf = self.df.groupby('audio_type').agg({
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

    def get_trending_threshold(self, percentile=75):
        """
        Calculate trending threshold based on percentile

        Args:
            percentile (int): Percentile to use (default 75)

        Returns:
            float: Threshold value for views
        """
        if self.df is None:
            self.load_data()

        return self.df['playCount'].quantile(percentile / 100)

    def get_correlation_matrix(self):
        """
        Get correlation matrix for numeric features

        Returns:
            pd.DataFrame: Correlation matrix
        """
        if self.df is None:
            self.load_data()

        numeric_cols = ['playCount', 'diggCount', 'commentCount', 'shareCount', 'videoMeta.duration', 'engagement_rate']
        return self.df[numeric_cols].corr()

    def prepare_features_for_prediction(self, raw_features):
        """
        Prepare raw features for model prediction
        This should match the feature engineering done during training

        Args:
            raw_features (dict): Raw input features

        Returns:
            pd.DataFrame: Processed features ready for model
        """
        # This is a placeholder - actual feature engineering would depend on training process
        # For now, we'll create a basic template

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
            'Kekuatan_Tren_Audio': raw_features.get('audio_trend_strength', 0.5),
            'Kekuatan_Tren_Hashtag': raw_features.get('hashtag_trend_strength', 0.5),
            'Apakah_Kolaborasi': raw_features.get('is_collaboration', 0),
            'Format_Konten_Video': raw_features.get('video_format', 1),
            'Tipe_Konten_Lainnya': 1 if raw_features.get('content_type') == 'Lainnya' else 0,
            'Tipe_Konten_OOTD': 1 if raw_features.get('content_type') == 'OOTD' else 0,
            'Tipe_Konten_Tutorial': 1 if raw_features.get('content_type') == 'Tutorial' else 0,
            'Tipe_Konten_Vlog': 1 if raw_features.get('content_type') == 'Vlog' else 0,
            'Tipe_Audio_Audio Lainnya': 1 if raw_features.get('audio_type') == 'Audio Lainnya' else 0,
            'Tipe_Audio_Audio Original': 1 if raw_features.get('audio_type') == 'Audio Original' else 0,
            'Tipe_Audio_Audio Populer': 1 if raw_features.get('audio_type') == 'Audio Populer' else 0,
            'Interaksi_Tutorial_x_Komentar': raw_features.get('comments', 0) if raw_features.get('content_type') == 'Tutorial' else 0,
            'Interaksi_OOTD_x_Dibagikan': raw_features.get('shares', 0) if raw_features.get('content_type') == 'OOTD' else 0,
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
