from db_library import Cart

def payment_menu_start(callback, user_id):
    if callback == 'payment':
        return view_payment_data(user_id)
    elif callback.startswith("payment_cash"):
        return process_cash_payment(user_id)
    elif callback.startswith("payment_card"):
        return process_card_payment(user_id)


def view_payment_data(user_id):
    total_amount = Cart.get_cart_total_amount(user_id)

    if total_amount == 0:
        return [{
            'message': 'Корзина пуста. Сформируйте заказ',
            'image_url': None,
            'markup': None,
            'buttons': None,
            'id': None
        }]

    payment_message = f'Сумма заказа - {total_amount} руб.'
    payment_buttons = [
        {'text': 'Наличные', 'callback_data': 'payment_cash'},
        {'text': 'Онлайн', 'callback_data': 'payment_card'}
    ]
    return [{
        'message': payment_message,
        'image_url': None,
        'markup': None,
        'buttons': payment_buttons,
        'id': None
    }]


def process_card_payment(user_id):
    payment_status = "оплачен картой"
    total_amount = Cart.get_cart_total_amount(user_id)

    order_id = Cart.create_order_from_cart(user_id, payment_status)
    if not order_id:
        return [{
            'message': "Ошибка",
            'image_url': None,
            'markup': None,
            'buttons': None,
            'id': None
        }]

    payment_message = f'Заказ № {order_id} на сумму {total_amount} оплачен и принят к исполнению.'
    return [{
        'message': payment_message,
        'image_url': None,
        'markup': None,
        'buttons': None,
        'id': None
    }]


def process_cash_payment(user_id):
    payment_status = "не оплачено"
    total_amount = Cart.get_cart_total_amount(user_id)

    order_id = Cart.create_order_from_cart(user_id, payment_status)
    if not order_id:
        return [{
            'message': "Ошибка",
            'image_url': None,
            'markup': None,
            'buttons': None,
            'id': None
        }]

    payment_message = f'Заказ № {order_id} на сумму {total_amount} принят к исполнению, оплата наличными курьеру'
    return [{
        'message': payment_message,
        'image_url': None,
        'markup': None,
        'buttons': None,
        'id': None
    }]



if __name__ == "__main__":
    # item = Cart.get_cart_total_amount(1295753599)

    item = process_card_payment(1295753599)
    print(item)