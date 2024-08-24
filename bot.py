import telebot
from telebot import types
from config import TELEGRAM_API_TOKEN
from db_library import Database, MenuItem
import os

class Menu:
    def __init__(self):
        # Определение структуры меню
        self.menu_structure = [
            {"name": "Меню кафе", "text": "Выберите категорию блюда", "callback": "menu", "parent_menu": None, "order_by": 1,
             "image_url": ""},
            {"name": "Корзина", "text": "Выбранные вами блюда", "callback": "cart", "parent_menu": None, "order_by": 2,
             "image_url": ""},
            {"name": "Оплата заказа", "text": "Выберите способ оплаты", "callback": "payment", "parent_menu": None,
             "order_by": 3, "image_url": ""},
            {"name": "Статус заказа", "text": "Выберите заказ для просмотра", "callback": "status", "parent_menu": None,
             "order_by": 4, "image_url": ""},
            {"name": "Отзывы", "text": "Выберите категорию отзыва", "callback": "feedback", "parent_menu": None,
             "order_by": 5, "image_url": ""},
            {"name": "Закуски", "text": "Выберите закуску", "callback": "appetizers", "parent_menu": "menu",
             "order_by": 1, "image_url": "img/appetizers.jpg"},
            {"name": "Салаты", "text": "Выберите салат", "callback": "salads", "parent_menu": "menu", "order_by": 2,
             "image_url": "img/salads.jpg"},
            {"name": "Первые блюда", "text": "Выберите суп", "callback": "soups", "parent_menu": "menu", "order_by": 3,
             "image_url": "img/soups.jpg"},
            {"name": "Основные блюда", "text": "Выберите горячее", "callback": "main_dishes", "parent_menu": "menu",
             "order_by": 4, "image_url": "img/main_dishes.jpg"},
            {"name": "Десерты", "text": "Выберите десерт", "callback": "desserts", "parent_menu": "menu", "order_by": 5,
             "image_url": ""}
        ]
        self.user_states = {}  # Словарь для хранения состояния пользователя

    def create_menu_keyboard(self, parent_callback):
        # Создание клавиатуры для текущего уровня меню
        markup = types.InlineKeyboardMarkup()
        filtered_menu = [item for item in self.menu_structure if item['parent_menu'] == parent_callback]
        sorted_menu = sorted(filtered_menu, key=lambda x: x['order_by'])

        for item in sorted_menu:
            button = types.InlineKeyboardButton(item['name'], callback_data=item['callback'])
            markup.add(button)

        # Если это не главное меню, добавляем кнопку для возврата
        if parent_callback is not None:
            parent_of_parent = self.get_parent_menu_callback(parent_callback)
            if parent_of_parent is None:
                parent_of_parent = "start"
            back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_" + parent_of_parent)
            markup.add(back_button)

        return markup

    def get_menu_text(self, callback):
        # Получение текста для меню на основе callback
        for item in self.menu_structure:
            if item['callback'] == callback:
                return item['text']
        return "Выберите категорию"

    def get_image_url(self, callback):
        # Получение URL изображения для меню на основе callback
        for item in self.menu_structure:
            if item['callback'] == callback:
                return item['image_url']
        return None

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
    # Отправка основного меню
    main_menu = menu.create_menu_keyboard(None)
    with open('img/main_photo.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo,
                                    caption="Добро пожаловать в наше кафе! Выберите действие:",
                                    reply_markup=main_menu)
    # Удаление предыдущего сообщения
    if message.text:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# Обработчик нажатий на inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id

    if call.data == "back_to_start":
        send_welcome(call.message)  # Возвращаемся на стартовое меню
        return

    if call.data.startswith("back_to_"):
        parent_callback = call.data[len("back_to_"):]

    else:
        parent_callback = call.data

    # menu.user_states[user_id] = parent_callback  # Обновление состояния пользователя
    menu_keys = menu.create_menu_keyboard(parent_callback)
    menu_text = menu.get_menu_text(parent_callback)
    image_url = menu.get_image_url(parent_callback)

    if not os.path.isfile(image_url):
        image_url = None

    # Если есть изображение в сообщении и есть изображение для меню - редактируем изображение
    if call.message.photo:
        if image_url:
            bot.edit_message_media(
                media=types.InputMediaPhoto(media=image_url, caption=menu_text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=menu_keys
            )
        elif call.message.text:
            bot.edit_message_text(text=menu_text,
                              chat_id=user_id,
                              message_id=call.message.message_id,
                              reply_markup=menu_keys)
        else:
            bot.send_message(user_id, text=menu_text, reply_markup=menu_keys)

        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    elif image_url:
        with open(image_url, 'rb') as photo:
            bot.send_photo(
                user_id,
                photo,
                caption=menu_text,
                reply_markup=menu_keys
            )

        if call.message.text:
            bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    elif call.message.text:
        # Если картинки нет, просто редактируем текст
        bot.edit_message_text(text=menu_text,
                              chat_id=user_id,
                              message_id=call.message.message_id,
                              reply_markup=menu_keys)
    else:
        bot.send_message(user_id, text=menu_text, reply_markup=menu_keys)


bot.polling()
