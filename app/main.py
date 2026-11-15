import redis
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.db import get_db
from app.redis_client import get_redis
from app.schemas import HealthResponse, ShortenRequest, ShortenResponse

app = FastAPI(title="URL Shortener")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


def cache_key(code: str) -> str:
    return f"url:{code}"


@app.post("/shorten", response_model=ShortenResponse)
def shorten(
    payload: ShortenRequest,
    db: Session = Depends(get_db),
    cache: redis.Redis = Depends(get_redis),
) -> ShortenResponse:
    url = crud.create_url(db, str(payload.url))
    cache.setex(cache_key(url.code), settings.cache_ttl_seconds, url.target_url)
    return ShortenResponse(
        code=url.code,
        short_url=f"{settings.base_url}/{url.code}",
        target_url=url.target_url,
    )


@app.get("/health", response_model=HealthResponse)
def health(
    db: Session = Depends(get_db),
    cache: redis.Redis = Depends(get_redis),
) -> HealthResponse:
    db_status = "ok"
    cache_status = "ok"

    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        cache.ping()
    except Exception:
        cache_status = "error"

    overall = "ok" if db_status == "ok" and cache_status == "ok" else "error"
    response = HealthResponse(status=overall, database=db_status, cache=cache_status)
    if overall != "ok":
        raise HTTPException(status_code=503, detail=response.model_dump())
    return response


# Catch-all redirect route: must be registered last so it doesn't shadow
# /health, /metrics, or any other fixed path.
@app.get("/{code}")
def redirect(
    code: str,
    db: Session = Depends(get_db),
    cache: redis.Redis = Depends(get_redis),
) -> RedirectResponse:
    target_url = cache.get(cache_key(code))
    if target_url is None:
        url = crud.get_url_by_code(db, code)
        if url is None:
            raise HTTPException(status_code=404, detail="Short URL not found")
        target_url = url.target_url
        cache.setex(cache_key(code), settings.cache_ttl_seconds, target_url)
    return RedirectResponse(url=target_url, status_code=302)
