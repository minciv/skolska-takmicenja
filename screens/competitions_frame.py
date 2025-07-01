# -*- encoding: utf-8 -*-
# @Аутор      : minciv
# @e-mail     : minciv@protonmail.com
# @Web        : https://github.com/minciv
# @Фајл       : competitions_frame.py
# @Верзија    : 0.1.05.
# @Програм    : Windsurf
# @Опис       : Екран за управљање такмичењима и предметима
# @Датум      : 01.07.2025.

from tkinter import ttk, messagebox, StringVar
from tkinter.constants import *
import pandas as pd

class CompetitionsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        
        # Иницијализација променљивих за форму
        self.competition_id = None
        self.competition_name_var = StringVar()
        
        # Променљиве за претрагу
        self.search_query = StringVar()
        
        # Подељени екран на два дела - такмичења и нивои
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Креирање првог таба за такмичења
        self.competitions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.competitions_tab, text="Такмичења/Предмети")
        
        # Креирање другог таба за нивое такмичења
        self.levels_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.levels_tab, text="Нивои такмичења")
        
        # Креирање UI компоненти
        self.setup_competitions_ui()
        self.setup_levels_ui()
        
        # Приказивање података
        self.load_competitions()
        self.load_levels()
    
    def setup_competitions_ui(self):
        """Креирање UI компоненти за управљање такмичењима"""
        # Главни контејнер са две колоне (форма и табела)
        main_frame = ttk.Frame(self.competitions_tab, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Лева колона - форма за унос
        form_frame = ttk.LabelFrame(main_frame, text="Подаци о такмичењу/предмету", padding=10)
        form_frame.pack(side=LEFT, fill=BOTH, expand=NO, padx=(0, 10))
        
        # Поља форме
        ttk.Label(form_frame, text="Назив:").grid(row=0, column=0, sticky=W, pady=5)
        ttk.Entry(form_frame, textvariable=self.competition_name_var, width=30).grid(row=0, column=1, sticky=W, pady=5)
        
        # Дугмад за акције
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Додај", command=self.add_competition).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Измени", command=self.update_competition).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Обриши", command=self.delete_competition).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Очисти", command=self.clear_competition_form).pack(side=LEFT, padx=5)
        
        # Десна колона - табела и претрага
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(side=RIGHT, fill=BOTH, expand=YES)
        
        # Оквир за претрагу
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill=X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Претрага:").pack(side=LEFT)
        ttk.Entry(search_frame, textvariable=self.search_query, width=30).pack(side=LEFT, padx=5)
        ttk.Button(search_frame, text="Тражи", command=self.search_competitions).pack(side=LEFT)
        ttk.Button(search_frame, text="Прикажи све", command=self.load_competitions).pack(side=LEFT, padx=5)
        
        # Табела такмичења
        self.comp_tree = ttk.Treeview(table_frame, columns=("ID", "Назив"))
        self.comp_tree.pack(fill=BOTH, expand=YES)
        
        # Подешавање заглавља колона
        self.comp_tree.heading("#0", text="")
        self.comp_tree.heading("ID", text="ИД")
        self.comp_tree.heading("Назив", text="Назив такмичења/предмета")
        
        # Подешавање ширине колона
        self.comp_tree.column("#0", width=0, stretch=NO)
        self.comp_tree.column("ID", width=50, anchor=CENTER)
        self.comp_tree.column("Назив", width=300)
        
        # Скролбар
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.comp_tree.yview)
        self.comp_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Везивање догађаја
        self.comp_tree.bind('<<TreeviewSelect>>', self.on_competition_select)
    
    def setup_levels_ui(self):
        """Креирање UI компоненти за управљање нивоима такмичења"""
        # Променљиве за нивое такмичења
        self.level_id = None
        self.level_name_var = StringVar()
        
        # Главни контејнер са две колоне (форма и табела)
        main_frame = ttk.Frame(self.levels_tab, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Лева колона - форма за унос
        form_frame = ttk.LabelFrame(main_frame, text="Подаци о нивоу такмичења", padding=10)
        form_frame.pack(side=LEFT, fill=BOTH, expand=NO, padx=(0, 10))
        
        # Поља форме
        ttk.Label(form_frame, text="Назив:").grid(row=0, column=0, sticky=W, pady=5)
        ttk.Entry(form_frame, textvariable=self.level_name_var, width=30).grid(row=0, column=1, sticky=W, pady=5)
        
        # Дугмад за акције
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Додај", command=self.add_level).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Измени", command=self.update_level).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Обриши", command=self.delete_level).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Очисти", command=self.clear_level_form).pack(side=LEFT, padx=5)
        
        # Десна колона - табела
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(side=RIGHT, fill=BOTH, expand=YES)
        
        # Табела нивоа такмичења
        self.level_tree = ttk.Treeview(table_frame, columns=("ID", "Назив"))
        self.level_tree.pack(fill=BOTH, expand=YES)
        
        # Подешавање заглавља колона
        self.level_tree.heading("#0", text="")
        self.level_tree.heading("ID", text="ИД")
        self.level_tree.heading("Назив", text="Назив нивоа")
        
        # Подешавање ширине колона
        self.level_tree.column("#0", width=0, stretch=NO)
        self.level_tree.column("ID", width=50, anchor=CENTER)
        self.level_tree.column("Назив", width=300)
        
        # Скролбар
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.level_tree.yview)
        self.level_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Везивање догађаја
        self.level_tree.bind('<<TreeviewSelect>>', self.on_level_select)
    
    #
    # Функције за такмичења
    #
    def load_competitions(self):
        """Учитавање свих такмичења из базе"""
        # Чишћење табеле
        for i in self.comp_tree.get_children():
            self.comp_tree.delete(i)
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT competition_id, competition_name 
                FROM Competitions
                ORDER BY competition_name
            """)
            
            for row in cursor.fetchall():
                competition_id, competition_name = row
                self.comp_tree.insert("", END, values=(competition_id, competition_name))
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању такмичења: {str(e)}")
    
    def search_competitions(self):
        """Претрага такмичења по називу"""
        search_term = self.search_query.get().strip()
        if not search_term:
            self.load_competitions()
            return
        
        # Чишћење табеле
        for i in self.comp_tree.get_children():
            self.comp_tree.delete(i)
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT competition_id, competition_name 
                FROM Competitions
                WHERE competition_name LIKE ?
                ORDER BY competition_name
            """, (f"%{search_term}%",))
            
            for row in cursor.fetchall():
                competition_id, competition_name = row
                self.comp_tree.insert("", END, values=(competition_id, competition_name))
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при претрази такмичења: {str(e)}")
    
    def add_competition(self):
        """Додавање новог такмичења у базу"""
        competition_name = self.competition_name_var.get().strip()
        if not competition_name:
            messagebox.showwarning("Упозорење", "Назив такмичења је обавезно поље.")
            return
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                INSERT INTO Competitions (competition_name)
                VALUES (?)
            """, (competition_name,))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Такмичење/предмет је успешно додат.")
            self.clear_competition_form()
            self.load_competitions()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при додавању такмичења: {str(e)}")
    
    def update_competition(self):
        """Ажурирање постојећег такмичења"""
        if not self.competition_id:
            messagebox.showwarning("Упозорење", "Молимо прво изаберите такмичење за измену.")
            return
            
        competition_name = self.competition_name_var.get().strip()
        if not competition_name:
            messagebox.showwarning("Упозорење", "Назив такмичења је обавезно поље.")
            return
            
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                UPDATE Competitions
                SET competition_name = ?
                WHERE competition_id = ?
            """, (competition_name, self.competition_id))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Такмичење је успешно ажурирано.")
            self.clear_competition_form()
            self.load_competitions()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при ажурирању такмичења: {str(e)}")
    
    def delete_competition(self):
        """Брисање такмичења из базе"""
        if not self.competition_id:
            messagebox.showwarning("Упозорење", "Молимо прво изаберите такмичење за брисање.")
            return
            
        # Провера да ли постоје успеси везани за ово такмичење
        cursor = self.app.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM StudentAchievements 
            WHERE competition_id = ?
        """, (self.competition_id,))
        
        if cursor.fetchone()[0] > 0:
            messagebox.showwarning(
                "Упозорење", 
                "Није могуће обрисати ово такмичење јер постоје евидентирани успеси ученика. "
                "Уклоните прво те успехе или измените назив такмичења."
            )
            return
        
        confirm = messagebox.askyesno("Потврда", "Да ли сте сигурни да желите да обришете ово такмичење?")
        if confirm:
            try:
                cursor.execute("DELETE FROM Competitions WHERE competition_id = ?", (self.competition_id,))
                self.app.conn.commit()
                messagebox.showinfo("Успех", "Такмичење је успешно обрисано.")
                self.clear_competition_form()
                self.load_competitions()
                
            except Exception as e:
                messagebox.showerror("Грешка", f"Грешка при брисању такмичења: {str(e)}")
    
    def on_competition_select(self, event):
        """Учитавање података изабраног такмичења у форму"""
        selected_items = self.comp_tree.selection()
        if not selected_items:
            return
            
        # Узимање ID-а изабраног такмичења
        values = self.comp_tree.item(selected_items[0], 'values')
        competition_id = values[0]
        
        # Учитавање података
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT competition_name FROM Competitions WHERE competition_id = ?", (competition_id,))
        competition = cursor.fetchone()
        
        if competition:
            self.competition_id = competition_id
            self.competition_name_var.set(competition[0])
    
    def clear_competition_form(self):
        """Брисање поља у форми такмичења"""
        self.competition_id = None
        self.competition_name_var.set("")
        # Скидање селекције из табеле
        for item in self.comp_tree.selection():
            self.comp_tree.selection_remove(item)
    
    #
    # Функције за нивое такмичења
    #
    def load_levels(self):
        """Учитавање свих нивоа такмичења из базе"""
        # Чишћење табеле
        for i in self.level_tree.get_children():
            self.level_tree.delete(i)
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT level_id, level_name 
                FROM CompetitionLevels
                ORDER BY level_id
            """)
            
            for row in cursor.fetchall():
                level_id, level_name = row
                self.level_tree.insert("", END, values=(level_id, level_name))
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању нивоа такмичења: {str(e)}")
    
    def add_level(self):
        """Додавање новог нивоа такмичења у базу"""
        level_name = self.level_name_var.get().strip()
        if not level_name:
            messagebox.showwarning("Упозорење", "Назив нивоа је обавезно поље.")
            return
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                INSERT INTO CompetitionLevels (level_name)
                VALUES (?)
            """, (level_name,))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Ниво такмичења је успешно додат.")
            self.clear_level_form()
            self.load_levels()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при додавању нивоа такмичења: {str(e)}")
    
    def update_level(self):
        """Ажурирање постојећег нивоа такмичења"""
        if not self.level_id:
            messagebox.showwarning("Упозорење", "Молимо прво изаберите ниво такмичења за измену.")
            return
            
        level_name = self.level_name_var.get().strip()
        if not level_name:
            messagebox.showwarning("Упозорење", "Назив нивоа је обавезно поље.")
            return
            
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                UPDATE CompetitionLevels
                SET level_name = ?
                WHERE level_id = ?
            """, (level_name, self.level_id))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Ниво такмичења је успешно ажуриран.")
            self.clear_level_form()
            self.load_levels()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при ажурирању нивоа такмичења: {str(e)}")
    
    def delete_level(self):
        """Брисање нивоа такмичења из базе"""
        if not self.level_id:
            messagebox.showwarning("Упозорење", "Молимо прво изаберите ниво такмичења за брисање.")
            return
            
        # Провера да ли постоје успеси везани за овај ниво
        cursor = self.app.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM StudentAchievements 
            WHERE level_id = ?
        """, (self.level_id,))
        
        if cursor.fetchone()[0] > 0:
            messagebox.showwarning(
                "Упозорење", 
                "Није могуће обрисати овај ниво такмичења јер постоје евидентирани успеси ученика. "
                "Уклоните прво те успехе или измените назив нивоа."
            )
            return
            
        # Провера да ли постоје правила бодовања везана за овај ниво
        cursor.execute("""
            SELECT COUNT(*) FROM ScoringRules 
            WHERE level_id = ?
        """, (self.level_id,))
        
        if cursor.fetchone()[0] > 0:
            messagebox.showwarning(
                "Упозорење", 
                "Није могуће обрисати овај ниво такмичења јер постоје правила бодовања. "
                "Уклоните прво та правила."
            )
            return
        
        confirm = messagebox.askyesno("Потврда", "Да ли сте сигурни да желите да обришете овај ниво такмичења?")
        if confirm:
            try:
                cursor.execute("DELETE FROM CompetitionLevels WHERE level_id = ?", (self.level_id,))
                self.app.conn.commit()
                messagebox.showinfo("Успех", "Ниво такмичења је успешно обрисан.")
                self.clear_level_form()
                self.load_levels()
                
            except Exception as e:
                messagebox.showerror("Грешка", f"Грешка при брисању нивоа такмичења: {str(e)}")
    
    def on_level_select(self, event):
        """Учитавање података изабраног нивоа такмичења у форму"""
        selected_items = self.level_tree.selection()
        if not selected_items:
            return
            
        # Узимање ID-а изабраног нивоа такмичења
        values = self.level_tree.item(selected_items[0], 'values')
        level_id = values[0]
        
        # Учитавање података
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT level_name FROM CompetitionLevels WHERE level_id = ?", (level_id,))
        level = cursor.fetchone()
        
        if level:
            self.level_id = level_id
            self.level_name_var.set(level[0])
    
    def clear_level_form(self):
        """Брисање поља у форми нивоа такмичења"""
        self.level_id = None
        self.level_name_var.set("")
        # Скидање селекције из табеле
        for item in self.level_tree.selection():
            self.level_tree.selection_remove(item)
