### === test_url_shortener.py ===
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_short_url():
    response = client.post(
        "/shorten",
        json={"original_url": "https://www.example.com"},
    )
    assert response.status_code == 201
    assert "short_url" in response.json()

def test_create_short_url_invalid_json():
    response = client.post(
        "/shorten",
        json={"invalid_key": "https://www.example.com"},
    )
    assert response.status_code == 422

def test_get_original_url():
    short_url = client.post(
        "/shorten",
        json={"original_url": "https://www.example.com"},
    ).json()["short_url"]
    response = client.get(f"/{short_url}")
    assert response.status_code == 301
    assert response.headers["Location"] == "https://www.example.com"

def test_get_original_url_invalid_short_url():
    response = client.get("/invalid_short_url")
    assert response.status_code == 404

def test_get_short_url_stats():
    short_url = client.post(
        "/shorten",
        json={"original_url": "https://www.example.com"},
    ).json()["short_url"]
    response = client.get(f"/{short_url}/stats")
    assert response.status_code == 200
    assert "clicks" in response.json()

def test_get_short_url_stats_invalid_short_url():
    response = client.get("/invalid_short_url/stats")
    assert response.status_code == 404
```

### === test_database.py ===
```python
import pytest
from database import get_db, create_short_url, get_original_url, increment_clicks

def test_create_short_url_in_database():
    original_url = "https://www.example.com"
    short_url = create_short_url(original_url)
    assert short_url is not None

def test_get_original_url_from_database():
    original_url = "https://www.example.com"
    short_url = create_short_url(original_url)
    retrieved_original_url = get_original_url(short_url)
    assert retrieved_original_url == original_url

def test_increment_clicks_in_database():
    original_url = "https://www.example.com"
    short_url = create_short_url(original_url)
    increment_clicks(short_url)
    retrieved_clicks = get_db().execute("SELECT clicks FROM urls WHERE short_url = ?", (short_url,)).fetchone()[0]
    assert retrieved_clicks == 1

def test_get_short_url_stats_from_database():
    original_url = "https://www.example.com"
    short_url = create_short_url(original_url)
    increment_clicks(short_url)
    retrieved_stats = get_db().execute("SELECT clicks FROM urls WHERE short_url = ?", (short_url,)).fetchone()
    assert retrieved_stats[0] == 1
```

### === test_main.py ===
```python
import pytest
from main import app

def test_app():
    assert app is not None

def test_app_routes():
    routes = [route.path for route in app.routes]
    assert "/shorten" in routes
    assert "/{short_url}" in routes
    assert "/{short_url}/stats" in routes
```

### === conftest.py ===
```python
import pytest
from main import app
from database import create_tables, drop_tables

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def db():
    create_tables()
    yield
    drop_tables()
```

### === test_utils.py ===
```python
import pytest
from utils import generate_short_url

def test_generate_short_url():
    short_url = generate_short_url()
    assert len(short_url) == 6
    assert short_url.isalnum()
```
These tests cover the following scenarios:

1.  **Unit Tests:**

    *   `test_url_shortener.py`: Tests the API endpoints for creating short URLs, retrieving original URLs, and getting short URL statistics.
    *   `test_database.py`: Tests the database interactions for creating short URLs, retrieving original URLs, and incrementing clicks.
    *   `test_main.py`: Tests the main application and its routes.
    *   `test_utils.py`: Tests the utility functions for generating short URLs.
2.  **Integration Tests:**

    *   The tests in `test_url_shortener.py` also serve as integration tests, as they test the API endpoints and the underlying database interactions.
3.  **Fixtures:**

    *   `conftest.py`: Provides fixtures for the test client and database setup/teardown.

These tests ensure that the URL shortener API is functioning correctly and that the database interactions are working as expected.