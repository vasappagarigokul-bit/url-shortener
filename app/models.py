from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.mysql import BIGINT
from .database import base

class URL(base):
    __tablename__ = "urls"

    # Column id
    id = Column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        index=True
    )

    # Column long_url
    long_url = Column(
        String(8192),
        nullable=False
    )

    # Column short_code
    short_code = Column(
        String(11),
        index=True
    )

    # Column created_at
    created_at = Column(
        DateTime,
        server_default=func.now(),
        index=True
    )