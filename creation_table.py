import sqlite3

conn = sqlite3.connect('food_ordering_sistem.db')
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

# Создаем таблицу menu_items
cur.execute("""
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    text TEXT NOT NULL,
    image_url TEXT,
    callback TEXT UNIQUE NOT NULL,
    parent_menu TEXT,
    order_by INTEGER NOT NULL,
    FOREIGN KEY (parent_menu) REFERENCES menu_items(callback)
);
""")

# Вставляем данные в таблицу menu_items
cur.executemany("""
INSERT INTO menu_items (name, text, callback, parent_menu, order_by, image_url)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    ('Меню кафе', 'Выберите категорию блюда', 'menu', None, 1, ''),
    ('Корзина', 'Выбранные вами блюда', 'cart', None, 2, ''),
    ('Оплата заказа', 'Выберите способ оплаты', 'payment', None, 3, ''),
    ('Статус заказа', 'Выберите заказ для просмотра', 'status', None, 4, ''),
    ('Отзывы', 'Выберите категорию отзыва', 'feedback', None, 5, ''),
    ('Закуски', 'Выберите закуску', 'appetizers', 'menu', 1, 'img/appetizers.jpg'),
    ('Салаты', 'Выберите салат', 'salads', 'menu', 2, 'img/salads.jpg'),
    ('Первые блюда', 'Выберите суп', 'soups', 'menu', 3, 'img/soups.jpg'),
    ('Основные блюда', 'Выберите горячее', 'main_dishes', 'menu', 4, 'img/main_dishes.jpg'),
    ('Десерты', 'Выберите десерт', 'desserts', 'menu', 5, '')
])

# Сохраняем изменения
conn.commit()
conn.close()
