from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

# Initialize the app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for session management
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Create all tables
with app.app_context():
    db.create_all()

# Setting up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Load user callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home page: Show list of products
@app.route('/')
@login_required
def index():
    products = Product.query.all()  # Get all products from the database
    return render_template('index.html', products=products)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get data from form
        username = request.form['username']
        password = request.form['password']

        # Check if user exists and verify password
        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password, password):
            flash('Tên đăng nhập hoặc mật khẩu không hợp lệ!', 'error')
            return redirect(url_for('login'))

        # If login is successful, store user in session
        login_user(user)
        flash('Đăng nhập thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Mật khẩu không khớp!', 'danger')
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Tên người dùng đã tồn tại!', 'danger')
            else:
                new_user = User(username=username)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash('Đăng ký thành công! Bạn có thể đăng nhập ngay.', 'success')
                return redirect(url_for('login'))
    return render_template('register.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất!', 'success')
    return redirect(url_for('login'))

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
