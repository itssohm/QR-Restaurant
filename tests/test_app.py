import pytest
# Note: Changed from 'from app import app' to 'from app import create_app'
from app import create_app 

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_homepage(client):
    """Test that the homepage is accessible."""
    response = client.get('/')
    assert response.status_code == 200


