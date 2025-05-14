# -*- encoding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : login_screen.py
# @Верзија  : 0.1.01.
# @Програм  : Windsurf
# @Опис     : Екран за пријаву корисника у апликацију
# @Датум   : 14.05.2025.

# Увоз потребних модула
import tkinter as tk
from tkinter import messagebox
from .db import get_user_by_username
import hashlib
'''
Класа LoginScreen наследује tk.Frame и представља екран за пријаву корисника
у апликацију. Она садржи улазне форме за корисничко име и лозинку,
као и дугме за пријаву. Када корисник кликне на дугме, проверава се
да ли су унесени подаци исправни. Уколико јесу, корисник се пријављује,
а уколико нису, приказује се порука о грешци.
'''
class LoginScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, sticky="nsew")
        tk.Label(self, text="Пријава", font=("Arial", 20)).pack(pady=30)
        tk.Label(self, text="Корисничко име:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()
        tk.Label(self, text="Лозинка:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()
        tk.Button(self, text="Пријави се", command=self.login).pack(pady=10)
    # Дефиниција метода за пријаву корисника
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        user = get_user_by_username(username)
        if user and user[2] == hashlib.sha256(password.encode()).hexdigest():
            self.master.current_user = {"id": user[0], "username": user[1], "role": user[3]}
            messagebox.showinfo("Успех", f"Добродошли, {user[1]}!")
            # self.master.show_frame(MainMenuScreen) # Placeholder for next screen
        else:
            messagebox.showerror("Грешка", "Погрешно корисничко име или лозинка.")