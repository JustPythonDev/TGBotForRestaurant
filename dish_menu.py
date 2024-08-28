from telebot import types
from db_library import MenuItems, Dishes, Cart

def dishes_menu_start(callback, user_id):
    if MenuItems.check_is_menu_callback(callback):
        dish_messages = view_category_dishes_menu(callback)
    elif callback.startswith("menu_order_"):
        dish_messages = add_dish_from_menu_to_cart(callback, user_id)
    elif callback.startswith("menu_remove_"):
        dish_messages = remove_dish_from_menu_from_cart(callback, user_id)

    return dish_messages


def view_category_dishes_menu(callback):
    # Получаем список блюд из базы данных
    dishes_list = Dishes.get_dishes_by_menu_callback(callback)
    dish_messages = []
    # Если список блюд пуст, отправляем сообщение об этом
    if not dishes_list:
        return dish_messages

    for dish in dishes_list:
        # Создаем разметку с кнопкой для каждого изображения
        # markup = types.InlineKeyboardMarkup()
        # button = types.InlineKeyboardButton(text=f"Выбрать", callback_data=f"menu_order_{dish['id']}")
        # markup.add(button)
        button = {'text': 'Выбрать', 'callback_data': f'menu_order_{dish['id']}'}

        # Отправляем изображение с подписью и кнопкой
        message = f"<b>{dish['name']}</b>\nЦена: {dish['price']} руб."
        image_url = dish['image_url']
        dish_id = dish['id']

        dish_messages.append({
            'message': message,
            'image_url': image_url,
            'markup': None,
            'button': button,
            'id': dish_id
        })
    return dish_messages


def add_dish_from_menu_to_cart(callback, user_id):
    dish_id = callback[len("menu_order_")::]
    status = Cart.add_dish_to_cart(user_id, dish_id)
    # button = types.InlineKeyboardButton(text=f"ВЫБРАНО", callback_data=f"menu_remove_{dish['id']}")
    if not status:
        return
    button = {'text': '✅', 'callback_data': f'menu_remove_{dish_id}'}
    dish_messages = [{
        'message': None,
        'image_url': None,
        'markup': None,
        'button': button,
        'id': dish_id
    }]
    return dish_messages

def remove_dish_from_menu_from_cart(callback, user_id):
    dish_id = callback[len("menu_remove_")::]
    status = Cart.remove_dish_from_cart(user_id, dish_id)
    # button = types.InlineKeyboardButton(text=f"ВЫБРАНО", callback_data=f"menu_remove_{dish['id']}")
    if not status:
        return
    button = {'text': 'Выбрать', 'callback_data': f'menu_order_{dish_id}'}
    dish_messages = [{
        'message': None,
        'image_url': None,
        'markup': None,
        'button': button,
        'id': dish_id
    }]
    return dish_messages
