# -*- encoding: utf-8 -*-
# @Аутор      : minciv
# @e-mail     : minciv@protonmail.com
# @Web        : https://github.com/minciv
# @Фајл       : diploma_criteria.py
# @Верзија    : 0.1.05.
# @Програм    : Windsurf
# @Опис       : Детаљно објашњење критеријума за дипломе
# @Датум      : 01.07.2025.

from tkinter import ttk, messagebox
from tkinter.constants import *

class DiplomaCriteriaFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        """Креирање корисничког интерфејса за приказ критеријума"""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Наслов
        ttk.Label(main_frame, text="Критеријуми за Дипломе", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Notebook за различите табове
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=YES, pady=10)
        
        # Таб за Вукову диплому
        vuk_frame = ttk.Frame(notebook, padding=10)
        notebook.add(vuk_frame, text="Вукова диплома")
        self.setup_vuk_criteria(vuk_frame)
        
        # Таб за Доситејеву диплому
        dositej_frame = ttk.Frame(notebook, padding=10)
        notebook.add(dositej_frame, text="Доситејева диплома")
        self.setup_dositej_criteria(dositej_frame)
        
        # Таб за правне основе
        legal_frame = ttk.Frame(notebook, padding=10)
        notebook.add(legal_frame, text="Правне основе")
        self.setup_legal_info(legal_frame)

    def setup_vuk_criteria(self, parent):
        """Постављање критеријума за Вукову диплому"""
        # Заглавље
        ttk.Label(parent, text="Вукова диплома", font=("Helvetica", 14, "bold")).pack(pady=(0, 10))
        
        # Основни критеријуми
        criteria_frame = ttk.LabelFrame(parent, text="Основни критеријуми (Правилник 2022)", padding=10)
        criteria_frame.pack(fill=X, expand=NO, pady=5)
        
        ttk.Label(criteria_frame, text="1. Одличне оцене (5.00) из свих обавезних предмета од 2. до 8. разреда", 
                 justify='left', wraplength=600).pack(anchor='w', pady=2)
        ttk.Label(criteria_frame, text="2. Примерно владање у свакој школској години", 
                 justify='left', wraplength=600).pack(anchor='w', pady=2)
        ttk.Label(criteria_frame, text="3. Поседовање најмање једне Доситејеве дипломе", 
                 justify='left', wraplength=600).pack(anchor='w', pady=2)
        
        # Процес одлучивања
        process_frame = ttk.LabelFrame(parent, text="Процес доделе", padding=10)
        process_frame.pack(fill=X, expand=NO, pady=5)
        
        ttk.Label(process_frame, text="• Предлог даје Одељенско веће", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(process_frame, text="• Одлуку доноси Наставничко веће школе", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(process_frame, text="• Критеријуми се примењују у свим основним школама у Србији", 
                 justify='left').pack(anchor='w', pady=1)
        
        # Измене у односу на стари правилник
        changes_frame = ttk.LabelFrame(parent, text="Кључне промене (2022 vs 1993)", padding=10)
        changes_frame.pack(fill=X, expand=NO, pady=5)
        
        ttk.Label(changes_frame, text="• Стариј правилник: Критеријуми од 5. разреда", 
                 justify='left', foreground='red').pack(anchor='w', pady=1)
        ttk.Label(changes_frame, text="• Нови правилник: Критеријуми од 2. разреда", 
                 justify='left', foreground='green').pack(anchor='w', pady=1)
        ttk.Label(changes_frame, text="• Додат је услов поседовања Доситејеве дипломе", 
                 justify='left', foreground='green').pack(anchor='w', pady=1)

    def setup_dositej_criteria(self, parent):
        """Постављање критеријума за Доситејеву диплому"""
        # Заглавље
        ttk.Label(parent, text="Доситејева диплома", font=("Helvetica", 14, "bold")).pack(pady=(0, 10))
        
        # Основни критеријуми
        criteria_frame = ttk.LabelFrame(parent, text="Основни критеријуми", padding=10)
        criteria_frame.pack(fill=X, expand=NO, pady=5)
        
        ttk.Label(criteria_frame, text="1. Најмање врло добар општи успех и примерно владање на крају сваке школске године", 
                 justify='left', wraplength=600).pack(anchor='w', pady=2)
        ttk.Label(criteria_frame, text="2. Изузетни резултати у одређеном обавезном предмету или изборном програму", 
                 justify='left', wraplength=600).pack(anchor='w', pady=2)
        
        # Начини стицања
        ways_frame = ttk.LabelFrame(parent, text="Начини стицања", padding=10)
        ways_frame.pack(fill=X, expand=NO, pady=5)
        
        ttk.Label(ways_frame, text="ОСНОВНИ НАЧИН:", font=('Helvetica', 10, 'bold'), 
                 justify='left').pack(anchor='w', pady=2)
        ttk.Label(ways_frame, text="• Освајање једне од прве три награде на такмичењу", 
                 justify='left').pack(anchor='w', padx=20, pady=1)
        ttk.Label(ways_frame, text="• Нивои: општинско, градско, окружно, републичко, међународно", 
                 justify='left').pack(anchor='w', padx=20, pady=1)
        
        ttk.Label(ways_frame, text="АЛТЕРНАТИВНИ НАЧИН:", font=('Helvetica', 10, 'bold'), 
                 justify='left').pack(anchor='w', pady=(10,2))
        ttk.Label(ways_frame, text="• Одличан успех из предмета ако се не организује такмичење", 
                 justify='left').pack(anchor='w', padx=20, pady=1)
        ttk.Label(ways_frame, text="• Описна оцена 'истиче се' из изборног програма", 
                 justify='left').pack(anchor='w', padx=20, pady=1)
        
        # Такмичења
        competition_frame = ttk.LabelFrame(parent, text="О такмичењима", padding=10)
        competition_frame.pack(fill=X, expand=NO, pady=5)
        
        ttk.Label(competition_frame, text="• Министарство просвете сваке године објављује календар признатих такмичења", 
                 justify='left', wraplength=600).pack(anchor='w', pady=1)
        ttk.Label(competition_frame, text="• Узимају се у обзир и такмичења која организују школе у сарадњи са Министарством", 
                 justify='left', wraplength=600).pack(anchor='w', pady=1)

    def setup_legal_info(self, parent):
        """Постављање информација о правним основама"""
        # Заглавље
        ttk.Label(parent, text="Правне основе", font=("Helvetica", 14, "bold")).pack(pady=(0, 10))
        
        # Тренутни правилник
        current_frame = ttk.LabelFrame(parent, text="Важећи правилник", padding=10)
        current_frame.pack(fill=X, expand=NO, pady=5)
        
        ttk.Label(current_frame, text='Назив: "Правилник о дипломама за изузетан успех у основном образовању и васпитању"', 
                 justify='left', wraplength=600, font=('Helvetica', 9, 'bold')).pack(anchor='w', pady=2)
        ttk.Label(current_frame, text="Донет од стране: Министарства просвете Републике Србије", 
                 justify='left', wraplength=600).pack(anchor='w', pady=1)
        ttk.Label(current_frame, text="Објављен у: Службеном гласнику Републике Србије", 
                 justify='left', wraplength=600).pack(anchor='w', pady=1)
        ttk.Label(current_frame, text="Година: 2022.", 
                 justify='left').pack(anchor='w', pady=1)
        
        # Примена
        application_frame = ttk.LabelFrame(parent, text="Примена", padding=10)
        application_frame.pack(fill=X, expand=NO, pady=5)
        
        ttk.Label(application_frame, text="• Правилник се примењује у свим основним школама у Републици Србији", 
                 justify='left', wraplength=600).pack(anchor='w', pady=1)
        ttk.Label(application_frame, text="• Укључујући школе у граду Пироту (ОШ 'Свети Сава', ОШ 'Вук Караџић')", 
                 justify='left', wraplength=600).pack(anchor='w', pady=1)
        ttk.Label(application_frame, text="• Нема регионалних разлика у критеријумима", 
                 justify='left', wraplength=600).pack(anchor='w', pady=1)
        
        # Историјат
        history_frame = ttk.LabelFrame(parent, text="Историјат промена", padding=10)
        history_frame.pack(fill=X, expand=NO, pady=5)
        
        ttk.Label(history_frame, text="1993: Први правилник донет 25. маја 1993. године", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(history_frame, text="2022: Нови правилник замењује стари након 30 година", 
                 justify='left').pack(anchor='w', pady=1)
        ttk.Label(history_frame, text="Разлог: Усклађивање са образовним реформама и новим наставним плановима", 
                 justify='left', wraplength=600).pack(anchor='w', pady=1)
