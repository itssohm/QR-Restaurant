from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from extensions import db, migrate
from models import Restaurant, MenuItem, Table, Order, OrderItem
import os
from datetime import datetime

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_pyfile('config.py')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    
    # Ensure the uploads directory exists
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Home page route
    @app.route('/')
    def home():
        # Get featured restaurants
        restaurants = Restaurant.query.limit(3).all()
        return render_template('index.html', restaurants=restaurants, current_year=datetime.now().year)
    
    # Login required decorator
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'restaurant_id' not in session:
                flash('Please log in to access this page', 'error')
                return redirect(url_for('admin_login'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Admin login route
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            restaurant = Restaurant.query.filter_by(email=email).first()
            
            if restaurant and check_password_hash(restaurant.password, password):
                session['restaurant_id'] = restaurant.id
                session['restaurant_name'] = restaurant.name
                flash('Login successful', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid email or password', 'error')
        
        return render_template('admin_login.html')
    
    # Admin registration route
    @app.route('/admin/register', methods=['GET', 'POST'])
    def admin_register():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            description = request.form.get('description')
            
            # Check if passwords match
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('admin_register'))
            
            # Check if email is already registered
            existing_restaurant = Restaurant.query.filter_by(email=email).first()
            if existing_restaurant:
                flash('Email is already registered', 'error')
                return redirect(url_for('admin_register'))
            
            # Handle logo upload
            logo_url = None
            if 'logo' in request.files and request.files['logo'].filename:
                logo = request.files['logo']
                filename = secure_filename(logo.filename)
                logo_path = os.path.join(app.static_folder, 'uploads', filename)
                logo.save(logo_path)
                logo_url = url_for('static', filename=f'uploads/{filename}')
            
            # Create new restaurant
            new_restaurant = Restaurant(
                name=name,
                email=email,
                password=generate_password_hash(password),
                description=description,
                logo_url=logo_url
            )
            
            db.session.add(new_restaurant)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('admin_login'))
        
        return render_template('admin_register.html')
    
    # Admin logout route
    @app.route('/admin/logout')
    def admin_logout():
        session.pop('restaurant_id', None)
        session.pop('restaurant_name', None)
        flash('You have been logged out', 'success')
        return redirect(url_for('admin_login'))
    
    # Admin dashboard route
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        restaurant = Restaurant.query.get(session['restaurant_id'])
        return render_template('dashboard.html', restaurant=restaurant)
    
    # Admin menu management route
    @app.route('/admin/menu')
    @login_required
    def admin_menu():
        restaurant = Restaurant.query.get(session['restaurant_id'])
        menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).all()
        return render_template('admin_menu.html', restaurant=restaurant, menu_items=menu_items)
    
    # Admin table management route
    @app.route('/admin/tables')
    @login_required
    def admin_tables():
        restaurant = Restaurant.query.get(session['restaurant_id'])
        tables = Table.query.filter_by(restaurant_id=restaurant.id).all()
        return render_template('admin_tables.html', restaurant=restaurant, tables=tables)
    
    # API endpoint to get orders
    @app.route('/api/orders')
    @login_required
    def get_orders():
        status = request.args.get('status', 'all')
        restaurant_id = session['restaurant_id']
        
        if status == 'all':
            orders = Order.query.filter_by(restaurant_id=restaurant_id).order_by(Order.created_at.desc()).all()
        else:
            orders = Order.query.filter_by(restaurant_id=restaurant_id, status=status).order_by(Order.created_at.desc()).all()
        
        orders_list = []
        for order in orders:
            items = []
            for item in order.order_items:
                menu_item = MenuItem.query.get(item.menu_item_id)
                items.append({
                    'id': item.id,
                    'name': menu_item.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'special_instructions': item.special_instructions
                })
            
            orders_list.append({
                'id': order.id,
                'table_number': order.table.table_number,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat(),
                'items': items
            })
        
        return jsonify(orders_list)
    
    # API endpoint to update order status
    @app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
    @login_required
    def update_order_status(order_id):
        data = request.json
        status = data.get('status')
        
        order = Order.query.get_or_404(order_id)
        
        # Check if the order belongs to the logged-in restaurant
        if order.restaurant_id != session['restaurant_id']:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        order.status = status
        db.session.commit()
        
        # Emit a socket event to update clients
        order_data = {
            'id': order.id,
            'status': order.status,
            'table_number': order.table.table_number
        }
        socketio.emit('order_update', order_data)
        
        return jsonify({'success': True, 'order': order_data})
    
    # Customer-facing menu route
    @app.route('/menu')
    def view_menu():
        restaurant_id = request.args.get('rid')
        table_id = request.args.get('tid')
        
        if not restaurant_id or not table_id:
            return redirect(url_for('home'))
        
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        table = Table.query.get_or_404(table_id)
        menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
        
        return render_template('menu.html', restaurant=restaurant, table_id=table_id, menu_items=menu_items)


    # Add menu item route
    @app.route('/admin/add_menu_item', methods=['POST'])
    @login_required
    def add_menu_item():
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            category = request.form.get('category')
            is_available = 'is_available' in request.form
            
            # Handle image upload
            image_url = None
            if 'image' in request.files and request.files['image'].filename:
                image = request.files['image']
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.static_folder, 'uploads', filename)
                image.save(image_path)
                image_url = url_for('static', filename=f'uploads/{filename}')
            
            # Create new menu item
            new_item = MenuItem(
                name=name,
                description=description,
                price=price,
                category=category,
                is_available=is_available,
                image_url=image_url,
                restaurant_id=session['restaurant_id']
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            flash('Menu item added successfully', 'success')
            return redirect(url_for('admin_menu'))
        
        return redirect(url_for('admin_menu'))

    # Edit menu item route
    @app.route('/admin/edit_menu_item', methods=['POST'])
    @login_required
    def edit_menu_item():
        if request.method == 'POST':
            item_id = request.form.get('item_id')
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            category = request.form.get('category')
            is_available = 'is_available' in request.form
            
            # Get the menu item
            menu_item = MenuItem.query.get_or_404(item_id)
            
            # Check if the menu item belongs to the logged-in restaurant
            if menu_item.restaurant_id != session['restaurant_id']:
                flash('Unauthorized', 'error')
                return redirect(url_for('admin_menu'))
            
            # Update menu item
            menu_item.name = name
            menu_item.description = description
            menu_item.price = price
            menu_item.category = category
            menu_item.is_available = is_available
            
            # Handle image upload
            if 'image' in request.files and request.files['image'].filename:
                image = request.files['image']
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.static_folder, 'uploads', filename)
                image.save(image_path)
                menu_item.image_url = url_for('static', filename=f'uploads/{filename}')
            
            db.session.commit()
            
            flash('Menu item updated successfully', 'success')
            return redirect(url_for('admin_menu'))
        
        return redirect(url_for('admin_menu'))

    # Delete menu item route
    @app.route('/admin/delete_menu_item', methods=['POST'])
    @login_required
    def delete_menu_item():
        if request.method == 'POST':
            item_id = request.form.get('item_id')
            
            # Get the menu item
            menu_item = MenuItem.query.get_or_404(item_id)
            
            # Check if the menu item belongs to the logged-in restaurant
            if menu_item.restaurant_id != session['restaurant_id']:
                flash('Unauthorized', 'error')
                return redirect(url_for('admin_menu'))
            
            # Delete the menu item
            db.session.delete(menu_item)
            db.session.commit()
            
            flash('Menu item deleted successfully', 'success')
            return redirect(url_for('admin_menu'))
        
        return redirect(url_for('admin_menu'))

    # Update item availability route
    @app.route('/admin/update_item_availability', methods=['POST'])
    @login_required
    def update_item_availability():
        data = request.json
        item_id = data.get('item_id')
        is_available = data.get('is_available')
        
        # Get the menu item
        menu_item = MenuItem.query.get_or_404(item_id)
        
        # Check if the menu item belongs to the logged-in restaurant
        if menu_item.restaurant_id != session['restaurant_id']:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Update the availability
        menu_item.is_available = is_available
        db.session.commit()
        
        return jsonify({'success': True}) 
    



        # Add table route
    @app.route('/admin/add_table', methods=['POST'])
    @login_required
    def add_table():
        if request.method == 'POST':
            table_number = request.form.get('table_number')
            capacity = request.form.get('capacity') or 0
            location = request.form.get('location') or ''
            
            # Check if table number already exists for this restaurant
            existing_table = Table.query.filter_by(
                restaurant_id=session['restaurant_id'],
                table_number=table_number
            ).first()
            
            if existing_table:
                flash('Table number already exists', 'error')
                return redirect(url_for('admin_tables'))
            
            # Create new table
            new_table = Table(
                table_number=table_number,
                capacity=capacity,
                location=location,
                restaurant_id=session['restaurant_id']
            )
            
            db.session.add(new_table)
            db.session.commit()
            
            flash('Table added successfully', 'success')
            return redirect(url_for('admin_tables'))
        
        return redirect(url_for('admin_tables'))

    # Edit table route
    @app.route('/admin/edit_table', methods=['POST'])
    @login_required
    def edit_table():
        if request.method == 'POST':
            table_id = request.form.get('table_id')
            table_number = request.form.get('table_number')
            capacity = request.form.get('capacity') or 0
            location = request.form.get('location') or ''
            
            # Get the table
            table = Table.query.get_or_404(table_id)
            
            # Check if the table belongs to the logged-in restaurant
            if table.restaurant_id != session['restaurant_id']:
                flash('Unauthorized', 'error')
                return redirect(url_for('admin_tables'))
            
            # Check if table number already exists for this restaurant (excluding current table)
            existing_table = Table.query.filter(
                Table.restaurant_id == session['restaurant_id'],
                Table.table_number == table_number,
                Table.id != table_id
            ).first()
            
            if existing_table:
                flash('Table number already exists', 'error')
                return redirect(url_for('admin_tables'))
            
            # Update table
            table.table_number = table_number
            table.capacity = capacity
            table.location = location
            
            db.session.commit()
            
            flash('Table updated successfully', 'success')
            return redirect(url_for('admin_tables'))
        
        return redirect(url_for('admin_tables'))

    # Delete table route
    @app.route('/admin/delete_table', methods=['POST'])
    @login_required
    def delete_table():
        if request.method == 'POST':
            table_id = request.form.get('table_id')
            
            # Get the table
            table = Table.query.get_or_404(table_id)
            
            # Check if the table belongs to the logged-in restaurant
            if table.restaurant_id != session['restaurant_id']:
                flash('Unauthorized', 'error')
                return redirect(url_for('admin_tables'))
            
            # Check if the table has any orders
            has_orders = Order.query.filter_by(table_id=table_id).first() is not None
            
            if has_orders:
                flash('Cannot delete table with associated orders', 'error')
                return redirect(url_for('admin_tables'))
            
            # Delete the table
            db.session.delete(table)
            db.session.commit()
            
            flash('Table deleted successfully', 'success')
            return redirect(url_for('admin_tables'))
        
        return redirect(url_for('admin_tables'))



    # Cart route
    @app.route('/cart')
    def view_cart():
        restaurant_id = request.args.get('rid')
        table_id = request.args.get('tid')
        
        if not restaurant_id or not table_id:
            return redirect(url_for('home'))
        
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        table = Table.query.get_or_404(table_id)
        
        # Pass config to template so Razorpay key is available
        return render_template('cart.html', 
                            restaurant=restaurant, 
                            table=table, 
                            table_id=table_id,
                            config=app.config)
    
    # Place order route
    @app.route('/place_order', methods=['POST'])
    def place_order():
        data = request.json
        payment_id = data.get('paymentId')
        cart = data.get('cart')
        
        if not payment_id or not cart:
            return jsonify({'success': False, 'message': 'Invalid data'})
        
        restaurant_id = cart.get('restaurantId')
        table_id = cart.get('tableId')
        total = cart.get('total')
        items = cart.get('items')
        
        # Create a new order
        order = Order(
            total_amount=total,
            payment_status='completed',
            payment_id=payment_id,
            table_id=table_id,
            restaurant_id=restaurant_id
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item in items:
            order_item = OrderItem(
                quantity=item['quantity'],
                price=item['price'],
                menu_item_id=item['id'],
                order_id=order.id
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Emit a socket event for the new order
        order_data = {
            'id': order.id,
            'status': order.status,
            'table_number': order.table.table_number,
            'restaurant_id': order.restaurant_id
        }
        socketio.emit('new_order', order_data)
        
        return jsonify({'success': True, 'order_id': order.id})
    
    # Order confirmation route
    @app.route('/confirmation')
    def order_confirmation():
        order_id = request.args.get('order_id')
        if not order_id:
            return redirect(url_for('home'))
        
        order = Order.query.get_or_404(order_id)
        restaurant = Restaurant.query.get(order.restaurant_id)
        
        return render_template('confirmation.html', order=order, restaurant=restaurant)
    
    return app

if __name__ == '__main__':
    
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("APP_HOST", "127.0.0.1") 
    socketio.run(app, host=host, port=port)