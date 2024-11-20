import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import tkinter.scrolledtext as scrolledtext
from PIL import ImageTk, Image

def init_db():
    conn = sqlite3.connect('users.db')  # Tạo hoặc kết nối tới CSDL
    cursor = conn.cursor()

    # Tạo bảng nếu chưa tồn tại
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS danh_gia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_luong INTEGER,  -- 0 hoặc 1 (False/True)
            thiet_ke INTEGER,
            gia_ca INTEGER,
            dich_vu INTEGER,
            noi_dung TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS san_pham (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten TEXT,
            mo_ta TEXT,
            gia REAL,
            hinh_anh TEXT
        )
    ''')
    conn.commit() #Lưu thay đổi
    return conn, cursor

window = tk.Tk()
window.title("ĐĂNG NHẬP ỨNG DỤNG BÁN HÀNG")
window.geometry('750x550')
window.configure(bg='#d3d3d3')

def hash_password(password):
    # Mã hóa mật khẩu bằng thuật toán SHA-256
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def show_app():
    # Ẩn cửa sổ đăng nhập
    window.withdraw()
    
    # Tạo cửa sổ mới
    app = tk.Toplevel()
    app.title("ỨNG DỤNG BÁN HÀNG")
    app.geometry("850x650")
    
    label = tk.Label(app, text="Quản Lý Sản Phẩm", font=("Arial", 16, 'bold'))
    label.pack(pady=10)
    # Tạo notebook (tab control)
    notebook = ttk.Notebook(app)
    notebook.pack(fill="both", expand=True)

# Tạo tab "Thông tin sản phẩm"
    product_info_frame = ttk.Frame(notebook)
    notebook.add(product_info_frame, text="Thông tin sản phẩm")

# Hiển thị thông tin sản phẩm
    product_name_label = ttk.Label(product_info_frame, text="Tên sản phẩm:  Áo Stussy ", font=("Arial", 16))
    product_name_label.pack(padx=10, pady=10)

# Mở ảnh bằng PIL
    image = Image.open("D:\LTPNC\Hinhanh\sp1.png")
# Chỉnh sửa kích thước ảnh tại đây (ví dụ: 100x100)
    image = image.resize((350, 350), resample=Image.LANCZOS)  # Sử dụng LANCZOS để đảm bảo chất lượng tốt

# Chuyển đổi sang PhotoImage sau khi đã chỉnh sửa kích thước
    photo = ImageTk.PhotoImage(image)

# Tạo Label và hiển thị ảnh
    image_label = tk.Label(product_info_frame, image=photo)
    image_label.image = photo  # Giữ tham chiếu
    image_label.pack(padx=30, pady=30)  # Thêm padding nếu cần


    product_description_label = ttk.Label(
        product_info_frame,
        text="Mô tả sản phẩm: Đây là một sản phẩm rất hợp thời trang hiện nay với thiết kế nhẹ nhàng tinh tế giúp tôn lên vẻ đẹp người mặc."
)
    product_description_label.pack()

    product_price_label = ttk.Label(product_info_frame, text="Giá: 1.5000.000 VNĐ")
    product_price_label.pack()

    def open_write_review_window():
        review_window = tk.Toplevel(app)
        review_window.title("Viết đánh giá")

    # Frame chứa nội dung đánh giá
        content_frame = ttk.Frame(review_window)
        content_frame.pack(padx=10, pady=10)

        review_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, height=10)
        review_text.pack(fill="both", expand=True)

        submit_button = ttk.Button(review_window, text="Gửi đánh giá", command=lambda: submit_review(review_text, review_window))
        submit_button.pack(pady=10)

# Function to display product information
    def display_product_info(product_id):
        cursor.execute("SELECT * FROM san_pham WHERE id=?", (product_id,))
        product_data = cursor.fetchone()

        if product_data:
            product_name_label.config(text=f"Tên sản phẩm: {product_data[1]}")
            # ... (Update other labels with data from product_data)

            # Refresh reviews list
            display_reviews(product_id)
        else:
            # Clear information and display message
            product_name_label.config(text="Không tìm thấy sản phẩm")
            # ... (Clear contents of other labels)
            reviews_text.delete("1.0", tk.END)
            reviews_label.pack()


    # Function to display product reviews
    def display_reviews(product_id):
        reviews_text.delete("1.0", tk.END)
        cursor.execute("SELECT noi_dung FROM danh_gia WHERE id_san_pham=?", (product_id,))
        reviews = cursor.fetchall()
        if reviews:
            for review_data in reviews:
                reviews_text.insert(tk.END, review_data[0] + "\n---\n")
            reviews_label.pack_forget()
        else:
            reviews_label.pack()


    def submit_review(review_text, review_window):
        review = review_text.get("1.0", tk.END)
        if review.strip():
            reviews_text.insert(tk.END, review + "\n---\n")
            reviews_label.pack_forget()
            review_window.destroy()


            # --- Lưu đánh giá vào CSDL ---
            chat_luong = int(rating_vars[0].get())
            thiet_ke = int(rating_vars[1].get())
            gia_ca = int(rating_vars[2].get())
            dich_vu = int(rating_vars[3].get())

            cursor.execute('''
                INSERT INTO danh_gia (chat_luong, thiet_ke, gia_ca, dich_vu, noi_dung)
                VALUES (?, ?, ?, ?, ?)
            ''', (chat_luong, thiet_ke, gia_ca, dich_vu, review))
            conn.commit()




            # --- Hiển thị lại danh sách đánh giá từ CSDL ---

            reviews_text.delete("1.0", tk.END) # Xóa nội dung cũ
            cursor.execute("SELECT noi_dung FROM danh_gia")
            reviews = cursor.fetchall()
            for review_data in reviews:
                reviews_text.insert(tk.END, review_data[0] + "\n---\n")




        else:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đánh giá")


    reviews_frame = ttk.Frame(notebook)
    notebook.add(reviews_frame, text="Đánh giá")

    # Frame cho tiêu chí đánh giá
    criteria_frame = ttk.LabelFrame(reviews_frame, text="Tiêu chí đánh giá", padding=(10, 5))
    criteria_frame.pack(pady=10)

    rating_labels = ["Chất lượng", "Thiết kế", "Giá cả", "Dịch vụ"]
    rating_vars = []
    for label_text in rating_labels:
        rating_var = tk.BooleanVar()
        rating_vars.append(rating_var)

        checkbutton = ttk.Checkbutton(criteria_frame, text=label_text, variable=rating_var, style="Custom.TCheckbutton")
        checkbutton.pack(side=tk.LEFT, padx=5)

    # Tạo style cho Checkbutton (tuỳ chỉnh giao diện)
    style = ttk.Style()
    style.configure("Custom.TCheckbutton", padding=5)

    reviews_text = scrolledtext.ScrolledText(reviews_frame, wrap=tk.WORD)
    reviews_text.pack(fill="both", expand=True)

    write_review_button = ttk.Button(reviews_frame, text="Viết đánh giá", command=open_write_review_window)
    write_review_button.pack(pady=10)

    # Label hiển thị khi chưa có đánh giá
    reviews_label = ttk.Label(reviews_frame, text="Chưa có đánh giá nào")
    reviews_label.pack()

    specs_frame = ttk.Frame(notebook)
    notebook.add(specs_frame, text="Thông số kỹ thuật")

    # Sử dụng LabelFrame để nhóm các thông số
    specs_group = ttk.LabelFrame(specs_frame, text="Chi tiết sản phẩm", padding=(10, 5))
    specs_group.pack(pady=10, padx=10, fill=tk.X)

    # --- Màu sắc ---
    color_label = ttk.Label(specs_group, text="Màu sắc:")
    color_label.grid(row=0, column=0, sticky=tk.W)

    color_combobox = ttk.Combobox(specs_group, values=["Đỏ", "Xanh", "Vàng", "Đen", "Trắng"])
    color_combobox.current(0)  # Chọn giá trị mặc định
    color_combobox.grid(row=0, column=1, padx=5, sticky=tk.W)

    # --- Kích thước ---
    size_label = ttk.Label(specs_group, text="Kích thước:")
    size_label.grid(row=1, column=0, sticky=tk.W)

    size_values = {"S": "S", "M": "M", "L": "L", "XL": "XL"}
    size_var = tk.StringVar()  # Biến StringVar để lưu giá trị radiobutton đã chọn

    for i, (size_value, size_text) in enumerate(size_values.items()):
        size_radiobutton = ttk.Radiobutton(specs_group, text=size_text, value=size_value, variable=size_var)
        size_radiobutton.grid(row=1, column=i + 1, padx=2, sticky=tk.W)

    size_var.set("M")  # set giá trị mặt định

    # --- Chất liệu ---
    material_label = ttk.Label(specs_group, text="Chất liệu:")
    material_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))  # Thêm padding

    material_text = "Vải cao cấp, mềm mại và thoáng mát. Thân thiện với làn da."
    material_display = tk.Text(specs_group, wrap=tk.WORD, height=3, width=30, borderwidth=1, relief="solid")  # Đặt border solid cho đẹp hơn
    material_display.insert(tk.END, material_text)  # Chèn văn bản
    material_display.config(state=tk.DISABLED)  # Không cho phép chỉnh sửa (chỉ hiển thị)
    material_display.grid(row=2, column=1, padx=5, sticky=tk.W)

    class CreateToolTip(object):
        def __init__(self, widget, text_func):
            self.widget = widget
            self.text = text_func
            self.waittime = 500
            self.wraplength = 200
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)
            self.widget.bind("<ButtonPress>", self.leave)
            self.id = None
            self.tw = None

        def enter(self, event=None):
            self.schedule()

        def leave(self, event=None):
            self.unschedule()
            self.hidetip()

        def schedule(self):
            self.unschedule()
            self.id = self.widget.after(self.waittime, self.showtip)

        def unschedule(self):
            id_ = self.id
            self.id = None
            if id_:
                self.widget.after_cancel(id_)

        def showtip(self):
            x, y = self.widget.winfo_pointerxy()
            x += 20
            y += 10
            self.tw = tk.Toplevel(self.widget)
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))
            label = tk.Label(self.tw, text=self.text, justify='left',
                            background="#ffffff", relief='solid', borderwidth=1,
                            wraplength=self.wraplength)
            label.pack(ipadx=1)

        def hidetip(self):
            tw = self.tw
            self.tw = None
            if tw:
                tw.destroy()
    def get_tooltip_text():
        color = color_combobox.get()
        size = size_var.get()
        return f"Thêm sản phẩm: Áo Stussy\nMàu: {color}\nKích thước: {size}"
    # def add_to_cart():
    #     quantity = int(quantity_spinbox.get())
    #     if quantity > 0:
    #         messagebox.showinfo("Thông báo", f"Đã thêm {quantity} sản phẩm vào giỏ hàng!")
    #     else:
    #         messagebox.showwarning("Lỗi", "Vui lòng chọn số lượng!")

    def add_to_cart():
        try:
            quantity = int(quantity_spinbox.get())  # Lấy số lượng từ Spinbox
            if quantity > 0:
                messagebox.showinfo("Thông báo", f"Đã thêm {quantity} sản phẩm vào giỏ hàng!")
            else:
                messagebox.showwarning("Lỗi", "Vui lòng chọn số lượng hợp lệ!")
        except ValueError:
            messagebox.showwarning("Lỗi", "Vui lòng nhập một số hợp lệ!")

    # Frame chứa nút và spinbox (đặt vào root để nằm dưới cùng)
    button_frame = tk.Frame(app)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))  # Thêm padding

    # Spinbox
    quantity_spinbox = tk.Spinbox(button_frame, from_=1, to=100, width=5)
    quantity_spinbox.pack(side=tk.LEFT, padx=5)

    # Nút "Thêm vào giỏ hàng"
    add_to_cart_button = tk.Button(button_frame, text="Thêm vào giỏ hàng", width=20, command=add_to_cart)  # Thêm command
    add_to_cart_button.pack(side=tk.LEFT)

    # Tooltip cho nút "Thêm vào giỏ hàng"
    
    tooltip = CreateToolTip(add_to_cart_button, get_tooltip_text)
 
def register(window, user_data, cursor):
     window.withdraw()  # Ẩn cửa sổ đăng nhập
     app = tk.Tk()
     app.title('Đăng Ký')
     app.geometry('750x550')

    # Set background color
     app.config(bg='#F5BABA')

     # Create labels for the registration form
     register_label = tk.Label(app, text="Đăng Ký", bg='#F5BABA', fg="#8B0000", font=("Arial", 30, 'bold'))
     username_register_label = tk.Label(app, text="Tài khoản: ", bg='#F5BABA', fg="#000000", font=("Arial", 16, 'bold'))
     password_register_label = tk.Label(app, text="Mật khẩu: ", bg='#F5BABA', fg="#000000", font=("Arial", 16, 'bold'))
     confirm_password_register_label = tk.Label(app, text="Xác nhận mật khẩu: ", bg='#F5BABA', fg="#000000", font=("Arial", 16, 'bold'))

     # Entry widgets for registration
     username_register_entry = tk.Entry(app, font=("Arial", 16))
     password_register_entry = tk.Entry(app, show="*", font=("Arial", 16))
     confirm_password_register_entry = tk.Entry(app, show="*", font=("Arial", 16))

    # Submit registration function
     def submit_registration():
          username = username_register_entry.get()
          password = password_register_entry.get()
          confirm_password = confirm_password_register_entry.get()

          if not username or not password or not confirm_password:
               messagebox.showwarning(title="Lỗi", message="Vui lòng điền đủ thông tin!")
          elif password != confirm_password:
               messagebox.showwarning(title="Lỗi", message="Mật khẩu không khớp!")
          else:
               # Store the user in the database
               hashed_password = hash_password(password)
               cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
               cursor.connection.commit()

               messagebox.showinfo(title="Đăng ký thành công", message="Bạn đã đăng ký thành công!")
               app.withdraw()  # Hide the registration window
               window.deiconify()  # Show the login window

     # Back to login button
     back_to_login_label = tk.Label(app, text="Đã có tài khoản ->     ", bg='#F5BABA', fg="#8B0000", font=("Arial", 16))
     back_to_login_button = tk.Button(app, text="Quay lại", bg="#8B0000", fg="#FFFFFF", font=("Arial", 16), command=lambda: [app.withdraw(), window.deiconify()])
     register_button = tk.Button(app, text="Đăng Ký", bg="#DC143C", fg="#FFFFFF", font=("Arial", 16), command=submit_registration)
     # Layout widgets
     register_label.grid(row=0, column=0, columnspan=2, pady=40, padx=20)
     username_register_label.grid(row=1, column=0, padx=20, pady=10)
     username_register_entry.grid(row=1, column=1, padx=20, pady=10)
     password_register_label.grid(row=2, column=0, padx=20, pady=10)
     password_register_entry.grid(row=2, column=1, padx=20, pady=10)
     confirm_password_register_label.grid(row=3, column=0, padx=20, pady=10)
     confirm_password_register_entry.grid(row=3, column=1, padx=20, pady=10)
     register_button.grid(row=4, column=0, columnspan=2, pady=20)
     back_to_login_button.grid(row=5, column=1, columnspan=2)
     back_to_login_label.grid(row=5, column=0, columnspan=2)

     app.mainloop()

# Login function
def login(window, cursor, username_entry, password_entry):
     window.withdraw()
     # Lấy dữ liệu người dùng nhập vào
     username_input = username_entry.get()
     password_input = password_entry.get()

     # Kiểm tra nếu thông tin nhập vào bị trống
     if not username_input or not password_input:
          messagebox.showwarning(title="Lỗi", message="Vui lòng nhập đầy đủ thông tin đăng nhập!")
          return

     # Mã hóa mật khẩu người dùng nhập vào
     hashed_password_input = hash_password(password_input)

     # Kiểm tra tài khoản và mật khẩu trong cơ sở dữ liệu
     cursor.execute("SELECT * FROM users WHERE username=?", (username_input,))
     user = cursor.fetchone()

    # Kiểm tra xem tài khoản có tồn tại và mật khẩu có đúng không
     if user:
          # user[1] là mật khẩu đã được mã hóa từ cơ sở dữ liệu
          if user[1] == hashed_password_input:
               messagebox.showinfo(title="Đăng nhập thành công", message="Bạn đã đăng nhập thành công.")
               # Mở cửa sổ chính hoặc thực hiện hành động sau khi đăng nhập thành công
               # Ẩn cửa sổ đăng nhập
               # Mở cửa sổ chính (thêm mã mở cửa sổ chính ở đây)
               show_app() 
          else:
               messagebox.showerror(title="Lỗi", message="Mật khẩu không đúng!")
     else:
          messagebox.showerror(title="Lỗi", message="Tài khoản không tồn tại!")


# Main login window
def main_login_window():

    # Create login labels and inputs
    login_label = tk.Label(window, text="Đăng Nhập", bg='#d3d3d3', fg="#800000", font=("Arial", 30, 'bold'))
    username_label = tk.Label(window, text="Tài khoản: ", bg='#d3d3d3', fg="#000000", font=("Arial", 16, 'bold'))
    password_label = tk.Label(window, text="Mật khẩu: ", bg='#d3d3d3', fg="#000000", font=("Arial", 16, 'bold'))

    username_entry = tk.Entry(window, font=("Arial", 16))
    password_entry = tk.Entry(window, show="*", font=("Arial", 16))
    login_button = tk.Button(window, text="Đăng nhập", bg="#DC143C", fg="#FFFFFF", font=("Arial", 16), command=lambda: login(window, cursor,username_entry, password_entry))

     # Registration label and button
    register_label = tk.Label(window, text="Bạn chưa có tài khoản? Hãy nhấn -> ", bg='#d3d3d3', fg="#8B0000", font=("Arial", 16))
    register_button = tk.Button(window, text='Đăng Kí', bg="#DC143C", fg="#FFFFFF", font=("Arial", 16), command=lambda: register(window, {}, cursor))
    register_label1 = tk.Label(window, text="tại đây.", bg='#d3d3d3', fg="#8B0000", font=("Arial", 16))
    

     # Layout login widgets
    login_label.grid(row=0, column=0, columnspan=8,padx=40, pady=40)
    username_label.grid(row=1, column=0, columnspan=1,sticky="e")
    username_entry.grid(row=1, column=1,columnspan=6, pady=20)
    password_label.grid(row=2, column=0, columnspan=1)
    password_entry.grid(row=2, column=1, columnspan=6, pady=20)
    login_button.grid(row=3, column=0, columnspan=6, pady=20)
    register_label.grid(row=4, column=1, columnspan=2, sticky="e")
    register_button.grid(row=4, column=3, columnspan=2, pady=5)
    register_label1.grid(row=4, column=5, columnspan=2, sticky="e") 
    window.mainloop()


# Start database connection
conn, cursor = init_db()

# Start the main login window
main_login_window()

# Don't forget to close the database connection after use
conn.close()