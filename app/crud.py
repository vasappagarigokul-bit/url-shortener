from sqlalchemy.orm import Session
from .models import URL
from .utils import encode_base62

def create_url(db: Session, long_url: str) -> URL:
    db_entry = URL(long_url=long_url)
    db.add(db_entry)
    db.flush()

    # Create short code
    db_entry.short_code = encode_base62(db_entry.id)
    db.commit()
    db.refresh(db_entry)

    return db_entry

def get_url_by_code(db: Session, short_code: str) -> str:
    db_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if db_entry:
        return db_entry.long_url

    return None