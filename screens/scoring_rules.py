# -*- encoding: utf-8 -*-
# @Аутор      : minciv
# @e-mail     : minciv@protonmail.com
# @Web        : https://github.com/minciv
# @Фајл       : scoring_rules.py
# @Верзија    : 0.1.05.
# @Програм    : Windsurf
# @Опис       : Правила бодовања за ђака генерације
# @Датум      : 01.07.2025.

from tkinter import ttk, messagebox, StringVar, DoubleVar
from tkinter.constants import *

class ScoringRulesFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        
        # Проверавамо да ли је корисник администратор
        if not self.app.current_user or self.app.current_user["role"] != "administrator":
            self.show_access_denied()
            return
        
        # Иницијализација променљивих
        self.rule_id = None
        self.level_var = StringVar()
        self.placement_var = StringVar()
        self.points_var = DoubleVar()
        
        # Речници за мапирање
        self.levels_dict = {}
        
        # Креирање UI компоненти
        self.setup_ui()
        
        # Учитавање листе нивоа такмичења
        self.load_levels_list()
        
        # Учитавање постојећих правила
        self.load_rules()
    
    def show_access_denied(self):
        """Приказ поруке о одбијеном приступу"""
        access_denied = ttk.Label(
            self, 
            text="Приступ овом модулу имају само администратори.",
            font=('Helvetica', 14, 'bold'),
            foreground="red"
        )
        access_denied.pack(pady=50)
    
    def setup_ui(self):
        """Креирање корисничког интерфејса"""
        # Главни контејнер
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Горњи део - форма за унос правила
        form_frame = ttk.LabelFrame(main_frame, text="Дефинисање правила бодовања", padding=10)
        form_frame.pack(fill=X, expand=NO, pady=(0, 10))
        
        # Поља форме
        ttk.Label(form_frame, text="Ниво такмичења:").grid(row=0, column=0, sticky=W, pady=5, padx=5)
        self.level_cb = ttk.Combobox(form_frame, textvariable=self.level_var, width=30)
        self.level_cb.grid(row=0, column=1, sticky=W, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Пласман:").grid(row=1, column=0, sticky=W, pady=5, padx=5)
        placements = ["1. место", "2. место", "3. место", "Похвала", "Учешће"]
        self.placement_cb = ttk.Combobox(form_frame, textvariable=self.placement_var, values=placements, width=30)
        self.placement_cb.grid(row=1, column=1, sticky=W, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Број бодова:").grid(row=2, column=0, sticky=W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.points_var, width=10).grid(row=2, column=1, sticky=W, pady=5, padx=5)
        
        # Дугмад за акције
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Додај", command=self.add_rule).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Измени", command=self.update_rule).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Обриши", command=self.delete_rule).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Очисти", command=self.clear_form).pack(side=LEFT, padx=5)
        
        # Информациона порука о бодовању
        ttk.Label(
            form_frame, 
            text="Напомена: Правила бодовања се користе за рачунање бодова за ђака генерације.",
            font=('Helvetica', 9, 'italic')
        ).grid(row=4, column=0, columnspan=2, sticky=W, pady=(10, 0))
        
        # Доњи део - табела са правилима
        table_frame = ttk.LabelFrame(main_frame, text="Постојећа правила", padding=10)
        table_frame.pack(fill=BOTH, expand=YES)
        
        # Табела правила
        columns = ("ID", "Ниво такмичења", "Пласман", "Број бодова")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.pack(fill=BOTH, expand=YES)
        
        # Подешавање заглавља колона
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=50, anchor=CENTER)
            elif col == "Број бодова":
                self.tree.column(col, width=100, anchor=CENTER)
            else:
                self.tree.column(col, width=200)
        
        # Скролбар
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Везивање догађаја
        self.tree.bind('<<TreeviewSelect>>', self.on_rule_select)
    
    def load_levels_list(self):
        """Учитавање листе нивоа такмичења"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT level_id, level_name 
                FROM CompetitionLevels
                ORDER BY level_id
            """)
            
            levels = []
            for row in cursor.fetchall():
                level_id, level_name = row
                levels.append(level_name)
                self.levels_dict[level_name] = level_id
            
            self.level_cb['values'] = levels
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању нивоа такмичења: {str(e)}")
    
    def load_rules(self):
        """Учитавање постојећих правила бодовања"""
        # Чишћење табеле
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT r.rule_id, l.level_name, r.placement_description, r.points
                FROM ScoringRules r
                JOIN CompetitionLevels l ON r.level_id = l.level_id
                ORDER BY l.level_id, r.placement_description
            """)
            
            for row in cursor.fetchall():
                rule_id, level_name, placement, points = row
                self.tree.insert("", END, values=(rule_id, level_name, placement, points))
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању правила бодовања: {str(e)}")
    
    def add_rule(self):
        """Додавање новог правила бодовања"""
        if not self._validate_form():
            return
        
        level_name = self.level_var.get()
        level_id = self.levels_dict.get(level_name)
        placement = self.placement_var.get()
        points = self.points_var.get()
        
        try:
            cursor = self.app.conn.cursor()
            
            # Проверавамо да ли већ постоји правило за овај ниво и пласман
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ScoringRules 
                WHERE level_id = ? AND placement_description = ?
            """, (level_id, placement))
            
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Упозорење", 
                    f"Већ постоји правило за ниво '{level_name}' и пласман '{placement}'."
                )
                return
            
            # Додајемо ново правило
            cursor.execute("""
                INSERT INTO ScoringRules (level_id, placement_description, points)
                VALUES (?, ?, ?)
            """, (level_id, placement, points))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Правило бодовања је успешно додато.")
            self.clear_form()
            self.load_rules()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при додавању правила: {str(e)}")
    
    def update_rule(self):
        """Ажурирање постојећег правила бодовања"""
        if not self.rule_id:
            messagebox.showwarning("Упозорење", "Молимо прво изаберите правило за измену.")
            return
            
        if not self._validate_form():
            return
        
        level_name = self.level_var.get()
        level_id = self.levels_dict.get(level_name)
        placement = self.placement_var.get()
        points = self.points_var.get()
        
        try:
            cursor = self.app.conn.cursor()
            
            # Проверавамо да ли већ постоји друго правило за овај ниво и пласман
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ScoringRules 
                WHERE level_id = ? AND placement_description = ? AND rule_id != ?
            """, (level_id, placement, self.rule_id))
            
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Упозорење", 
                    f"Већ постоји правило за ниво '{level_name}' и пласман '{placement}'."
                )
                return
            
            # Ажурирамо правило
            cursor.execute("""
                UPDATE ScoringRules
                SET level_id = ?, placement_description = ?, points = ?
                WHERE rule_id = ?
            """, (level_id, placement, points, self.rule_id))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Правило бодовања је успешно ажурирано.")
            self.clear_form()
            self.load_rules()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при ажурирању правила: {str(e)}")
    
    def delete_rule(self):
        """Брисање правила бодовања"""
        if not self.rule_id:
            messagebox.showwarning("Упозорење", "Молимо прво изаберите правило за брисање.")
            return
        
        confirm = messagebox.askyesno("Потврда", "Да ли сте сигурни да желите да обришете ово правило?")
        if confirm:
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("DELETE FROM ScoringRules WHERE rule_id = ?", (self.rule_id,))
                self.app.conn.commit()
                
                messagebox.showinfo("Успех", "Правило бодовања је успешно обрисано.")
                self.clear_form()
                self.load_rules()
                
            except Exception as e:
                messagebox.showerror("Грешка", f"Грешка при брисању правила: {str(e)}")
    
    def on_rule_select(self, event):
        """Учитавање података изабраног правила у форму"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        # Узимање ID-а изабраног правила
        values = self.tree.item(selected_items[0], 'values')
        rule_id = values[0]
        
        # Учитавање података
        cursor = self.app.conn.cursor()
        cursor.execute("""
            SELECT r.level_id, l.level_name, r.placement_description, r.points
            FROM ScoringRules r
            JOIN CompetitionLevels l ON r.level_id = l.level_id
            WHERE r.rule_id = ?
        """, (rule_id,))
        
        rule = cursor.fetchone()
        
        if rule:
            _, level_name, placement, points = rule
            self.rule_id = rule_id
            self.level_var.set(level_name)
            self.placement_var.set(placement)
            self.points_var.set(points)
    
    def clear_form(self):
        """Брисање поља у форми"""
        self.rule_id = None
        self.level_var.set("")
        self.placement_var.set("")
        self.points_var.set(0.0)
        # Скидање селекције из табеле
        for item in self.tree.selection():
            self.tree.selection_remove(item)
    
    def _validate_form(self):
        """Валидација унетих података у форми"""
        level_name = self.level_var.get()
        if not level_name or level_name not in self.levels_dict:
            messagebox.showwarning("Упозорење", "Молимо изаберите валидан ниво такмичења.")
            return False
        
        placement = self.placement_var.get()
        if not placement:
            messagebox.showwarning("Упозорење", "Молимо изаберите пласман.")
            return False
        
        try:
            points = float(self.points_var.get())
            if points < 0:
                messagebox.showwarning("Упозорење", "Број бодова мора бити позитиван број.")
                return False
        except:
            messagebox.showwarning("Упозорење", "Број бодова мора бити валидан број.")
            return False
            
        return True
