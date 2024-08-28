from database import Orders, Base

def check_order_statuses(user_id):

    orders = get_orders_by_user_id(user_id=user_id)

    if orders:
        status_message = ""
        for order in orders:
            status_message += f"Ваш заказ {order.id} на сумму {order.total_amount} {order.status}\n\n\n"
    else:
        status_message = "У вас нет активных заказов на сегодня."

    return status_message

