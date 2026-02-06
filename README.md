# Restaurant Management System 🍽️

A modern, full-featured restaurant management web application built with Flask. This system enables restaurants to manage their menus, tables, and orders with real-time updates, QR code-based ordering, and integrated payment processing.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.x-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### For Restaurant Admins
- **Restaurant Registration & Authentication** - Secure login system for restaurant owners
- **Menu Management** - Add, edit, delete menu items with images, descriptions, and pricing
- **Table Management** - Organize and manage restaurant tables with QR codes
- **Order Dashboard** - Real-time order tracking with status updates
- **Real-time Notifications** - WebSocket-based live updates for new orders

### For Customers
- **QR Code Ordering** - Scan table QR codes to access the menu
- **Browse Menu** - View menu items with images and descriptions
- **Shopping Cart** - Add items and customize orders
- **Payment Integration** - Secure payment via Razorpay
- **Order Confirmation** - Instant confirmation with order details

## 🛠️ Technology Stack

- **Backend Framework**: Flask (Python)
- **Database**: SQLAlchemy with SQLite (easily switchable to PostgreSQL)
- **Real-time Communication**: Flask-SocketIO (WebSockets)
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Database Migrations**: Flask-Migrate (Alembic)
- **Payment Gateway**: Razorpay Integration
- **QR Code Generation**: Python qrcode library
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment support (venv)
- Razorpay account (for payment processing - optional for testing)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/restaurant-app.git
cd restaurant-app
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///restaurant.db
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

> **Note**: For testing without payment processing, you can skip Razorpay configuration or use test keys from [Razorpay Dashboard](https://dashboard.razorpay.com/).

### 5. Initialize Database

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 6. Run the Application

```bash
# Using Python directly
python app.py

# Or using Flask CLI
flask run
```

The application will be available at `http://localhost:8080`

## 📖 Detailed Setup

For detailed setup instructions, troubleshooting, and advanced configuration, see [SETUP.md](SETUP.md).

## 🎯 Usage

### Admin Panel

1. **Register a Restaurant**
   - Navigate to `/admin/register`
   - Fill in restaurant details (name, email, password, description, logo)
   - Submit to create your account

2. **Login**
   - Go to `/admin/login`
   - Use your registered email and password

3. **Manage Menu**
   - Add menu items with names, descriptions, prices, categories, and images
   - Toggle item availability
   - Edit or delete existing items

4. **Manage Tables**
   - Add tables with numbers, capacity, and location
   - Generate QR codes for each table
   - View and manage all tables

5. **Track Orders**
   - View real-time order updates
   - Change order status (pending → preparing → ready → delivered)
   - Monitor all active and past orders

### Customer Flow

1. **Scan QR Code** - Customer scans the QR code on their table
2. **Browse Menu** - View available items with details
3. **Add to Cart** - Select items and quantities
4. **Checkout** - Review order and proceed to payment
5. **Payment** - Complete payment via Razorpay
6. **Confirmation** - Receive order confirmation

## 📁 Project Structure

```
restaurant-app/
├── app.py                 # Main application file with routes
├── config.py              # Configuration settings
├── extensions.py          # Flask extensions initialization
├── models.py              # Database models
├── manage.py              # Management script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── migrations/           # Database migration files
├── instance/             # Instance-specific files (database)
├── static/               # Static files (CSS, JS, images)
│   └── uploads/          # User-uploaded files
└── templates/            # HTML templates
    ├── index.html        # Landing page
    ├── admin_login.html  # Admin login
    ├── admin_register.html
    ├── dashboard.html    # Admin dashboard
    ├── admin_menu.html   # Menu management
    ├── admin_tables.html # Table management
    ├── menu.html         # Customer menu view
    ├── cart.html         # Shopping cart
    └── confirmation.html # Order confirmation
```

## 🗄️ Database Schema

The application uses the following main models:

- **Restaurant** - Restaurant information and credentials
- **MenuItem** - Menu items with details and pricing
- **Table** - Restaurant tables with QR codes
- **Order** - Customer orders with status tracking
- **OrderItem** - Individual items within orders

## 🔒 Security Notes

- **Never commit `.env` file** - Contains sensitive credentials
- **Change SECRET_KEY** - Use a strong random key in production
- **Use HTTPS** - Always use HTTPS in production
- **Validate payments** - Implement server-side payment verification
- **Input validation** - Sanitize all user inputs

## 🐛 Troubleshooting

**Database errors**: Delete `instance/restaurant.db` and run migrations again

**Port already in use**: Change the port in `app.py` or set `PORT` environment variable

**Module not found**: Ensure virtual environment is activated and dependencies are installed

For more troubleshooting tips, see [SETUP.md](SETUP.md).

## 🤝 Contributing

Contributions are welcome! This is a testing/learning project, so feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- Flask framework and its extensions
- Razorpay for payment gateway
- The open-source community

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Happy Coding! 🚀**
