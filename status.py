
# Нужно добавить в таблицу Order поле 'status = Column(String, nullable=False)'

from telebot import TeleBot, types
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_
from datetime import datetime
from database import Orders, Base

# Инициализация базы данных
engine = create_engine('sqlite:///data/food_ordering_system.db')
Session = sessionmaker(bind=engine)
session = Session()

# Обработчик нажатия кнопки "Статус заказа"
@bot.message_handler(func=lambda message: message.text == "Статус заказа")
def check_order_status(message):
    user_id = message.chat.id
    today = datetime.now().strftime('%Y-%m-%d')  # Получаем текущую дату в формате 'YYYY-MM-DD'

    # Извлечение всех заказов пользователя за текущий день
    orders = session.query(Orders).filter(
        and_(
            Orders.user_id == user_id,
            Orders.order_date.startswith(today)  # Предполагается, что order_date хранится в текстовом формате
        )
    ).order_by(Orders.order_date.asc()).all()

    if orders:
        status_message = ""
        for order in orders:
            status_message += f"ID заказа: {order.id}\n" \
                              f"Сумма: {order.total_amount}\n" \
                              f"Статус вашего заказа: {order.status}\n\n\n"
    else:
        status_message = "У вас нет активных заказов на сегодня."

    # Отправка сообщения пользователю
    bot.send_message(message.chat.id, status_message)

# Запуск бота
bot.polling()
