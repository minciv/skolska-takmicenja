# -*- encoding: utf-8 -*-
# @Аутор      : minciv
# @e-mail     : minciv@protonmail.com
# @Web        : https://github.com/minciv
# @Фајл       : dositejeva_diploma_report.py
# @Верзија    : 0.1.05.
# @Програм    : Windsurf
# @Опис       : Извештај за Доситејеву диплому
# @Датум      : 01.07.2025.

from tkinter import ttk, messagebox, StringVar
from tkinter.constants import *

class DositejevaDiplomaReportFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.setup_ui()
        self.load_candidates()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Наслов
        ttk.Label(main_frame, text="Извештај: Доситејева диплома", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Информације о критеријумима
        criteria_frame = ttk.LabelFrame(main_frame, text="Критеријуми за Досitejeву диплому (Праvilник 2022)", padding=10)
        criteria_frame.pack(fill=X, expand=NO, pady=(0, 10))
        
        ttk.Label(criteria_frame, text="• Најмање врло добар општи успех и примерно владање на крају свaке школске године", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(criteria_frame, text="• Освајање једне од прве три награде на такмичењу (општинско до међународно ниво)", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(criteria_frame, text="• Алтернативно: Одличан успех из предмета ако нема организованих такмичења", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(criteria_frame, text="• Одлуку доноси Наставничко веће на предлог Одељенског већа", 
                 justify='left', font=('Helvetica', 8, 'italic')).pack(anchor='w', pady=1)
        # Форма за унос кандидата
        form_frame = ttk.LabelFrame(main_frame, text="Додај кандидата", padding=10)
        form_frame.pack(fill=X, expand=NO, pady=(0, 10))
        self.student_var = StringVar()
        self.mentor_var = StringVar()
        self.council_decision_var = StringVar(value="Да")
        ttk.Label(form_frame, text="Ученик:").grid(row=0, column=0, sticky=W, pady=5)
        self.student_cb = ttk.Combobox(form_frame, textvariable=self.student_var, width=30)
        self.student_cb.grid(row=0, column=1, sticky=W, pady=5)
        self.populate_students()
        ttk.Label(form_frame, text="Наставник/учитељ:").grid(row=1, column=0, sticky=W, pady=5)
        self.mentor_entry = ttk.Entry(form_frame, textvariable=self.mentor_var, width=30)
        self.mentor_entry.grid(row=1, column=1, sticky=W, pady=5)
        ttk.Label(form_frame, text="Одлука Наставничког већа:").grid(row=2, column=0, sticky=W, pady=5)
        self.council_cb = ttk.Combobox(form_frame, textvariable=self.council_decision_var, values=["Да", "Не"], width=10, state="readonly")
        self.council_cb.grid(row=2, column=1, sticky=W, pady=5)
        ttk.Button(form_frame, text="Додај кандидата", command=self.add_candidate).grid(row=3, column=0, columnspan=2, pady=10)
        self.result_frame = ttk.LabelFrame(main_frame, text="Кандидати", padding=10)
        self.result_frame.pack(fill=BOTH, expand=YES)

    def populate_students(self):
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT first_name || ' ' || last_name FROM Students WHERE active = 1 ORDER BY last_name, first_name")
            students = [row[0] for row in cursor.fetchall()]
            self.student_cb['values'] = students
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању ученика: {str(e)}")

    def add_candidate(self):
        student_name = self.student_var.get()
        mentor = self.mentor_var.get()
        council_decision = self.council_decision_var.get()
        if not student_name or not mentor:
            messagebox.showwarning("Упозорење", "Молимо изаберите ученика и унесите наставника/учитеља.")
            return
        if council_decision != "Да":
            messagebox.showwarning("Упозорење", "Кандидат мора имати одобрење Наставничког већа.")
            return
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT student_id FROM Students WHERE first_name || ' ' || last_name = ?", (student_name,))
            row = cursor.fetchone()
            if not row:
                messagebox.showerror("Грешка", "Ученика није пронађен у бази.")
                return
            student_id = row[0]
            cursor.execute('''
                INSERT OR REPLACE INTO StudentYearResults (student_id, school_year, grade, average_grade, behavior_grade, has_dositej_diploma, notes)
                VALUES (?, (SELECT MAX(school_year) FROM StudentYearResults WHERE student_id = ?), 8, 5.0, 'примерно', 1, ?)
            ''', (student_id, student_id, f'Наставник/учитељ: {mentor}'))
            self.app.conn.commit()
            messagebox.showinfo("Успех", "Кандидат је додат као добитник Доситејеве дипломе.")
            self.load_candidates()
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при додавању кандидата: {str(e)}")

    def load_candidates(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        try:
            cursor = self.app.conn.cursor()
            # Пример упита: ученици који имају бар један унос has_dositej_diploma=1 у StudentYearResults
            cursor.execute('''
                SELECT DISTINCT s.student_id, s.first_name || ' ' || s.last_name as name
                FROM Students s
                JOIN StudentYearResults r ON r.student_id = s.student_id
                WHERE s.active = 1 AND r.has_dositej_diploma = 1
                ORDER BY s.last_name, s.first_name
            ''')
            candidates = cursor.fetchall()
            columns = ("Име и презиме",)
            tree = ttk.Treeview(self.result_frame, columns=columns, show="headings")
            tree.pack(fill=BOTH, expand=YES)
            tree.heading("Име и презиме", text="Име и презиме")
            for c in candidates:
                tree.insert("", END, values=(c[1],))
            if not candidates:
                ttk.Label(self.result_frame, text="Нема кандидата за Доситејеву диплому.", font=("Helvetica", 12)).pack(pady=30)
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању кандидата: {str(e)}")
