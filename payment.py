
# Функция для отображения корзины
def show_cart(chat_id):
    cursor.execute("""
        SELECT d.name, d.price, c.quantity 
        FROM cart c 
        JOIN dishes d ON c.dish_id = d.id 
        WHERE c.user_id=?
    """, (chat_id,))
    items = cursor.fetchall()

    total_price = sum(item[1] * item[2] for item in items)  # Учитываем количество
    items_list = "\n".join([f"{item[0]} (x{item[2]}) - {item[1] * item[2]} руб." for item in items])

    cart_text = f"Ваш заказ:\n{items_list}\n\nОбщая сумма: {total_price} руб."
    markup = telebot.types.InlineKeyboardMarkup()
    order_button = telebot.types.InlineKeyboardButton("Заказать", callback_data="order")
    markup.add(order_button)

    bot.send_message(chat_id, cart_text, reply_markup=markup)

# Обработчик нажатия кнопки "Заказать"
@bot.callback_query_handler(func=lambda call: call.data == "order")
def process_order(call):
    chat_id = call.message.chat.id
    # Запрос способа оплаты
    markup = telebot.types.InlineKeyboardMarkup()
    cash_button = telebot.types.InlineKeyboardButton("Наличные", callback_data="pay_cash")
    online_button = telebot.types.InlineKeyboardButton("Онлайн", callback_data="pay_online")
    markup.add(cash_button, online_button)

    bot.send_message(chat_id, "Выберите способ оплаты:", reply_markup=markup)

# Обработчик выбора оплаты наличными
@bot.callback_query_handler(func=lambda call: call.data == "pay_cash")
def cash_payment(call):
    chat_id = call.message.chat.id

    # Обновление статуса заказа в базе данных
    cursor.execute("SELECT total_amount FROM orders WHERE user_id=?", (chat_id,))
    total_price = cursor.fetchone()[0]
    cursor.execute("UPDATE orders SET status='оформлен' WHERE user_id=?", (chat_id,))
    conn.commit()

    # Сообщение пользователю
    bot.send_message(chat_id, f"Спасибо за заказ. Он принят к исполнению. Оплата в размере {total_price} руб. при получении заказа.")

# Обработчик выбора онлайн-оплаты
@bot.callback_query_handler(func=lambda call: call.data == "pay_online")
def online_payment(call):
    chat_id = call.message.chat.id
    cursor.execute("SELECT total_amount FROM orders WHERE user_id=?", (chat_id,))
    total_price = cursor.fetchone()[0]

    bot.send_message(chat_id, f"Пожалуйста, оплатите заказ на сумму {total_price} руб.")

    # Эмуляция перехода на страницу эквайринга
    time.sleep(2)

    # Интеграция с платежной системой

    # После успешной оплаты:
    bot.send_message(chat_id, "Спасибо, заказ принят к исполнению и оплачен. Он будет доставлен в ближайшее время.")