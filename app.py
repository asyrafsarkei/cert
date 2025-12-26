from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(200))
    google_id = db.Column(db.String(200), unique=True, nullable=True)
    is_approved = db.Column(db.Boolean, default=False)

db.create_all()

# Hardcoded admin
ADMIN_EMAIL = "rouge.qaz@gmail.com"
ADMIN_PASSWORD = "admin"

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        user = User(name=name, email=email, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registration submitted. Waiting for approval.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Admin login
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['user'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        user = User.query.filter_by(email=email).first()
        if user:
            if not user.is_approved:
                return render_template('pending.html')
            if check_password_hash(user.password_hash, password):
                session['user'] = user.email
                return "Logged in successfully!"
        flash('Invalid login')
        return redirect(url_for('login'))
    return render_template('login.html')

# Admin dashboard
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('user') != 'admin':
        return redirect(url_for('login'))
    pending_users = User.query.filter_by(is_approved=False).all()
    if request.method == 'POST':
        approve_id = request.form.get('approve_id')
        user = User.query.get(approve_id)
        if user:
            user.is_approved = True
            db.session.commit()
            flash(f'Approved {user.email}')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin.html', users=pending_users)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
