import telebot
from telebot import types
from config import TELEGRAM_API_TOKEN
from db_library import Database, MenuItem
import os

class Menu:
    def __init__(self):
        # Создаем экземпляр базы данных и получаем сессию
        self.db = Database()
        self.session = self.db.get_session()
        self.last_menu = ""

    def create_menu_keyboard(self, parent_callback):
        # Создание клавиатуры для текущего уровня меню
        markup = types.InlineKeyboardMarkup()

        # Получение элементов меню из базы данных
        filtered_menu = MenuItem.get_menu_items_by_parent(self.session, parent_callback)

        for item in filtered_menu:
            button = types.InlineKeyboardButton(item["name"], callback_data=item["callback"])
            markup.add(button)

        # Если это не главное меню, добавляем кнопку для возврата
        if parent_callback is not None and parent_callback != "start":
            parent_of_parent = self.get_parent_menu_callback(parent_callback)
            if parent_of_parent is None:
                parent_of_parent = "start"
            back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_" + parent_of_parent)
            markup.add(back_button)

        return markup

    def get_menu_text(self, callback):
        # Получение текста для меню на основе callback
        item = MenuItem.get_menu_item_data(self.session, callback)
        if item:
            return item['text']
        return None

    def get_image_url(self, callback):
        # Получение URL изображения для меню на основе callback
        item = MenuItem.get_menu_item_data(self.session, callback)
        if item:
            return item['image_url']
        return None

    def get_parent_menu_callback(self, callback):
        # Получение родительского меню на основе значения callback
        item = MenuItem.get_menu_item_data(self.session, callback)
        if item:
            return item['parent_menu']
        return None


# Токен вашего бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Создаем экземпляр класса Menu
menu = Menu()


def process_menu(user_id, parent_callback, msg=None):
    # Создание клавиатуры и получение текста и изображения
    if parent_callback == menu.last_menu:
        return
    else:
        menu.last_menu = parent_callback

    menu_keys = menu.create_menu_keyboard(parent_callback)
    menu_text = menu.get_menu_text(parent_callback)
    image_url = menu.get_image_url(parent_callback)

    # Проверяем, если image_url указан и файл существует
    if image_url and os.path.isfile(image_url):
        image_media = types.InputMediaPhoto(media=open(image_url, 'rb'), caption=menu_text)
    else:
        image_media = None

    # Если есть изображение в сообщении и есть изображение для меню - редактируем изображение
    if msg:
        if msg.photo:
            if image_media:
                bot.edit_message_media(
                    media=image_media,
                    chat_id=user_id,
                    message_id=msg.message_id,
                    reply_markup=menu_keys
                )
            elif msg.text:
                bot.edit_message_text(text=menu_text,
                                      chat_id=user_id,
                                      message_id=msg.message_id,
                                      reply_markup=menu_keys)
            else:
                bot.send_message(user_id, text=menu_text, reply_markup=menu_keys)

           # bot.delete_message(chat_id=user_id, message_id=msg.message_id)
        elif image_media:
            with open(image_url, 'rb') as photo:
                bot.send_photo(
                    user_id,
                    image_media.media,
                    caption=menu_text,
                    reply_markup=menu_keys
                )

            if msg.text:
                bot.delete_message(chat_id=user_id, message_id=msg.message_id)
        elif msg.text:
            # Если картинки нет, просто редактируем текст
            bot.edit_message_text(text=menu_text,
                                  chat_id=user_id,
                                  message_id=msg.message_id,
                                  reply_markup=menu_keys)
        else:
            bot.send_message(user_id, text=menu_text, reply_markup=menu_keys)
    else:
        if image_media:
            bot.send_photo(
                user_id,
                image_media.media,
                caption=menu_text,
                reply_markup=menu_keys
            )
        else:
            bot.send_message(user_id, text=menu_text, reply_markup=menu_keys)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    process_menu(user_id, "start", msg=message)


# Обработчик нажатий на inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    parent_callback = call.data[len("back_to_"): ] if call.data.startswith("back_to_") else call.data
    # Вызываем process_menu для обработки inline-кнопок
    process_menu(user_id, parent_callback, msg=call.message)


bot.polling()
