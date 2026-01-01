from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from config import SLEEP_MIN, SLEEP_MAX, WATER_MIN, WATER_MAX, MOOD_MIN, MOOD_MAX

class HabitEntry(BaseModel):
    sleep_hours: float = Field(..., ge=SLEEP_MIN, le=SLEEP_MAX, description="Sleep duration in hours")
    water_litres: float = Field(..., ge=WATER_MIN, le=WATER_MAX, description="Water intake in litres")
    mood: int = Field(..., ge=MOOD_MIN, le=MOOD_MAX, description="Mood rating from 1-5") 

    @validator('sleep_hours')
    def validate_sleep_precision(cls, v):
        if len(str(v).split('.')[-1]) > 1:
            return round(v, 1)
        return v

    @validator('water_litres')
    def validate_water_precision(cls, v):
        if len(str(v).split('.')[-1]) > 1:
            return round(v, 1)
        return v

class HabitResponse(BaseModel):
    id: int
    sleep_hours: float
    water_litres: float
    mood: int
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class FeedbackResponse(BaseModel):
    message: str
    feedback: list[str]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)