import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error
import os
import shutil
import time
import random
import string

DB_CONFIG = {
    'host': 'localhost',
    'database': 'ShoeStore1',
    'user': 'root',
    'password': 'anya281104!'
}

IMAGES_DIR = r"D:\Praktika\product_images"
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

class OrdersWindow:
    def __init__(self, parent, user_info, main_app):
        self.parent = parent
        self.user_info = user_info
        self.main_app = main_app
        self.edit_window = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Управление заказами - ООО Обувь")
        self.window.geometry("1200x600")
        self.window.configure(bg='#FFFFFF')
        
        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass
        
        top_frame = tk.Frame(self.window, bg='#7FFF00', height=50)
        top_frame.pack(fill=tk.X)
        
        lbl_title = tk.Label(top_frame, text="Список заказов", font=("Times New Roman", 14, "bold"), 
                             bg='#7FFF00', fg='#000000')
        lbl_title.pack(side=tk.LEFT, padx=20, pady=10)
        
        lbl_fio = tk.Label(top_frame, text="Вы вошли как: " + self.user_info['full_name'],
                           font=("Times New Roman", 12), bg='#7FFF00', fg='#000000')
        lbl_fio.pack(side=tk.RIGHT, padx=20, pady=10)
        
        btn_back = tk.Button(top_frame, text="Назад к товарам", command=self.window.destroy,
                             font=("Times New Roman", 10), bg='#00FA9A')
        btn_back.pack(side=tk.RIGHT, padx=10, pady=10)
        
        if self.user_info['role_id'] == 1:
            btn_frame = tk.Frame(self.window, bg='#FFFFFF')
            btn_frame.pack(fill=tk.X, padx=10, pady=5)
            
            btn_add = tk.Button(btn_frame, text="Добавить заказ", command=self.add_order,
                                font=("Times New Roman", 10), bg='#00FA9A', width=15)
            btn_add.pack(side=tk.LEFT, padx=5)
        
        columns = ('order_id', 'order_date', 'delivery_date', 'point_id', 'address', 'user_id', 'full_name', 'pickup_code', 'status')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', height=20)
        
        self.tree.heading('order_id', text='Номер заказа')
        self.tree.heading('order_date', text='Дата заказа')
        self.tree.heading('delivery_date', text='Дата выдачи')
        self.tree.heading('point_id', text='ID пункта')
        self.tree.heading('address', text='Адрес пункта выдачи')
        self.tree.heading('user_id', text='ID клиента')
        self.tree.heading('full_name', text='Клиент')
        self.tree.heading('pickup_code', text='Код получения')
        self.tree.heading('status', text='Статус')
        
        self.tree.column('order_id', width=80)
        self.tree.column('order_date', width=100)
        self.tree.column('delivery_date', width=100)
        self.tree.column('point_id', width=60)
        self.tree.column('address', width=200)
        self.tree.column('user_id', width=60)
        self.tree.column('full_name', width=180)
        self.tree.column('pickup_code', width=100)
        self.tree.column('status', width=100)
        
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        if self.user_info['role_id'] == 1:
            btn_frame2 = tk.Frame(self.window, bg='#FFFFFF')
            btn_frame2.pack(fill=tk.X, padx=10, pady=5)
            
            btn_edit = tk.Button(btn_frame2, text="Редактировать заказ", command=self.edit_order,
                                 font=("Times New Roman", 10), bg='#00FA9A', width=18)
            btn_edit.pack(side=tk.LEFT, padx=5)
            
            btn_delete = tk.Button(btn_frame2, text="Удалить заказ", command=self.delete_order,
                                   font=("Times New Roman", 10), bg='#FF6B6B', width=18)
            btn_delete.pack(side=tk.LEFT, padx=5)
        
        self.load_orders()
    
    def load_orders(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT o.order_id, o.order_date, o.delivery_date, o.point_id, p.address, 
                       o.user_id, u.full_name, o.pickup_code, o.status
                FROM Orders o
                JOIN PickupPoints p ON o.point_id = p.point_id
                JOIN Users u ON o.user_id = u.user_id
                ORDER BY o.order_id
            """
            cursor.execute(query)
            orders = cursor.fetchall()
            
            for order in orders:
                self.tree.insert('', tk.END, values=(
                    order['order_id'],
                    order['order_date'],
                    order['delivery_date'] if order['delivery_date'] else '',
                    order['point_id'],
                    order['address'],
                    order['user_id'],
                    order['full_name'],
                    order['pickup_code'],
                    order['status']
                ))
            
            cursor.close()
            conn.close()
            
        except Error as e:
            messagebox.showerror("Ошибка БД", f"Не удалось загрузить заказы: {e}")
    
    def add_order(self):
        if self.edit_window is not None:
            messagebox.showwarning("Внимание", "Закройте окно редактирования")
            return
        OrderForm(self.window, self, self.user_info, mode='add')
    
    def edit_order(self):
        if self.edit_window is not None:
            messagebox.showwarning("Внимание", "Закройте окно редактирования")
            return
        
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для редактирования")
            return
        
        order_id = self.tree.item(selected[0])['values'][0]
        OrderForm(self.window, self, self.user_info, mode='edit', order_id=order_id)
    
    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для удаления")
            return
        
        order_id = self.tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить заказ №{order_id}?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Orders WHERE order_id = %s", (order_id,))
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Успех", "Заказ удален")
                self.load_orders()
                if self.main_app:
                    self.main_app.load_products()
            except Error as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить заказ: {e}")
    
    def refresh(self):
        self.load_orders()

class OrderForm:
    def __init__(self, parent, orders_window, user_info, mode='add', order_id=None):
        self.orders_window = orders_window
        self.user_info = user_info
        self.mode = mode
        self.order_id = order_id
        
        self.window = tk.Toplevel(parent)
        self.window.title("Добавление заказа" if mode == 'add' else "Редактирование заказа")
        self.window.geometry("500x500")
        self.window.configure(bg='#FFFFFF')
        self.window.grab_set()
        
        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass
        
        orders_window.edit_window = self.window
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        row = 0
        
        if mode == 'edit':
            tk.Label(self.window, text="Номер заказа:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
            self.order_id_label = tk.Label(self.window, text="", font=("Times New Roman", 11), bg='#FFFFFF')
            self.order_id_label.grid(row=row, column=1, padx=10, pady=5, sticky='w')
            row += 1
        
        tk.Label(self.window, text="Дата заказа (ГГГГ-ММ-ДД):", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.order_date_entry = tk.Entry(self.window, width=30)
        self.order_date_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Дата выдачи (ГГГГ-ММ-ДД):", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.delivery_date_entry = tk.Entry(self.window, width=30)
        self.delivery_date_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Пункт выдачи (ID):", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.point_id_entry = tk.Entry(self.window, width=30)
        self.point_id_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="ID клиента:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.user_id_entry = tk.Entry(self.window, width=30)
        self.user_id_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Код получения:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.pickup_code_entry = tk.Entry(self.window, width=30)
        self.pickup_code_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Статус:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.status_combo = ttk.Combobox(self.window, values=["Новый", "В обработке", "Завершен"], width=27)
        self.status_combo.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        btn_frame = tk.Frame(self.window, bg='#FFFFFF')
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        btn_save = tk.Button(btn_frame, text="Сохранить", command=self.save_order,
                             font=("Times New Roman", 11), bg='#00FA9A', width=12)
        btn_save.pack(side=tk.LEFT, padx=10)
        
        btn_cancel = tk.Button(btn_frame, text="Отмена", command=self.on_close,
                               font=("Times New Roman", 11), bg='#FF6B6B', width=12)
        btn_cancel.pack(side=tk.LEFT, padx=10)
        
        if mode == 'edit' and order_id:
            self.load_order_data()
    
    def load_order_data(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Orders WHERE order_id = %s", (self.order_id,))
            order = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if order:
                self.order_id_label.config(text=str(order['order_id']))
                self.order_date_entry.insert(0, str(order['order_date']))
                if order['delivery_date']:
                    self.delivery_date_entry.insert(0, str(order['delivery_date']))
                self.point_id_entry.insert(0, str(order['point_id']))
                self.user_id_entry.insert(0, str(order['user_id']))
                self.pickup_code_entry.insert(0, order['pickup_code'])
                self.status_combo.set(order['status'])
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
    
    def save_order(self):
        try:
            order_date = self.order_date_entry.get().strip()
            delivery_date = self.delivery_date_entry.get().strip() or None
            point_id = int(self.point_id_entry.get())
            user_id = int(self.user_id_entry.get())
            pickup_code = self.pickup_code_entry.get().strip()
            status = self.status_combo.get()
            
            if not order_date or not pickup_code or not status:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
            
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            if self.mode == 'add':
                cursor.execute("""
                    INSERT INTO Orders (order_id, order_date, delivery_date, point_id, user_id, pickup_code, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (random.randint(100, 999), order_date, delivery_date, point_id, user_id, pickup_code, status))
                messagebox.showinfo("Успех", "Заказ добавлен")
            else:
                cursor.execute("""
                    UPDATE Orders SET order_date=%s, delivery_date=%s, point_id=%s, 
                                   user_id=%s, pickup_code=%s, status=%s
                    WHERE order_id=%s
                """, (order_date, delivery_date, point_id, user_id, pickup_code, status, self.order_id))
                messagebox.showinfo("Успех", "Заказ обновлен")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            self.orders_window.refresh()
            self.on_close()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат данных")
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def on_close(self):
        self.orders_window.edit_window = None
        self.window.destroy()

class MainApp:
    def __init__(self, root, user_info):
        self.root = root
        self.user_info = user_info
        self.current_sort = "Без сортировки"
        self.current_filter_supplier = "Все поставщики"
        self.current_search = ""
        self.edit_window = None
        self.photo_cache = {}
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.root.title("ООО Обувь - Добро пожаловать, " + self.user_info['full_name'])
        self.root.geometry("1400x700")
        self.root.configure(bg='#FFFFFF')

        top_frame = tk.Frame(root, bg='#7FFF00', height=50)
        top_frame.pack(fill=tk.X)
        
        lbl_fio = tk.Label(top_frame, text="Вы вошли как: " + self.user_info['full_name'],
                           font=("Times New Roman", 12), bg='#7FFF00', fg='#000000')
        lbl_fio.pack(side=tk.RIGHT, padx=20, pady=10)
        
        btn_logout = tk.Button(top_frame, text="Выйти", command=self.logout,
                               font=("Times New Roman", 10), bg='#00FA9A')
        btn_logout.pack(side=tk.LEFT, padx=20, pady=10)
        
        if self.user_info['role_id'] == 1 or self.user_info['role_id'] == 2:
            btn_orders = tk.Button(top_frame, text="Заказы", command=self.open_orders,
                                   font=("Times New Roman", 10), bg='#00FA9A')
            btn_orders.pack(side=tk.LEFT, padx=10, pady=10)

        if self.user_info['role_id'] == 1 or self.user_info['role_id'] == 2:
            filter_frame = tk.Frame(root, bg='#FFFFFF')
            filter_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(filter_frame, text="Поиск:", font=("Times New Roman", 10), bg='#FFFFFF').pack(side=tk.LEFT, padx=5)
            self.search_entry = tk.Entry(filter_frame, font=("Times New Roman", 10), width=30)
            self.search_entry.pack(side=tk.LEFT, padx=5)
            self.search_entry.bind('<KeyRelease>', self.on_search)
            
            tk.Label(filter_frame, text="Поставщик:", font=("Times New Roman", 10), bg='#FFFFFF').pack(side=tk.LEFT, padx=5)
            self.supplier_var = tk.StringVar(value="Все поставщики")
            self.supplier_combo = ttk.Combobox(filter_frame, textvariable=self.supplier_var, width=20)
            self.supplier_combo.pack(side=tk.LEFT, padx=5)
            self.supplier_combo.bind('<<ComboboxSelected>>', self.on_filter)
            
            tk.Label(filter_frame, text="Сортировка по складу:", font=("Times New Roman", 10), bg='#FFFFFF').pack(side=tk.LEFT, padx=5)
            self.sort_var = tk.StringVar(value="Без сортировки")
            self.sort_combo = ttk.Combobox(filter_frame, textvariable=self.sort_var, 
                                           values=["Без сортировки", "По возрастанию", "По убыванию"], width=15)
            self.sort_combo.pack(side=tk.LEFT, padx=5)
            self.sort_combo.bind('<<ComboboxSelected>>', self.on_sort)

        main_frame = tk.Frame(root, bg='#FFFFFF')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = tk.Frame(main_frame, bg='#FFFFFF')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        columns = ('article', 'name', 'category', 'description', 'manufacturer', 
                   'supplier', 'price', 'unit', 'stock', 'discount')
        self.tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=25)
        
        self.tree.heading('article', text='Артикул')
        self.tree.heading('name', text='Название')
        self.tree.heading('category', text='Категория')
        self.tree.heading('description', text='Описание')
        self.tree.heading('manufacturer', text='Производитель')
        self.tree.heading('supplier', text='Поставщик')
        self.tree.heading('price', text='Цена')
        self.tree.heading('unit', text='Ед.')
        self.tree.heading('stock', text='На складе')
        self.tree.heading('discount', text='Скидка %')

        self.tree.column('article', width=80)
        self.tree.column('name', width=150)
        self.tree.column('category', width=100)
        self.tree.column('description', width=200)
        self.tree.column('manufacturer', width=120)
        self.tree.column('supplier', width=100)
        self.tree.column('price', width=120)
        self.tree.column('unit', width=50)
        self.tree.column('stock', width=80)
        self.tree.column('discount', width=80)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_product_select)
        
        right_frame = tk.Frame(main_frame, bg='#FFFFFF', width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        tk.Label(right_frame, text="Фото товара", font=("Times New Roman", 12, "bold"), bg='#FFFFFF').pack(pady=10)
        
        self.product_image = tk.Label(right_frame, bg='#F0F0F0', width=280, height=200)
        self.product_image.pack(pady=10)
        
        self.product_info = tk.Label(right_frame, text="Выберите товар для просмотра фото", 
                                      bg='#FFFFFF', font=("Times New Roman", 10), wraplength=260)
        self.product_info.pack(pady=10)
        
        if self.user_info['role_id'] == 1:
            btn_frame = tk.Frame(root, bg='#FFFFFF')
            btn_frame.pack(fill=tk.X, padx=10, pady=5)
            
            btn_add = tk.Button(btn_frame, text="Добавить товар", command=self.add_product,
                                font=("Times New Roman", 10), bg='#00FA9A', width=15)
            btn_add.pack(side=tk.LEFT, padx=5)
            
            btn_edit = tk.Button(btn_frame, text="Редактировать товар", command=self.edit_product,
                                 font=("Times New Roman", 10), bg='#00FA9A', width=15)
            btn_edit.pack(side=tk.LEFT, padx=5)
            
            btn_delete = tk.Button(btn_frame, text="Удалить товар", command=self.delete_product,
                                   font=("Times New Roman", 10), bg='#FF6B6B', width=15)
            btn_delete.pack(side=tk.LEFT, padx=5)

        self.load_suppliers()
        self.load_products()
    
    def open_orders(self):
        OrdersWindow(self.root, self.user_info, self)
    
    def load_image(self, photo_filename, size=(200, 150)):
        if not photo_filename:
            return None
        try:
            if photo_filename in self.photo_cache:
                return self.photo_cache[photo_filename]
            photo_path = os.path.join(IMAGES_DIR, photo_filename)
            if not os.path.exists(photo_path):
                img = Image.new('RGB', size, color='#D3D3D3')
                photo = ImageTk.PhotoImage(img)
                self.photo_cache[photo_filename] = photo
                return photo
            img = Image.open(photo_path)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.thumbnail(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.photo_cache[photo_filename] = photo
            return photo
        except Exception:
            img = Image.new('RGB', size, color='#D3D3D3')
            photo = ImageTk.PhotoImage(img)
            return photo

    def on_product_select(self, event):
        selected = self.tree.selection()
        if selected:
            article = self.tree.item(selected[0])['values'][0]
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT photo_filename, name, price, stock_quantity FROM Products WHERE article = %s", (article,))
                product = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if product:
                    photo = self.load_image(product['photo_filename'], (280, 200))
                    if photo:
                        self.product_image.config(image=photo)
                        self.product_image.image = photo
                    else:
                        self.product_image.config(image='', text="Нет фото")
                        self.product_image.configure(text="Нет фото")
                    
                    info_text = f"{product['name']}\nЦена: {product['price']} руб.\nОстаток: {product['stock_quantity']} шт."
                    self.product_info.config(text=info_text)
            except Error as e:
                print(f"Ошибка БД: {e}")

    def load_suppliers(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT supplier FROM Products WHERE supplier IS NOT NULL AND supplier != ''")
            suppliers = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            suppliers_list = ["Все поставщики"] + suppliers
            if hasattr(self, 'supplier_combo'):
                self.supplier_combo['values'] = suppliers_list
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить поставщиков: {e}")

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM Products WHERE 1=1"
            params = []
            
            if hasattr(self, 'current_filter_supplier') and self.current_filter_supplier != "Все поставщики":
                query += " AND supplier = %s"
                params.append(self.current_filter_supplier)
            
            if hasattr(self, 'current_search') and self.current_search:
                query += """ AND (article LIKE %s OR name LIKE %s OR category LIKE %s 
                               OR description LIKE %s OR manufacturer LIKE %s OR supplier LIKE %s)"""
                search_pattern = f"%{self.current_search}%"
                params.extend([search_pattern] * 6)
            
            if hasattr(self, 'current_sort') and self.current_sort == "По возрастанию":
                query += " ORDER BY stock_quantity ASC"
            elif hasattr(self, 'current_sort') and self.current_sort == "По убыванию":
                query += " ORDER BY stock_quantity DESC"
            
            cursor.execute(query, params)
            products = cursor.fetchall()
            
            for product in products:
                if product['discount_percent'] > 0:
                    final_price = float(product['price']) * (1 - float(product['discount_percent']) / 100)
                    price_text = f"{product['price']:.2f} руб. -> {final_price:.2f} руб."
                else:
                    price_text = f"{product['price']:.2f} руб."
                
                desc = str(product['description']) if product['description'] else ''
                if len(desc) > 50:
                    desc = desc[:50] + "..."
                
                tag = ''
                if product['discount_percent'] > 15:
                    tag = 'high_discount'
                elif product['stock_quantity'] == 0:
                    tag = 'out_of_stock'
                
                self.tree.insert('', tk.END, values=(
                    product['article'], 
                    product['name'], 
                    product['category'], 
                    desc,
                    product['manufacturer'], 
                    product['supplier'], 
                    price_text, 
                    product['unit'],
                    product['stock_quantity'], 
                    str(product['discount_percent']) + "%"
                ), tags=(tag,))
            
            self.tree.tag_configure('high_discount', background='#2E8B57')
            self.tree.tag_configure('out_of_stock', foreground='blue')
            
            cursor.close()
            conn.close()
            
        except Error as e:
            messagebox.showerror("Ошибка БД", f"Не удалось загрузить товары: {e}")

    def on_search(self, event):
        self.current_search = self.search_entry.get()
        self.load_products()

    def on_filter(self, event):
        self.current_filter_supplier = self.supplier_var.get()
        self.load_products()

    def on_sort(self, event):
        self.current_sort = self.sort_var.get()
        self.load_products()

    def add_product(self):
        if self.edit_window is not None:
            messagebox.showwarning("Внимание", "Закройте окно редактирования")
            return
        ProductForm(self.root, self, mode='add')

    def edit_product(self):
        if self.edit_window is not None:
            messagebox.showwarning("Внимание", "Закройте окно редактирования")
            return
        
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для редактирования")
            return
        
        article = self.tree.item(selected[0])['values'][0]
        ProductForm(self.root, self, mode='edit', article=article)

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для удаления")
            return
        
        article = self.tree.item(selected[0])['values'][0]
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM OrderItems WHERE article = %s", (article,))
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            if count > 0:
                messagebox.showerror("Ошибка", "Товар присутствует в заказах. Удаление невозможно.")
                return
            
            if messagebox.askyesno("Подтверждение", f"Удалить товар {article}?"):
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT photo_filename FROM Products WHERE article = %s", (article,))
                result = cursor.fetchone()
                if result and result[0]:
                    photo_path = os.path.join(IMAGES_DIR, result[0])
                    if os.path.exists(photo_path):
                        os.remove(photo_path)
                
                cursor.execute("DELETE FROM Products WHERE article = %s", (article,))
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Успех", "Товар удален")
                self.load_products()
                self.load_suppliers()
                
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить товар: {e}")

    def logout(self):
        self.root.destroy()
        open_login_window()

class ProductForm:
    def __init__(self, parent, main_app, mode='add', article=None):
        self.main_app = main_app
        self.mode = mode
        self.article = article
        self.photo_path = None
        self.old_photo = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Добавление товара" if mode == 'add' else "Редактирование товара")
        self.window.geometry("550x750")
        self.window.configure(bg='#FFFFFF')
        self.window.grab_set()
        
        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass
        
        main_app.edit_window = self.window
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        row = 0
        tk.Label(self.window, text="Фото:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.photo_label = tk.Label(self.window, text="Фото не выбрано", bg='#FFFFFF', width=30)
        self.photo_label.grid(row=row, column=1, padx=10, pady=5)
        btn_photo = tk.Button(self.window, text="Выбрать фото", command=self.select_photo,
                              font=("Times New Roman", 10), bg='#00FA9A')
        btn_photo.grid(row=row, column=2, padx=10, pady=5)
        row += 1
        
        self.photo_preview = tk.Label(self.window, bg='#F0F0F0', width=300, height=150)
        self.photo_preview.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1
        
        tk.Label(self.window, text="Наименование:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.name_entry = tk.Entry(self.window, width=40, font=("Times New Roman", 10))
        self.name_entry.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Категория:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.category_combo = ttk.Combobox(self.window, values=["Женская обувь", "Мужская обувь", "Детская обувь"], width=37)
        self.category_combo.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Описание:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='ne')
        self.desc_text = tk.Text(self.window, width=40, height=4, font=("Times New Roman", 10))
        self.desc_text.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Производитель:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.manufacturer_entry = tk.Entry(self.window, width=40, font=("Times New Roman", 10))
        self.manufacturer_entry.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Поставщик:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.supplier_entry = tk.Entry(self.window, width=40, font=("Times New Roman", 10))
        self.supplier_entry.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Цена:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.price_entry = tk.Entry(self.window, width=40, font=("Times New Roman", 10))
        self.price_entry.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Единица измерения:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.unit_entry = tk.Entry(self.window, width=40, font=("Times New Roman", 10))
        self.unit_entry.insert(0, "шт.")
        self.unit_entry.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Количество:", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.stock_entry = tk.Entry(self.window, width=40, font=("Times New Roman", 10))
        self.stock_entry.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        row += 1
        
        tk.Label(self.window, text="Скидка (%):", font=("Times New Roman", 11), bg='#FFFFFF').grid(row=row, column=0, padx=10, pady=5, sticky='e')
        self.discount_entry = tk.Entry(self.window, width=40, font=("Times New Roman", 10))
        self.discount_entry.insert(0, "0")
        self.discount_entry.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        row += 1
        
        btn_frame = tk.Frame(self.window, bg='#FFFFFF')
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        btn_save = tk.Button(btn_frame, text="Сохранить", command=self.save_product,
                             font=("Times New Roman", 11), bg='#00FA9A', width=12)
        btn_save.pack(side=tk.LEFT, padx=10)
        
        btn_cancel = tk.Button(btn_frame, text="Отмена", command=self.on_close,
                               font=("Times New Roman", 11), bg='#FF6B6B', width=12)
        btn_cancel.pack(side=tk.LEFT, padx=10)
        
        if mode == 'edit' and article:
            self.load_product_data()

    def select_photo(self):
        file_path = filedialog.askopenfilename(
            title="Выберите фото",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            try:
                img = Image.open(file_path)
                img.thumbnail((280, 140), Image.Resampling.LANCZOS)
                preview = ImageTk.PhotoImage(img)
                self.photo_preview.config(image=preview)
                self.photo_preview.image = preview
                self.photo_path = file_path
                self.photo_label.config(text=os.path.basename(file_path))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить фото: {e}")

    def load_product_data(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Products WHERE article = %s", (self.article,))
            product = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if product:
                self.name_entry.insert(0, product['name'] or '')
                self.category_combo.set(product['category'] or '')
                self.desc_text.insert('1.0', product['description'] or '')
                self.manufacturer_entry.insert(0, product['manufacturer'] or '')
                self.supplier_entry.insert(0, product['supplier'] or '')
                self.price_entry.insert(0, str(product['price']))
                self.unit_entry.delete(0, tk.END)
                self.unit_entry.insert(0, product['unit'] or 'шт.')
                self.stock_entry.insert(0, str(product['stock_quantity']))
                self.discount_entry.delete(0, tk.END)
                self.discount_entry.insert(0, str(product['discount_percent']))
                
                if product['photo_filename']:
                    self.old_photo = product['photo_filename']
                    self.photo_label.config(text=product['photo_filename'])
                    photo_path = os.path.join(IMAGES_DIR, product['photo_filename'])
                    if os.path.exists(photo_path):
                        img = Image.open(photo_path)
                        img.thumbnail((280, 140), Image.Resampling.LANCZOS)
                        preview = ImageTk.PhotoImage(img)
                        self.photo_preview.config(image=preview)
                        self.photo_preview.image = preview
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

    def save_product(self):
        try:
            name = self.name_entry.get().strip()
            category = self.category_combo.get()
            description = self.desc_text.get('1.0', tk.END).strip()
            manufacturer = self.manufacturer_entry.get().strip()
            supplier = self.supplier_entry.get().strip()
            price = float(self.price_entry.get())
            unit = self.unit_entry.get().strip()
            stock = int(self.stock_entry.get())
            discount = int(self.discount_entry.get())
            
            if price < 0:
                messagebox.showerror("Ошибка", "Цена не может быть отрицательной")
                return
            if stock < 0:
                messagebox.showerror("Ошибка", "Количество не может быть отрицательным")
                return
            if discount < 0 or discount > 100:
                messagebox.showerror("Ошибка", "Скидка должна быть от 0 до 100")
                return
            
            photo_filename = None
            if self.photo_path:
                ext = os.path.splitext(self.photo_path)[1]
                photo_filename = f"product_{int(time.time())}{ext}"
                dest_path = os.path.join(IMAGES_DIR, photo_filename)
                shutil.copy2(self.photo_path, dest_path)
                
                if self.mode == 'edit' and self.old_photo:
                    old_path = os.path.join(IMAGES_DIR, self.old_photo)
                    if os.path.exists(old_path):
                        os.remove(old_path)
            
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            if self.mode == 'add':
                article = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                cursor.execute("""
                    INSERT INTO Products (article, name, category, description, manufacturer, supplier, 
                                         price, unit, stock_quantity, discount_percent, photo_filename)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (article, name, category, description, manufacturer, supplier, 
                      price, unit, stock, discount, photo_filename))
                messagebox.showinfo("Успех", f"Товар добавлен. Артикул: {article}")
            else:
                if photo_filename is None and self.old_photo:
                    photo_filename = self.old_photo
                cursor.execute("""
                    UPDATE Products SET name=%s, category=%s, description=%s, manufacturer=%s, 
                                   supplier=%s, price=%s, unit=%s, stock_quantity=%s, 
                                   discount_percent=%s, photo_filename=%s
                    WHERE article=%s
                """, (name, category, description, manufacturer, supplier, 
                      price, unit, stock, discount, photo_filename, self.article))
                messagebox.showinfo("Успех", "Товар обновлен")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            self.main_app.load_products()
            self.main_app.load_suppliers()
            self.on_close()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных: {e}")
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_close(self):
        self.main_app.edit_window = None
        self.window.destroy()

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизация - ООО Обувь")
        self.root.geometry("450x450")
        self.root.configure(bg='#FFFFFF')
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        try:
            logo_img = Image.open("logo.png")
            logo_img.thumbnail((150, 150), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(root, image=self.logo, bg='#FFFFFF')
            logo_label.pack(pady=20)
        except:
            lbl_title_big = tk.Label(root, text="ООО Обувь", font=("Times New Roman", 24, "bold"), bg='#FFFFFF')
            lbl_title_big.pack(pady=20)

        lbl_title = tk.Label(root, text="Вход в систему", font=("Times New Roman", 16, "bold"), bg='#FFFFFF')
        lbl_title.pack(pady=10)
        
        frame = tk.Frame(root, bg='#FFFFFF')
        frame.pack(pady=20)
        
        lbl_login = tk.Label(frame, text="Логин:", font=("Times New Roman", 12), bg='#FFFFFF')
        lbl_login.grid(row=0, column=0, padx=10, pady=10)
        self.entry_login = tk.Entry(frame, font=("Times New Roman", 12), width=20)
        self.entry_login.grid(row=0, column=1, padx=10, pady=10)
        
        lbl_password = tk.Label(frame, text="Пароль:", font=("Times New Roman", 12), bg='#FFFFFF')
        lbl_password.grid(row=1, column=0, padx=10, pady=10)
        self.entry_password = tk.Entry(frame, show="*", font=("Times New Roman", 12), width=20)
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)
        
        btn_frame = tk.Frame(root, bg='#FFFFFF')
        btn_frame.pack(pady=20)
        
        btn_login = tk.Button(btn_frame, text="Войти", command=self.login,
                              font=("Times New Roman", 12), bg='#00FA9A', width=12)
        btn_login.pack(side=tk.LEFT, padx=10)
        
        btn_guest = tk.Button(btn_frame, text="Войти как Гость", command=self.guest_login,
                              font=("Times New Roman", 12), bg='#7FFF00', width=15)
        btn_guest.pack(side=tk.LEFT, padx=10)

    def login(self):
        login = self.entry_login.get()
        password = self.entry_password.get()
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT u.user_id, u.full_name, u.role_id, r.role_name 
                FROM Users u 
                JOIN Roles r ON u.role_id = r.role_id 
                WHERE u.login = %s AND u.password = %s
            """
            cursor.execute(query, (login, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                self.root.destroy()
                main_root = tk.Tk()
                MainApp(main_root, {'full_name': user['full_name'], 'role_id': user['role_id']})
                main_root.mainloop()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
        except Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка подключения: {e}")

    def guest_login(self):
        self.root.destroy()
        main_root = tk.Tk()
        MainApp(main_root, {'full_name': 'Гость', 'role_id': 4})
        main_root.mainloop()

def open_login_window():
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    open_login_window()