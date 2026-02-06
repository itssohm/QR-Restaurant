# Detailed Setup Guide

This guide provides step-by-step instructions for setting up the Restaurant Management System on your local machine.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Creating Test Data](#creating-test-data)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Check version: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **pip (Python Package Installer)**
   - Usually comes with Python
   - Check version: `pip --version`

3. **Git** (for cloning the repository)
   - Download from: https://git-scm.com/downloads

### Optional

- **PostgreSQL** (if you want to use PostgreSQL instead of SQLite)
- **Razorpay Account** (for payment processing)
  - Sign up at: https://razorpay.com/
  - Get test keys from: https://dashboard.razorpay.com/app/keys

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/restaurant-app.git
cd restaurant-app
```

### Step 2: Create a Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- SQLAlchemy (database ORM)
- Flask-Login (authentication)
- Flask-SocketIO (real-time communication)
- Flask-Migrate (database migrations)
- qrcode (QR code generation)
- eventlet (async server)

### Step 4: Verify Installation

```bash
python -c "import flask; print(flask.__version__)"
```

If you see a version number, Flask is installed correctly.

## Database Setup

### Option 1: SQLite (Recommended for Testing)

SQLite is the default and requires no additional setup.

**Initialize the database:**

```bash
# Windows
python manage.py

# macOS/Linux  
python3 manage.py
```

Or use Flask-Migrate for better control:

```bash
# Initialize migrations (only needed once)
flask db init

# Create initial migration
flask db migrate -m "Initial database schema"

# Apply migrations to create tables
flask db upgrade
```

The database file will be created at `instance/restaurant.db`.

### Option 2: PostgreSQL (For Production)

1. **Install PostgreSQL**
   - Download from: https://www.postgresql.org/download/

2. **Create Database**
   ```sql
   CREATE DATABASE restaurant_db;
   CREATE USER restaurant_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE restaurant_db TO restaurant_user;
   ```

3. **Set Environment Variable**
   In your `.env` file:
   ```
   DATABASE_URL=postgresql://restaurant_user:your_password@localhost/restaurant_db
   ```

4. **Run Migrations**
   ```bash
   flask db upgrade
   ```

## Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### Step 2: Edit Configuration

Open `.env` in a text editor and configure:

```env
# Generate a strong secret key (use Python):
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_generated_secret_key_here

# Database (default is SQLite)
DATABASE_URL=sqlite:///restaurant.db

# Razorpay (optional for testing)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_secret_key

# Server (optional)
PORT=8080
HOST=0.0.0.0
```

### Step 3: Generate Secret Key

**Using Python:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your `SECRET_KEY` in `.env`.

## Running the Application

### Method 1: Using app.py (Recommended)

```bash
python app.py
```

The application will start with SocketIO support on `http://localhost:8080`.

### Method 2: Using Flask CLI

```bash
# Set Flask app environment variable first

# Windows PowerShell
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"

# Windows CMD
set FLASK_APP=app.py
set FLASK_ENV=development

# macOS/Linux
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the server
flask run --port=8080
```

**Note:** Flask CLI method may not enable SocketIO. Use `python app.py` for full functionality.

### Accessing the Application

- **Home Page**: http://localhost:8080/
- **Admin Login**: http://localhost:8080/admin/login
- **Admin Register**: http://localhost:8080/admin/register

## Creating Test Data

### Option 1: Through the Web Interface

1. **Register a Restaurant**
   - Go to http://localhost:8080/admin/register
   - Fill in:
     - Name: "Test Restaurant"
     - Email: "test@restaurant.com"
     - Password: "testpass123"
     - Description: "A test restaurant"
     - Logo: (optional, upload an image)

2. **Login**
   - Email: test@restaurant.com
   - Password: testpass123

3. **Add Menu Items**
   - Go to Menu Management
   - Add items with names, descriptions, prices, categories
   - Upload images (optional)

4. **Add Tables**
   - Go to Table Management
   - Add tables: Table 1, Table 2, etc.
   - Set capacity and location

### Option 2: Using Python Script

Create a file `seed_data.py` in the project root:

```python
from app import create_app
from extensions import db
from models import Restaurant, MenuItem, Table
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Create restaurant
    restaurant = Restaurant(
        name="Demo Restaurant",
        email="demo@restaurant.com",
        password=generate_password_hash("demo123"),
        description="A demo restaurant for testing"
    )
    db.session.add(restaurant)
    db.session.commit()
    
    # Add menu items
    items = [
        MenuItem(name="Burger", description="Delicious burger", price=9.99, 
                category="Main Course", is_available=True, restaurant_id=restaurant.id),
        MenuItem(name="Pizza", description="Fresh pizza", price=12.99, 
                category="Main Course", is_available=True, restaurant_id=restaurant.id),
        MenuItem(name="Salad", description="Green salad", price=5.99, 
                category="Appetizer", is_available=True, restaurant_id=restaurant.id),
    ]
    db.session.add_all(items)
    
    # Add tables
    tables = [
        Table(table_number="1", capacity=2, location="Window", restaurant_id=restaurant.id),
        Table(table_number="2", capacity=4, location="Center", restaurant_id=restaurant.id),
        Table(table_number="3", capacity=6, location="Corner", restaurant_id=restaurant.id),
    ]
    db.session.add_all(tables)
    
    db.session.commit()
    print("Test data created successfully!")
```

Run it:
```bash
python seed_data.py
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
- Ensure virtual environment is activated (you should see `(venv)` in terminal)
- Reinstall dependencies: `pip install -r requirements.txt`

### Issue: Database errors / "table does not exist"

**Solution:**
```bash
# Delete the database and start fresh
# Windows
Remove-Item instance\restaurant.db

# macOS/Linux
rm instance/restaurant.db

# Re-run migrations
flask db upgrade
```

### Issue: Port 8080 already in use

**Solution:**
- Change port in `app.py` (line 542): `port = int(os.environ.get("PORT", 8081))`
- Or set environment variable: `$env:PORT=8081` (Windows) or `export PORT=8081` (Linux/Mac)

### Issue: SocketIO not working / Real-time updates not appearing

**Solution:**
- Make sure you're running with `python app.py`, not `flask run`
- eventlet should be installed: `pip install eventlet`
- Check browser console for WebSocket connection errors

### Issue: File upload errors

**Solution:**
- Ensure `static/uploads/` directory exists
- Check file permissions on the directory
- Verify file size isn't too large (adjust `MAX_CONTENT_LENGTH` in config if needed)

### Issue: Razorpay payment not working

**Solution:**
- Verify Razorpay keys are set in `.env`
- Use test keys for development (start with `rzp_test_`)
- Check browser console for JavaScript errors
- Ensure you're using HTTPS in production (Razorpay requirement)

### Issue: CSS/JS not loading

**Solution:**
- Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
- Check that static files are in `static/` directory
- Verify Flask is serving static files correctly

### Issue: Migration conflicts

**Solution:**
```bash
# Delete migrations folder (keep migrations/README)
# Windows
Remove-Item -Recurse migrations\versions

# macOS/Linux
rm -rf migrations/versions

# Recreate migrations
flask db migrate -m "Fresh migration"
flask db upgrade
```

## Development Tips

### Running in Debug Mode

Debug mode enables:
- Auto-reload on code changes
- Detailed error pages
- Interactive debugger

Already enabled in `manage.py`:
```bash
python manage.py
```

### Viewing Database

**SQLite:**
- Use DB Browser for SQLite: https://sqlitebrowser.org/
- Or command line: `sqlite3 instance/restaurant.db`

**PostgreSQL:**
- Use pgAdmin: https://www.pgadmin.org/
- Or command line: `psql restaurant_db`

### Testing WebSocket Events

Open browser console and monitor:
```javascript
// In the admin dashboard, your browser connects to SocketIO
// Check for connection messages in console
```

## Next Steps

Once your application is running:

1. **Customize the UI** - Edit templates in `templates/`
2. **Add Features** - Extend models and routes in `models.py` and `app.py`
3. **Deploy** - Consider platforms like Heroku, Railway, or DigitalOcean
4. **Add Tests** - Write unit tests for your routes and models

## Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Flask-SocketIO: https://flask-socketio.readthedocs.io/
- Razorpay API Docs: https://razorpay.com/docs/

---

**Need Help?** Open an issue on GitHub or check existing issues for solutions.
