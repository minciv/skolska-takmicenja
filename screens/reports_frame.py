# -*- encoding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : reports_frame.py
# @Верзија  : 0.1.01.
# @Програм  : Windsurf
# @Опис     : Главни оквир за извештаје
# @Датум   : 14.05.2025.

from tkinter import ttk
from tkinter.constants import *

# Увоз појединачних модула за изештаје
from screens.vukova_diploma_report import VukovaDiplomaReportFrame
from screens.dositejeva_diploma_report import DositejevaDiplomaReportFrame
from screens.best_student_report import BestStudentReportFrame
from screens.scoring_rules import ScoringRulesFrame

class ReportsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        
        # Креирање главне структуре са табовима
        self.setup_ui()
    
    def setup_ui(self):
        """Креирање корисничког интерфејса са табовима"""
        # Главни контејнер са табовима
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Таб за Вукову диплому
        vukova_frame = VukovaDiplomaReportFrame(self.notebook, self.app)
        self.notebook.add(vukova_frame, text="Вукова диплома")
        
        # Таб за Доситејеву диплому
        dositejeva_frame = DositejevaDiplomaReportFrame(self.notebook, self.app)
        self.notebook.add(dositejeva_frame, text="Доситејева диплома")
        
        # Таб за ђака генерације
        best_student_frame = BestStudentReportFrame(self.notebook, self.app)
        self.notebook.add(best_student_frame, text="Ђак генерације")
        
        # Таб за правила бодовања (само за администраторе)
        if self.app.current_user and self.app.current_user["role"] == "administrator":
            scoring_rules_frame = ScoringRulesFrame(self.notebook, self.app)
            self.notebook.add(scoring_rules_frame, text="Правила бодовања")
