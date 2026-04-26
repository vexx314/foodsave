import sqlite3
import os

# No Render: use /var/data (Persistent Disk) se disponível
# Localmente: usa a pasta do projeto
DATA_DIR = os.environ.get('RENDER_DISK_PATH', os.path.dirname(__file__) + '/..')
DB_PATH  = os.path.join(DATA_DIR, 'foodsave.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Garante que o diretório existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_db()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            role TEXT DEFAULT 'pessoal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            categoria TEXT DEFAULT 'Outros',
            quantidade TEXT NOT NULL,
            validade TEXT NOT NULL,
            preco REAL DEFAULT 0,
            status TEXT DEFAULT 'ativo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            food_category TEXT DEFAULT 'Outros',
            tipo TEXT NOT NULL,
            preco REAL DEFAULT 0,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
