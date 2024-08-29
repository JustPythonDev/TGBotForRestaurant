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
        return cart_messages

    for dish in dishes_list:
        image_url = dish['image_url']
        dish_id = dish['dish_id']

        buttons = [
                    {'text': '➕', 'callback_data': f'cart_add_{dish_id}'},
                    {'text': '➕', 'callback_data': f'cart_add_{dish_id}'},
                    {'text': '➖', 'callback_data': f'cart_reduce_{dish_id}'}
                  ]

        message = f"<b>{dish['name']}</b>\nЦена: {dish['price']} руб."

        cart_messages.append({
            'message': message,
            'image_url': image_url,
            'markup': None,
            'buttons': buttons,
            'id': dish_id
        })
    return cart_messages
