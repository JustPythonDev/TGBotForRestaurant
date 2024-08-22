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
            parent_of_parent = self.get_parent_menu_callback(parent_callback)
            if parent_of_parent is not None:
                back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_" + parent_of_parent)
            else:
                back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_start")
            markup.add(back_button)

        return markup

    def get_menu_text(self, callback):
        # Получение текста для меню на основе callback
        for item in self.menu_structure:
            if item['callback'] == callback:
                return item['text']
        return "Выберите категорию"

    def get_parent_menu_callback(self, callback):
        for item in self.menu_structure:
            if item['callback'] == callback:
                return item['parent_menu']
        return None


# Токен вашего бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Создаем экземпляр класса Menu
menu = Menu()


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Удаление предыдущего сообщения
    if message.text:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    # Отправка основного меню
    main_menu = menu.create_menu_keyboard(None)
    with open('img/main_photo.jpg', 'rb') as photo:
        sent_message = bot.send_photo(message.chat.id, photo,
                                      caption="Добро пожаловать в наше кафе! Выберите действие:",
                                      reply_markup=main_menu)
        # Сохранение ID последнего отправленного сообщения
        menu.last_message_ids[message.chat.id] = sent_message.message_id


# Обработчик нажатий на inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id

    if call.data == "back_to_start":
        send_welcome(call.message)  # Возвращаемся на стартовое меню
        return

    if call.data.startswith("back_to_"):
        parent_callback = call.data[len("back_to_"):]
        main_menu = menu.create_menu_keyboard(parent_callback)
        menu.user_states[user_id] = parent_callback  # Обновление состояния пользователя
        menu_text = menu.get_menu_text(parent_callback)

        if call.message.text:  # Проверка на наличие текста в сообщении
            bot.edit_message_text(text=menu_text,
                                  chat_id=user_id,
                                  message_id=call.message.message_id,
                                  reply_markup=main_menu)
        else:
            bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
            bot.send_message(user_id, text=menu_text, reply_markup=main_menu)

    else:
        menu.user_states[user_id] = call.data  # Сохранение состояния текущего меню
        sub_menu = menu.create_menu_keyboard(call.data)
        menu_text = menu.get_menu_text(call.data)

        if sub_menu.keyboard:
            if call.message.text:  # Проверка на наличие текста в сообщении
                bot.edit_message_text(text=menu_text,
                                      chat_id=user_id,
                                      message_id=call.message.message_id,
                                      reply_markup=sub_menu)
            else:
                bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                bot.send_message(user_id, text=menu_text, reply_markup=sub_menu)
        else:
            bot.send_message(user_id, f"Вы выбрали: {call.data}")


bot.polling()
