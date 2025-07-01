# -*- encoding: utf-8 -*-
# @Аутор      : minciv
# @e-mail     : minciv@protonmail.com
# @Web        : https://github.com/minciv
# @Фајл       : users_frame.py
# @Верзија    : 0.1.05.
# @Програм    : Windsurf
# @Опис       : Екран за управљање корисницима
# @Датум      : 01.07.2025.

from tkinter import ttk, messagebox, StringVar
from tkinter.constants import *
import hashlib
from sqlite3 import IntegrityError

class UsersFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        
        # Иницијализација променљивих за форму
        self.user_id = None
        self.username_var = StringVar()
        self.password_var = StringVar()
        self.confirm_password_var = StringVar()
        self.role_var = StringVar(value="user")
        
        # Променљиве за промену лозинке
        self.old_password_var = StringVar()
        self.new_password_var = StringVar()
        self.confirm_new_password_var = StringVar()
        
        # Креирање UI компоненти
        self.setup_ui()
        
        # Приказивање података
        self.load_users()
    
    def setup_ui(self):
        """Креирање корисничког интерфејса"""
        # Главни контејнер са две колоне
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Notebook за таб контролу
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=YES)
        
        # Таб за управљање корисницима (само за администраторе)
        if self.app.current_user['role'] == 'administrator':
            users_tab = ttk.Frame(notebook, padding=10)
            notebook.add(users_tab, text="Управљање корисницима")
            
            # Лева колона - форма за унос
            form_frame = ttk.LabelFrame(users_tab, text="Подаци о кориснику", padding=10)
            form_frame.pack(side=LEFT, fill=BOTH, expand=NO, padx=(0, 10))
            
            # Поља форме
            ttk.Label(form_frame, text="Корисничко име:").grid(row=0, column=0, sticky=W, pady=5)
            ttk.Entry(form_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky=W, pady=5)
            
            ttk.Label(form_frame, text="Лозинка:").grid(row=1, column=0, sticky=W, pady=5)
            ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=30).grid(row=1, column=1, sticky=W, pady=5)
            
            ttk.Label(form_frame, text="Потврда лозинке:").grid(row=2, column=0, sticky=W, pady=5)
            ttk.Entry(form_frame, textvariable=self.confirm_password_var, show="*", width=30).grid(row=2, column=1, sticky=W, pady=5)
            
            ttk.Label(form_frame, text="Улога:").grid(row=3, column=0, sticky=W, pady=5)
            role_frame = ttk.Frame(form_frame)
            role_frame.grid(row=3, column=1, sticky=W, pady=5)
            ttk.Radiobutton(role_frame, text="Администратор", variable=self.role_var, value="administrator").pack(side=LEFT)
            ttk.Radiobutton(role_frame, text="Корисник", variable=self.role_var, value="user").pack(side=LEFT)
            
            # Дугмад за акције
            button_frame = ttk.Frame(form_frame)
            button_frame.grid(row=4, column=0, columnspan=2, pady=10)
            
            ttk.Button(button_frame, text="Додај", command=self.add_user).pack(side=LEFT, padx=5)
            ttk.Button(button_frame, text="Измени", command=self.update_user).pack(side=LEFT, padx=5)
            ttk.Button(button_frame, text="Обриши", command=self.delete_user).pack(side=LEFT, padx=5)
            ttk.Button(button_frame, text="Очисти", command=self.clear_form).pack(side=LEFT, padx=5)
            
            # Десна колона - табела
            table_frame = ttk.Frame(users_tab)
            table_frame.pack(side=RIGHT, fill=BOTH, expand=YES)
            
            # Табела корисника
            self.tree = ttk.Treeview(table_frame, columns=("id", "username", "role"))
            self.tree.pack(fill=BOTH, expand=YES)
            
            # Подешавање заглавља колона
            self.tree.heading("#0", text="")
            self.tree.heading("id", text="ИД")
            self.tree.heading("username", text="Корисничко име")
            self.tree.heading("role", text="Улога")
            
            # Подешавање ширине колона
            self.tree.column("#0", width=0, stretch=NO)
            self.tree.column("id", width=50, anchor=CENTER)
            self.tree.column("username", width=200, anchor=W)
            self.tree.column("role", width=150, anchor=W)
            
            # Скролбар
            scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=RIGHT, fill=Y)
            
            # Везивање догађаја
            self.tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # Таб за промену лозинке (доступан свим пријављеним корисницима)
        change_password_tab = ttk.Frame(notebook, padding=10)
        notebook.add(change_password_tab, text="Промена лозинке")
        
        # Форма за промену лозинке
        password_frame = ttk.LabelFrame(change_password_tab, text="Промена лозинке", padding=10)
        password_frame.pack(fill=BOTH, expand=NO, padx=20, pady=20)
        
        ttk.Label(password_frame, text="Тренутна лозинка:").grid(row=0, column=0, sticky=W, pady=5)
        ttk.Entry(password_frame, textvariable=self.old_password_var, show="*", width=30).grid(row=0, column=1, sticky=W, pady=5)
        
        ttk.Label(password_frame, text="Нова лозинка:").grid(row=1, column=0, sticky=W, pady=5)
        ttk.Entry(password_frame, textvariable=self.new_password_var, show="*", width=30).grid(row=1, column=1, sticky=W, pady=5)
        
        ttk.Label(password_frame, text="Потврда нове лозинке:").grid(row=2, column=0, sticky=W, pady=5)
        ttk.Entry(password_frame, textvariable=self.confirm_new_password_var, show="*", width=30).grid(row=2, column=1, sticky=W, pady=5)
        
        # Дугме за промену лозинке
        change_button = ttk.Button(password_frame, text="Промени лозинку", command=self.change_password)
        change_button.grid(row=3, column=0, columnspan=2, pady=10)
    
    def hash_password(self, password):
        """Хеширање лозинке користећи SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Учитавање списка корисника из базе"""
        if self.app.current_user['role'] != 'administrator':
            return  # Само администратори могу да виде листу корисника
        
        # Брисање постојећих редова
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT user_id, username, role FROM Users ORDER BY username")
            
            for row in cursor.fetchall():
                user_id, username, role = row
                role_display = "Администратор" if role == "administrator" else "Корисник"
                self.tree.insert("", END, values=(user_id, username, role_display))
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању корисника: {str(e)}")
    
    def on_user_select(self, event):
        """Учитавање података изабраног корисника у форму"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        # Узимање ID-а изабраног корисника
        values = self.tree.item(selected_items[0], 'values')
        user_id = values[0]
        
        # Учитавање података
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT username, role FROM Users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            self.user_id = user_id
            self.username_var.set(user[0])
            self.role_var.set(user[1])
            self.password_var.set("")  # Брисање поља за лозинку
            self.confirm_password_var.set("")
    
    def add_user(self):
        """Додавање новог корисника у базу"""
        if not self._validate_form():
            return
            
        username = self.username_var.get().strip()
        password = self.password_var.get()
        role = self.role_var.get()
        
        # Хеширање лозинке
        password_hash = self.hash_password(password)
        
        cursor = self.app.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            self.app.conn.commit()
            
            messagebox.showinfo("Успех", "Корисник је успешно додат.")
            self.clear_form()
            self.load_users()
            
        except IntegrityError:
            messagebox.showerror("Грешка", f"Корисник са именом '{username}' већ постоји.")
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при додавању корисника: {str(e)}")
    
    def update_user(self):
        """Ажурирање постојећег корисника"""
        if not self.user_id:
            messagebox.showerror("Грешка", "Нисте изабрали корисника за измену.")
            return
            
        # Ако се мења тренутни пријављени корисник
        if int(self.user_id) == self.app.current_user['user_id'] and self.role_var.get() != "administrator":
            messagebox.showerror("Грешка", "Не можете променити своју улогу из администратора.")
            return
            
        username = self.username_var.get().strip()
        password = self.password_var.get()
        role = self.role_var.get()
        
        # Провера да ли је бар једно поље за унос попуњено
        if not username:
            messagebox.showwarning("Упозорење", "Корисничко име је обавезно поље.")
            return
        
        try:
            cursor = self.app.conn.cursor()
            
            # Ако је унета нова лозинка, ажурирати је
            if password:
                if password != self.confirm_password_var.get():
                    messagebox.showwarning("Упозорење", "Лозинке се не подударају.")
                    return
                    
                password_hash = self.hash_password(password)
                cursor.execute(
                    "UPDATE Users SET username = ?, password_hash = ?, role = ? WHERE user_id = ?",
                    (username, password_hash, role, self.user_id)
                )
            else:
                # Без промене лозинке
                cursor.execute(
                    "UPDATE Users SET username = ?, role = ? WHERE user_id = ?",
                    (username, role, self.user_id)
                )
                
            self.app.conn.commit()
            
            messagebox.showinfo("Успех", "Корисник је успешно ажуриран.")
            self.clear_form()
            self.load_users()
            
        except IntegrityError:
            messagebox.showerror("Грешка", f"Корисник са именом '{username}' већ постоји.")
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при ажурирању корисника: {str(e)}")
    
    def delete_user(self):
        """Брисање корисника из базе"""
        if not self.user_id:
            messagebox.showerror("Грешка", "Нисте изабрали корисника за брисање.")
            return
            
        # Провера да ли корисник брише сам себе
        if int(self.user_id) == self.app.current_user['user_id']:
            messagebox.showerror("Грешка", "Не можете обрисати свој налог.")
            return
            
        confirm = messagebox.askyesno("Потврда", "Да ли сте сигурни да желите да обришете овог корисника?")
        if confirm:
            try:
                cursor = self.app.conn.cursor()
                
                # Провера да ли је то једини преостали администратор
                cursor.execute("SELECT COUNT(*) FROM Users WHERE role = 'administrator'")
                admin_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT role FROM Users WHERE user_id = ?", (self.user_id,))
                user_role = cursor.fetchone()[0]
                
                if admin_count <= 1 and user_role == 'administrator':
                    messagebox.showerror("Грешка", "Не можете обрисати последњег администратора у систему.")
                    return
                
                cursor.execute("DELETE FROM Users WHERE user_id = ?", (self.user_id,))
                self.app.conn.commit()
                
                messagebox.showinfo("Успех", "Корисник је успешно обрисан.")
                self.clear_form()
                self.load_users()
                
            except Exception as e:
                messagebox.showerror("Грешка", f"Грешка при брисању корисника: {str(e)}")
    
    def change_password(self):
        """Промена лозинке пријављеног корисника"""
        old_password = self.old_password_var.get()
        new_password = self.new_password_var.get()
        confirm_new = self.confirm_new_password_var.get()
        
        # Провера да ли су унета сва поља
        if not old_password or not new_password or not confirm_new:
            messagebox.showwarning("Упозорење", "Морате унети све тражене лозинке.")
            return
            
        # Провера да ли се нове лозинке подударају
        if new_password != confirm_new:
            messagebox.showwarning("Упозорење", "Нове лозинке се не подударају.")
            return
            
        # Провера минималне дужине нове лозинке
        if len(new_password) < 6:
            messagebox.showwarning("Упозорење", "Нова лозинка мора имати најмање 6 знакова.")
            return
            
        # Хеширање и провера старе лозинке
        old_password_hash = self.hash_password(old_password)
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute(
                "SELECT user_id FROM Users WHERE user_id = ? AND password_hash = ?",
                (self.app.current_user['user_id'], old_password_hash)
            )
            
            if not cursor.fetchone():
                messagebox.showerror("Грешка", "Тренутна лозинка није исправна.")
                return
                
            # Хеширање и чување нове лозинке
            new_password_hash = self.hash_password(new_password)
            
            cursor.execute(
                "UPDATE Users SET password_hash = ? WHERE user_id = ?",
                (new_password_hash, self.app.current_user['user_id'])
            )
            
            self.app.conn.commit()
            
            # Брисање поља
            self.old_password_var.set("")
            self.new_password_var.set("")
            self.confirm_new_password_var.set("")
            
            messagebox.showinfo("Успех", "Ваша лозинка је успешно промењена.")
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при промени лозинке: {str(e)}")
    
    def clear_form(self):
        """Брисање поља у форми за управљање корисницима"""
        self.user_id = None
        self.username_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")
        self.role_var.set("user")
        
        # Скидање селекције из табеле
        for item in self.tree.selection():
            self.tree.selection_remove(item)
    
    def _validate_form(self):
        """Валидација унетих података у форми за додавање/измену корисника"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        confirm = self.confirm_password_var.get()
        
        if not username:
            messagebox.showwarning("Упозорење", "Корисничко име је обавезно поље.")
            return False
            
        if not self.user_id and not password:  # Само при додавању новог корисника
            messagebox.showwarning("Упозорење", "Лозинка је обавезна при додавању новог корисника.")
            return False
            
        if password and password != confirm:
            messagebox.showwarning("Упозорење", "Лозинке се не подударају.")
            return False
            
        if password and len(password) < 6:
            messagebox.showwarning("Упозорење", "Лозинка мора имати најмање 6 знакова.")
            return False
            
        return True
