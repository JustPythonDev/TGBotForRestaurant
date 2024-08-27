
# Нужно добавить 2 поля в таблицу 'dishes'
# total_rating = Column(Integer, default=0)
# rating_count = Column(Integer, default=0)

from telebot import TeleBot, types
from database import Session, Dishes, Reviews, Users

# Обработчик кнопки "Оставить отзыв"
@bot.message_handler(commands=['leave_review'])
def leave_review(message):
    markup = types.InlineKeyboardMarkup()

    # Поле для ввода текста отзыва
    review_text = types.InlineKeyboardButton("Ваш отзыв", callback_data="enter_review_text")
    markup.add(review_text)

    # Поле для выставления оценки ресторану
    for i in range(1, 6):
        markup.add(types.InlineKeyboardButton(f"★ {i}", callback_data=f"set_restaurant_rating_{i}"))

    # Вывод блюд из последнего заказа
    last_order_dishes = get_last_order_dishes(message.from_user.id)
    for dish in last_order_dishes:
        for i in range(1, 6):
            markup.add(
                types.InlineKeyboardButton(f"{dish.name} - ★ {i}", callback_data=f"set_dish_rating_{dish.id}_{i}"))

    # Кнопки "Читать отзывы" и "Отправить отзыв"
    markup.add(types.InlineKeyboardButton("Читать отзывы", callback_data="read_reviews"))
    markup.add(types.InlineKeyboardButton("Отправить отзыв", callback_data="submit_review"))

    bot.send_message(message.chat.id, "Пожалуйста, оставьте свой отзыв и оцените блюда:", reply_markup=markup)

# Обработчик ввода текста отзыва
@bot.callback_query_handler(func=lambda call: call.data == "enter_review_text")
def enter_review_text(call):
    bot.send_message(call.message.chat.id, "Введите ваш отзыв:")
    bot.register_next_step_handler(call.message, save_review_text)

def save_review_text(message):
    # Сохранение текста отзыва
    user_data[message.from_user.id]['review_text'] = message.text
    bot.send_message(message.chat.id, "Спасибо! Теперь оцените ресторан и блюда.")


# Обработчик выставления оценки ресторану
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_restaurant_rating_"))
def set_restaurant_rating(call):
    rating = int(call.data.split("_")[-1])
    user_data[call.from_user.id]['restaurant_rating'] = rating
    bot.send_message(call.message.chat.id, f"Вы поставили ресторану {rating}★")

# Обработчик выставления оценки блюдам
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_dish_rating_"))
def set_dish_rating(call):
    _, dish_id, rating = call.data.split("_")
    rating = int(rating)
    user_data[call.from_user.id]['dish_ratings'][int(dish_id)] = min(max(rating, 1), 5)
    bot.send_message(call.message.chat.id, f"Оценка {rating}★ для блюда установлена.")

# Обработчик отправки отзыва
@bot.callback_query_handler(func=lambda call: call.data == "submit_review")
def submit_review(call):
    user_id = call.from_user.id
    review_text = user_data[user_id].get('review_text')
    restaurant_rating = user_data[user_id].get('restaurant_rating')
    dish_ratings = user_data[user_id].get('dish_ratings', {})

    session = Session()
    try:
        # Сохраняем отзыв в базе данных
        if review_text and restaurant_rating:
            review = Reviews(user_id=user_id, review_text=review_text, rating=restaurant_rating,
                             review_date=datetime.datetime.utcnow())
            session.add(review)
            session.commit()

        # Обновляем рейтинг ресторану
        update_restaurant_rating(restaurant_rating, session)

        # Обновляем рейтинг для каждого блюда
        for dish_id, rating in dish_ratings.items():
            dish = session.query(Dishes).filter(Dishes.id == dish_id).one()
            dish.total_rating += rating
            dish.rating_count += 1
            session.commit()

        bot.send_message(call.message.chat.id, "Спасибо, Ваш отзыв отправлен.")
    except Exception as e:
        session.rollback()
        bot.send_message(call.message.chat.id, "Произошла ошибка, попробуйте позже.")
    finally:
        session.close()

# Обработчик кнопки "Читать отзывы"
@bot.callback_query_handler(func=lambda call: call.data == "read_reviews")
def read_reviews(call):
    session = Session()
    try:
        reviews = session.query(Reviews).order_by(Reviews.review_date.desc()).limit(5).all()
        avg_rating = session.query(func.avg(Reviews.rating)).scalar()
        total_reviews = session.query(Reviews).count()

        bot.send_message(call.message.chat.id,
                         f"Средний рейтинг ресторана: {avg_rating:.1f}★ по результатам {total_reviews} отзывов.")

        for review in reviews:
            bot.send_message(call.message.chat.id, f"{review.review_text}\nРейтинг: {review.rating}★")

        # Кнопка для загрузки больше отзывов
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Больше отзывов", callback_data="load_more_reviews"))
        bot.send_message(call.message.chat.id, "Вот несколько отзывов:", reply_markup=markup)
    except Exception as e:
        bot.send_message(call.message.chat.id, "Произошла ошибка при загрузке отзывов.")
    finally:
        session.close()

# Обработчик загрузки большего количества отзывов
@bot.callback_query_handler(func=lambda call: call.data == "load_more_reviews")
def load_more_reviews(call):
    # Логика для загрузки следующих 10 отзывов
    pass

# Функция для обновления среднего рейтинга ресторана
def update_restaurant_rating(new_rating, session):
    total_reviews = session.query(Reviews).count()
    if total_reviews == 0:
        return
    avg_rating = session.query(func.avg(Reviews.rating)).scalar()

    avg_rating = (avg_rating * total_reviews + new_rating) / (total_reviews + 1)
    return avg_rating

# Функция для получения блюд из последнего заказа пользователя
def get_last_order_dishes(user_id):
    session = Session()
    last_order = session.query(Orders).filter(Orders.user_id == user_id).order_by(Orders.order_date.desc()).first()
    if last_order:
        dishes = session.query(Dishes).filter(Dishes.order_id == last_order.id).all()
        return dishes
    return []

# Словарь для хранения временных данных о пользователе
user_data = {}

bot.polling()

