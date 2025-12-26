from flask_cors import CORS
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # change this
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    approved = db.Column(db.Boolean, default=False)

# Create tables within app context
with app.app_context():
    db.create_all()

# Load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Default admin account (if not exists)
with app.app_context():
    admin_email = 'rouge.qaz@gmail.com'
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(email=admin_email, password=generate_password_hash('admin', method='pbkdf2:sha256'), approved=True)
        db.session.add(admin)
        db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if not user.approved:
                flash('Account not approved yet.')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form.get('name', '')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password, method='sha256')
        new_user = User(email=email, password=hashed_pw, approved=False)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration submitted. Wait for approval.')
        return redirect(url_for('login'))
    return render_template('register.html')
    
@app.route('/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if current_user.email != 'rouge.qaz@gmail.com':
        return "Access Denied", 403
    user = User.query.get(user_id)
    if user:
        user.approved = True
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/reject/<int:user_id>', methods=['POST'])
@login_required
def reject_user(user_id):
    if current_user.email != 'rouge.qaz@gmail.com':
        return "Access Denied", 403
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.email}!'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Run app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
