import sqlite3

conn = sqlite3.connect('table.db')
cur = conn.cursor()

# Создание таблицы для меню
cur.execute("""
    CREATE TABLE menu (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
    )
""")

# Создание таблицы для блюд
cur.execute("""
    CREATE TABLE dishes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image_url TEXT,
    menu_id INTEGER,
    FOREIGN KEY (menu_id) REFERENCES menu(id)
    )
""")

# Создание таблицы для текущих заказов пользователей (корзина)
cur.execute("""
    CREATE TABLE cart (
    user_id INTEGER,
    dish_id INTEGER,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
    )
""")

# Создание таблицы для заказов
cur.execute("""
    CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    total_amount REAL NOT NULL,
    payment_status TEXT NOT NULL,
    delivery_address TEXT NOT NULL,
    order_date TEXT NOT NULL
    )
""")

# Создание таблицы для отзывов
cur.execute("""
    CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    dish_id INTEGER,
    review_text TEXT,
    rating INTEGER,
    review_date TEXT NOT NULL,
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
    )
""")

# Создание таблицы для пользователей
cur.execute("""
    CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    telegram_user_id INTEGER NOT NULL UNIQUE
    )
""")

conn.commit()
conn.close()
