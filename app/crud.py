from sqlalchemy.orm import Session
from .models import URL
from .redis import redis_cache, CACHE_TTL
from .utils import encode_base62

def create_url(db: Session, long_url: str) -> URL:
    db_entry = URL(long_url=long_url)
    db.add(db_entry)
    db.flush()

    # Create short code
    db_entry.short_code = encode_base62(db_entry.id)
    db.commit()
    db.refresh(db_entry)

    # Pre-cache the entry
    try:
        redis_cache.setex(
            db_entry.short_code,
            CACHE_TTL,
            long_url
        )
    except Exception:
        pass

    return db_entry

def get_url_by_code(db: Session, short_code: str) -> str:
    # Fetch from cache
    try:
        cached_url = redis_cache.get(short_code)
        if cached_url:
            return cached_url
    except Exception:
        cached_url = None

    # Fallback to database (cache miss)
    if not cached_url:
        db_entry = db.query(URL).filter(URL.short_code == short_code).first()
        if db_entry:
            return db_entry.long_url

    return None