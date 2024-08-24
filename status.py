# from telebot import TeleBot, types
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from your_database_file import Orders, Base  # Импортируйте ваши модели

# Обработчик нажатия кнопки "Статус заказа"
@bot.message_handler(func=lambda message: message.text == "Статус заказа")
def check_order_status(message):
    user_id = message.chat.id

    # Извлечение последнего заказа пользователя из базы данных
    order = session.query(Orders).filter_by(user_id=user_id).order_by(Orders.order_date.desc()).first()

    if order:
        # Формирование сообщения о статусе заказа
        status_message = f"Статус вашего заказа:\n\n" \
                         f"ID заказа: {order.id}\n" \
                         f"Сумма: {order.total_amount}\n" \
                         f"Адрес доставки: {order.delivery_address}\n" \
                         f"Статус: {order.status}\n" \
                         f"Дата заказа: {order.order_date}"
    else:
        status_message= "У вас нет активных заказов."

    # Отправка сообщения пользователю
    bot.send_message(message.chat.id, status_message)

# Запуск бота
bot.polling()

