from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_pymongo import PyMongo
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from bson.objectid import ObjectId
from datetime import datetime
from flask_socketio import SocketIO, emit

# Initialize Flask App
app = Flask(__name__)

# Secret Key and MongoDB Config
app.secret_key = 'your_generated_secret_key_here'  # Replace with a generated key
app.config['MONGO_URI'] = 'mongodb://localhost:53333/gps_data'  # Ensure MongoDB runs on this port

# Initialize Extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Initialize SocketIO
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

# Routes
@app.route('/')
def home():
    return render_template('index.html')  # Landing page with options for login

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username already exists
        if mongo.db.users.find_one({"username": form.username.data}):
            flash("Username already exists!", 'danger')
            return redirect(url_for('register'))

        # Hash password and save to MongoDB
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        mongo.db.users.insert_one({"username": form.username.data, "password": hashed_password, "role": "user"})  # Default role is "user"
        flash("Account created successfully! Please log in.", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(user["username"], str(user["_id"]), user.get("role", "user"))
            login_user(user_obj)
            flash("Login successful!", 'success')

            # Redirect based on user role
            if user_obj.role == "admin":
                return redirect(url_for('admin_dashboard'))
            elif user_obj.role == "vendor":
                return redirect(url_for('vendor_dashboard'))
            else:
                return redirect(url_for('map'))
        else:
            flash("Invalid username or password", 'danger')
    return render_template('login.html', form=form)

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')

@app.route('/vendor-dashboard')
@login_required
def vendor_dashboard():
    if current_user.role != "vendor":
        flash("Access denied!", "danger")
        return redirect(url_for('home'))
    return render_template('vendor_dashboard.html')

@app.route('/map')
@login_required
def map():
    return render_template('map.html')  # Protected map page

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", 'success')
    return redirect(url_for('home'))

# API Route for GPS Data
@app.route('/api/gps')
@login_required
def get_gps_data():
    user_gps_data = mongo.db.locations.find({"user_id": current_user.username})
    gps_data = []
    for data in user_gps_data:
        gps_data.append({
            "device_id": data['device_id'],
            "latitude": data['latitude'],
            "longitude": data['longitude'],
            "equipment": data['equipment'],
            "state": data['state'],
            "timestamp": data['timestamp']
        })
    return jsonify(gps_data)

if __name__ == '__main__':
    socketio.run(app, debug=True)
