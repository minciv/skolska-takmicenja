# -*- encoding: utf-8 -*-
# @Аутор      : minciv
# @e-mail     : minciv@protonmail.com
# @Web        : https://github.com/minciv
# @Фајл       : db.py
# @Верзија    : 0.1.05.
# @Програм    : Windsurf
# @Опис       : База података пројекта
# @Датум      : 01.07.2025.
import sqlite3
# Овде можете додати додатне библиотеке ако су потребне у будућности
DB_PATH = "school.db"
# Функција за повезивање са базом података
def get_conn():
    return sqlite3.connect(DB_PATH)

# Иницијализација базе података и креирање табела ако не постоје
def init_db():
    conn = get_conn()
    c = conn.cursor()
    # Корисници
    c.execute("""
    CREATE TABLE IF NOT EXISTS korisnici (
        korisnik_id INTEGER PRIMARY KEY AUTOINCREMENT,
        korisnicko_ime TEXT UNIQUE NOT NULL,
        hash_lozinke TEXT NOT NULL,
        uloga TEXT NOT NULL CHECK (uloga IN ('administrator', 'korisnik'))
    )""")
    # Ученици
    c.execute("""
    CREATE TABLE IF NOT EXISTS ucenici (
        ucenik_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ime TEXT NOT NULL,
        prezime TEXT NOT NULL,
        odeljenje_upisa TEXT,
        aktivan INTEGER DEFAULT 1
    )""")
    # Предмети/Такмичења
    c.execute("""
    CREATE TABLE IF NOT EXISTS predmeti_takmicenja (
        predmet_id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv_predmeta_takmicenja TEXT UNIQUE NOT NULL
    )""")
    # Нивои такмичења
    c.execute("""
    CREATE TABLE IF NOT EXISTS nivoi_takmicenja (
        nivo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv_nivoа TEXT UNIQUE NOT NULL
    )""")
    # Успеси ученика
    c.execute("""
    CREATE TABLE IF NOT EXISTS uspesi_ucenika (
        uspeh_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ucenik_id_fk INTEGER NOT NULL,
        predmet_id_fk INTEGER NOT NULL,
        nivo_id_fk INTEGER NOT NULL,
        skolska_godina TEXT NOT NULL,
        razred_uspeha INTEGER NOT NULL,
        plasman TEXT NOT NULL,
        mentor_ime_prezime TEXT,
        datum_unosa TEXT DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
        napomena TEXT,
        FOREIGN KEY (ucenik_id_fk) REFERENCES ucenici(ucenik_id),
        FOREIGN KEY (predmet_id_fk) REFERENCES predmeti_takmicenja(predmet_id),
        FOREIGN KEY (nivo_id_fk) REFERENCES nivoi_takmicenja(nivo_id)
    )""")
    # Правила бодовања
    c.execute("""
    CREATE TABLE IF NOT EXISTS pravila_bodovanja (
        pravilo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nivo_id_fk INTEGER NOT NULL,
        opis_plasmana_za_bodovanje TEXT NOT NULL,
        broj_bodова REAL NOT NULL,
        FOREIGN KEY (nivo_id_fk) REFERENCES nivoi_takmicenja(nivo_id)
    )""")
    # Креирање подразумеваног администратора ако не постоји
    c.execute("SELECT * FROM korisnici WHERE korisnicko_ime = 'admin'")
    if not c.fetchone():
        import hashlib
        c.execute("INSERT INTO korisnici (korisnicko_ime, hash_lozinke, uloga) VALUES (?, ?, ?)",
                  ('admin', hashlib.sha256('admin'.encode()).hexdigest(), 'administrator'))
    conn.commit()
    conn.close()

# Функција за добијање корисника по корисничком имену
def get_user_by_username(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT korisnik_id, korisnicko_ime, hash_lozinke, uloga FROM korisnici WHERE korisnicko_ime = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user
