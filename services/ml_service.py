import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from typing import Optional, Tuple
from functools import lru_cache
import traceback

from config import MODEL_WINDOW_SIZE, RF_ESTIMATORS, RF_RANDOM_STATE
from services.data_service import load_habit_data, compute_trends, safe_rolling_last
from utils.error_handlers import ModelTrainingException

def train_enhanced_mood_model(window: int = MODEL_WINDOW_SIZE) -> Optional[Tuple[RandomForestRegressor, list]]:
    try:
        df = load_habit_data()

        if len(df) < window:
            print(f"Not enough data for training. Need {window} entries, have {len(df)}")
            return None

        df = df.sort_values("timestamp")

        trends = compute_trends(df, window=window)
        df['sleep_slope'] = trends['sleep_hours']
        df['water_slope'] = trends['water_litres']
        df['mood_slope'] = trends['mood']

        df['avg_sleep'] = df['sleep_hours'].rolling(window).mean()
        df['avg_water'] = df['water_litres'].rolling(window).mean()
        df['avg_mood'] = df['mood'].rolling(window).mean()

        df = df.dropna()

        if len(df) == 0:
            print("No valid data after cleaning")
            return None

        features = ['sleep_hours', 'water_litres', 'sleep_slope', 'water_slope', 'mood_slope', 'avg_sleep', 'avg_water', 'avg_mood']

        x = df[features]
        y = df['mood']

        model = RandomForestRegressor(
            n_estimators=RF_ESTIMATORS,
            random_state=RF_RANDOM_STATE,
            max_depth=10,
            min_samples_split=5
        )
        model.fit(x, y)

        print(f"Model tranined successfully on {len(df)} samples")
        return model, features
    except Exception as e:
        raise ModelTrainingException(f"Failed to train mood model: {str(e)}")

@lru_cache(maxsize=1)
def get_trained_model() -> Optional[Tuple[RandomForestRegressor, list]]:
    try:
        return train_enhanced_mood_model()
    except Exception as e:
        print(f"Error getting trained model: {e}")
        return None
    
def predict_mood(features_df: pd.DataFrame) -> Optional[float]:
    try:
        model_data = get_trained_model()
        if not model_data:
            return None
        
        model, features_cols = model_data

        if features_df.empty or not all (col in features_df.columns for col in features_cols):
            return None
        
        prediction = model.predict(features_df[features_cols])
        return float(prediction[0])

    except Exception as e:
        print(f"Error predicting mood: {e}")
        return None
    
def get_feature_importance() -> Optional[pd.DataFrame]:
    try:
        model_data = get_trained_model()
        if not model_data:
            return None
        
        model, feature_cols = model_data

        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': feature_cols,
            'importance': importances
        }).sort_values('importance', ascending=False)

        return importance_df
    except Exception as e:
        print(f"Error getting feature importance: {e}")
        return None
    