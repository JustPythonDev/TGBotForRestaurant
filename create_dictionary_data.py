import sqlite3
from config import DATABASE_NAME

conn = sqlite3.connect(DATABASE_NAME)
cur = conn.cursor()


# Вставляем данные в таблицу menu_items
cur.execute("DELETE FROM menu_items")

cur.executemany("""
INSERT INTO menu_items (name, text, callback, parent_menu, order_by, image_url)
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT(callback) DO NOTHING
""", [
    ('Главное меню', 'Добро пожаловать в наше кафе!\nВыберите действие', 'start', None, 1, 'img/main_photo.jpg'),

    ('🍽️ Меню кафе', 'Выберите категорию блюда', 'menu', 'start', 1, 'img/menu.jpg'),
    ('🧺 Корзина', 'Выбранные вами блюда', 'cart', 'start', 2, 'img/cart.jpg'),
    ('💵 Оплата заказа', 'Выберите способ оплаты', 'payment', 'start', 3, 'img/payment.jpg'),
    ('🚚 Статус заказа', 'Ваши заказы за текущие сутки', 'status', 'start', 4, 'img/status.jpg'),
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

cur.executemany("""
INSERT INTO dishes (name, dishes_category, price, image_url)
VALUES (?, ?, ?, ?)
ON CONFLICT(name) DO NOTHING
""", [
    # Закуски
    ('Чесночные крутоны', 'appetizers', 230.0, 'img/ap_bruschetta.jpg'),
    ('Пряные оливки', 'appetizers', 280.0, 'img/ap_olives.jpg'),
    ('Хрустящие креветки', 'appetizers', 350.0, 'img/ap_shrimp_tempura.jpg'),
    ('Тартар из северного лосося', 'appetizers', 350.0, 'img/ap_tartar.jpg'),
    ('Итальянское капрезе', 'appetizers', 200.0, 'img/ap_caprese.jpg'),

    # Супы
    ('Традиционный борщ', 'soups', 300.0, 'img/soup_borscht.jpg'),
    ('Огненный Том Ям', 'soups', 400.0, 'img/soup_tomyam.jpg'),
    ('Домашний куриный суп', 'soups', 250.0, 'img/soup_chicken.jpg'),
    ('Мисо на закате', 'soups', 350.0, 'img/soup_miso.jpg'),

    # Салаты
    ('Классический Цезарь', 'salads', 350.0, 'img/salad_caesar.jpg'),
    ('Солнечный греческий', 'salads', 300.0, 'img/salad_greek.jpg'),
    ('Тунец на зелёной волне', 'salads', 320.0, 'img/salad_tuna.jpg'),
    ('Креветки в авокадо', 'salads', 350.0, 'img/salad_avocado_shrimp.jpg'),
    ('Киноа-праздник', 'salads', 330.0, 'img/salad_quinoa.jpg'),

    # Основные блюда
    ('Рибай-гриль', 'main_dishes', 1200.0, 'img/main_steak.jpg'),
    ('Карбонара по-домашнему', 'main_dishes', 450.0, 'img/main_pasta.jpg'),
    ('Рыба в огне', 'main_dishes', 600.0, 'img/main_grilled_fish.jpg'),
    ('Пельмешки бабушки', 'main_dishes', 400.0, 'img/main_dumplings.jpg'),
    ('Курица в золотой корочке', 'main_dishes', 550.0, 'img/main_roasted_chicken.jpg'),

    # Десерты
    ('Тирамису мечты', 'desserts', 300.0, 'img/dessert_tiramisu.jpg'),
    ('Нежный чизкейк', 'desserts', 350.0, 'img/dessert_cheesecake.jpg'),
    ('Шоколадные эклеры', 'desserts', 250.0, 'img/dessert_eclair.jpg'),
    ('Торт "Сладкая ночь"', 'desserts', 400.0, 'img/dessert_choco_cake.jpg'),
    ('Радужные макароны', 'desserts', 280.0, 'img/dessert_macarons.jpg'),

    # Напитки
    ('Эспрессо бодрости', 'drinks', 150.0, 'img/drink_coffee.jpg'),
    ('Чай "Утренний рассвет"', 'drinks', 100.0, 'img/drink_tea.jpg'),
    ('Фреш из солнечных апельсинов', 'drinks', 120.0, 'img/drink_orange_juice.jpg'),
    ('Ледяная горная вода', 'drinks', 80.0, 'img/drink_water.jpg'),
    ('Домашний лимонад', 'drinks', 140.0, 'img/drink_lemonade.jpg'),
])

# Сохраняем изменения
conn.commit()
conn.close()

# Сохраняем изменения
conn.commit()
conn.close()