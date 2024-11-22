from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for
from jinja2 import Environment


app = Flask(__name__)
db = SQLAlchemy()

@app.template_filter()
def intcomma(value):
    # Function to format number with commas
    return "{:,}".format(value)


# Mô hình người dùng
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        """Cài đặt mật khẩu cho người dùng."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Kiểm tra mật khẩu người dùng."""
        return check_password_hash(self.password, password)

    @classmethod
    def create_user(cls, username, password):
        """Tạo người dùng mới."""
        new_user = cls(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def get_user(cls, user_id):
        """Lấy thông tin người dùng theo ID."""
        return cls.query.get(user_id)

    @classmethod
    def update_user(cls, user_id, username=None, password=None):
        """Cập nhật thông tin người dùng."""
        user = cls.query.get(user_id)
        if not user:
            return None
        
        if username:
            user.username = username
        if password:
            user.set_password(password)
        
        db.session.commit()
        return user

    @classmethod
    def delete_user(cls, user_id):
        """Xóa người dùng."""
        user = cls.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

# Mô hình sản phẩm
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        """Hiển thị thông tin sản phẩm."""
        return f"<Product {self.name}>"

    @classmethod
    def create_product(cls, name, price, quantity):
        """Tạo sản phẩm mới."""
        new_product = cls(name=name, price=price, quantity=quantity)
        db.session.add(new_product)
        db.session.commit()
        return new_product

    @classmethod
    def get_product(cls, product_id):
        """Lấy thông tin sản phẩm theo ID."""
        return cls.query.get(cls,product_id)
    def update_product(product_id):
        product = Product.query.get_or_404(product_id)
        if request.method == 'POST':
            product.name = request.form['name']
            product.price = int(request.form['price'])
            product.quantity = request.form['quantity']
    @classmethod
    def update_product(cls, product_id, name=None, price=None, quantity=None):
        """Cập nhật thông tin sản phẩm."""
        product = cls.query.get(product_id)
        if not product:
            return None
        
        if name:
            product.name = name
        if price is not None:
            product.price = int(price)
        if quantity is not None:
           product.quantity = quantity
            
        db.session.commit()
        return product
    @classmethod
    def delete_product(cls, product_id):
        """Xóa sản phẩm."""
        product = cls.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()

def create_db():
    """Tạo cơ sở dữ liệu và bảng."""
    db.create_all()
