import pytest
from app import app # Import your Flask app object

@pytest.fixture
def client():
    # Setup the test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the homepage returns a 200 OK status."""
    response = client.get('/')
    assert response.status_code == 200

def test_health_check(client):
    """Test a specific health endpoint (if you have one)."""
    response = client.get('/health') # Change this to an actual route you have
    # If the route exists, check the status
    if response.status_code != 404:
        assert response.status_code == 200