import telebot
from telebot import types
import time
import os

from config import TELEGRAM_API_TOKEN
from db_library import MenuItems
from dish_menu import dishes_menu_start
from status import status_menu_start
from cart import cart_menu_start
from payment import payment_menu_start
from review import review_menu_start


class Menu:
    def __init__(self):
        self.last_menu = {}

    def create_menu_keyboard(self, callback):
        # Создание клавиатуры для текущего уровня меню
        markup = types.InlineKeyboardMarkup()

        if not MenuItems.check_is_menu_callback(callback):
            return None

        filtered_menu = MenuItems.get_menu_items_by_parent(callback)

        for item in filtered_menu:
            button = types.InlineKeyboardButton(item["name"], callback_data=item["callback"])
            markup.add(button)

        parent_callback = self.item(callback)['parent_menu']

        # Если это не главное меню, добавляем кнопку для возврата
        if parent_callback:
            back_button = types.InlineKeyboardButton("↩️ Назад", callback_data="back_to_" + parent_callback)
            markup.add(back_button)

        return markup

    def item(self, callback):
        # Получение текста для меню на основе callback
        item = MenuItems.get_menu_item_data(callback)
        if item:
            return item


class Messages:
    sent_messages = {}  # Переместили инициализацию переменной выше

    @classmethod
    def save_message_id(cls, user_id, message_id, id):
        """Сохраняет ID сообщения, отправленного ботом, с привязкой к идентификатору."""

        # Проверяем, есть ли уже записи для данного пользователя
        if user_id not in cls.sent_messages:
            cls.sent_messages[user_id] = {}  # Инициализируем словарь для конкретного пользователя

        # Сохраняем id под конкретным message_id
        cls.sent_messages[user_id][message_id] = id

    @classmethod
    def clear_chat_history(cls, user_id):
        """Удаляет все сообщения, отправленные ботом в данном чате."""
        if user_id in cls.sent_messages:
            # Получаем список message_id для удаления
            message_ids = list(cls.sent_messages[user_id].keys())

            for message_id in message_ids:
                try:
                    bot.delete_message(user_id, message_id)
                    time.sleep(0.05)  # Задержка, чтобы избежать лимитов API
                except Exception as e:
                    print(f"Не удалось удалить сообщение {message_id}: {e}")

            # Очистка словаря сообщений после их удаления
            cls.sent_messages[user_id] = {}

    @classmethod
    def send_new_message(cls, user_id, msg_text, image_url, markup_keys, buttons, id, old_message):
        """Отправка сообщения - только текст или текст/картинка + markup_keys
        Сохраняет ID сообщения, отправленного ботом, с привязкой к идентификатору"""
        try:
            if not markup_keys and buttons:
                markup_keys = types.InlineKeyboardMarkup()
                for button in buttons:
                    markup_button = types.InlineKeyboardButton(button["text"], callback_data=button["callback_data"])
                    markup_keys.add(markup_button)

            if not msg_text and old_message and markup_keys: # нет текста - меняем только кнопки у старого сообщения
                bot.edit_message_reply_markup(
                              chat_id=user_id,
                              message_id=old_message.message_id,
                              reply_markup=markup_keys)
                return

            with open(image_url, 'rb') as photo:
                msg = bot.send_photo(
                    user_id,
                    photo,
                    caption=msg_text,
                    reply_markup=markup_keys)
            cls.save_message_id(user_id, msg.message_id, id)
        except (TypeError, FileNotFoundError):
            msg = bot.send_message(
                user_id,
                text=msg_text,
                reply_markup=markup_keys
            )
            cls.save_message_id(user_id, msg.message_id, id)


# Токен вашего бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN, parse_mode='HTML')

# Создаем экземпляр класса Menu
menu = Menu()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    process_menu("start", message)


# Обработчик нажатий на inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("back_to_"):
        callback = call.data[len("back_to_"):]
        # if callback == "menu":
        Messages.clear_chat_history(call.message.chat.id)
    else:
        callback = call.data

    if callback.startswith("order_"):
        pass
    process_menu(callback, call.message)


def process_menu(callback, message):
    user_id = message.chat.id
    if user_id not in menu.last_menu:
        menu.last_menu[user_id] = {}

    menu_keys = menu.create_menu_keyboard(callback)

    if menu_keys:
        if callback == menu.last_menu[user_id] and callback != 'start':
            return

        menu_text = menu.item(callback)['text']
        image_url = menu.item(callback)['image_url']
        menu.last_menu[user_id] = callback

        send_or_change_menu_msg(user_id, menu_text, menu_keys, image_url, message)

    messages = []
    # выбрали категорию пункта "Меню кафе" или находимся в ней
    if menu.item(callback)['parent_menu'] == 'menu' or callback.startswith("menu_"):
        messages = dishes_menu_start(callback, user_id)
    elif callback.startswith("status"):
        messages = status_menu_start(callback, user_id)
    elif callback.startswith("cart"):
        messages = cart_menu_start(callback, user_id)
    elif callback.startswith("payment"):
        messages = payment_menu_start(callback, user_id)
    elif 'review' in callback:
        messages = review_menu_start(callback, user_id)


    if messages:
        for msg in messages:
            Messages.send_new_message(user_id, msg['message'], msg['image_url'],
                                      msg['markup'], msg['buttons'], msg['id'], message)

def send_or_change_menu_msg(user_id, menu_text, menu_keys=None, image_url=None, old_msg=None):
    if image_url and os.path.isfile(image_url):
        image_media = types.InputMediaPhoto(media=open(image_url, 'rb'), caption=menu_text)
    else:
        image_media = None

    # Если есть изображение в сообщении и есть изображение для меню - редактируем изображение
    if old_msg:
        if old_msg.photo:
            if image_media:
                bot.edit_message_media(
                    media=image_media,
                    chat_id=user_id,
                    message_id=old_msg.message_id,
                    reply_markup=menu_keys
                )
            else:
                bot.delete_message(chat_id=user_id, message_id=old_msg.message_id)
                bot.send_message(user_id, text=menu_text, reply_markup=menu_keys)

        elif image_media:
            with open(image_url, 'rb') as photo:
                bot.send_photo(
                    user_id,
                    image_media.media,
                    caption=menu_text,
                    reply_markup=menu_keys
                )
            bot.delete_message(chat_id=user_id, message_id=old_msg.message_id)
        elif old_msg.text:
            # Если картинки нет, просто редактируем текст
            bot.edit_message_text(text=menu_text,
                                  chat_id=user_id,
                                  message_id=old_msg.message_id,
                                  reply_markup=menu_keys)
        else:
            bot.send_message(user_id, text=menu_text, reply_markup=menu_keys)
            bot.delete_message(chat_id=user_id, message_id=old_msg.message_id)
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


bot.polling()
