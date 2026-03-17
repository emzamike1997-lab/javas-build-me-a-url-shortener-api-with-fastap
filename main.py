```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from hashlib import sha256
from redis import Redis

# Initialize the FastAPI application
app = FastAPI()

# Initialize the Redis client
redis_client = Redis(host='localhost', port=6379, db=0)

# Define the URL model
class URL(BaseModel):
    original_url: str
    shortened_url: Optional[str] = None

# Define the error model
class ErrorResponse(BaseModel):
    error: str

# Generate a shortened URL
def generate_shortened_url(original_url: str) -> str:
    # Generate a unique hash for the original URL
    hash_object = sha256(original_url.encode())
    # Generate a shortened URL
    shortened_url = hash_object.hexdigest()[:6]
    return shortened_url

# Create a new shortened URL
@app.post("/shorten", response_model=URL)
async def create_shortened_url(url: URL):
    try:
        # Generate a shortened URL
        shortened_url = generate_shortened_url(url.original_url)
        # Check if the shortened URL already exists
        if redis_client.exists(shortened_url):
            # If it exists, generate a new one
            shortened_url = str(uuid4())[:6]
        # Store the original URL in Redis
        redis_client.set(shortened_url, url.original_url)
        # Return the shortened URL
        return {"original_url": url.original_url, "shortened_url": shortened_url}
    except Exception as e:
        # Handle any exceptions
        raise HTTPException(status_code=500, detail=str(e))

# Get the original URL from a shortened URL
@app.get("/{shortened_url}", response_model=URL)
async def get_original_url(shortened_url: str):
    try:
        # Get the original URL from Redis
        original_url = redis_client.get(shortened_url)
        if original_url is None:
            # If the shortened URL does not exist, raise an error
            raise HTTPException(status_code=404, detail="Shortened URL not found")
        # Return the original URL
        return {"original_url": original_url.decode(), "shortened_url": shortened_url}
    except Exception as e:
        # Handle any exceptions
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

###