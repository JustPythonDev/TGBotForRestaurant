import sqlite3
from config import DATABASE_NAME

conn = sqlite3.connect(DATABASE_NAME)
cur = conn.cursor()

# Создаем таблицу menu_items - пункты меню
cur.execute("DROP TABLE if exists menu_items")
cur.execute("""
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    text TEXT NULL,
    image_url TEXT,
    callback TEXT UNIQUE NOT NULL,
    parent_menu TEXT,
    order_by INTEGER NOT NULL,
    FOREIGN KEY (parent_menu) REFERENCES menu_items(callback)
);
""")


# Создание таблицы для категорий блюд
cur.execute("""DROP TABLE if exists dishes_categories """)
cur.execute("""
    CREATE TABLE dishes_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    menu_item_callback TEXT UNIQUE REFERENCES menu_items(callback)
    )
""")

# Создание таблицы для блюд
cur.execute("""
    CREATE TABLE if not exists dishes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    price REAL NOT NULL,
    image_url TEXT,
    dishes_category TEXT,
    FOREIGN KEY (dishes_category) REFERENCES dishes_categories(menu_item_callback)
    )
""")


# Создание таблицы для текущих заказов пользователей (корзина)
cur.execute("""
    CREATE TABLE if not exists cart (
    user_id INTEGER,
    dish_id INTEGER,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
    )
""")

# Создание таблицы для заказов
cur.execute("""
    CREATE TABLE if not exists orders (
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
    CREATE TABLE if not exists reviews (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    dish_id INTEGER,
    review_text TEXT,    
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    review_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
    )
""")

# # Создание таблицы для пользователей
# cur.execute("""
#     CREATE TABLE if not exists users (
#     id INTEGER PRIMARY KEY,
#     telegram_user_id INTEGER NOT NULL UNIQUE
#     )
# """)

# Сохраняем изменения
conn.commit()
conn.close()
