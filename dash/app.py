from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_pymongo import PyMongo
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
from bson.objectid import ObjectId
from datetime import datetime
from flask_socketio import SocketIO, emit

# Initialize Flask App
app = Flask(__name__)

# Secret Key and MongoDB Config 
app.secret_key = 'your_generated_secret_key_here'
app.config['MONGO_URI'] = 'mongodb://localhost:53333/gps_data'

# Initialize Extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
socketio = SocketIO(app)

# User Class for Flask-Login
class User(UserMixin):
    def __init__(self, username, id, role):
        self.username = username
        self.id = id
        self.role = role

# Load User Function
@login_manager.user_loader
def load_user(user_id):
    try:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(user["username"], str(user["_id"]), user.get("role", "user"))
    except Exception as e:
        print("Error loading user:", e)
    return None

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username already exists
        if mongo.db.users.find_one({"username": form.username.data}):
            flash("Username already exists!", 'danger')
            return redirect(url_for('register'))
        
        # Check if it's a vendor registration
        role = 'vendor' if 'vendor' in request.form else 'user'  # Assign role based on form input

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Insert the user with their role (user or vendor)
        user_id = mongo.db.users.insert_one({
            "username": form.username.data, 
            "password": hashed_password, 
            "role": role
        }).inserted_id
        
        # If the user is a vendor, create a corresponding vendor entry
        if role == 'vendor':
            company_name = request.form.get('company_name', '')
            contact_info = request.form.get('contact_info', '')
            
            # Insert vendor details in the vendors collection
            mongo.db.vendors.insert_one({
                "user_id": user_id,
                "company_name": company_name,
                "contact_info": contact_info
            })

        flash(f"Account created successfully as {role}! Please log in.", 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(user["username"], str(user["_id"]), user.get("role", "user"))
            login_user(user_obj, remember=form.remember_me.data)
            flash("Login successful!", 'success')
            return redirect(url_for('map'))
        else:
            flash("Invalid username or password", 'danger')
    return render_template('login.html', form=form)

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))
    
    # Fetch users and devices to show on the dashboard
    users = mongo.db.users.find({"role": "user"})
    devices = mongo.db.devices.find()  # Add a collection for devices if not already present
    return render_template('admin_dashboard.html', users=users, devices=devices)

@app.route('/vendor-dashboard')
@login_required
def vendor_dashboard():
    if current_user.role != "vendor":
        flash("Access denied! Vendors only.", "danger")
        return redirect(url_for('home'))
    
    return render_template('vendor_dashboard.html')

@app.route('/map')
@login_required
def map():
    return render_template('map.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", 'success')
    return redirect(url_for('home'))

@app.route('/api/gps')
@login_required
def get_gps_data():
    user_gps_data = mongo.db.locations.find({"user_id": current_user.username})
    gps_data = []
    for data in user_gps_data:
        if all(key in data for key in ('device_id', 'latitude', 'longitude', 'equipment', 'state', 'timestamp')):
            gps_data.append({
                "device_id": data['device_id'],
                "latitude": data['latitude'],
                "longitude": data['longitude'],
                "equipment": data['equipment'],
                "state": data['state'],
                "timestamp": data['timestamp']
            })
    return jsonify(gps_data)

@socketio.on('send_gps_update')
def handle_gps_update(data):
    """
    Receive real-time GPS updates and broadcast them.
    """
    try:
        if all(key in data for key in ('device_id', 'latitude', 'longitude', 'equipment', 'state', 'timestamp')):
            mongo.db.locations.insert_one(data)  # Save to DB if necessary
            emit('gpsData', data, broadcast=True)  # Broadcast to all clients
    except Exception as e:
        print(f"Error processing GPS update: {e}")

@app.route('/add_device', methods=['POST'])
@login_required
def add_device():
    if current_user.role != "admin":
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('admin_dashboard'))
    
    user_id = request.form['user_id']
    device_name = request.form['device_name']
    device_id = request.form['device_id']
    
    # Insert device into the devices collection
    mongo.db.devices.insert_one({
        "user_id": user_id,
        "device_name": device_name,
        "device_id": device_id,
        "timestamp": datetime.utcnow()
    })
    flash(f"Device {device_name} added to user {user_id}.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/create_vendor', methods=['POST'])
@login_required
def create_vendor():
    if current_user.role != "admin":
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('admin_dashboard'))
    
    vendor_username = request.form['vendor_username']
    vendor_password = request.form['vendor_password']
    vendor_confirm_password = request.form['vendor_confirm_password']

    if vendor_password != vendor_confirm_password:
        flash("Passwords do not match!", "danger")
        return redirect(url_for('admin_dashboard'))

    # Hash the vendor's password
    hashed_password = bcrypt.generate_password_hash(vendor_password).decode('utf-8')
    
    # Create the vendor account
    mongo.db.users.insert_one({
        "username": vendor_username,
        "password": hashed_password,
        "role": "vendor",
        "created_at": datetime.utcnow()
    })
    flash(f"Vendor {vendor_username} created successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/vendor-login', methods=['GET', 'POST'])
def vendor_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data, "role": "vendor"})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(user["username"], str(user["_id"]), user.get("role", "vendor"))
            login_user(user_obj, remember=form.remember_me.data)
            flash("Login successful!", 'success')
            return redirect(url_for('vendor_dashboard'))
        else:
            flash("Invalid username or password for vendor.", 'danger')
    return render_template('login.html', form=form)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data, "role": "admin"})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(user["username"], str(user["_id"]), user.get("role", "admin"))
            login_user(user_obj, remember=form.remember_me.data)
            flash("Login successful!", 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password for admin.", 'danger')
    return render_template('login.html', form=form)

@app.route('/account_settings')
@login_required
def account_settings():
    return render_template('account_settings.html')  # Create this template as per your needs


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

if __name__ == '__main__':
    socketio.run(app, debug=True)
