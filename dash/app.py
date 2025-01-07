from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_pymongo import PyMongo
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from bson.objectid import ObjectId
from functools import wraps

# Initialize Flask App
app = Flask(__name__)
app.secret_key = 'your_generated_secret_key_here'
app.config['MONGO_URI'] = 'mongodb://localhost:53333/gps_data'

# Initialize Extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User Class
class User(UserMixin):
    def __init__(self, username, email, id, role):
        self.username = username
        self.email = email
        self.id = str(id)
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    try:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(user["username"], user["email"], user["_id"], user.get("role", "user"))
    except Exception:
        pass
    return None

# Role Decorator
def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                flash("Access denied!", "danger")
                return abort(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    register_as_vendor = BooleanField('Register as Vendor')
    company_name = StringField('Company Name', validators=[Length(min=3, max=100)])
    contact_info = TextAreaField('Contact Information', validators=[Length(min=10)])
    submit = SubmitField('Register')

class CreateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

# LoginForm class update
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Check if the user registered as vendor
        role = 'vendor' if form.register_as_vendor.data else 'user'  # Check the vendor registration checkbox

        user_id = mongo.db.users.insert_one({
            "username": form.username.data,
            "email": form.email.data,  # Store email in MongoDB
            "password": hashed_password,
            "role": role
        }).inserted_id
        
        # If vendor, add vendor-specific data
        if role == 'vendor':
            mongo.db.vendors.insert_one({
                "user_id": user_id,
                "company_name": form.company_name.data,  # Store vendor data
                "contact_info": form.contact_info.data
            })

        # Flash the confirmation message
        flash(f"Account created as {role}! Please login.", "success")

        # Redirect to the login page
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Find the user by email instead of username
        user = mongo.db.users.find_one({"email": form.email.data})  # Search by email
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(user["username"], user["email"], user["_id"], user.get("role", "user"))
            login_user(user_obj, remember=form.remember_me.data)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "danger")
    return render_template('login.html', form=form)

# Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'vendor':
        return redirect(url_for('vendor_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    flash("No specific dashboard assigned.", "warning")
    return redirect(url_for('map'))

# Vendor Dashboard Route
@app.route('/vendor_dashboard')
@login_required
@role_required('vendor')
def vendor_dashboard():
    try:
        # Fetch vendor details using the current user's ID (assuming vendor is identified by the user's ID)
        vendor = mongo.db.vendors.find_one({"user_id": ObjectId(current_user.id)})
        if not vendor:
            flash("Vendor profile not found.", "danger")
            return redirect(url_for('dashboard'))

        # Fetch admin users associated with the vendor
        admin_users = mongo.db.users.find({"role": "admin", "vendor_id": vendor["_id"]})

        # Prepare list of admin user details
        admin_users_details = list(admin_users)

        # Fetch sub-users of the vendor (if any) that are not admins
        sub_users = mongo.db.vendor_users.find({"vendor_id": vendor["_id"]})
        sub_users_details = []
        for sub_user in sub_users:
            if "user_id" in sub_user:
                user_details = mongo.db.users.find_one({"_id": ObjectId(sub_user["user_id"])})
            else:
                user_details = mongo.db.users.find_one({"_id": sub_user["vendor_id"]})  # Fallback to vendor_id
            if user_details:
                sub_users_details.append(user_details)

        form = RegistrationForm()
        return render_template('vendor_dashboard.html', vendor=vendor, sub_users=sub_users_details, admin_users=admin_users_details, form=form)

    except Exception:
        flash("Error loading vendor dashboard.", "danger")
        return redirect(url_for('dashboard'))

# Admin Dashboard Route
@app.route('/admin_dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    try:
        users = mongo.db.users.find({"role": "admin"})
        return render_template('admin_dashboard.html', users=users)
    except Exception:
        flash("Error loading admin dashboard.", "danger")
        return redirect(url_for('dashboard'))

@app.route('/vendor/create_admin', methods=['GET', 'POST'])
@login_required
@role_required('vendor')
def create_admin():
    form = CreateAccountForm()
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('create_admin'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        vendor = mongo.db.vendors.find_one({"user_id": ObjectId(current_user.id)})
        if not vendor:
            flash("Vendor profile not found.", "danger")
            return redirect(url_for('vendor_dashboard'))

        # Insert into the database
        mongo.db.users.insert_one({
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "role": "admin",
            "vendor_id": vendor["_id"]
        })

        flash("Admin created successfully!", "success")
        return redirect(url_for('vendor_dashboard'))

    return render_template('create_admin.html', form=form)

@app.route('/vendor/create_sub_user', methods=['GET', 'POST'])
@login_required
@role_required('vendor')
def create_sub_user():
    form = CreateAccountForm()
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('create_sub_user'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        vendor = mongo.db.vendors.find_one({"user_id": ObjectId(current_user.id)})
        if not vendor:
            flash("Vendor profile not found.", "danger")
            return redirect(url_for('vendor_dashboard'))

        # Insert the sub-user into the database
        user_id = mongo.db.users.insert_one({
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "role": "sub_user"
        }).inserted_id

        mongo.db.vendor_users.insert_one({
            "vendor_id": vendor["_id"],
            "user_id": user_id
        })

        flash("Sub-user created successfully!", "success")
        return redirect(url_for('vendor_dashboard'))

    return render_template('create_sub_user.html', form=form)

# Update User Route
@app.route('/update_user/<user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    # Convert user_id to ObjectId to query MongoDB
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        # Update the user information
        username = request.form['username']
        email = request.form['email']  # Update email field
        password = request.form.get('password')
        role = request.form['role']
        
        if password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": username, "email": email, "password": hashed_password, "role": role}})
        else:
            mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": username, "email": email, "role": role}})
        
        flash("User updated successfully.", "success")
        return redirect(url_for('vendor_dashboard'))
    
    return render_template('update_user.html', user=user)

# Delete User Route
@app.route('/delete_user/<user_id>', methods=['POST'])
@login_required
@role_required('vendor')
def delete_user(user_id):
    try:
        # Delete the user from the 'vendor_users' collection
        result = mongo.db.vendor_users.delete_one({"user_id": ObjectId(user_id)})
        if result.deleted_count > 0:
            # Also delete from the 'users' collection
            mongo.db.users.delete_one({"_id": ObjectId(user_id)})
            flash("User deleted successfully.", "success")
        else:
            flash("User not found in vendor_users collection.", "danger")
        
        return redirect(url_for('vendor_dashboard'))

    except Exception:
        flash("Error deleting user.", "danger")
        return redirect(url_for('vendor_dashboard'))

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

# Error Handling
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
