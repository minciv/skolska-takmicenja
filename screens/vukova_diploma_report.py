# -*- encoding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : vukova_diploma_report.py
# @Верзија  : 0.1.01.
# @Програм  : Windsurf
# @Опис     : Извештај за Вукову диплому
# @Датум   : 14.05.2025.

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
        ttk.Label(main_frame, text="Извештај: Вукова диплома", font=("Helvetica", 16, "bold")).pack(pady=10)
        self.result_frame = ttk.LabelFrame(main_frame, text="Кандидати", padding=10)
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
