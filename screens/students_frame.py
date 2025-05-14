# -*- encoding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : students_frame.py
# @Верзија  : 0.1.01.
# @Програм  : Windsurf
# @Опис     : Екран за управљање ученицима
# @Датум   : 14.05.2025.

from tkinter import ttk, messagebox, StringVar, IntVar
from tkinter.constants import *
import pandas as pd
from datetime import datetime

class StudentsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        
        # Иницијализација променљивих за форму
        self.student_id = None
        self.first_name_var = StringVar()
        self.middle_name_var = StringVar()  # Додајемо променљиву за средње име
        self.last_name_var = StringVar()
        self.class_enrolled_var = StringVar()
        self.active_var = StringVar(value="1")
        # Користимо подразумевани разред при иницијализацији
        self.grade_var = IntVar(value=self.calculate_current_grade())
        self.school_year_var = StringVar(value=self.get_current_school_year())
        
        # Променљиве за претрагу
        self.search_query = StringVar()
        
        # Речници за мапирање такмичења и нивоа
        self.competitions_dict = {}
        self.levels_dict = {}
        
        # Креирање UI компоненти
        self.setup_ui()
        
        # Учитавање листи такмичења и нивоа
        self.load_competitions_list()
        self.load_levels_list()
        self.load_school_years_list()
        
        # Приказивање података
        self.load_students()
    
    def setup_ui(self):
        """Креирање корисничког интерфејса"""
        # Главни контејнер са две колоне (форма и табела)
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Лева колона - форма за унос
        form_frame = ttk.LabelFrame(main_frame, text="Подаци о ученику", padding=10)
        form_frame.pack(side=LEFT, fill=BOTH, expand=NO, padx=(0, 10))
        
        # Поља форме
        ttk.Label(form_frame, text="Име:").grid(row=0, column=0, sticky=W, pady=5)
        ttk.Entry(form_frame, textvariable=self.first_name_var, width=30).grid(row=0, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Средње име:").grid(row=1, column=0, sticky=W, pady=5)
        ttk.Entry(form_frame, textvariable=self.middle_name_var, width=30).grid(row=1, column=1, sticky=W, pady=5)
        ttk.Label(form_frame, text="(Ако постоје са истим именом и презименом)", font=('Helvetica', 8, 'italic')).grid(row=2, column=1, sticky=W, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Презиме:").grid(row=3, column=0, sticky=W, pady=5)
        ttk.Entry(form_frame, textvariable=self.last_name_var, width=30).grid(row=3, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Одељење:").grid(row=4, column=0, sticky=W, pady=5)
        ttk.Entry(form_frame, textvariable=self.class_enrolled_var, width=30).grid(row=4, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Разред:").grid(row=5, column=0, sticky=W, pady=5)
        grade_frame = ttk.Frame(form_frame)
        grade_frame.grid(row=5, column=1, sticky=W, pady=5)
        for i in range(1, 9):
            ttk.Radiobutton(grade_frame, text=str(i), variable=self.grade_var, value=i).grid(row=0, column=i-1, padx=2)
        
        ttk.Label(form_frame, text="Школска година:").grid(row=6, column=0, sticky=W, pady=5)
        self.school_year_cb = ttk.Combobox(form_frame, textvariable=self.school_year_var, width=30)
        self.school_year_cb.grid(row=6, column=1, sticky=W, pady=5)
        
        ttk.Label(form_frame, text="Активан:").grid(row=7, column=0, sticky=W, pady=5)
        active_frame = ttk.Frame(form_frame)
        active_frame.grid(row=7, column=1, sticky=W, pady=5)
        ttk.Radiobutton(active_frame, text="Да", variable=self.active_var, value="1").pack(side=LEFT)
        ttk.Radiobutton(active_frame, text="Не", variable=self.active_var, value="0").pack(side=LEFT)
        
        # Дугмад за акције
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Додај", command=self.add_student).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Ажурирај", command=self.update_student).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Обриши", command=self.delete_student).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Очисти", command=self.clear_form).pack(side=LEFT, padx=5)
        
        # Десна колона - листа ученика и претрага
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Претрага
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Претрага:").pack(side=LEFT, padx=5)
        ttk.Entry(search_frame, textvariable=self.search_query, width=30).pack(side=LEFT, padx=5)
        ttk.Button(search_frame, text="Тражи", command=self.search_students).pack(side=LEFT, padx=5)
        ttk.Button(search_frame, text="Прикажи све", command=self.load_students).pack(side=LEFT, padx=5)
        ttk.Button(search_frame, text="Извоз у Excel", command=self.export_to_excel).pack(side=LEFT, padx=5)
        
        # Табела ученика
        table_frame = ttk.Frame(right_frame)
        table_frame.pack(fill=BOTH, expand=YES)
        
        # Креирање Treeview компоненте
        self.students_table = ttk.Treeview(table_frame, 
                                     columns=('id', 'first_name', 'last_name', 'class', 'grade', 'school_year', 'active'),
                                     show='headings')
        
        # Постављање заглавља
        self.students_table.heading('id', text='ИД')
        self.students_table.heading('first_name', text='Име')
        self.students_table.heading('last_name', text='Презиме')
        self.students_table.heading('class', text='Одељење')
        self.students_table.heading('grade', text='Разред')
        self.students_table.heading('school_year', text='Школска година')
        self.students_table.heading('active', text='Активан')
        
        # Постављање ширине колона
        self.students_table.column('id', width=50, minwidth=50)
        self.students_table.column('first_name', width=150, minwidth=100)
        self.students_table.column('last_name', width=150, minwidth=100)
        self.students_table.column('class', width=100, minwidth=80)
        self.students_table.column('grade', width=80, minwidth=60)
        self.students_table.column('school_year', width=120, minwidth=100)
        self.students_table.column('active', width=80, minwidth=60)
        
        # Додавање scrollbar-а
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.students_table.yview)
        self.students_table.configure(yscrollcommand=scrollbar.set)
        
        # Паковање компоненти
        self.students_table.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Повезивање догађаја селекције
        self.students_table.bind('<<TreeviewSelect>>', self.on_student_select)
    
    def load_students(self):
        """Учитавање свих ученика из базе"""
        # Брисање претходних ставки из табеле
        for i in self.students_table.get_children():
            self.students_table.delete(i)
            
        try:
            # Извршавање упита
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT student_id, first_name, last_name, class_enrolled, grade, school_year,
                       CASE WHEN active = 1 THEN 'Да' ELSE 'Не' END as active
                FROM Students
                ORDER BY last_name, first_name
            """)
            
            # Додавање редова у табелу
            for row in cursor.fetchall():
                self.students_table.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању ученика: {str(e)}")
    
    def search_students(self):
        """Претрага ученика по имену или презимену"""
        # Добијање текста за претрагу
        search_text = self.search_query.get().strip()
        if not search_text:
            self.load_students()
            return
            
        # Брисање претходних ставки из табеле
        for i in self.students_table.get_children():
            self.students_table.delete(i)
            
        try:
            # Извршавање упита
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT student_id, first_name, last_name, class_enrolled, grade, school_year, 
                       CASE WHEN active = 1 THEN 'Да' ELSE 'Не' END as active
                FROM Students 
                WHERE first_name LIKE ? OR last_name LIKE ?
                ORDER BY last_name, first_name
            """, (f'%{search_text}%', f'%{search_text}%'))
            
            # Додавање редова у табелу
            for row in cursor.fetchall():
                self.students_table.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при претрази ученика: {str(e)}")
    
    def add_student(self):
        """Додавање новог ученика у базу"""
        # Валидација података
        if not self._validate_form():
            return
            
        try:
            # Извршавање упита
            cursor = self.app.conn.cursor()
            cursor.execute("""
                INSERT INTO Students (first_name, last_name, class_enrolled, grade, school_year, active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.first_name_var.get().strip(),
                self.last_name_var.get().strip(),
                self.class_enrolled_var.get().strip(),
                self.grade_var.get(),
                self.school_year_var.get(),
                self.active_var.get()
            ))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Нови ученик је успешно додат.")
            self.clear_form()
            self.load_students()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при додавању ученика: {str(e)}")
    
    def update_student(self):
        """Ажурирање постојећег ученика"""
        # Провера да ли је ученик изабран
        if not self.student_id:
            messagebox.showwarning("Упозорење", "Прво изаберите ученика за ажурирање.")
            return
            
        # Валидација података
        if not self._validate_form():
            return
            
        try:
            # Извршавање упита
            cursor = self.app.conn.cursor()
            cursor.execute("""
                UPDATE Students 
                SET first_name = ?, last_name = ?, class_enrolled = ?, 
                    grade = ?, school_year = ?, active = ?
                WHERE student_id = ?
            """, (
                self.first_name_var.get().strip(),
                self.last_name_var.get().strip(),
                self.class_enrolled_var.get().strip(),
                self.grade_var.get(),
                self.school_year_var.get(),
                self.active_var.get(),
                self.student_id
            ))
            
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Ученик је успешно ажуриран.")
            self.clear_form()
            self.load_students()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при ажурирању ученика: {str(e)}")
    
    def delete_student(self):
        """Брисање ученика из базе"""
        # Провера да ли је ученик изабран
        if not self.student_id:
            messagebox.showwarning("Упозорење", "Прво изаберите ученика за брисање.")
            return
            
        # Потврда брисања
        confirm = messagebox.askyesno(
            "Потврда", 
            "Да ли сте сигурни да желите да обришете овог ученика? "
            "Ова акција се не може поништити."
        )
        
        if not confirm:
            return
            
        try:
            # Провера да ли ученик има успехе
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Achievements WHERE student_id = ?", (self.student_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Уместо брисања, означавамо као неактивног
                cursor.execute("UPDATE Students SET active = 0 WHERE student_id = ?", (self.student_id,))
                self.app.conn.commit()
                messagebox.showinfo(
                    "Успех", 
                    "Ученик има евидентиране успехе, па је означен као неактиван уместо брисања."
                )
            else:
                # Брисање ученика
                cursor.execute("DELETE FROM Students WHERE student_id = ?", (self.student_id,))
                self.app.conn.commit()
                messagebox.showinfo("Успех", "Ученик је успешно обрисан.")
                
            self.clear_form()
            self.load_students()
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при брисању ученика: {str(e)}")
    
    def on_student_select(self, event):
        """Учитавање података изабраног ученика у форму"""
        selection = self.students_table.selection()
        if not selection:
            return
            
        # Добијање ID-а изабраног ученика
        item = self.students_table.item(selection[0])
        student_id = item['values'][0]
        
        try:
            # Учитавање података о ученику
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT first_name, last_name, class_enrolled, grade, school_year, active 
                FROM Students 
                WHERE student_id = ?
            """, (student_id,))
            
            student = cursor.fetchone()
            if not student:
                return
                
            # Постављање података у форму
            self.student_id = student_id
            self.first_name_var.set(student[0])
            self.last_name_var.set(student[1])
            self.class_enrolled_var.set(student[2] or "")
            
            stored_grade = student[3] or 5
            stored_school_year = student[4] or self.get_current_school_year()
            
            # Израчунавање тренутног разреда на основу почетних података
            calculated_grade = self.calculate_current_grade(stored_grade, stored_school_year)
            
            self.grade_var.set(calculated_grade)
            self.school_year_var.set(stored_school_year)
            self.active_var.set(str(student[5]))
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању података ученика: {str(e)}")
    
    def clear_form(self):
        """Брисање поља у форми"""
        self.student_id = None
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.class_enrolled_var.set("")
        # Постављање на тренутни разред и школску годину
        self.grade_var.set(self.calculate_current_grade())
        self.school_year_var.set(self.get_current_school_year())
        self.active_var.set("1")
        
        # Скидање селекције из табеле
        for item in self.students_table.selection():
            self.students_table.selection_remove(item)
    
    def _validate_form(self):
        """Валидација унетих података у форми"""
        # Основна валидација - провера да ли су попуњена обавезна поља
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()
        
        if not first_name or not last_name:
            messagebox.showwarning("Упозорење", "Име и презиме су обавезна поља.")
            return False
            
        return True
    
    def calculate_current_grade(self, initial_grade=None, initial_school_year=None):
        """Израчунавање тренутног разреда на основу датума система и почетне године уписа
        
        Args:
            initial_grade: Разред у којем је ученик био уписан (ако је познат)
            initial_school_year: Школска година уписа у формату 'YYYY/YYYY+1' (ако је позната)
        """
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Одређивање текуће школске године
        if current_month >= 9:  # Септембар и касније
            current_school_year = f"{current_year}/{current_year + 1}"
        else:  # Јануар до август
            current_school_year = f"{current_year - 1}/{current_year}"
        
        # Ако су дати иницијални разред и година уписа, израчунавамо напредак
        if initial_grade and initial_school_year:
            try:
                # Добијамо почетну годину из школске године (нпр. из "2023/2024" добијамо 2023)
                initial_year = int(initial_school_year.split('/')[0])
                
                # Одређивање текуће године из текуће школске године
                current_start_year = int(current_school_year.split('/')[0])
                
                # Израчунавање колико је школских година прошло
                years_passed = current_start_year - initial_year
                
                # Израчунавање тренутног разреда
                calculated_grade = initial_grade + years_passed
                
                # Осигуравамо да је разред у опсегу 1-8 за основну школу
                return max(1, min(calculated_grade, 8))
            except Exception:
                # У случају грешке, вратимо подразумевану вредност
                pass
        
        # Ако не можемо израчунати прецизан разред, враћамо 5 као подразумевану вредност
        return 5
    
    def get_current_school_year(self):
        """Одређивање текуће школске године"""
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # У Србији школска година почиње у септембру
        if current_month >= 9:  # Септембар и касније
            return f"{current_year}/{current_year + 1}"
        else:  # Јануар до август
            return f"{current_year - 1}/{current_year}"
    
    def load_competitions_list(self):
        """Учитавање листе такмичења за combobox"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT competition_id, competition_name FROM Competitions ORDER BY competition_name")
            competitions = cursor.fetchall()
            
            # Чување мапирања назива и ID-а
            self.competitions_dict = {comp[1]: comp[0] for comp in competitions}
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању такмичења: {str(e)}")
    
    def load_levels_list(self):
        """Учитавање листе нивоа такмичења"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT level_id, level_name FROM CompetitionLevels ORDER BY level_id")
            levels = cursor.fetchall()
            
            # Чување мапирања назива и ID-а
            self.levels_dict = {level[1]: level[0] for level in levels}
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању нивоа такмичења: {str(e)}")
    
    def load_school_years_list(self):
        """Учитавање листе школских година или генерисање последњих 8 година за ретроактивни унос"""
        try:
            # Генерисање листе последњих 8 школских година (текућа + 7 претходних)
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            
            # Одређивање текуће школске године
            if current_month >= 9:  # Септембар или касније
                start_year = current_year
            else:  # Јануар до август
                start_year = current_year - 1
                
            # Генерисање последњих 8 школских година (текућа + 7 претходних за ретроактивни унос)
            school_years = []
            for i in range(8):
                year = start_year - i
                school_years.append(f"{year}/{year + 1}")
                
            # Постављање вредности у combobox
            self.school_year_cb['values'] = school_years
            
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању школских година: {str(e)}")
    
    def export_to_excel(self):
        """Извоз података о ученицима у Excel фајл"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT student_id, first_name, last_name, class_enrolled, grade, school_year,
                       CASE WHEN active = 1 THEN 'Да' ELSE 'Не' END as active
                FROM Students
                ORDER BY last_name, first_name
            """)
            
            # Конверзија у pandas DataFrame
            df = pd.DataFrame(cursor.fetchall(), 
                           columns=['ИД', 'Име', 'Презиме', 'Одељење', 'Разред', 'Школска година', 'Активан'])
            
            # Отварање дијалога за чување
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel фајлови", "*.xlsx")],
                title="Сачувај извештај о ученицима"
            )
            
            if filename:
                df.to_excel(filename, index=False)
                messagebox.showinfo("Успех", f"Подаци су извезени у фајл {filename}")
                
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при извозу података: {str(e)}")
