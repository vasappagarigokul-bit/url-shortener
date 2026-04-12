<p align="center">
  <img src="https://github.com/vasappagarigokul-bit/readme-images/blob/main/url-shortener/URL%20Shortener-590x296.png">
</p>

This URL shortener is a high-performance backend service designed to convert long URLs into compact, shareable short links while ensuring fast redirection, scalability, and operational reliability.
<br>
<br>
At its core, the system accepts a valid long URL through a REST API endpoint and stores it in a MySQL database. Each URL is assigned a unique numeric identifier, which is then converted into a short, human-friendly string using a Base62 encoding algorithm. This approach ensures that generated short codes are compact, URL-safe, and efficiently derived without requiring additional lookup tables or collision handling mechanisms.
<br>
<br>
Once a short URL is created, the system immediately caches the mapping between the short code and the original long URL in Redis. This caching layer significantly reduces database load and enables ultra-fast read performance during redirection. When a user accesses a short URL, the service first checks Redis for a cached entry. If found, it returns the original URL instantly; otherwise, it falls back to querying the database. This hybrid lookup strategy ensures both speed and reliability.
<br>
<br>
The application includes a rate-limiting mechanism implemented using Redis sorted sets. Each incoming request is tracked per client IP within a rolling time window, allowing the system to enforce strict request limits and protect against abuse or traffic spikes. If a client exceeds the allowed number of requests, the service responds with an appropriate HTTP error, maintaining system stability under load.
<br>
<br>
Security and administrative control are handled through HTTP Basic Authentication for protected endpoints. These endpoints allow only Admin to verify the health of the database and Redis instances, ensuring that all critical components are operational. The system also includes robust error handling to gracefully manage failures in database connections, cache access, or unexpected runtime issues.
<br>
<br>
To maintain data hygiene and control storage growth, the service enforces a time-based expiration policy. URLs older than 15 days are automatically removed from the database through a scheduled GitHub Actions workflow that runs daily. This ensures that stale data does not accumulate and that the system remains efficient over time.
<br>
<br>
Additionally, the service includes middleware to measure and provide response times for each request, providing visibility into performance metrics. With a redirection latency of under 220 milliseconds, the system is optimized for fast user experiences.
<br>
<br>
Overall, this URL shortener is a well-structured, production-oriented backend system that combines efficient encoding, database persistence, caching, rate limiting, and automated maintenance to deliver a reliable and scalable link-shortening solution.

# Local Setup
## Prerequisites
- Python 3.9+
- MySQL database
- Dockerized Redis

## Clone the Repository
git clone https://github.com/vasappagarigokul-bit/url-shortener
<br>
cd url-shortener

## Create a Virtual Environment
python -m venv venv
- __Linux / Mac__: venv/bin/activate
- __Windows__: venv\Scripts\activate

## Install Dependencies
pip install -r requirements.txt

## Environment Configuration
Create a `.env` file in the root directory:
- __DATABASE_URL__=mysql+pymysql://[user]:[password]@localhost:3306/<db_name>
- __REDIS_CACHE_URL__=redis://localhost:6379/<db_number_0-15>
- __REDIS_RATE_LIMITER_URL__=redis://localhost:6379/<db_number_0-15>
- __ADMIN__=[username]
- __PASSWORD__=<admin_password>
- __BASE_URL__=http://localhost:8000

__Note__: Remove `SSL/CA` certificate arguments from the `create_engine` call in `database.py` file.

## Run the application
uvicorn app.main:app --reload
<br>
<br>
API will be available at: `http://localhost:8000`
<br>
Access the interactive Swagger documentation at: `http://localhost:8000/docs`
