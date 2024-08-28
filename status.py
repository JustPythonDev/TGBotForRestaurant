from db_library import Orders

def status_menu_start(callback, user_id):
    status_messages = check_order_statuses(user_id)
    return status_messages

def check_order_statuses(user_id):
    orders = Orders.get_orders_by_user_id(user_id=user_id)
    if orders:
        status_message = ""
        for order in orders:
            status_message += (f"Заказ № <b>{order['id']}</b> на сумму <b>{order['total_amount']}</b>. "
                               f"Статус оплаты: <b>{order['payment_status']}</b>. Статус заказа: <b>{order['order_status']}</b>\n")
    else:
        status_message = "У вас нет активных заказов на сегодня."

    return [{
        'message': status_message,
        'image_url': None,
        'markup': None,
        'button': None,
        'id': None
    }]

