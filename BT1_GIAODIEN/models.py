from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Mô hình người dùng
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
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


def create_db():
    """Tạo cơ sở dữ liệu và bảng."""
    db.create_all()
