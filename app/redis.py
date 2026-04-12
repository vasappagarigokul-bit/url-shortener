import redis
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")
REDIS_CACHE_URL = os.getenv("REDIS_CACHE_URL")
REDIS_RATE_LIMITER_URL = os.getenv("REDIS_RATE_LIMITER_URL")
if not (REDIS_CACHE_URL and REDIS_RATE_LIMITER_URL):
    raise ValueError(
        "Server Misconfiguration."
    )

# Redis Cache -----

redis_cache = redis.from_url(
    REDIS_CACHE_URL,
    decode_responses=True
)

CACHE_TTL = 86400 #Seconds = 24 hours

# Redis Rate Limiter -----

redis_rate_limiter = redis.from_url(
    REDIS_RATE_LIMITER_URL,
    decode_responses=True
)

RATE_LIMIT_WINDOW = 60 #Seconds = 1 minute
MAX_REQUESTS = 5