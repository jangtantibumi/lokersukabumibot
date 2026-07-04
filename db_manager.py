import sqlite3
import os

DB_FILE = 'posted_jobs.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posted_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def is_posted(url):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM posted_jobs WHERE url = ?', (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_as_posted(url):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posted_jobs (url) VALUES (?)', (url,))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        pass
