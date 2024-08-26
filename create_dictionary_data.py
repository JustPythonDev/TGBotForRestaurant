import sqlite3
from config import DATABASE_NAME

conn = sqlite3.connect(DATABASE_NAME)
cur = conn.cursor()


# Вставляем данные в таблицу menu_items
cur.execute("DELETE FROM menu_items")

cur.executemany("""
INSERT INTO menu_items (name, text, callback, parent_menu, order_by, image_url)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    ('Главное меню', 'Добро пожаловать в наше кафе!\nВыберите действие', 'start', None, 1, 'img/main_photo.jpg'),

    ('🍽️ Меню кафе', 'Выберите категорию блюда', 'menu', 'start', 1, 'img/menu.jpg'),
    ('🧺 Корзина', 'Выбранные вами блюда', 'cart', 'start', 2, 'img/cart.jpg'),
    ('💵 Оплата заказа', 'Выберите способ оплаты', 'payment', 'start', 3, 'img/payment.jpg'),
    ('🚚 Статус заказа', 'Выберите заказ для просмотра', 'status', 'start', 4, 'img/status.jpg'),
    ('💬 Отзывы', 'Выберите категорию отзыва', 'feedback', 'start', 5, 'img/feedback.jpg'),

    ('Закуски', 'Выберите закуску', 'appetizers', 'menu', 1, 'img/appetizers.jpg'),
    ('Салаты', 'Выберите салат', 'salads', 'menu', 2, 'img/salads.jpg'),
    ('Первые блюда', 'Выберите суп', 'soups', 'menu', 3, 'img/soups.jpg'),
    ('Основные блюда', 'Выберите горячее', 'main_dishes', 'menu', 4, 'img/main_dishes.jpg'),
    ('Десерты', 'Выберите десерт', 'desserts', 'menu', 5, 'img/desserts.jpg'),
    ('Напитки', 'Выберите напиток', 'drinks', 'menu', 6, 'img/drinks.jpg'),

    ('Оставить отзыв', 'Напишите ваш отзыв', 'set_review', 'feedback', 1, None),
    ('Просмотреть отзывы', 'Последние отзывы', 'view_reviews', 'feedback', 2, None)
])


# Вставляем данные в таблицу dishes_categories

cur.executemany("""
INSERT INTO dishes_categories (name, menu_item_callback)
VALUES (?, ?)
ON CONFLICT(menu_item_callback) DO NOTHING
""", [
    ('Закуски', 'appetizers'),
    ('Салаты', 'salads'),
    ('Первые блюда', 'soups'),
    ('Основные блюда', 'main_dishes'),
    ('Десерты', 'desserts'),
    ('Напитки', 'drinks')
])

# Сохраняем изменения
conn.commit()
conn.close()