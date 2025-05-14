# -*- encoding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : login_frame.py
# @Верзија  : 0.1.01.
# @Програм  : Windsurf
# @Опис     : Модул пројекта Школска такмичења за управљање корисницима
# @Датум   : 14.05.2025.

from tkinter import ttk, StringVar
from tkinter.messagebox import showerror
import hashlib
from sqlite3 import IntegrityError

class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Креирање променљивих
        self.username = StringVar()
        self.password = StringVar()
        
        # Подешавање корисничког интерфејса
        self.setup_ui()
    
    def setup_ui(self):
        """Креирање форме за пријаву"""
        # Главни контејнер са размаком
        main_container = ttk.Frame(self, padding="40")
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # Наслов
        title_label = ttk.Label(main_container, text="Пријава на систем", font=('Helvetica', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Форма за пријаву
        ttk.Label(main_container, text="Корисничко име:").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        username_entry = ttk.Entry(main_container, textvariable=self.username, width=30)
        username_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(main_container, text="Лозинка:").grid(row=2, column=0, pady=5, padx=5, sticky="e")
        password_entry = ttk.Entry(main_container, textvariable=self.password, show="*", width=30)
        password_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Дугме за пријаву
        login_btn = ttk.Button(main_container, text="Пријава", command=self.login, width=20)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Повезивање тастера Enter са пријавом
        username_entry.bind('<Return>', lambda e: password_entry.focus())
        password_entry.bind('<Return>', lambda e: self.login())
        
        # Центрирање форме
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Фокус на поље за корисничко име
        username_entry.focus()
        
        # Провера/креирање админ налога
        self.ensure_admin_exists()
    
    def hash_password(self, password):
        """Хеширање лозинке користећи SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def ensure_admin_exists(self):
        """Креирање подразумеваног админ налога ако не постоји ниједан корисник"""
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] == 0:
            admin_pass = "admin123"  # Подразумевана лозинка
            pass_hash = self.hash_password(admin_pass)
            try:
                cursor.execute(
                    "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", pass_hash, "administrator")
                )
                self.app.conn.commit()
            except IntegrityError:
                pass  # Админ налог већ постоји
    
    def login(self):
        """Обрада покушаја пријаве"""
        username = self.username.get().strip()
        password = self.password.get()
        
        if not username or not password:
            showerror("Грешка", "Молимо унесите корисничко име и лозинку")
            return
        
        # Хеширање лозинке
        password_hash = self.hash_password(password)
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute(
                "SELECT user_id, role FROM Users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            result = cursor.fetchone()
            
            if result:
                user_id, role = result
                self.app.current_user = {
                    'user_id': user_id,
                    'username': username,
                    'role': role
                }
                self.password.set("")  # Брисање лозинке
                self.app.show_main_window()  # Placeholder for transitioning
            else:
                showerror("Грешка", "Погрешно корисничко име или лозинка")
                self.password.set("")  # Брисање поља за лозинку
        except Exception as e:
            showerror("Грешка", f"Грешка при пријави: {str(e)}")