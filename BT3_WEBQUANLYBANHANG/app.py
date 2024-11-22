from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from jinja2 import Environment
from markupsafe import Markup
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename



# Initialize the app and database
app = Flask(__name__)


app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for session management
db = SQLAlchemy(app)
migrate = Migrate(app, db)


UPLOAD_FOLDER = 'D:\\Ảnh\\static\\dongho.jpeg'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.template_filter('intcomma')
def intcomma_filter(value):
    """Format a number with commas as thousands separator, remove decimals"""
    try:
        # Convert value to an integer, removing any decimals
        value = int(float(value))
        return "{:,}".format(value)
    except ValueError:
        return value

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # Cột ảnh sản phẩm
    
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
    for product in products:
        # Chuyển giá thành int để loại bỏ phần thập phân
        product.price = int(product.price)
    return render_template('index.html', products=products)
@app.route('/view_product/<int:product_id>')
@login_required
def view_product(product_id):
    product = Product.query.get(product_id)
    product.image_url = 'D:\\Ảnh\\static\\image'
    product = Product.query.get_or_404(product_id)
    return render_template('view_product.html', product=product)
# search product
@app.route('/search_product', methods=['GET', 'POST'])
@login_required
def search_product():
    search_query = request.args.get('search')  # Get search query from URL parameter
    products = Product.query.all()

    if search_query:
        # Perform search based on product name
        products = products.filter(Product.name.like(f'%{search_query}%'))

    for product in products:
        product.price = int(product.price)
    return render_template('index.html', products=products, search_query=search_query)



# Add product
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        price = int(price)
        quantity = int(request.form['quantity'])
        image= request.files.get('image')
        if image and allowed_file(image.filename):
            # Lưu ảnh vào thư mục static và bảo vệ tên file
            filename = secure_filename(image.filename)  # Lấy tên file bảo mật
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Đường dẫn file
            image.save(image_path)  # Lưu file vào thư mục static
            image_url = filename  # Lưu tên file để lưu vào cơ sở dữ liệu
        else:
            image_url = None  # Không có ảnh thì để None
            
        new_product = Product(name=name, price=price, quantity=quantity,image_url=image_url)
        db.session.add(new_product)
        db.session.commit()
        
        flash('Sản phẩm đã được thêm thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_product.html')

# Edit product
@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        price = float(request.form['price'])  # Chuyển thành float trước
        price = int(price)  # Chuyển sang int
        
        product.price = price
        product.quantity = int(request.form['quantity'])
    
        db.session.commit()
        flash('Sản phẩm đã được cập nhật thành công!', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', product=product)


# Delete product
@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)  # Get the product or return 404
    db.session.delete(product)
    db.session.commit()
    flash('Sản phẩm đã được xóa thành công!', 'success')
    return redirect(url_for('index'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password, password):
            flash('Tên đăng nhập hoặc mật khẩu không hợp lệ!', 'error')
            return redirect(url_for('login'))

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
