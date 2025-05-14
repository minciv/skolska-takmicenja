# -*- encoding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : achievements_frame.py
# @Верзија  : 0.1.01.
# @Програм  : Windsurf
# @Опис     : Екран за евиденцију успеха ученика на такмичењима
# @Датум   : 14.05.2025.

from tkinter import ttk, messagebox, StringVar, IntVar
from tkinter.constants import *
import pandas as pd
from datetime import datetime

class AchievementsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        
        # Иницијализација променљивих за форму
        self.achievement_id = None
        self.student_var = StringVar()
        self.competition_var = StringVar()
        self.level_var = StringVar()
        self.school_year_var = StringVar()
        self.placement_var = StringVar()
        self.mentor_var = StringVar()
        self.notes_var = StringVar()
        
        # Речници за мапирање ID-ева и назива
        self.students_dict = {}
        self.competitions_dict = {}
        self.levels_dict = {}
        self.mentors_dict = {}
        
        # Променљиве за филтрирање
        self.filter_student_var = StringVar()
        self.filter_competition_var = StringVar()
        self.filter_school_year_var = StringVar()
        
        # Креирање UI компоненти
        self.setup_ui()
        
        # Учитавање листи 
        self.load_students_list()
        self.load_competitions_list()
        self.load_levels_list()
        self.load_school_years_list()
        self.load_mentors_list()
        
        # Приказивање података
        self.load_achievements()
    
    def setup_ui(self):
        """Креирање корисничког интерфејса"""
        # Главни контејнер са две колоне (форма и табела)
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Лева колона - форма за унос
        form_frame = ttk.LabelFrame(main_frame, text="Подаци о успеху ученика", padding=10)
        form_frame.pack(side=LEFT, fill=BOTH, expand=NO, padx=(0, 10))
        
        # Поља форме
        ttk.Label(form_frame, text="Ученик:").grid(row=0, column=0, sticky=W, pady=5)
        self.student_cb = ttk.Combobox(form_frame, textvariable=self.student_var, width=30)
        self.student_cb.grid(row=0, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Такмичење/Предмет:").grid(row=1, column=0, sticky=W, pady=5)
        self.competition_cb = ttk.Combobox(form_frame, textvariable=self.competition_var, width=30)
        self.competition_cb.grid(row=1, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Ниво такмичења:").grid(row=2, column=0, sticky=W, pady=5)
        self.level_cb = ttk.Combobox(form_frame, textvariable=self.level_var, width=30)
        self.level_cb.grid(row=2, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Школска година:").grid(row=3, column=0, sticky=W, pady=5)
        self.school_year_cb = ttk.Combobox(form_frame, textvariable=self.school_year_var, width=30)
        self.school_year_cb.grid(row=3, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Пласман:").grid(row=4, column=0, sticky=W, pady=5)
        placement_values = ["1. место", "2. место", "3. место", "Похвала", "Учешће"]
        self.placement_cb = ttk.Combobox(form_frame, textvariable=self.placement_var, values=placement_values, width=30)
        self.placement_cb.grid(row=4, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Ментор:").grid(row=5, column=0, sticky=W, pady=5)
        self.mentor_cb = ttk.Combobox(form_frame, textvariable=self.mentor_var, width=30)
        self.mentor_cb.grid(row=5, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Напомена:").grid(row=6, column=0, sticky=NW, pady=5)
        ttk.Entry(form_frame, textvariable=self.notes_var, width=30).grid(row=6, column=1, sticky=W, pady=5)
        
        # Дугмад за акције
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Додај", command=self.add_achievement).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Измени", command=self.update_achievement).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Обриши", command=self.delete_achievement).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Очисти", command=self.clear_form).pack(side=LEFT, padx=5)
        
        # Додајемо филтере испод форме за унос
        filter_frame = ttk.LabelFrame(form_frame, text="Филтери", padding=5)
        filter_frame.grid(row=8, column=0, columnspan=2, sticky=EW, pady=10, padx=5)
        
        # Филтер по ученику
        ttk.Label(filter_frame, text="Ученик:").grid(row=0, column=0, padx=5, pady=2, sticky=W)
        self.filter_student_cb = ttk.Combobox(filter_frame, textvariable=self.filter_student_var, width=30)
        self.filter_student_cb.grid(row=0, column=1, padx=5, pady=2, sticky=W)
        
        # Филтер по такмичењу
        ttk.Label(filter_frame, text="Такмичење:").grid(row=1, column=0, padx=5, pady=2, sticky=W)
        self.filter_competition_cb = ttk.Combobox(filter_frame, textvariable=self.filter_competition_var, width=30)
        self.filter_competition_cb.grid(row=1, column=1, padx=5, pady=2, sticky=W)
        
        # Филтер по школској години
        ttk.Label(filter_frame, text="Школска година:").grid(row=2, column=0, padx=5, pady=2, sticky=W)
        self.filter_school_year_cb = ttk.Combobox(filter_frame, textvariable=self.filter_school_year_var, width=30)
        self.filter_school_year_cb.grid(row=2, column=1, padx=5, pady=2, sticky=W)
        
        # Дугмад за филтрирање
        button_filter_frame = ttk.Frame(filter_frame)
        button_filter_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=W)
        
        ttk.Button(button_filter_frame, text="Филтрирај", command=self.apply_filters).pack(side=LEFT, padx=5)
        ttk.Button(button_filter_frame, text="Поништи филтере", command=self.clear_filters).pack(side=LEFT, padx=5)
        ttk.Button(button_filter_frame, text="Извоз у Excel", command=self.export_to_excel).pack(side=LEFT, padx=5)
        
        # Десна колона - табела
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(side=RIGHT, fill=BOTH, expand=YES)
        
        # Табела успеха
        columns = ("ID", "Ученик", "Такмичење", "Ниво", "Школска година", "Пласман", "Ментор", "Датум уноса")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.pack(fill=BOTH, expand=YES)
        
        # Подешавање заглавља колона
        for col in columns:
            self.tree.heading(col, text=col)
            if col in ["ID"]:
                self.tree.column(col, width=50, anchor=CENTER)
            elif col == "Датум уноса":
                self.tree.column(col, width=120, anchor=CENTER)
            else:
                self.tree.column(col, width=120)
        
        # Скролбар
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Везивање догађаја
        self.tree.bind('<<TreeviewSelect>>', self.on_achievement_select)
    
    def load_students_list(self):
        """Учитавање листе ученика за combobox"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT student_id, first_name, last_name 
                FROM Students
                WHERE active = 1
                ORDER BY last_name, first_name
            """)
            
            students = []
            for row in cursor.fetchall():
                student_id, first_name, last_name = row
                full_name = f"{first_name} {last_name}"
                students.append(full_name)
                self.students_dict[full_name] = student_id
            
            self.student_cb['values'] = students
            self.filter_student_cb['values'] = [""] + students  # Додајемо празну опцију за филтер
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању ученика: {str(e)}")
    
    def load_competitions_list(self):
        """Учитавање листе такмичења за combobox"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT competition_id, competition_name 
                FROM Competitions
                ORDER BY competition_name
            """)
            
            competitions = []
            for row in cursor.fetchall():
                competition_id, competition_name = row
                competitions.append(competition_name)
                self.competitions_dict[competition_name] = competition_id
            
            self.competition_cb['values'] = competitions
            self.filter_competition_cb['values'] = [""] + competitions  # Додајемо празну опцију за филтер
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању такмичења: {str(e)}")
    
    def load_levels_list(self):
        """Учитавање листе нивоа такмичења за combobox"""
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
    
    def load_school_years_list(self):
        """Учитавање листе школских година или генерисање последње 4"""
        # Проверавамо да ли постоје уноси у бази
        current_year = datetime.now().year
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT DISTINCT school_year 
                FROM StudentAchievements
                ORDER BY school_year DESC
            """)
            
            years = cursor.fetchall()
            
            if years:
                school_years = [year[0] for year in years]
            else:
                # Ако нема уноса, генеришемо последње 4 школске године
                school_years = [
                    f"{current_year-i-1}/{current_year-i}" 
                    for i in range(4)
                ]
            
            self.school_year_cb['values'] = school_years
            self.filter_school_year_cb['values'] = [""] + school_years  # Додајемо празну опцију за филтер
            
            # Постављамо тренутну школску годину као подразумевану
            current_school_year = f"{current_year-1}/{current_year}"
            if current_school_year in school_years:
                self.school_year_var.set(current_school_year)
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању школских година: {str(e)}")
    
    def load_achievements(self, where_clause="", params=()):
        """Учитавање успеха ученика из базе са опционим филтером"""
        # Чишћење табеле
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        try:
            cursor = self.app.conn.cursor()
            
            query = """
                SELECT a.achievement_id, 
                       s.first_name || ' ' || s.last_name, 
                       c.competition_name, 
                       l.level_name, 
                       a.school_year, 
                       a.placement, 
                       a.mentor_name, 
                       a.entry_date
                FROM StudentAchievements a
                JOIN Students s ON a.student_id = s.student_id
                JOIN Competitions c ON a.competition_id = c.competition_id
                JOIN CompetitionLevels l ON a.level_id = l.level_id
            """
            
            if where_clause:
                query += " WHERE " + where_clause
                
            query += " ORDER BY a.entry_date DESC"
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                self.tree.insert("", END, values=row)
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању успеха: {str(e)}")
    
    def apply_filters(self):
        """Примена филтера на приказ успеха"""
        filters = []
        params = []
        
        # Филтер по ученику
        if self.filter_student_var.get():
            student_id = self.students_dict.get(self.filter_student_var.get())
            if student_id:
                filters.append("a.student_id = ?")
                params.append(student_id)
        
        # Филтер по такмичењу
        if self.filter_competition_var.get():
            competition_id = self.competitions_dict.get(self.filter_competition_var.get())
            if competition_id:
                filters.append("a.competition_id = ?")
                params.append(competition_id)
        
        # Филтер по школској години
        if self.filter_school_year_var.get():
            filters.append("a.school_year = ?")
            params.append(self.filter_school_year_var.get())
        
        # Конструисање WHERE клаузуле
        where_clause = " AND ".join(filters) if filters else ""
        
        # Учитавање филтрираних података
        self.load_achievements(where_clause, tuple(params))
    
    def clear_filters(self):
        """Поништавање свих филтера"""
        self.filter_student_var.set("")
        self.filter_competition_var.set("")
        self.filter_school_year_var.set("")
        self.load_achievements()
    
    def add_achievement(self):
        """Додавање новог успеха ученика у базу"""
        if not self._validate_form():
            return
        
        try:
            # Добијање ID вредности из речника
            student_id = self.students_dict.get(self.student_var.get())
            competition_id = self.competitions_dict.get(self.competition_var.get())
            level_id = self.levels_dict.get(self.level_var.get())
            
            cursor = self.app.conn.cursor()
            cursor.execute("""
                INSERT INTO StudentAchievements (
                    student_id, competition_id, level_id, school_year, 
                    placement, mentor_name, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                competition_id,
                level_id,
                self.school_year_var.get(),
                self.placement_var.get(),
                self.mentor_var.get(),
                self.notes_var.get()
            ))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Успех ученика је успешно додат.")
            self.clear_form()
            self.load_achievements()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при додавању успеха: {str(e)}")
    
    def update_achievement(self):
        """Ажурирање постојећег успеха ученика"""
        if not self.achievement_id:
            messagebox.showwarning("Упозорење", "Молимо прво изаберите успех за измену.")
            return
            
        if not self._validate_form():
            return
            
        try:
            # Добијање ID вредности из речника
            student_id = self.students_dict.get(self.student_var.get())
            competition_id = self.competitions_dict.get(self.competition_var.get())
            level_id = self.levels_dict.get(self.level_var.get())
            
            cursor = self.app.conn.cursor()
            cursor.execute("""
                UPDATE StudentAchievements
                SET student_id = ?, competition_id = ?, level_id = ?, 
                    school_year = ?, placement = ?, 
                    mentor_name = ?, notes = ?
                WHERE achievement_id = ?
            """, (
                student_id,
                competition_id,
                level_id,
                self.school_year_var.get(),
                self.placement_var.get(),
                self.mentor_var.get(),
                self.notes_var.get(),
                self.achievement_id
            ))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Успех ученика је успешно ажуриран.")
            self.clear_form()
            self.load_achievements()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при ажурирању успеха: {str(e)}")
    
    def delete_achievement(self):
        """Брисање успеха ученика из базе"""
        if not self.achievement_id:
            messagebox.showwarning("Упозорење", "Молимо прво изаберите успех за брисање.")
            return
        
        confirm = messagebox.askyesno("Потврда", "Да ли сте сигурни да желите да обришете овај успех?")
        if confirm:
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("DELETE FROM StudentAchievements WHERE achievement_id = ?", (self.achievement_id,))
                self.app.conn.commit()
                messagebox.showinfo("Успех", "Успех ученика је успешно обрисан.")
                self.clear_form()
                self.load_achievements()
                
            except Exception as e:
                messagebox.showerror("Грешка", f"Грешка при брисању успеха: {str(e)}")
    
    def on_achievement_select(self, event):
        """Учитавање података изабраног успеха у форму"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        # Узимање ID-а изабраног успеха
        values = self.tree.item(selected_items[0], 'values')
        achievement_id = values[0]
        
        # Учитавање комплетних података из базе
        cursor = self.app.conn.cursor()
        cursor.execute("""
            SELECT a.student_id, a.competition_id, a.level_id, a.school_year, 
                   a.placement, a.mentor_name, a.notes,
                   s.first_name || ' ' || s.last_name as student_name,
                   c.competition_name, l.level_name
            FROM StudentAchievements a
            JOIN Students s ON a.student_id = s.student_id
            JOIN Competitions c ON a.competition_id = c.competition_id
            JOIN CompetitionLevels l ON a.level_id = l.level_id
            WHERE a.achievement_id = ?
        """, (achievement_id,))
        
        achievement = cursor.fetchone()
        
        if achievement:
            self.achievement_id = achievement_id
            self.student_var.set(achievement[7])
            self.competition_var.set(achievement[8])
            self.level_var.set(achievement[9])
            self.school_year_var.set(achievement[3])
            self.placement_var.set(achievement[4])
            self.mentor_var.set(achievement[5] if achievement[5] else "")
            self.notes_var.set(achievement[6] if achievement[6] else "")
    
    def clear_form(self):
        """Брисање поља у форми"""
        self.achievement_id = None
        self.student_var.set("")
        self.competition_var.set("")
        self.level_var.set("")
        # Не чистимо школску годину - корисно је да остане селектована
        # self.school_year_var.set("")
        self.placement_var.set("")
        self.mentor_var.set("")
        self.notes_var.set("")
        # Скидање селекције из табеле
        for item in self.tree.selection():
            self.tree.selection_remove(item)
    
    def _validate_form(self):
        """Валидација унетих података у форми"""
        # Провера да ли су сва обавезна поља попуњена
        if not self.student_var.get():
            messagebox.showwarning("Упозорење", "Молимо изаберите ученика.")
            return False
            
        if not self.competition_var.get():
            messagebox.showwarning("Упозорење", "Молимо изаберите такмичење/предмет.")
            return False
            
        if not self.level_var.get():
            messagebox.showwarning("Упозорење", "Молимо изаберите ниво такмичења.")
            return False
            
        if not self.school_year_var.get():
            messagebox.showwarning("Упозорење", "Молимо унесите школску годину.")
            return False
            
        if not self.placement_var.get():
            messagebox.showwarning("Упозорење", "Молимо унесите пласман.")
            return False
        
        # Провера да ли постоје ID-еви у речницима
        if self.student_var.get() not in self.students_dict:
            messagebox.showwarning("Упозорење", "Изабрани ученик не постоји у бази.")
            return False
            
        if self.competition_var.get() not in self.competitions_dict:
            messagebox.showwarning("Упозорење", "Изабрано такмичење не постоји у бази.")
            return False
            
        if self.level_var.get() not in self.levels_dict:
            messagebox.showwarning("Упозорење", "Изабрани ниво такмичења не постоји у бази.")
            return False
            
        return True

    def load_mentors_list(self):
        """Учитавање листе ментора из постојећих уноса"""
        try:
            cursor = self.app.conn.cursor()
            
            # Учитавање уникатних ментора из базе
            cursor.execute("""
                SELECT DISTINCT mentor_name 
                FROM StudentAchievements 
                WHERE mentor_name IS NOT NULL AND mentor_name != '' 
                ORDER BY mentor_name
            """)
            
            # Припрема листе ментора
            mentors = [row[0] for row in cursor.fetchall()]
            self.mentors_list = mentors
            
            # Постављање вредности у combobox
            self.mentor_cb['values'] = mentors
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању ментора: {str(e)}")
    
    def export_to_excel(self):
        """Извоз података о успесима у Excel фајл"""
        try:
            # Припрема упита - користимо исте филтере као у табели
            filters = []
            params = []
            
            if self.filter_student_var.get():
                student_id = self.students_dict.get(self.filter_student_var.get())
                if student_id:
                    filters.append("a.student_id = ?")
                    params.append(student_id)
            
            if self.filter_competition_var.get():
                competition_id = self.competitions_dict.get(self.filter_competition_var.get())
                if competition_id:
                    filters.append("a.competition_id = ?")
                    params.append(competition_id)
            
            if self.filter_school_year_var.get():
                filters.append("a.school_year = ?")
                params.append(self.filter_school_year_var.get())
            
            where_clause = " AND ".join(filters) if filters else ""
            
            # Извршавање упита
            cursor = self.app.conn.cursor()
            
            query = """
                SELECT 
                    s.first_name || ' ' || s.last_name as Ученик, 
                    c.competition_name as Такмичење, 
                    l.level_name as Ниво, 
                    a.school_year as 'Школска година', 
                    a.placement as Пласман, 
                    a.mentor_name as Ментор, 
                    a.notes as Напомена,
                    a.entry_date as 'Датум уноса'
                FROM StudentAchievements a
                JOIN Students s ON a.student_id = s.student_id
                JOIN Competitions c ON a.competition_id = c.competition_id
                JOIN CompetitionLevels l ON a.level_id = l.level_id
            """
            
            if where_clause:
                query += " WHERE " + where_clause
                
            query += " ORDER BY s.last_name, s.first_name, a.school_year DESC"
            
            cursor.execute(query, params)
            
            # Конверзија у pandas DataFrame
            df = pd.DataFrame(cursor.fetchall(), 
                           columns=['Ученик', 'Такмичење', 'Ниво', 'Школска година', 
                                   'Пласман', 'Ментор', 'Напомена', 'Датум уноса'])
            
            # Отварање дијалога за чување
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel фајлови", "*.xlsx")],
                title="Сачувај извештај о успесима"
            )
            
            if filename:
                df.to_excel(filename, index=False)
                messagebox.showinfo("Успех", f"Подаци су извезени у фајл {filename}")
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при извозу података: {str(e)}")
