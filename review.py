from db_library import Reviews

# Метод 'create_review(rating)'
# Создает новый отзыв, принимает user_id и rating

# Метод 'get_review_stats'
# Возвращает средний рейтинг (rating) по всем записям
# Если нет отзывов, возвращает 0

def review_menu_start(callback, user_id):
    review_messages = []
    if callback == 'set_review':
        review_messages = set_review(user_id)
    if callback == 'view_reviews':
        review_messages = view_reviews(user_id)
    if callback.startswith("create_review_"):
        review_messages = create_review(callback, user_id)

    return review_messages


def view_reviews(user_id):
    # Получаем средний рейтинг по всем отзывам в БД
    rating = Reviews.get_review_stats()

    review_messages = []
    if rating == 0:
        # buttons = [{'text': 'Оставить первый отзыв', 'callback_data': 'set_review'}]
        review_messages.append({
            'message': 'Пока у нас нет отзывов о кафе. Ваш отзыв может стать первым!',
            'image_url': None,
            'markup': None,
            'buttons': None,
            'id': None
        })
    else:
        review_messages.append({
            'message': f'Пользователи оценили наше кафе в среднем на {rating} баллов из 5',
            'image_url': None,
            'markup': None,
            'buttons': None,
            'id': None
        })
    return review_messages

def set_review(user_id):
    review_messages = []
    buttons = [
        {'text': '⭐️⭐️⭐️⭐️⭐️', 'callback_data': 'create_review_5'},
        {'text': '⭐️⭐️⭐️⭐️', 'callback_data': 'create_review_4'},
        {'text': '⭐️⭐️⭐️', 'callback_data': 'create_review_3'},
        {'text': '⭐️⭐️', 'callback_data': 'create_review_2'},
        {'text': '⭐️', 'callback_data': 'create_review_1'}
    ]
    review_messages.append({
        'message': 'Укажите оценку заведения от 1 до 5',
        'image_url': None,
        'markup': None,
        'buttons': buttons,
        'id': None
    })
    return review_messages

# Отправляем оценку в БД
def create_review(callback, user_id):
    rating = callback[len("create_review_")::]

    Reviews.create_review(user_id, rating)


    return [{
        'message': "Спасибо, ваш отзыв принят",
        'image_url': None,
        'markup': None,
        'buttons': None,
        'id': None
    }]