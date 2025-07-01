# -*- encoding: utf-8 -*-
# @Аутор      : minciv
# @e-mail     : minciv@protonmail.com
# @Web        : https://github.com/minciv
# @Фајл       : vukova_diploma_report.py
# @Верзија    : 0.1.05.
# @Програм    : Windsurf
# @Опис       : Извештај за Вукову диплому
# @Датум      : 01.07.2025.

from tkinter import ttk, messagebox, StringVar
from tkinter.constants import *

class VukovaDiplomaReportFrame(ttk.Frame):
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
        ttk.Label(main_frame, text="Извештај: Вукова диплома", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Информације о критеријумима
        criteria_frame = ttk.LabelFrame(main_frame, text="Критеријуми за Вукову диплому (Праvilnik 2022)", padding=10)
        criteria_frame.pack(fill=X, expand=NO, pady=(0, 10))
        
        ttk.Label(criteria_frame, text="• Одличан успех (5.00) из свих обавезних предмета од 2. до 8. разреда", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(criteria_frame, text="• Примерно владање у свакој школској години", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(criteria_frame, text="• Поседовање најмање једне Доситејеве дипломе", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(criteria_frame, text="• Одлуку доноси Наставничко веће на предлог Одељенског већа", 
                 justify='left', font=('Helvetica', 8, 'italic')).pack(anchor='w', pady=1)
        
        self.result_frame = ttk.LabelFrame(main_frame, text="Кандидати за Вукову диплому", padding=10)
        self.result_frame.pack(fill=BOTH, expand=YES)

    def load_candidates(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        try:
            cursor = self.app.conn.cursor()
            # Пример упита: ученици са просеком 5.00 и примерним владањем у свим разредима 2-8 и имају Dositejevu diplomu
            cursor.execute('''
                SELECT s.student_id, s.first_name || ' ' || s.last_name as name
                FROM Students s
                WHERE s.active = 1 AND NOT EXISTS (
                    SELECT 1 FROM StudentYearResults r
                    WHERE r.student_id = s.student_id
                    AND (r.grade BETWEEN 2 AND 8)
                    AND (r.average_grade < 5 OR r.behavior_grade != 'примерно' OR r.has_dositej_diploma = 0)
                )
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
                ttk.Label(self.result_frame, text="Нема кандидата за Вукову диплому.", font=("Helvetica", 12)).pack(pady=30)
        except Exception as e:
            messagebox.showerror("Грешка", f"Грешка при учитавању кандидата: {str(e)}")
