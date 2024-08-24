
# Обработчик команды для оставления отзыва
@bot.message_handler(commands=['leave_review'])
def handle_leave_review(message):
    bot.send_message(message.chat.id, "Пожалуйста, оцените ваш опыт от 1 до 5 звёзд.")
    bot.register_next_step_handler(message, process_rating_step)

def process_rating_step(message):
    try:
        rating = int(message.text)
        if 1 <= rating <= 5:
            bot.send_message(message.chat.id, "Пожалуйста, оставьте текстовый комментарий.")
            bot.register_next_step_handler(message, lambda msg: process_comment_step(msg, rating))
        else:
            bot.send_message(message.chat.id, "Оценка должна быть от 1 до 5. Попробуйте снова.")
            handle_leave_review(message)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число от 1 до 5.")
        handle_leave_review(message)

def process_review_text_step(message, rating):
    review_text = message.text
    user_id = message.from_user.id
    cur.execute('INSERT INTO reviews (user_id, rating, review_text) VALUES (?, ?, ?)', (user_id, rating, review_text))
    conn.commit()
    bot.send_message(message.chat.id, "Спасибо за ваш отзыв! Он был успешно сохранён.")

# Обработчик команды для чтения отзывов
@bot.message_handler(commands=['read_reviews'])
def handle_read_reviews(message):
    cur.execute('SELECT rating, comment FROM reviews ORDER BY id DESC LIMIT 5')
    reviews = cur.fetchall()

    if reviews:
        response = "\n\n".join([f"Оценка: {rating}\nКомментарий: {review_text}" for rating, review_text in reviews])
        bot.send_message(message.chat.id, response)

        # Подсчёт средней оценки
        cur.execute('SELECT AVG(rating), COUNT(*) FROM reviews')
        avg_rating, total_reviews = cur.fetchone()
        bot.send_message(message.chat.id, f"Средняя оценка: {avg_rating:.1f}, Всего отзывов: {total_reviews}")
    else:
        bot.send_message(message.chat.id, "Пока нет отзывов.")

