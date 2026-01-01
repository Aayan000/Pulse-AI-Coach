from typing import List
import pandas as pd

from models import HabitEntry
from services.data_service import load_habit_data, compute_trends, safe_rolling_last
from services.ml_service import predict_mood, get_feature_importance
from config import FEEDBACK_DAYS_AHEAD

def generate_feedback(entry: HabitEntry, days_ahead: int = FEEDBACK_DAYS_AHEAD) -> List[str]:
    feedback = []

    try:
        df = load_habit_data()
        feedback.append("Great job on sleep!" if entry.sleep_hours >= 7 else "Try to sleep at least 7 hours")
        feedback.append("Good water intake!" if entry.water_litres >=2 else "Drink more water")

        if df.empty or len(df) < 2:
            feedback.append("Keep logging data to unlock AI predictions")
            return feedback
        
        trends = compute_trends(df)

        features = pd.DataFrame([{
                'sleep_hours': entry.sleep_hours,
                'water_litres': entry.water_litres,
                'sleep_slope': trends['sleep_hours'],
                'water_slope': trends['water_litres'],
                'mood_slope': trends['mood'],
                'avg_sleep': safe_rolling_last(df['sleep_hours'], 3),
                'avg_water': safe_rolling_last(df['water_litres'], 3),
                'avg_mood': safe_rolling_last(df['mood'], 3),
            }])
        
        predicted_mood = predict_mood(features)

        if predicted_mood is not None:
            projected_sleep = entry.sleep_hours + trends['sleep_hours'] * days_ahead
            projected_water = entry.water_litres + trends['water_litres'] * days_ahead
                    
            future_features = features.copy()
            future_features['sleep_hours'] = projected_sleep
            future_features['water_litres'] = projected_water

            future_mood = predict_mood(future_features)
            if future_mood is not None:

                if future_mood is not None:

                    current_mood = entry.mood
                    mood_change = future_mood - current_mood
                    
                    if mood_change > 0.5:
                        feedback.append(f"Based on your habits, mood could improve to {future_mood:.1f}/5 in {days_ahead} days")
                    elif mood_change < -0.5:
                        feedback.append(f"Current trends suggest mood might drop to {future_mood:.1f}/5 in {days_ahead} days")
                    else:
                        feedback.append(f"Mood likely to stay around {future_mood:.1f}/5 in {days_ahead} days")


            importance_df = get_feature_importance()
            if importance_df is not None and not importance_df.empty:
                top_feature = importance_df.iloc[0]['feature']
                readable_names = {
                    'sleep_hours': 'Sleep Duration',
                    'water_litres': 'Water Intake',
                    'sleep_slope': 'Sleep Trend',
                    'water_slope': 'Water Trend',
                    'mood_slope': 'Mood Trend',
                    'avg_sleep': 'Average Sleep',
                    'avg_water': 'Average Water',
                    'avg_mood': 'Mood' 
                }
                readable_name = readable_names.get(top_feature, top_feature.replace('_', ' ').title())
                feedback.append(f"Most influential factor: {readable_name}")
        
        for habit, slope in trends.items():
            if abs(slope) < 0.05:
                continue
            habit_names = {
                'sleep_hours': 'sleep duration',
                'water_litres': 'water intake',
                'mood': 'mood'
            }
            habit_name = habit_names.get(habit, habit.replace('_', ' '))
            if slope < -0.1:
                feedback.append(f"Your {habit_name} is declining")
            
            elif slope < 0:
                feedback.append(f"Your {habit_name} shows a slight decrease")
            
            elif slope > 0.1:
                feedback.append(f"Your {habit_name} is improving")
            
            elif slope > 0:
                feedback.append(f"Your {habit_name} shows slight improvement")

        if len(feedback) < 3:
            feedback.append("Consistency is key! Keep logging daily for better insights")
    
    except Exception as e:
        print(f"Error generating feedback: {e}")
        feedback.append("Thanks for logging! More data will improve insights")
    
    return feedback
    