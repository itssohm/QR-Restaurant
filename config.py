# config.py
import os

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_development_only_change_in_production')

# Database configuration
# For SQLite (default for development)
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL', 
    'sqlite:///restaurant.db'
)

# If you want to use PostgreSQL, set DATABASE_URL environment variable:
# DATABASE_URL=postgresql://username:password@localhost/restaurant_db

SQLALCHEMY_TRACK_MODIFICATIONS = False 

# Razorpay Configuration (for payment processing)
# IMPORTANT: Set these as environment variables in production!
# For testing, you can use Razorpay test keys
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'your_razorpay_test_key_id')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'your_razorpay_test_key_secret')    