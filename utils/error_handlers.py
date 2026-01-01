from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import traceback
from datetime import datetime

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class DatabaseException(AppException):
    pass

class ModelTrainingException(AppException):
    pass

class ChartGenerationException(AppException):
    pass

def register_error_handler(app):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc:AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append(f"{field}: {error['msg']}")

            return JSONResponse(
                status_code=422,
                content={
                    "error": "Validation failed",
                    "details": errors,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        print(f"Database error: {exc}")
        print(traceback.format_exc())

        return JSONResponse(
            status_code=500,
            content={
                "error": "Database error occurred",
                "details": str(exc) if str(exc) else "Unknown database error",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        print(f"Unhandled error: {exc}")
        print(traceback.format_exc())

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "details": str(exc) if str(exc) else "Unknown error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        )
