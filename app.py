from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
import random
import string
import requests
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

@app.template_filter('format_currency')
def format_currency(value):
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value

def generate_secret_code():
    return ''.join(random.choices(string.digits, k=6))

MPESA_CONSUMER_KEY = 'oDTlxlydNAxjVMj34v3kLioXlh8JA0KZmFjhE7zQHfdHd4z8'
MPESA_CONSUMER_SECRET = 'ZVeVNLOwkEBbjMxBz2Sv7ufkYpdVXAqIBIXPxSxh7AuTlmsCFJrOM1A7qmxEtSRF'
MPESA_SHORTCODE = '174379' 
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  
MPESA_CALLBACK_URL = 'https://yourdomain.com/mpesa/callback'  

def get_mpesa_access_token():
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(api_url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def initiate_stk_push(phone_number, amount, account_reference, transaction_desc):
    access_token = get_mpesa_access_token()
    if not access_token:
        return {'success': False, 'message': 'Failed to get access token'}
    
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode()).decode()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'BusinessShortCode': MPESA_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(amount),
        'PartyA': phone_number,
        'PartyB': MPESA_SHORTCODE,
        'PhoneNumber': phone_number,
        'CallBackURL': MPESA_CALLBACK_URL,
        'AccountReference': account_reference,
        'TransactionDesc': transaction_desc
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {'success': False, 'message': str(e)}

DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({
            'admin': {
                'password': generate_password_hash('admin123'),
                'email': 'admin@primecuts.com',
                'is_admin': True
            }
        }, f)

if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, 'w') as f:
        json.dump([], f)

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_orders():
    with open(ORDERS_FILE, 'r') as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    products = [
        {
            'id': 1,
            'name': 'Test Product - 1 KSH',
            'description': 'Test product for M-Pesa payment',
            'price': 1,
            'image': 'https://images.unsplash.com/photo-1603048588665-791ca8aea617?w=500'
        },
        {
            'id': 2,
            'name': 'Fresh Chicken Breast',
            'description': 'Organic, free-range chicken breast',
            'price': 450,
            'image': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=500'
        },
        {
            'id': 3,
            'name': 'Chicken Legs',
            'description': 'Tender chicken drumsticks',
            'price': 380,
            'image': 'https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=500'
        },
        {
            'id': 4,
            'name': 'Goat Meat (Mbuzi)',
            'description': 'Fresh goat meat, locally sourced',
            'price': 850,
            'image': 'https://images.unsplash.com/photo-1607623488235-ffa127d5c193?w=500'
        },
        {
            'id': 5,
            'name': 'Whole Cow Meat',
            'description': 'Premium quality beef cuts',
            'price': 950,
            'image': 'https://images.unsplash.com/photo-1603048588665-791ca8aea617?w=500'
        },
        {
            'id': 6,
            'name': 'Fresh Fish (Tilapia)',
            'description': 'Fresh tilapia from local farms',
            'price': 600,
            'image': 'https://images.unsplash.com/photo-1615141982883-c7ad0e69fd62?w=500'
        },
        {
            'id': 7,
            'name': 'Camel Meat',
            'description': 'Lean and nutritious camel meat',
            'price': 750,
            'image': 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=500'
        },
        {
            'id': 8,
            'name': 'Lamb Chops',
            'description': 'Tender and flavorful lamb cuts',
            'price': 920,
            'image': 'https://images.unsplash.com/photo-1546549032-9571cd6b27df?w=500'
        },
        {
            'id': 9,
            'name': 'Ground Turkey',
            'description': 'Low-fat, high-protein option',
            'price': 500,
            'image': 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500'
        },
        {
            'id': 11,
            'name': 'Premium Sausages',
            'description': 'Artisan blend of spices',
            'price': 480,
            'image': 'https://images.unsplash.com/photo-1624374053163-c622b2a2b6bf?w=500'
        },
        {
            'id': 12,
            'name': 'Whole Chicken',
            'description': 'Farm-fresh whole chicken',
            'price': 780,
            'image': 'https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=500'
        }
    ]
    return render_template('products.html', products=products)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = load_users()
        
        if username in users and check_password_hash(users[username]['password'], password):
            session['user'] = username
            session['is_admin'] = users[username].get('is_admin', False)
            flash('Login successful!', 'success')
            
            if session['is_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        users = load_users()
        
        if username in users:
            flash('Username already exists', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
        else:
            users[username] = {
                'password': generate_password_hash(password),
                'email': email,
                'is_admin': False
            }
            save_users(users)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    if 'user' not in session:
        flash('Please login to view your cart', 'error')
        return redirect(url_for('login'))
    
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        return {'success': False, 'message': 'Please login first'}
    
    product_id = int(request.form.get('product_id'))
    product_name = request.form.get('product_name')
    product_price = float(request.form.get('product_price'))
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    
    # Check if item already in cart
    found = False
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        cart.append({
            'id': product_id,
            'name': product_name,
            'price': product_price,
            'quantity': quantity
        })
    
    session['cart'] = cart
    session.modified = True
    
    return {'success': True, 'cart_count': len(cart)}

@app.route('/update_cart', methods=['POST'])
def update_cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    
    cart = session.get('cart', [])
    
    for item in cart:
        if item['id'] == product_id:
            if quantity <= 0:
                cart.remove(item)
            else:
                item['quantity'] = quantity
            break
    
    session['cart'] = cart
    session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    
    session['cart'] = cart
    session.modified = True
    
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    cart_items = session.get('cart', [])
    
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        postal_code = request.form.get('postal_code')
        notes = request.form.get('notes', '')
        payment_method = request.form.get('payment_method', 'cash')
        mpesa_phone = request.form.get('mpesa_phone', '')
        
        secret_code = generate_secret_code()
        
        order_total = sum(item['price'] * item['quantity'] for item in cart_items) + 1
        
        orders = load_orders()
        
        order = {
            'id': len(orders) + 1,
            'user': session['user'],
            'order_items': cart_items,
            'total': order_total,
            'status': 'pending',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'delivery_info': {
                'phone': phone,
                'address': address,
                'city': city,
                'postal_code': postal_code,
                'notes': notes
            },
            'payment_method': payment_method,
            'secret_code': secret_code,
            'code_verified': False,
            'payment_status': 'pending'
        }
        
        if payment_method == 'mpesa' and mpesa_phone:
            mpesa_response = initiate_stk_push(
                phone_number=mpesa_phone,
                amount=order_total,
                account_reference='PrimeCuts',
                transaction_desc=f'Prime Cuts Meat Order #{order["id"]}'
            )
            
            order['mpesa_checkout_id'] = mpesa_response.get('CheckoutRequestID', '')
            order['mpesa_response'] = mpesa_response
            
            if mpesa_response.get('ResponseCode') == '0':
                flash(f'M-Pesa payment request sent to {mpesa_phone}. Please enter your M-Pesa PIN to complete payment. Your order code is: {secret_code}', 'success')
                order['payment_status'] = 'initiated'
            else:
                flash(f'M-Pesa payment failed: {mpesa_response.get("errorMessage", "Unknown error")}. Order placed but payment pending. Your order code is: {secret_code}', 'error')
        else:
            flash(f'Order placed successfully! Your secret code is: {secret_code}. Please save this code for verification.', 'success')
        
        orders.append(order)
        save_orders(orders)
        
        session['cart'] = []
        session['last_order_code'] = secret_code  # Store code in session to display
        session.modified = True
        
        return redirect(url_for('order_history'))
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/order_history')
def order_history():
    if 'user' not in session:
        flash('Please login to view order history', 'error')
        return redirect(url_for('login'))
    
    orders = load_orders()
    user_orders = [order for order in orders if order['user'] == session['user']]
    user_orders.reverse()
    
    return render_template('order_history.html', orders=user_orders)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or not session.get('is_admin'):
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('home'))
    
    orders = load_orders()
    orders.reverse()
    
    stats = {
        'total_orders': len(orders),
        'pending_orders': len([o for o in orders if o['status'] == 'pending']),
        'confirmed_orders': len([o for o in orders if o['status'] == 'confirmed']),
        'delivered_orders': len([o for o in orders if o['status'] == 'delivered'])
    }
    
    return render_template('admin_dashboard.html', orders=orders, stats=stats)

@app.route('/admin/update_order_status', methods=['POST'])
def update_order_status():
    if 'user' not in session or not session.get('is_admin'):
        return {'success': False, 'message': 'Access denied'}
    
    order_id = int(request.form.get('order_id'))
    new_status = request.form.get('status')
    
    orders = load_orders()
    
    for order in orders:
        if order['id'] == order_id:
            order['status'] = new_status
            break
    
    save_orders(orders)
    
    flash(f'Order #{order_id} status updated to {new_status}', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/verify_code', methods=['POST'])
def verify_code():
    if 'user' not in session or not session.get('is_admin'):
        return redirect(url_for('home'))
    
    order_id = int(request.form.get('order_id'))
    entered_code = request.form.get('secret_code')
    
    orders = load_orders()
    
    for order in orders:
        if order['id'] == order_id:
            if order.get('secret_code') == entered_code:
                order['code_verified'] = True
                order['status'] = 'confirmed'
                save_orders(orders)
                flash(f'Order #{order_id} verified successfully!', 'success')
            else:
                flash(f'Invalid secret code for Order #{order_id}', 'error')
            break
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/confirm_payment', methods=['POST'])
def confirm_payment():
    if 'user' not in session or not session.get('is_admin'):
        return redirect(url_for('home'))
    
    order_id = int(request.form.get('order_id'))
    
    orders = load_orders()
    
    for order in orders:
        if order['id'] == order_id:
            order['payment_status'] = 'completed'
            if order['status'] == 'pending':
                order['status'] = 'confirmed'
            save_orders(orders)
            flash(f'Payment confirmed for Order #{order_id}!', 'success')
            break
    
    return redirect(url_for('admin_dashboard'))

@app.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json()
    
    with open(os.path.join(DATA_DIR, 'mpesa_callbacks.json'), 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
    checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
    
    if result_code == 0:
        orders = load_orders()
        for order in orders:
            if order.get('mpesa_checkout_id') == checkout_request_id:
                order['payment_status'] = 'completed'
                order['status'] = 'confirmed'
                break
        save_orders(orders)
    
    return {'ResultCode': 0, 'ResultDesc': 'Accepted'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
