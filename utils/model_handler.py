"""
Model Handler Module
Handles loading the trained model and making predictions
"""
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class ModelHandler:
    """Handle model loading and predictions"""

    def __init__(self, model_path="models/tiktok_model_final_CLASSIFIER.pkl"):
        """
        Initialize model handler

        Args:
            model_path (str): Path to the trained model file
        """
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.load_model()

    def load_model(self):
        """Load the trained model from file"""
        try:
            self.model = joblib.load(self.model_path)

            # Get feature names
            if hasattr(self.model, 'feature_names_in_'):
                self.feature_names = list(self.model.feature_names_in_)
            else:
                # Default feature names from inspection
                self.feature_names = [
                    'Suka', 'Komentar', 'Dibagikan', 'Durasi_Video', 'Jumlah_Hashtag',
                    'Jam_Sejak_Publikasi', 'Panjang_Caption', 'Hari_Upload', 'Jam_Upload',
                    'Format_Konten_Video', 'Tipe_Konten_Lainnya', 'Tipe_Konten_OOTD',
                    'Tipe_Konten_Tutorial', 'Tipe_Konten_Vlog', 'Tipe_Audio_Audio Lainnya',
                    'Tipe_Audio_Audio Original', 'Tipe_Audio_Audio Populer'
                ]
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

    def predict(self, features):
        """
        Make a prediction

        Args:
            features (pd.DataFrame or dict): Features for prediction

        Returns:
            tuple: (prediction, probability)
        """
        try:
            # Convert dict to DataFrame if needed
            if isinstance(features, dict):
                features = pd.DataFrame([features])

            # Ensure all required features are present
            for feature in self.feature_names:
                if feature not in features.columns:
                    features[feature] = 0

            # Order features correctly
            features = features[self.feature_names]

            # Make prediction
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            confidence = probabilities[prediction]

            return prediction, confidence, probabilities
        except Exception as e:
            print(f"Error making prediction: {str(e)}")
            return None, None, None

    def predict_batch(self, features_df):
        """
        Make predictions for multiple samples

        Args:
            features_df (pd.DataFrame): DataFrame with features

        Returns:
            tuple: (predictions, probabilities)
        """
        try:
            # Ensure all required features are present
            for feature in self.feature_names:
                if feature not in features_df.columns:
                    features_df[feature] = 0

            # Order features correctly
            features_df = features_df[self.feature_names]

            # Make predictions
            predictions = self.model.predict(features_df)
            probabilities = self.model.predict_proba(features_df)

            return predictions, probabilities
        except Exception as e:
            print(f"Error making batch prediction: {str(e)}")
            return None, None

    def get_feature_importance(self):
        """
        Get feature importance from the model

        Returns:
            pd.DataFrame: Feature importance sorted by value
        """
        try:
            if hasattr(self.model, 'feature_importances_'):
                importance = self.model.feature_importances_
                feature_importance = pd.DataFrame({
                    'feature': self.feature_names,
                    'importance': importance
                })
                feature_importance = feature_importance.sort_values('importance', ascending=False)
                return feature_importance
            else:
                return None
        except Exception as e:
            print(f"Error getting feature importance: {str(e)}")
            return None

    def get_model_info(self):
        """
        Get model information

        Returns:
            dict: Model information
        """
        info = {
            'model_type': type(self.model).__name__,
            'n_features': len(self.feature_names),
            'features': self.feature_names
        }

        if hasattr(self.model, 'n_estimators'):
            info['n_estimators'] = self.model.n_estimators
        if hasattr(self.model, 'max_depth'):
            info['max_depth'] = self.model.max_depth
        if hasattr(self.model, 'classes_'):
            info['classes'] = list(self.model.classes_)

        return info


# Singleton instance
_model_handler = None

def get_model_handler():
    """Get or create model handler instance"""
    global _model_handler
    if _model_handler is None:
        _model_handler = ModelHandler()
    return _model_handler
