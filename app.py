from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_wtf.csrf import CSRFProtect
import mysql.connector
import bcrypt
import os
from datetime import datetime
import csv
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from functools import wraps
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-2024-protrack-rpt-system')
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600
csrf = CSRFProtect(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'protrack_rpt'
}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        return None

def init_database():
    """Initialize database tables if they don't exist"""
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Create consumables table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consumables (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                quantity INT DEFAULT 0,
                image_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(255) NOT NULL,
                department VARCHAR(255) NOT NULL,
                purpose TEXT NOT NULL,
                date_needed DATE NOT NULL,
                status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create order_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT,
                consumable_id INT,
                quantity INT NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (consumable_id) REFERENCES consumables(id) ON DELETE CASCADE
            )
        """)
        
        # Create admin_users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create audit_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                admin_username VARCHAR(100),
                action VARCHAR(255),
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create laboratory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laboratory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                status ENUM('Active', 'Inactive', 'Maintenance') DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create lab_assets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_assets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lab_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                status ENUM('Available', 'In Use', 'Maintenance', 'Retired') DEFAULT 'Available',
                purchase_date DATE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (lab_id) REFERENCES laboratory(id) ON DELETE CASCADE
            )
        """)
        
        # Insert default admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        if cursor.fetchone()[0] == 0:
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO admin_users (username, password) VALUES (%s, %s)
            """, ('admin', hashed_password.decode('utf-8')))
            
            # Insert sample consumables
            sample_items = [
                ('Office Paper A4', 'High quality A4 paper for printing', 'Office Supplies', 500, '/static/images/paper.jpg'),
                ('Blue Pens', 'Blue ballpoint pens, pack of 10', 'Writing Supplies', 100, '/static/images/pens.jpg'),
                ('Stapler', 'Heavy duty stapler with staples', 'Office Equipment', 25, '/static/images/stapler.jpg'),
                ('Notebooks', 'Spiral bound notebooks, A5 size', 'Writing Supplies', 75, '/static/images/notebooks.jpg'),
                ('USB Cables', 'USB Type-C cables, 1m length', 'Electronics', 50, '/static/images/usb.jpg')
            ]
            
            for item in sample_items:
                cursor.execute("""
                    INSERT INTO consumables (name, description, category, quantity, image_url) 
                    VALUES (%s, %s, %s, %s, %s)
                """, item)
        
        connection.commit()
        return True
        
    except mysql.connector.Error as err:
        logger.error(f"Database initialization error: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login as admin to access this page', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def log_admin_action(action, details):
    """Log admin actions for audit trail"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO audit_logs (admin_username, action, details) 
                VALUES (%s, %s, %s)
            """, (session.get('admin_username'), action, details))
            connection.commit()
        except mysql.connector.Error as err:
            logger.error(f"Audit log error: {err}")
        finally:
            cursor.close()
            connection.close()

@app.route('/')
def index():
    """Public home page with consumables listing"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return render_template('index.html', consumables=[])
    
    cursor = connection.cursor(dictionary=True)
    
    # Get search and filter parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Build query with filters
    query = "SELECT * FROM consumables WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE %s OR description LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    # Get total count for pagination
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    cursor.execute(count_query, params)
    total_items = cursor.fetchone()['COUNT(*)']
    
    # Add pagination
    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    consumables = cursor.fetchall()
    
    # Get unique categories for filter
    cursor.execute("SELECT DISTINCT category FROM consumables ORDER BY category")
    categories = [row['category'] for row in cursor.fetchall()]
    
    cursor.close()
    connection.close()
    
    total_pages = (total_items + per_page - 1) // per_page
    
    return render_template('index.html', 
                         consumables=consumables, 
                         categories=categories,
                         search=search,
                         category=category,
                         page=page,
                         total_pages=total_pages)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Add item to cart (session-based)"""
    if 'cart' not in session:
        session['cart'] = {}
    
    consumable_id = request.form.get('consumable_id')
    quantity = int(request.form.get('quantity', 1))
    
    if consumable_id in session['cart']:
        session['cart'][consumable_id] += quantity
    else:
        session['cart'][consumable_id] = quantity
    
    session.modified = True
    flash('Item added to cart successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    """View cart contents"""
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty', 'info')
        return redirect(url_for('index'))
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))
    
    cursor = connection.cursor(dictionary=True)
    cart_items = []
    total = 0
    
    for consumable_id, quantity in session['cart'].items():
        cursor.execute("SELECT * FROM consumables WHERE id = %s", (consumable_id,))
        item = cursor.fetchone()
        if item:
            item['cart_quantity'] = quantity
            cart_items.append(item)
            total += quantity
    
    cursor.close()
    connection.close()
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart quantities"""
    consumable_id = request.form.get('consumable_id')
    quantity = int(request.form.get('quantity', 0))
    
    if quantity <= 0:
        session['cart'].pop(consumable_id, None)
    else:
        session['cart'][consumable_id] = quantity
    
    session.modified = True
    flash('Cart updated successfully!', 'success')
    return redirect(url_for('cart'))

@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    """Place order from cart"""
    if request.method == 'GET':
        if 'cart' not in session or not session['cart']:
            flash('Your cart is empty', 'info')
            return redirect(url_for('index'))
        return render_template('place_order.html')
    
    # Process order
    user_name = request.form.get('user_name')
    department = request.form.get('department')
    purpose = request.form.get('purpose')
    date_needed = request.form.get('date_needed')
    
    if not all([user_name, department, purpose, date_needed]):
        flash('Please fill in all required fields', 'error')
        return render_template('place_order.html')
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return render_template('place_order.html')
    
    cursor = connection.cursor()
    
    try:
        # Create order
        cursor.execute("""
            INSERT INTO orders (user_name, department, purpose, date_needed) 
            VALUES (%s, %s, %s, %s)
        """, (user_name, department, purpose, date_needed))
        
        order_id = cursor.lastrowid
        
        # Add order items
        for consumable_id, quantity in session['cart'].items():
            cursor.execute("""
                INSERT INTO order_items (order_id, consumable_id, quantity) 
                VALUES (%s, %s, %s)
            """, (order_id, consumable_id, quantity))
        
        connection.commit()
        
        # Clear cart
        session.pop('cart', None)
        
        flash('Order placed successfully! Your order ID is: ' + str(order_id), 'success')
        return redirect(url_for('index'))
        
    except mysql.connector.Error as err:
        connection.rollback()
        flash('Error placing order. Please try again.', 'error')
        logger.error(f"Order placement error: {err}")
    finally:
        cursor.close()
        connection.close()
    
    return render_template('place_order.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection error', 'error')
            return render_template('admin/login.html')
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            log_admin_action('Login', f'Admin {username} logged in')
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    if 'admin_logged_in' in session:
        log_admin_action('Logout', f'Admin {session.get("admin_username")} logged out')
        session.pop('admin_logged_in', None)
        session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return render_template('admin/dashboard.html')
    
    cursor = connection.cursor(dictionary=True)
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as total_items FROM consumables")
    total_items = cursor.fetchone()['total_items']
    
    cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
    total_orders = cursor.fetchone()['total_orders']
    
    cursor.execute("SELECT COUNT(*) as pending_orders FROM orders WHERE status = 'Pending'")
    pending_orders = cursor.fetchone()['pending_orders']
    
    cursor.execute("SELECT COUNT(*) as low_stock FROM consumables WHERE quantity < 10")
    low_stock = cursor.fetchone()['low_stock']
    
    # Get recent orders
    cursor.execute("""
        SELECT o.*, COUNT(oi.id) as item_count 
        FROM orders o 
        LEFT JOIN order_items oi ON o.id = oi.order_id 
        GROUP BY o.id 
        ORDER BY o.created_at DESC 
        LIMIT 5
    """)
    recent_orders = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('admin/dashboard.html',
                         total_items=total_items,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         low_stock=low_stock,
                         recent_orders=recent_orders)

@app.route('/admin/inventory')
@admin_required
def admin_inventory():
    """Manage laboratories list"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return render_template('admin/inventory.html', labs=[], search='', sort_by='name', sort_order='asc', page=1, total_pages=0)

    cursor = connection.cursor(dictionary=True)
    
    # Get search and filter parameters
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Build query with search
    query = "SELECT * FROM laboratory WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE %s OR status LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    # Get total count for pagination
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    cursor.execute(count_query, params)
    total_labs = cursor.fetchone()['COUNT(*)']
    
    # Add sorting and pagination
    query += f" ORDER BY {sort_by} {sort_order.upper()}"
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])
    
    try:
        cursor.execute(query, params)
        labs = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    total_pages = (total_labs + per_page - 1) // per_page
    
    return render_template('admin/inventory.html', 
                         labs=labs, 
                         search=search,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         page=page,
                         total_pages=total_pages)


@app.route('/admin/labs/add', methods=['POST'])
@admin_required
def admin_add_lab():
    """Add a new laboratory (name, status)"""
    name = (request.form.get('name') or '').strip()
    status = (request.form.get('status') or '').strip()

    if not name or status not in ('Active', 'Inactive', 'Maintenance'):
        flash('Please provide a valid Lab Name and Status', 'error')
        return redirect(url_for('admin_inventory'))

    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_inventory'))

    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO laboratory (name, status)
            VALUES (%s, %s)
            """,
            (name, status),
        )
        connection.commit()
        log_admin_action('Add Lab', f'Added lab: {name} ({status})')
        flash('Laboratory added successfully!', 'success')
    except mysql.connector.Error as err:
        connection.rollback()
        logger.error(f"Add laboratory error: {err}")
        flash('Error adding laboratory', 'error')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_inventory'))

@app.route('/admin/inventory/add', methods=['GET', 'POST'])
@admin_required
def admin_add_consumable():
    """Add new consumable"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        quantity = int(request.form.get('quantity', 0))
        image_url = request.form.get('image_url', '')
        
        if not all([name, description, category]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('admin_inventory'))
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection error', 'error')
            return redirect(url_for('admin_inventory'))
        
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO consumables (name, description, category, quantity, image_url) 
                VALUES (%s, %s, %s, %s, %s)
            """, (name, description, category, quantity, image_url))
            
            connection.commit()
            log_admin_action('Add Consumable', f'Added: {name}')
            flash('Consumable added successfully!', 'success')
            return redirect(url_for('admin_inventory'))
            
        except mysql.connector.Error as err:
            connection.rollback()
            flash('Error adding consumable', 'error')
            logger.error(f"Add consumable error: {err}")
        finally:
            cursor.close()
            connection.close()
    
    # For GET requests, redirect to inventory (no standalone page)
    return redirect(url_for('admin_inventory'))

@app.route('/admin/inventory/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_consumable(id):
    """Edit existing consumable"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_inventory'))
    
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'GET':
        cursor.execute("SELECT * FROM consumables WHERE id = %s", (id,))
        consumable = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not consumable:
            flash('Consumable not found', 'error')
            return redirect(url_for('admin_inventory'))
        
        return render_template('admin/edit_consumable.html', consumable=consumable)
    
    # Process edit
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')
    quantity = int(request.form.get('quantity', 0))
    image_url = request.form.get('image_url', '')
    
    if not all([name, description, category]):
        flash('Please fill in all required fields', 'error')
        return redirect(url_for('admin_edit_consumable', id=id))
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            UPDATE consumables 
            SET name = %s, description = %s, category = %s, quantity = %s, image_url = %s 
            WHERE id = %s
        """, (name, description, category, quantity, image_url, id))
        
        connection.commit()
        log_admin_action('Edit Consumable', f'Edited: {name}')
        flash('Consumable updated successfully!', 'success')
        return redirect(url_for('admin_inventory'))
        
    except mysql.connector.Error as err:
        connection.rollback()
        flash('Error updating consumable', 'error')
        logger.error(f"Edit consumable error: {err}")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_edit_consumable', id=id))

@app.route('/admin/inventory/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_consumable(id):
    """Delete consumable"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_inventory'))
    
    cursor = connection.cursor(dictionary=True)
    
    # Get consumable name for audit log
    cursor.execute("SELECT name FROM consumables WHERE id = %s", (id,))
    consumable = cursor.fetchone()
    
    if not consumable:
        flash('Consumable not found', 'error')
        return redirect(url_for('admin_inventory'))
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("DELETE FROM consumables WHERE id = %s", (id,))
        connection.commit()
        log_admin_action('Delete Consumable', f'Deleted: {consumable["name"]}')
        flash('Consumable deleted successfully!', 'success')
    except mysql.connector.Error as err:
        connection.rollback()
        flash('Error deleting consumable', 'error')
        logger.error(f"Delete consumable error: {err}")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_inventory'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    """View and manage orders"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return render_template('admin/orders.html', orders=[])
    
    cursor = connection.cursor(dictionary=True)
    
    # Get filter parameters
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    # Build query
    query = """
        SELECT o.*, COUNT(oi.id) as item_count, 
               SUM(oi.quantity) as total_quantity
        FROM orders o 
        LEFT JOIN order_items oi ON o.id = oi.order_id 
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND o.status = %s"
        params.append(status)
    
    if search:
        query += " AND (o.user_name LIKE %s OR o.department LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += " GROUP BY o.id ORDER BY o.created_at DESC"
    
    cursor.execute(query, params)
    orders = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('admin/orders.html',
                         orders=orders,
                         status=status,
                         search=search)

@app.route('/admin/orders/<int:id>')
@admin_required
def admin_order_detail(id):
    """View order details"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_orders'))
    
    cursor = connection.cursor(dictionary=True)
    
    # Get order details
    cursor.execute("SELECT * FROM orders WHERE id = %s", (id,))
    order = cursor.fetchone()
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('admin_orders'))
    
    # Get order items
    cursor.execute("""
        SELECT oi.*, c.name, c.description, c.category, c.quantity as stock_quantity
        FROM order_items oi
        JOIN consumables c ON oi.consumable_id = c.id
        WHERE oi.order_id = %s
    """, (id,))
    order_items = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('admin/order_detail.html', order=order, order_items=order_items)

@app.route('/admin/orders/<int:id>/approve', methods=['POST'])
@admin_required
def admin_approve_order(id):
    """Approve order and reduce stock"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_order_detail', id=id))
    
    cursor = connection.cursor()
    
    try:
        # Update order status
        cursor.execute("UPDATE orders SET status = 'Approved' WHERE id = %s", (id,))
        
        # Get order items and reduce stock
        cursor.execute("""
            SELECT oi.consumable_id, oi.quantity, c.name, c.quantity as current_stock
            FROM order_items oi
            JOIN consumables c ON oi.consumable_id = c.id
            WHERE oi.order_id = %s
        """, (id,))
        
        order_items = cursor.fetchall()
        
        for item in order_items:
            consumable_id, quantity, name, current_stock = item
            new_stock = current_stock - quantity
            
            if new_stock < 0:
                connection.rollback()
                flash(f'Insufficient stock for {name}. Available: {current_stock}, Requested: {quantity}', 'error')
                return redirect(url_for('admin_order_detail', id=id))
            
            cursor.execute("""
                UPDATE consumables SET quantity = %s WHERE id = %s
            """, (new_stock, consumable_id))
        
        connection.commit()
        log_admin_action('Approve Order', f'Approved order #{id}')
        flash('Order approved successfully! Stock quantities updated.', 'success')
        
    except mysql.connector.Error as err:
        connection.rollback()
        flash('Error approving order', 'error')
        logger.error(f"Approve order error: {err}")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_order_detail', id=id))

@app.route('/admin/orders/<int:id>/reject', methods=['POST'])
@admin_required
def admin_reject_order(id):
    """Reject order"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_order_detail', id=id))
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("UPDATE orders SET status = 'Rejected' WHERE id = %s", (id,))
        connection.commit()
        log_admin_action('Reject Order', f'Rejected order #{id}')
        flash('Order rejected successfully!', 'success')
    except mysql.connector.Error as err:
        connection.rollback()
        flash('Error rejecting order', 'error')
        logger.error(f"Reject order error: {err}")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_order_detail', id=id))

@app.route('/admin/export/orders')
@admin_required
def admin_export_orders():
    """Export orders to CSV"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_orders'))
    
    cursor = connection.cursor(dictionary=True)
    
    # Get all orders with items
    cursor.execute("""
        SELECT o.*, GROUP_CONCAT(CONCAT(c.name, ' (', oi.quantity, ')') SEPARATOR '; ') as items
        FROM orders o 
        LEFT JOIN order_items oi ON o.id = oi.order_id 
        LEFT JOIN consumables c ON oi.consumable_id = c.id
        GROUP BY o.id 
        ORDER BY o.created_at DESC
    """)
    
    orders = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Order ID', 'User Name', 'Department', 'Purpose', 'Date Needed', 'Status', 'Items', 'Created At'])
    
    # Write data
    for order in orders:
        writer.writerow([
            order['id'],
            order['user_name'],
            order['department'],
            order['purpose'],
            order['date_needed'],
            order['status'],
            order['items'] or 'No items',
            order['created_at']
        ])
    
    output.seek(0)
    
    log_admin_action('Export Orders', f'Exported {len(orders)} orders to CSV')
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'orders_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/admin/export/inventory')
@admin_required
def admin_export_inventory():
    """Export inventory to Excel"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_inventory'))
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM consumables ORDER BY category, name")
    consumables = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory"
    
    # Style headers
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
    
    # Write headers
    headers = ['ID', 'Name', 'Description', 'Category', 'Quantity', 'Image URL', 'Created At']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
    
    # Write data
    for row, item in enumerate(consumables, 2):
        ws.cell(row=row, column=1, value=item['id'])
        ws.cell(row=row, column=2, value=item['name'])
        ws.cell(row=row, column=3, value=item['description'])
        ws.cell(row=row, column=4, value=item['category'])
        ws.cell(row=row, column=5, value=item['quantity'])
        ws.cell(row=row, column=6, value=item['image_url'])
        ws.cell(row=row, column=7, value=item['created_at'])
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    log_admin_action('Export Inventory', f'Exported {len(consumables)} items to Excel')
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'inventory_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@app.route('/admin/audit-logs')
@admin_required
def admin_audit_logs():
    """View audit logs"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return render_template('admin/audit_logs.html', logs=[])
    
    cursor = connection.cursor(dictionary=True)
    
    # Get logs with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    cursor.execute("SELECT COUNT(*) as total FROM audit_logs")
    total_logs = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT * FROM audit_logs 
        ORDER BY timestamp DESC 
        LIMIT %s OFFSET %s
    """, (per_page, (page - 1) * per_page))
    
    logs = cursor.fetchall()
    cursor.close()
    connection.close()
    
    total_pages = (total_logs + per_page - 1) // per_page
    
    return render_template('admin/audit_logs.html',
                         logs=logs,
                         page=page,
                         total_pages=total_pages)


@app.route('/admin/labs/<int:lab_id>/assets')
@admin_required
def admin_lab_assets(lab_id):
    """View all assets in a specific laboratory"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_inventory'))
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get lab information
        cursor.execute("SELECT * FROM laboratory WHERE id = %s", (lab_id,))
        lab = cursor.fetchone()
        
        if not lab:
            flash('Laboratory not found', 'error')
            return redirect(url_for('admin_inventory'))
        
        # Get search and filter parameters
        search = request.args.get('search', '')
        category_filter = request.args.get('category_filter', '')
        status_filter = request.args.get('status_filter', '')
        
        # Build query for assets
        query = "SELECT * FROM lab_assets WHERE lab_id = %s"
        params = [lab_id]
        
        if search:
            query += " AND (name LIKE %s OR description LIKE %s)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        if category_filter:
            query += " AND category = %s"
            params.append(category_filter)
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        assets = cursor.fetchall()
        
    finally:
        cursor.close()
        connection.close()
    
    return render_template('admin/lab_assets.html', 
                         lab=lab, 
                         assets=assets,
                         search=search,
                         category_filter=category_filter,
                         status_filter=status_filter)


@app.route('/admin/labs/<int:lab_id>/assets/add', methods=['POST'])
@admin_required
def admin_add_asset(lab_id):
    """Add a new asset to a laboratory"""
    name = (request.form.get('name') or '').strip()
    category = (request.form.get('category') or '').strip()
    status = (request.form.get('status') or '').strip()
    purchase_date = request.form.get('purchase_date') or None
    description = (request.form.get('description') or '').strip()
    
    if not all([name, category, status]):
        flash('Please provide Asset Name, Category, and Status', 'error')
        return redirect(url_for('admin_lab_assets', lab_id=lab_id))
    
    if status not in ('Available', 'In Use', 'Maintenance', 'Retired'):
        flash('Invalid status selected', 'error')
        return redirect(url_for('admin_lab_assets', lab_id=lab_id))
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_lab_assets', lab_id=lab_id))
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO lab_assets (lab_id, name, category, status, purchase_date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (lab_id, name, category, status, purchase_date, description),
        )
        connection.commit()
        log_admin_action('Add Asset', f'Added asset: {name} to lab #{lab_id}')
        flash('Asset added successfully!', 'success')
    except mysql.connector.Error as err:
        connection.rollback()
        logger.error(f"Add asset error: {err}")
        flash('Error adding asset', 'error')
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_lab_assets', lab_id=lab_id))


@app.route('/admin/labs/<int:lab_id>/edit', methods=['POST'])
@admin_required
def admin_edit_lab(lab_id):
    """Edit laboratory information"""
    name = (request.form.get('name') or '').strip()
    status = (request.form.get('status') or '').strip()
    
    if not name or status not in ('Active', 'Inactive', 'Maintenance'):
        flash('Please provide a valid Lab Name and Status', 'error')
        return redirect(url_for('admin_lab_assets', lab_id=lab_id))
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_lab_assets', lab_id=lab_id))
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE laboratory SET name = %s, status = %s WHERE id = %s
            """,
            (name, status, lab_id),
        )
        connection.commit()
        log_admin_action('Edit Lab', f'Updated lab: {name} (ID: {lab_id})')
        flash('Laboratory updated successfully!', 'success')
    except mysql.connector.Error as err:
        connection.rollback()
        logger.error(f"Edit laboratory error: {err}")
        flash('Error updating laboratory', 'error')
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_lab_assets', lab_id=lab_id))


@app.route('/admin/labs/<int:lab_id>/delete', methods=['POST'])
@admin_required
def admin_delete_lab(lab_id):
    """Delete a laboratory only if it has no assets"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('admin_lab_assets', lab_id=lab_id))

    cursor = connection.cursor(dictionary=True)
    try:
        # Verify lab exists and get its name
        cursor.execute("SELECT name FROM laboratory WHERE id = %s", (lab_id,))
        lab = cursor.fetchone()
        if not lab:
            flash('Laboratory not found', 'error')
            return redirect(url_for('admin_inventory'))

        # Check if lab has any assets
        cursor.execute("SELECT COUNT(*) AS cnt FROM lab_assets WHERE lab_id = %s", (lab_id,))
        asset_count = cursor.fetchone()['cnt']

        if asset_count and int(asset_count) > 0:
            flash('Cannot delete this laboratory because it has assets. Remove all assets first.', 'error')
            return redirect(url_for('admin_lab_assets', lab_id=lab_id))

        # Safe to delete
        cursor.execute("DELETE FROM laboratory WHERE id = %s", (lab_id,))
        connection.commit()
        log_admin_action('Delete Lab', f"Deleted lab: {lab['name']} (ID: {lab_id})")
        flash('Laboratory deleted successfully!', 'success')
        return redirect(url_for('admin_inventory'))

    except mysql.connector.Error as err:
        connection.rollback()
        logger.error(f"Delete laboratory error: {err}")
        flash('Error deleting laboratory', 'error')
        return redirect(url_for('admin_lab_assets', lab_id=lab_id))
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    # Initialize database
    if init_database():
        print("Database initialized successfully!")
    else:
        print("Database initialization failed!")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 