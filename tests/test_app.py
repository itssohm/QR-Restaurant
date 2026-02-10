import pytest
import os
from app import create_app # Ensure this is where your factory is

@pytest.fixture
def app():
    # 1. Create the app instance
    app = create_app()
    
    # 2. OVERRIDE the Database URI to use an in-memory SQLite database
    # This ensures no local file or external DB is needed
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    # 3. Create the tables in the in-memory database
    # Assuming you are using Flask-SQLAlchemy
    with app.app_context():
        from app import db # Import your db object
        db.create_all() # Create tables for testing
        
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200