import matplotlib
matplotlib.use('Agg')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database import init_db
from api.endpoints import router
from utils.error_handlers import register_error_handler

os.makedirs("static", exist_ok=True)

app = FastAPI(
    title="Pulse AI Coach API",
    description="AI powered habit tracking and coaching",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

register_error_handler(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    print("Starting Pulse AI Coach")
    init_db()
    print("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down application")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
    )