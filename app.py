from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(200))
    google_id = db.Column(db.String(200), unique=True, nullable=True)
    is_approved = db.Column(db.Boolean, default=False)

db.create_all()

ADMIN_EMAIL = "rouge.qaz@gmail.com"
ADMIN_PASSWORD = "admin"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered"})
    hashed_pw = generate_password_hash(password)
    user = User(name=name, email=email, password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True, "message": "Registration submitted. Waiting for approval."})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Admin login
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session['user'] = 'admin'
        return jsonify({"success": True, "message": "Admin logged in"})

    user = User.query.filter_by(email=email).first()
    if user:
        if not user.is_approved:
            return jsonify({"success": False, "message": "Pending approval"})
        if check_password_hash(user.password_hash, password):
            session['user'] = user.email
            return jsonify({"success": True, "message": "Logged in successfully"})
    return jsonify({"success": False, "message": "Invalid login"})

if __name__ == '__main__':
    app.run(debug=True)
