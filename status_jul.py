from database import Orders, Base

def check_order_statuses(user_id):

    orders = get_orders_by_user_id(user_id=user_id)


    if orders:
        status_message = ""
        for order in orders:
            status_message += f"ID заказа: {order.id}\n" \
                              f"Сумма: {order.total_amount}\n" \
                              f"Статус вашего заказа: {order.status}\n\n\n"
    else:
        status_message = "У вас нет активных заказов на сегодня."

    return status_message
