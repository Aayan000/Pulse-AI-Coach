import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import traceback
from datetime import datetime, timedelta

from database import get_db, HabitDB
from utils.error_handlers import DatabaseException

def load_habit_data():
    try:
        with get_db() as db:
            habits = db.query(HabitDB).all()

        data = []

        for i in habits:
            data.append({
                "sleep_hours": i.sleep_hours,
                "water_litres": i.water_litres,
                "mood": i.mood,
                "timestamp": i.timestamp
            })

        return pd.DataFrame(data)
    except Exception as e:
        raise DatabaseException(f"Failed to load habit data: {str(e)}")
    
def compute_trends(df: pd.DataFrame, window: int = 3) -> Dict[str, float]:
    try:
        if df.empty or len(df) < 2:
            return {'sleep_hours': 0, 'water_litres': 0, 'mood':0}
    
        df = df.sort_values("timestamp")
        trends = {}

        for column in ["sleep_hours", "water_litres", "mood"]:
            if len(df) < window:
                trends[column] = 0
                continue
            
            rolling = df[column].rolling(window=window).mean().dropna()
            if len(rolling) < 2:
                trends[column] = 0
                continue

            x = np.arange(len(rolling))
            y = rolling.values
            slope = np.polyfit(x,y,1)[0]
            trends[column] = slope
    
        return trends

    except Exception as e:
        print(f"Error computing trends: {e}")
        return {'sleep_hours': 0, 'water_litres': 0, 'mood': 0}

def safe_rolling_last(series: pd.Series, window: int) -> float:
    try:
        if len(series) == 0:
            return 0
        if len(series) < window:
            return float(series.mean())
        
        rolling = series.rolling(window).mean().dropna()

        if len(rolling) == 0:
            return float(series.mean())
        
        return float(rolling.iloc[-1])
    
    except Exception as e:
        print(f"Error in safe_rolling_last: {e}")
        return float(series.mean()) if len(series) > 0 else 0
    
def get_recent_entries(days: int = 7) -> List[Dict]:
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with get_db() as db:
            entries = db.query(HabitDB)\
                .filter(HabitDB.timestamp >= cutoff_date)\
                .order_by(HabitDB.timestamp.desc())\
                .all()
        return [
            {
                "id": entry.id,
                "sleep_hours": entry.sleep_hours,
                "water_litres": entry.water_litres,
                "mood": entry.mood,
                "timestamp": entry.timestamp.isoformat()
            }
            for entry in entries
        ]
    except Exception as e:
        raise DatabaseException(f"Failed to get recent entries: {str(e)}")


