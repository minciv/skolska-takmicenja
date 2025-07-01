# -*- encoding: utf-8 -*-
# @Аутор      : minciv
# @e-mail     : minciv@protonmail.com
# @Web        : https://github.com/minciv
# @Фајл       : takmicenja.py
# @Верзија    : 0.1.05.
# @Програм    : Windsurf
# @Опис       : Главни фајл за покретање програма
# @Датум      : 01.07.2025.

from tkinter import Tk, Menu, messagebox, filedialog
from tkinter import ttk
from pandas import DataFrame, read_excel
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from sqlite3 import connect, OperationalError, IntegrityError
from login_frame import LoginFrame
from screens.students_frame import StudentsFrame
from screens.competitions_frame import CompetitionsFrame
from screens.achievements_frame import AchievementsFrame
from screens.reports_frame import ReportsFrame
from screens.users_frame import UsersFrame

# Константе за наслове и поруке
WINDOW_TITLE = "Школска такмичења"
WINDOW_SIZE = "1024x768"
DB_PATH = "bаза_takmicenja.db"

# Поруке о грешкама
ERR_DB_CONNECT = "Грешка при повезивању са базом: {}"
ERR_DB_QUERY = "Грешка при извршавању упита: {}"
ERR_LOGIN_FAILED = "Погрешно корисничко име или лозинка"
ERR_REQUIRED_FIELDS = "Сва обавезна поља морају бити попуњена"

class SkolskaTakmicenjaApp:
    def __init__(self):
        """Иницијализација главне апликације"""
        self.root = Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # Иницијализација везе са базом
        self.conn = None
        self.setup_database()
        
        # Иницијализација променљивих за корисника
        self.current_user = None
        
        # Постављање главног контејнера
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True)
        
        # Креирање менија
        self.setup_menu()
        
        # Речник за чување фрејмова
        self.frames = {}
        
        # Иницијализација прозора за пријаву
        self.current_frame = None
        self.current_user = None
        self.show_login_frame()
    
    def setup_database(self):
        """Иницијализација везе са базом и креирање табела ако не постоје"""
        try:
            self.conn = connect(DB_PATH)
            self.create_tables()
        except OperationalError as e:
            messagebox.showerror("Грешка", ERR_DB_CONNECT.format(e))
    
    def create_tables(self):
        """Креирање свих неопходних табела у бази"""
        cursor = self.conn.cursor()
        
        # Креирање табеле корисника
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('administrator', 'user'))
        )''')
        
        # Креирање табеле ученика
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            class_enrolled TEXT,
            grade INTEGER,
            school_year TEXT,
            active INTEGER DEFAULT 1
        )''')
        
        # Провера и додавање недостајућих колона у евентуално већ постојећу табелу
        try:
            # Провери да ли постоји колона grade
            cursor.execute("PRAGMA table_info(Students)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'grade' not in columns:
                cursor.execute("ALTER TABLE Students ADD COLUMN grade INTEGER")
                
            if 'school_year' not in columns:
                cursor.execute("ALTER TABLE Students ADD COLUMN school_year TEXT")
                
            self.conn.commit()
        except Exception as e:
            print(f"Грешка при ажурирању шеме табеле Students: {e}")
        
        # Креирање табеле предмета/такмичења
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Competitions (
            competition_id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_name TEXT UNIQUE NOT NULL
        )''')
        
        # Креирање табеле нивоа такмичења
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CompetitionLevels (
            level_id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_name TEXT UNIQUE NOT NULL
        )''')
        
        # Креирање табеле успеха ученика
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS StudentAchievements (
            achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            competition_id INTEGER NOT NULL,
            level_id INTEGER NOT NULL,
            school_year TEXT NOT NULL,
            grade INTEGER NOT NULL,
            placement TEXT NOT NULL,
            mentor_name TEXT,
            entry_date TEXT DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (competition_id) REFERENCES Competitions(competition_id),
            FOREIGN KEY (level_id) REFERENCES CompetitionLevels(level_id)
        )''')
        
        # Креирање табеле правила бодовања
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ScoringRules (
            rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_id INTEGER NOT NULL,
            placement_description TEXT NOT NULL,
            points REAL NOT NULL,
            FOREIGN KEY (level_id) REFERENCES CompetitionLevels(level_id)
        )''')
        
        # Додајемо табелу за успех на крају године (2-8 разред)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS StudentYearResults (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            school_year TEXT NOT NULL,
            grade INTEGER NOT NULL,
            average_grade REAL NOT NULL,
            behavior_grade TEXT NOT NULL,
            has_dositej_diploma INTEGER DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES Students(student_id)
        )''')
        
        self.conn.commit()
    
    def setup_menu(self):
        """Постављање главног менија апликације"""
        # Креирамо главни menubar
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Мени “Навигација”
        self.nav_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Навигација", menu=self.nav_menu)
        self.nav_menu.add_command(label="Ученици", command=self.show_students_frame)
        self.nav_menu.add_command(label="Такмичења", command=self.show_competitions_frame)
        self.nav_menu.add_command(label="Успеси", command=self.show_achievements_frame)
        self.nav_menu.add_command(label="Извештаји", command=self.show_reports_frame)
        self.nav_menu.add_command(label="Корисници", command=self.show_users_frame)
        
        # Мени “Налог”
        self.account_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Налог", menu=self.account_menu)
        self.account_menu.add_command(label="Одјава", command=self.logout)
        
        # Мени "Помоћ"
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Помоћ", menu=self.help_menu)
        self.help_menu.add_command(label="Критеријуми диплома", command=self.show_criteria_dialog)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="О апликацији", command=lambda: self.show_about_dialog())
        
        # Почетно сакривамо мени док се корисник не пријави
        self.disable_menu()
    
    def enable_menu(self):
        """Омогућавање менија након пријаве"""
        self.root.config(menu=self.menu_bar)
        
    def disable_menu(self):
        """Онемогућавање менија када корисник није пријављен"""
        self.root.config(menu="")
    
    def logout(self):
        """Одјава корисника"""
        self.current_user = None
        self.disable_menu()
        self.show_login_frame()
    
    def show_login_frame(self):
        """Приказ прозора за пријаву"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self.main_container, self)
        self.current_frame.pack(fill='both', expand=True)
    
    def show_main_window(self):
        """Пребацивање на главни прозор апликације"""
        # Очисти све што је било на главном прозору
        if self.current_frame:
            self.current_frame.destroy()
            
        # Прикажи мени траку
        self.enable_menu()  # Приказивање менија
        
        # Креирамо главни екран добродошлице
        welcome_frame = ttk.Frame(self.main_container, padding=20)
        welcome_frame.pack(fill='both', expand=True)
        
        # Наслов апликације
        ttk.Label(
            welcome_frame, 
            text="Добродошли у апликацију за евиденцију школских такмичења", 
            font=('Helvetica', 16, 'bold')
        ).pack(pady=20)
        
        # Информације о кориснику
        user_info = ttk.Frame(welcome_frame, padding=10)
        user_info.pack(pady=10)
        
        ttk.Label(
            user_info, 
            text=f"Пријављени као: {self.current_user['username']} ({self.current_user['role']})",
            font=('Helvetica', 12)
        ).pack()
        
        # Упутство
        instructions = ttk.LabelFrame(welcome_frame, text="Упутство за коришћење", padding=10)
        instructions.pack(fill='both', expand=True, pady=20)
        
        ttk.Label(instructions, text="• Користите мени изнад за навигацију између екрана", justify='left').pack(anchor='w', pady=2)
        ttk.Label(instructions, text="• Ученици: Управљање подацима о ученицима и њиховим резултатима", justify='left').pack(anchor='w', pady=2)
        ttk.Label(instructions, text="• Такмичења: Дефинисање типова такмичења и нивоа", justify='left').pack(anchor='w', pady=2)
        ttk.Label(instructions, text="• Успеси: Евиденција успеха ученика на такмичењима", justify='left').pack(anchor='w', pady=2)
        ttk.Label(instructions, text="• Извештаји: Генерисање извештаја за Вукове и Доситејеве дипломе", justify='left').pack(anchor='w', pady=2)
        
        # Додавање информација о дипломама
        diplomas_info = ttk.LabelFrame(welcome_frame, text="Информације о дипломама", padding=10)
        diplomas_info.pack(fill='both', expand=True, pady=10)
        
        ttk.Label(diplomas_info, text="ВУКОВА ДИПЛОМА - Критеријуми:", font=('Helvetica', 10, 'bold'), justify='left').pack(anchor='w', pady=2)
        ttk.Label(diplomas_info, text="• Одличне оцене (5.00) из свих предмета од 2. до 8. разреда", justify='left').pack(anchor='w', padx=20, pady=1)
        ttk.Label(diplomas_info, text="• Примерно владање у свакој школској години", justify='left').pack(anchor='w', padx=20, pady=1)
        ttk.Label(diplomas_info, text="• Поседовање најмање једне Доситејеве дипломе", justify='left').pack(anchor='w', padx=20, pady=1)
        
        ttk.Label(diplomas_info, text="ДОСИТЕЈЕВА ДИПЛОМА - Критеријуми:", font=('Helvetica', 10, 'bold'), justify='left').pack(anchor='w', pady=(10,2))
        ttk.Label(diplomas_info, text="• Најмање врло добар општи успех и примерно владање", justify='left').pack(anchor='w', padx=20, pady=1)
        ttk.Label(diplomas_info, text="• Једна од прве три награде на такмичењу (општинско до међународно)", justify='left').pack(anchor='w', padx=20, pady=1)
        ttk.Label(diplomas_info, text="• Или одличан успех из предмета ако нема такмичења", justify='left').pack(anchor='w', padx=20, pady=1)
        
        self.current_frame = welcome_frame
    
    def show_students_frame(self):
        """Приказ фрејма за рад са ученицима"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = StudentsFrame(self.main_container, self)
        self.current_frame.pack(fill='both', expand=True)
    
    def show_competitions_frame(self):
        """Приказ фрејма за рад са такмичењима"""
        # Провера да ли корисник има право приступа
        if not self.current_user or self.current_user['role'] != 'administrator':
            messagebox.showerror("Приступ одбијен", "Само администратори имају приступ овом модулу.")
            return
            
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = CompetitionsFrame(self.main_container, self)
        self.current_frame.pack(fill='both', expand=True)
    
    def show_achievements_frame(self):
        """Приказ фрејма за рад са успесима"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = AchievementsFrame(self.main_container, self)
        self.current_frame.pack(fill='both', expand=True)
    
    def show_reports_frame(self):
        """Приказ фрејма за извештаје"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ReportsFrame(self.main_container, self)
        self.current_frame.pack(fill='both', expand=True)
    
    def show_users_frame(self):
        """Приказ фрејма за управљање корисницима"""
        # Сви корисници имају приступ форми за промену лозинке,
        # а UsersFrame ће приказати одговарајуће опције на основу улоге
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = UsersFrame(self.main_container, self)
        self.current_frame.pack(fill='both', expand=True)
    
    def show_criteria_dialog(self):
        """Приказује брзи преглед критеријума за дипломе"""
        import tkinter as tk
        criteria_win = tk.Toplevel(self.root)
        criteria_win.title("Критеријуми за дипломе")
        criteria_win.geometry("600x500")
        
        # Креирање табова
        notebook = ttk.Notebook(criteria_win)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Таб за Вукову диплому
        vuk_frame = ttk.Frame(notebook, padding=10)
        notebook.add(vuk_frame, text="Вукова диплома")
        
        ttk.Label(vuk_frame, text="Критеријуми за Вукову диплому", font=('Helvetica', 12, 'bold')).pack(pady=5)
        ttk.Label(vuk_frame, text="• Одличне оцене (5.00) из свих обавезних предмета од 2. до 8. разреда", justify='left').pack(anchor='w', pady=2)
        ttk.Label(vuk_frame, text="• Примерно владање у свакој школској години", justify='left').pack(anchor='w', pady=2)
        ttk.Label(vuk_frame, text="• Поседовање најмање једне Доситејеве дипломе", justify='left').pack(anchor='w', pady=2)
        ttk.Label(vuk_frame, text="• Одлуку доноси Наставничко веће на предлог Одељенског већа", justify='left', font=('Helvetica', 9, 'italic')).pack(anchor='w', pady=2)
        
        # Таб за Доситејеву диплому
        dositej_frame = ttk.Frame(notebook, padding=10)
        notebook.add(dositej_frame, text="Доситејева диплома")
        
        ttk.Label(dositej_frame, text="Критеријуми за Доситејеву диплому", font=('Helvetica', 12, 'bold')).pack(pady=5)
        ttk.Label(dositej_frame, text="• Најмање врло добар општи успех и примерно владање", justify='left').pack(anchor='w', pady=2)
        ttk.Label(dositej_frame, text="• Освајање једне од прве три награде на такмичењу", justify='left').pack(anchor='w', pady=2)
        ttk.Label(dositej_frame, text="  (општинско, градско, окружно, републичко, међународно)", justify='left').pack(anchor='w', padx=20, pady=1)
        ttk.Label(dositej_frame, text="• Алтернативно: Одличан успех из предмета ако нема такмичења", justify='left').pack(anchor='w', pady=2)
        ttk.Label(dositej_frame, text="• Одлуку доноси Наставничко веће на предлог Одељенског већа", justify='left', font=('Helvetica', 9, 'italic')).pack(anchor='w', pady=2)
        
        # Дугме за детаљније информације
        button_frame = ttk.Frame(criteria_win)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Детаљније (Извештаји)", command=lambda: [criteria_win.destroy(), self.show_reports_frame()]).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Затвори", command=criteria_win.destroy).pack(side='left', padx=5)
        
        criteria_win.transient(self.root)
        criteria_win.grab_set()
        criteria_win.focus_set()
    
    def show_about_dialog(self):
        """Приказује прозор са текстом из Pravilnik.txt"""
        try:
            with open("Pravilnik.txt", encoding="utf-8") as f:
                pravilnik_text = f.read()
        except Exception as e:
            pravilnik_text = f"Грешка при учитавању текста: {str(e)}"
        import tkinter as tk
        about_win = tk.Toplevel(self.root)
        about_win.title("О програму и дипломама")
        about_win.geometry("700x600")
        text = tk.Text(about_win, wrap="word", font=("Helvetica", 11))
        text.insert("1.0", pravilnik_text)
        text.config(state="disabled")
        text.pack(fill="both", expand=True)
        ttk.Button(about_win, text="Затвори", command=about_win.destroy).pack(pady=10)
        about_win.transient(self.root)
        about_win.grab_set()
        about_win.focus_set()
    
    def run(self):
        """Покретање апликације"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SkolskaTakmicenjaApp()
    app.run()
