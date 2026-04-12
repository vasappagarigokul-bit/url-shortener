import redis
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")
REDIS_RATE_LIMITER_URL = os.getenv("REDIS_RATE_LIMITER_URL")
if not REDIS_RATE_LIMITER_URL:
    raise ValueError(
        "Server Misconfiguration."
    )



# Redis Rate Limiter -----

redis_rate_limiter = redis.from_url(
    REDIS_RATE_LIMITER_URL,
    decode_responses=True
)

RATE_LIMIT_WINDOW = 60 #Seconds = 1 minute
MAX_REQUESTS = 5