from fastapi import (
    FastAPI,
    status,
    Depends,
    HTTPException,
    dependencies,
    Request
)
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from redis.exceptions import ConnectionError, ResponseError
from dotenv import load_dotenv
import os
import time

from .database import engine, SessionMaker, base
from .schemas import URLRequest, URLResponse
from .redis import redis_cache, redis_rate_limiter
from .utils import rate_limiter, authorize
from .crud import create_url, get_url_by_code
from typing import Generator


load_dotenv(dotenv_path=".env")
BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise ValueError(
        "Server Misconfiguration."
    )

base.metadata.create_all(bind=engine)

def get_db() -> Generator:
    db = SessionMaker()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="URL Shortener",
    description="High-Performance URL Shortening Service."
)

# Middleware -----

@app.middleware("http")
async def get_response_time(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    response.headers["X-Response-Time-Ms"] = f"{process_time * 1000:.2f}ms"
    return response

# App Health -----

@app.get(
    path="/api",
    tags=['Health'],
    status_code=status.HTTP_200_OK,
    summary="Try it out: click Execute.",
    description="This a simple health check for the API."
)
def get_api_health():
    return {
        "message": "URL Shortener API is running successfully!"
    }

@app.get(
    path="/check_1",
    tags=['Health'],
    status_code=status.HTTP_200_OK,
    summary="Admin only."
)
async def get_db_health(db: Session=Depends(get_db), admin: bool=Depends(authorize)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "Ok",
            "database": "Connected"
        }
    except OperationalError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
    except ProgrammingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get(
    path="/check_2",
    tags=['Health'],
    status_code=status.HTTP_200_OK,
    summary="Admin only."
)
async def get_cache_db_health(admin: bool=Depends(authorize)):
    try:
        if redis_cache.ping():
            return {
                "status": "Ok",
                "redis_cache_db": "Connected"
            }
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis cache database connection failed: {str(e)}"
        )
    except ResponseError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Redis cache database requests out of limit: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redis cache database error: {str(e)}"
        )

@app.get(
    path="/check_3",
    tags=['Health'],
    status_code=status.HTTP_200_OK,
    summary="Admin only."
)
async def get_rate_limiter_db_health(admin: bool=Depends(authorize)):
    try:
        if redis_rate_limiter.ping():
            return {
                "status": "Ok",
                "redis_rate_limiter_db": "Connected"
            }
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis rate limiter database connection failed: {str(e)}"
        )
    except ResponseError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Redis rate limiter database requests out of limit: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redis rate limiter database error: {str(e)}"
        )

# URL EndPoints -----

@app.post(
    path="/shorten",
    response_model=URLResponse,
    tags=['Shortener'],
    status_code=status.HTTP_201_CREATED,
    summary="Try it out: copy-paste a long URL and click Execute.",
    description="Creates a unique short code for a long URL valid for 15 days. Returns short URL.",
    dependencies=[Depends(rate_limiter)]
)
def shorten_url(request: URLRequest, db: Session=Depends(get_db)):
    db_url = create_url(db, str(request.long_url))
    short_url = f"{BASE_URL}/{db_url.short_code}"
    return URLResponse(short_url=short_url)

@app.get(
    path="/{short_code}",
    tags=['Redirection'],
    status_code=status.HTTP_302_FOUND,
    description="Retrieves the original long URL from a short code and performs a 302 temporary redirect."
)
def redirect_to_long_url(short_code: str, db: Session=Depends(get_db)):
    long_url = get_url_by_code(db, short_code)
    if not long_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Code."
        )

    return RedirectResponse(
        url=long_url,
        status_code=status.HTTP_302_FOUND
    )