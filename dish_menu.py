from db_library import MenuItems, Dishes, Cart

def dishes_menu_start(callback, user_id):
    dish_messages = []
    if MenuItems.check_is_menu_callback(callback):
        dish_messages = view_category_dishes_menu(callback, user_id)
    elif callback.startswith("menu_order_"):
        dish_messages = add_dish_from_menu_to_cart(callback, user_id)
    elif callback.startswith("menu_remove_"):
        dish_messages = remove_dish_from_menu_from_cart(callback, user_id)

    return dish_messages


def view_category_dishes_menu(callback, user_id):
    # Получаем список блюд из базы данных
    dishes_list = Dishes.get_dishes_by_menu_callback(callback)
    dish_messages = []
    # Если список блюд пуст, отправляем сообщение об этом
    if not dishes_list:
        return dish_messages

    for dish in dishes_list:
        dish_id = dish['id']

        if Cart.check_is_dish_in_cart(user_id, dish_id):
            button = {'text': '✅', 'callback_data': f'menu_remove_{dish_id}'}
        else:
            button = {'text': 'Выбрать', 'callback_data': f'menu_order_{dish_id}'}

        # Отправляем изображение с подписью и кнопкой
        message = f"<b>{dish['name']}</b>\nЦена: {dish['price']} руб."
        image_url = dish['image_url']

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
    if not status:
        return
    button = {'text': '✅', 'callback_data': f'menu_remove_{dish_id}'}

    return [{
        'message': None,
        'image_url': None,
        'markup': None,
        'button': button,
        'id': dish_id
    }]

def remove_dish_from_menu_from_cart(callback, user_id):
    dish_id = callback[len("menu_remove_")::]
    status = Cart.remove_dish_from_cart(user_id, dish_id)
    if not status:
        return
    button = {'text': 'Выбрать', 'callback_data': f'menu_order_{dish_id}'}

    return [{
        'message': None,
        'image_url': None,
        'markup': None,
        'button': button,
        'id': dish_id
    }]