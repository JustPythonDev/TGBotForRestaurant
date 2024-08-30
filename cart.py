from db_library import Cart

def cart_menu_start(callback, user_id):
    cart_messages = []
    if callback == 'cart':
        cart_messages = view_cart_info(user_id)
    if callback.startswith('cart_add_'):
        cart_messages = increase_dish_in_cart(callback, user_id)
    if callback.startswith('cart_reduce_'):
        cart_messages = decrease_dish_in_cart(callback, user_id)

    return cart_messages


def view_cart_info(user_id):
    # Получаем список блюд из базы данных
    dishes_list = Cart.get_cart_dishes(user_id)
    cart_messages = []
    # Если список блюд пуст, отправляем сообщение об этом
    if not dishes_list:
        cart_messages.append({
            'message': 'В корзине пока нет заказов. Зайдите в наше меню и найдите себе восхитительные блюда, которые мы делаем с любовью!',
            'image_url': None,
            'markup': None,
            'buttons': None,
            'id': None
        })
        return cart_messages

    for dish in dishes_list:
        dish_id = dish['dish_id']
        name = dish['name']
        price = dish['price']
        image_url = dish['image_url']
        quantity = dish['quantity']

        buttons = [
                    {'text': '🔺➕', 'callback_data': f'cart_add_{dish_id}'},
                    {'text': quantity, 'callback_data': f'cart_q_{dish_id}'},
                    {'text': '🔻➖', 'callback_data': f'cart_reduce_{dish_id}'}
                  ]

        message = f"<b>{name}</b>\nЦена: {price} руб."

        cart_messages.append({
            'message': message,
            'image_url': image_url,
            'markup': None,
            'buttons': buttons,
            'id': dish_id
        })

    return cart_messages


def increase_dish_in_cart(callback, user_id):
    dish_id = callback[len("cart_add_")::]
    quantity = Cart.add_dish_to_cart(user_id, dish_id)
    if quantity == 0:
        return

    buttons = [
        {'text': '🔺➕', 'callback_data': f'cart_add_{dish_id}'},
        {'text': quantity, 'callback_data': f'cart_q_{dish_id}'},
        {'text': '🔻➖', 'callback_data': f'cart_reduce_{dish_id}'}
    ]

    cart_messages = [{
            'message': None,
            'image_url': None,
            'markup': None,
            'buttons': buttons,
            'id': dish_id
        }]
    return cart_messages


def decrease_dish_in_cart(callback, user_id):
    dish_id = callback[len("cart_reduce_")::]
    quantity = Cart.decrement_dish_quantity(user_id, dish_id)
    if quantity is None:
        return
    # удалять из списка! продумать
    print(quantity)
    buttons = [
        {'text': '➕', 'callback_data': f'cart_add_{dish_id}'},
        {'text': quantity, 'callback_data': f'cart_q_{dish_id}'},
        {'text': '➖', 'callback_data': f'cart_reduce_{dish_id}'}
    ]

    cart_messages = [{
            'message': None,
            'image_url': None,
            'markup': None,
            'buttons': buttons,
            'id': dish_id
        }]
    return cart_messages




if __name__ == '__main__':
    items = view_cart_info(1295753599)
    for item in items:
        print(item)
    increase_dish_in_cart('cart_add_4', 1295753599)
    items = view_cart_info(1295753599)
    for item in items:
        print(item)