# Нужно добавить поле в таблицу 'orders'
# status = Column(String, nullable=False)

import telebot
from telebot import types
from sqlalchemy.orm import sessionmaker
from database import engine, Cart, Orders, Dishes
import time  # для симуляции задержек

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()

bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')

@bot.message_handler(commands=['start', 'cart'])
def show_cart(message):
    user_id = message.from_user.id
    cart_items = session.query(Cart).filter_by(user_id=user_id).all()

    if not cart_items:
        bot.send_message(message.chat.id, "Ваша корзина пуста.")
        return

    total_amount = 0
    for item in cart_items:
        dish = session.query(Dishes).filter_by(id=item.dish_id).first()
        item_total = dish.price * item.quantity
        total_amount += item_total

        # Отображение блюда с картинкой и количеством
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"Удалить {dish.name}", callback_data=f"delete_{dish.id}"))
        bot.send_photo(message.chat.id, dish.image_url, caption=f"{dish.name}, {dish.price} руб. x {item.quantity} = {item_total} руб.", reply_markup=markup)

    # Итоговая сумма
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Наличными"), types.KeyboardButton("Онлайн-платеж"))
    bot.send_message(message.chat.id, f"Итоговая сумма: {total_amount} руб.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_item_from_cart(call):
    user_id = call.from_user.id
    dish_id = int(call.data.split('_')[1])
    cart_item = session.query(Cart).filter_by(user_id=user_id, dish_id=dish_id).first()

    if cart_item:
        session.delete(cart_item)
        session.commit()
        bot.answer_callback_query(call.id, "Блюдо удалено из корзины.")
    else:
        bot.answer_callback_query(call.id, "Блюдо не найдено в корзине.")

    show_cart(call.message)

@bot.message_handler(func=lambda message: message.text in ["Наличными", "Онлайн-платеж"])
def choose_payment_method(message):
    user_id = message.from_user.id
    cart_items = session.query(Cart).filter_by(user_id=user_id).all()

    if not cart_items:
        bot.send_message(message.chat.id, "Ваша корзина пуста.")
        return

    total_amount = 0
    order_items = []
    for item in cart_items:
        dish = session.query(Dishes).filter_by(id=item.dish_id).first()
        item_total = dish.price * item.quantity
        total_amount += item_total
        order_items.append((dish.name, dish.price, item.quantity, item_total))

    # Создаем заказ в базе данных
    order = Orders(
        user_id=user_id,
        total_amount=total_amount,
        payment_status="Не оплачен" if message.text == "Наличными" else "Оплачен",
        delivery_address="Ваш адрес доставки",
        order_date=time.strftime("%Y-%m-%d %H:%M:%S"),
        status="Оформлен" if message.text == "Наличными" else "Оплачен"
    )
    session.add(order)
    session.commit()

    if message.text == "Наличными":
        order_details = f"Спасибо, Вы выбрали наличный способ оплаты. Деньги получит курьер.\n\nВаш заказ № {order.id} от {order.order_date}:\n"
        for i, (name, price, quantity, item_total) in enumerate(order_items, start=1):
            order_details += f"{i}. {name}, {price} руб. x {quantity} = {item_total} руб.\n"
        order_details += f"Сумма заказа: {total_amount} руб. (Курьеру)\nАдрес: {order.delivery_address}"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Оформить заказ"))
        bot.send_message(message.chat.id, order_details, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Спасибо, вы выбрали онлайн-платеж. Соединяем Вас с терминалом оплаты.")
        time.sleep(4)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Оплатить"))
        bot.send_message(message.chat.id, "Оплатить", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Оплатить")
def process_payment(message):
    bot.send_message(message.chat.id, "Процесс оплаты...")
    time.sleep(3)
    bot.send_message(message.chat.id, "Спасибо, Ваш платеж прошел успешно. Заказ оформлен, оплачен и будет доставлен в ближайшее время.")
    # Возврат в главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Главное меню"))
    bot.send_message(message.chat.id, "Возврат в главное меню.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Оформить заказ")
def finalize_order(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Спасибо! Ваш заказ оформлен и будет доставлен в ближайшее время.")
    # Очистка корзины после оформления заказа
    session.query(Cart).filter_by(user_id=user_id).delete()
    session.commit()
    # Возврат в главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Главное меню"))
    bot.send_message(message.chat.id, "Возврат в главное меню.", reply_markup=markup)

# Запуск бота
bot.polling()
