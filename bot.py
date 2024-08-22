import telebot
from telebot import types
from config import TELEGRAM_API_TOKEN

class Menu:
    def __init__(self):
        # Определение структуры меню
        self.menu_structure = [
            {"name": "Кафе", "text": "Добро пожаловать в наше кафе! Выберите действие:", "callback": "start", "parent_menu": None, "order": 1},
            {"name": "Меню кафе", "text": "Выберите категорию", "callback": "menu", "parent_menu": "start", "order": 1},
            {"name": "Корзина", "text": "Выбранные вами блюда", "callback": "cart", "parent_menu": "start", "order": 2},
            {"name": "Оплата заказа", "text": "Выберите способ оплаты", "callback": "payment", "parent_menu": "start", "order": 3},
            {"name": "Статус заказа", "text": "Выберите заказ для просмотра", "callback": "status", "parent_menu": "start", "order": 4},
            {"name": "Отзывы", "text": "Выберите категорию отзыва", "callback": "feedback", "parent_menu": "start", "order": 5},
            {"name": "Закуски", "text": "Выберите закуску", "callback": "main_dishes", "parent_menu": "menu", "order": 1},
            {"name": "Салаты", "text": "Выберите салат", "callback": "main_dishes", "parent_menu": "menu", "order": 2},
            {"name": "Первые блюда", "text": "Выберите суп", "callback": "soups", "parent_menu": "menu", "order": 3},
            {"name": "Основные блюда", "text": "Выберите горячее", "callback": "main_dishes", "parent_menu": "menu", "order": 4},
            {"name": "Десерты", "text": "Выберите десерт", "callback": "desserts", "parent_menu": "menu", "order": 5},
        ]
        self.user_states = {}  # Словарь для хранения состояния пользователя

    def create_menu_keyboard(self, parent_callback):
        # Создание клавиатуры для текущего уровня меню
        markup = types.InlineKeyboardMarkup()
        filtered_menu = [item for item in self.menu_structure if item['parent_menu'] == parent_callback]
        sorted_menu = sorted(filtered_menu, key=lambda x: x['order'])

        for item in sorted_menu:
            button = types.InlineKeyboardButton(item['name'], callback_data=item['callback'])
            markup.add(button)

        # Если это не главное меню, добавляем кнопку для возврата
        if parent_callback is not None:
            back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_" + parent_callback)
            markup.add(back_button)

        return markup

    def get_menu_text(self, callback):
        # Получение текста для меню на основе callback
        for item in self.menu_structure:
            if item['callback'] == callback:
                return item['text']
        return "Выберите категорию"


# Токен вашего бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Создаем экземпляр класса Menu
menu = Menu()


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_start_button(message):
    # Создаем клавиатуру с кнопкой "Старт"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton("Старт")
    markup.add(start_button)
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите 'Старт', чтобы начать.", reply_markup=markup)

# # Обработчик нажатий на кнопку "Старт"
# @bot.message_handler(func=lambda message: message.text == "Старт")
# def send_welcome(message):
#     # Отправка основного меню
#     main_menu = menu.create_menu_keyboard(None)
#     with open('img/main_photo.jpg', 'rb') as photo:
#         bot.send_photo(message.chat.id, photo,
#                        caption="Добро пожаловать в наше кафе! Выберите действие:",
#                        reply_markup=main_menu)


# Обработчик нажатий на inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id

    if call.data.startswith("back_to_"):
        parent_callback = call.data[len("back_to_"):]
        main_menu = menu.create_menu_keyboard(parent_callback)
        menu.user_states[user_id] = parent_callback  # Обновление состояния пользователя
        menu_text = menu.get_menu_text(parent_callback)
        bot.edit_message_text(text=menu_text,
                              chat_id=user_id,
                              message_id=call.message.message_id,
                              reply_markup=main_menu)
    else:
        menu.user_states[user_id] = call.data  # Сохранение состояния текущего меню
        sub_menu = menu.create_menu_keyboard(call.data)
        menu_text = menu.get_menu_text(call.data)
        if sub_menu.keyboard:
            bot.edit_message_text(text=menu_text,
                                  chat_id=user_id,
                                  message_id=call.message.message_id,
                                  reply_markup=sub_menu)
        else:
            bot.send_message(user_id, f"Вы выбрали: {call.data}")


bot.polling()
