from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
import traceback
from datetime import datetime

from models import HabitEntry, HabitResponse, FeedbackResponse, ErrorResponse
from database import get_db_dependency, HabitDB
from services.feedback_service import generate_feedback
from services.chart_service import plot_habit_over_time
from utils.error_handlers import AppException

router = APIRouter()

@router.get("/")
async def read_root():
    try:
        return FileResponse("index.html")
    except Exception as e:
        raise AppException(f"Failed to load main page: {str(e)}", 500)
    
@router.post("/add_entry", response_model=FeedbackResponse)
async def add_entry(entry: HabitEntry, db: Session = Depends(get_db_dependency)):
    try:
        habit = HabitDB(
            sleep_hours=entry.sleep_hours,
            water_litres=entry.water_litres,
            mood=entry.mood
        )

        db.add(habit)
        db.commit()
        db.refresh(habit)

        feedback = generate_feedback(entry)

        return FeedbackResponse(
            message="Entry received successfully",
            feedback=feedback
        )
    except Exception as e:
        db.rollback()
        print(f"Error adding entry: {e}")
        print(traceback.format_exc())
        raise AppException(f"Failed to add entry: {str(e)}", 500)
    
@router.get("/entries", response_model=list[HabitResponse])
async def get_entries(db: Session = Depends(get_db_dependency)):
    try:
        entries = db.query(HabitDB).order_by(HabitDB.timestamp.desc()).all()
        return entries
    except Exception as e:
        raise AppException(f"Failed to get entries: {str(e)}", 500)
    
@router.get("/chart/sleep")
async def chart_sleep(t: int = Query(None, description="Cache busting timestamp")):
    try:
        buf = plot_habit_over_time('sleep_hours', 'Sleep Hours Over Time')
        return StreamingResponse(buf, media_type='image/png')
    except Exception as e:
        raise AppException(f"Failed to generate sleep chart: {str(e)}", 500)

@router.get("/chart/water")
async def chart_water(t: int = Query(None, description="Cache busting timestamp")):
    try:
        buf = plot_habit_over_time('water_litres', 'Water Intake Over Time')
        return StreamingResponse(buf, media_type='image/png')
    except Exception as e:
        raise AppException(f"Failed to generate water chart: {str(e)}", 500)

@router.get("/chart/mood")
async def chart_mood(t: int = Query(None, description="Cache busting timestamp")):
    try:
        buf = plot_habit_over_time('mood', 'Mood Over Time')
        return StreamingResponse(buf, media_type='image/png')
    except Exception as e:
        raise AppException(f"Failed to generate mood chart: {str(e)}", 500)
    
@router.get("/health")
async def health_check():
    try:
        with get_db_dependency() as db:
            count = db.query(HabitDB).count()

        return{
            "status": "healthy",
            "database": "connected",
            "entries_count": count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise AppException(f"Health check failed: {str(e)}", 500)
    
@router.get("/debug")
async def debug_info():
    try:
        from services.data_service import load_habit_data
        from services.ml_service import get_trained_model

        df = load_habit_data()
        model_data = get_trained_model()

        return{
            "database_records": len(df),
            "model_trained": model_data is not None,
            "data_columns": list(df.columns) if not df.empty else[],
            "sample_data": df.tail(3).to_dict('records') if not df.empty else[]
        }
    except Exception as e:
        raise AppException(f"Debug info failed: {str(e)}", 500)