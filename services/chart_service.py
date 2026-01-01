import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from datetime import timedelta
import traceback
import pandas as pd

from config import CHART_WIDTH, CHART_HEIGHT, CHART_DPI
from services.data_service import load_habit_data, compute_trends
from services.ml_service import get_trained_model
from utils.error_handlers import ChartGenerationException

def create_empty_chart(message: str = "No data available") -> BytesIO:
    try:
        buf = BytesIO()
        fig, ax = plt.subplots(figsize=(10,6))

        ax.text(0.5, 0.5, message,
                ha='center', va='center', fontsize=16,
                transform=ax.transAxes, wrap=True)
        ax.axis('off')

        fig.tight_layout()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf
    
    except Exception as e:
        raise ChartGenerationException(f"Failed to create empty chart: {str(e)}")
    
def plot_habit_over_time(habit_column: str, title: str, days_ahead: int = 3) -> BytesIO:
    try:
        df = load_habit_data()
        
        if df.empty or len(df) < 2:
            return create_empty_chart("Not enough data yet\nAdd more entries to see charts")
        
        df = df.sort_values('timestamp')

        sns.set(style='whitegrid')

        fig, ax = plt.subplots(figsize=(CHART_WIDTH, CHART_HEIGHT), dpi=CHART_DPI)

        ax.plot(df['timestamp'], df[habit_column],
                marker='o', linewidth=2, markersize=8,
                label='Actual', color='#2196F3')
        
        if habit_column == "mood":
            model_data = get_trained_model()
            if model_data:
                model, feature_cols = model_data
                trends = compute_trends(df)

                future_dates = []
                future_preds = []
                last_row = df.iloc[-1]

                for i in range(1, days_ahead+1):
                    features = {
                        'sleep_hours': last_row['sleep_hours'] + trends['sleep_hours'] * i,
                        'water_litres': last_row['water_litres'] + trends['water_litres'] * i,
                        'sleep_slope': trends['sleep_hours'],
                        'water_slope': trends['water_litres'],
                        'mood_slope': trends['mood'],
                        'avg_sleep': df['sleep_hours'].rolling(3).mean().iloc[-1],
                        'avg_water': df['water_litres'].rolling(3).mean().iloc[-1],
                        'avg_mood': df['mood'].rolling(3).mean().iloc[-1]
                    }

                    features_df = pd.DataFrame([features])
                    if all(col in features_df.columns for col in feature_cols):
                        prediction = model.predict(features_df[feature_cols])[0]
                        future_preds.append(prediction)
                        future_dates.append(last_row['timestamp'] + timedelta(days=i))
                
                if future_preds:
                    ax.plot(future_dates, future_preds,
                            linestyle='--', marker='s', linewidth=2,
                            markersize=8, label='AI Prediction', color='#4CAF50')
        else:
            trends = compute_trends(df)
            last_value = df[habit_column].iloc[-1]
            slope = trends.get(habit_column, 0)

            future_dates = [df['timestamp'].iloc[-1] + timedelta(days=i)
                            for i in range(1, days_ahead+1)]
            future_values = [last_value + slope * i
                             for i in range(1, days_ahead+1)]
            
            ax.plot(future_dates, future_values,
                    linestyle='--', marker='^', linewidth=2,
                    markersize=8, label='Trend Projection', color='#FF9800')
            
        ax.set_title(title, fontsize=18, pad=20, fontweight='bold')
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel(habit_column.replace('_', ' ').title(), fontsize=14)

        all_values = list(df[habit_column])
        if 'future_values' in locals():
            all_values.extend(future_values)

        y_min = min(all_values) * 0.9 if min(all_values) > 0 else min(all_values) - 0.5
        y_max = max(all_values) * 1.1

        ax.set_ylim(y_min, y_max)    
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)

        fig.autofmt_xdate()
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    except Exception as e:
        print(f"Error creating chart for {habit_column}: {e}")
        print(traceback.format_exc())
        return create_empty_chart(f"Error generating chart\n{str(e)[:50]}")
    
def plot_all_charts() -> dict:
    try:
        charts = {
            'sleep': plot_habit_over_time('sleep_hours', 'Sleep Hours Over Time'),
            'water': plot_habit_over_time('water_litres', 'Water Intake Over Time'),
            'mood': plot_habit_over_time('mood', 'Mood Over Time')
        }

        return charts
    except Exception as e:
        raise ChartGenerationException(f"Failed to generate all charts: {str(e)}")