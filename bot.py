import telebot
from telebot import types
from config import TELEGRAM_API_TOKEN

class Menu:
    def __init__(self):
        # Определение структуры меню
        self.menu_structure = [
            {"name": "Меню кафе", "text": "Выберите категорию", "callback": "menu", "parent_menu": None, "order": 1},
            {"name": "Корзина", "text": "Выбранные вами блюда", "callback": "cart", "parent_menu": None, "order": 2},
            {"name": "Оплата заказа", "text": "Выберите способ оплаты", "callback": "payment", "parent_menu": None, "order": 3},
            {"name": "Статус заказа", "text": "Выберите заказ для просмотра", "callback": "status", "parent_menu": None, "order": 4},
            {"name": "Отзывы", "text": "Выберите категорию отзыва", "callback": "feedback", "parent_menu": None, "order": 5},
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


# Токен вашего бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Создаем экземпляр класса Menu
menu = Menu()


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Отправка основного меню
    main_menu = menu.create_menu_keyboard(None)
    with open('img/main_photo.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo,
                       caption="Добро пожаловать в наше кафе! Выберите действие:",
                       reply_markup=main_menu)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id

    if call.data.startswith("back_to_"):
        parent_callback = call.data[len("back_to_"):]
        main_menu = menu.create_menu_keyboard(parent_callback)
        menu.user_states[user_id] = parent_callback  # Обновление состояния пользователя
        if call.message.text:  # Убедитесь, что сообщение содержит текст
            bot.edit_message_text(text="Выберите категорию из раздела.",
                                  chat_id=user_id,
                                  message_id=call.message.message_id,
                                  reply_markup=main_menu)
        else:
            bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
            bot.send_message(user_id, "Выберите категорию из раздела.", reply_markup=main_menu)
    else:
        menu.user_states[user_id] = call.data  # Сохранение состояния текущего меню
        sub_menu = menu.create_menu_keyboard(call.data)
        if sub_menu.keyboard:
            if call.message.text:  # Убедитесь, что сообщение содержит текст
                bot.edit_message_text(text="Выберите категорию из раздела.",
                                      chat_id=user_id,
                                      message_id=call.message.message_id,
                                      reply_markup=sub_menu)
            else:
                bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                bot.send_message(user_id, "Выберите категорию из раздела.", reply_markup=sub_menu)
        else:
            bot.send_message(user_id, f"Вы выбрали: {call.data}")


bot.polling()

