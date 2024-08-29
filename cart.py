from db_library import Dishes, Cart

def cart_menu_start(callback, user_id):
    cart_messages = []
    if callback == 'cart':
        cart_messages = view_cart_info(user_id)

    return cart_messages


def view_cart_info(user_id):
    # Получаем список блюд из базы данных
    dishes_list = Cart.get_cart_dishes(user_id)
    cart_messages = []
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

        cart_messages.append({
            'message': message,
            'image_url': image_url,
            'markup': None,
            'button': button,
            'id': dish_id
        })
    return cart_messages
