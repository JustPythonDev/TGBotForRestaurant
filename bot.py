import telebot
from telebot import types
import time
import os

from config import TELEGRAM_API_TOKEN
from db_library import Database, MenuItem


# ВРЕМЕННО!!!
import temp_db

sent_messages = {}

class Menu:
    def __init__(self):
        self.last_menu = ""

    def create_menu_keyboard(self, parent_callback):
        # Создание клавиатуры для текущего уровня меню
        markup = types.InlineKeyboardMarkup()

        # Получение элементов меню из базы данных
        filtered_menu = MenuItem.get_menu_items_by_parent(parent_callback)

        for item in filtered_menu:
            button = types.InlineKeyboardButton(item["name"], callback_data=item["callback"])
            markup.add(button)

        # Если это не главное меню, добавляем кнопку для возврата
        if parent_callback is not None and parent_callback != "start":
            parent_of_parent = self.item(parent_callback)['parent_menu']

            if parent_of_parent is None:
                parent_of_parent = "start"
            back_button = types.InlineKeyboardButton("↩️ Назад", callback_data="back_to_" + parent_of_parent)
            markup.add(back_button)

        return markup

    def item(self, callback):
        # Получение текста для меню на основе callback
        item = MenuItem.get_menu_item_data(callback)
        if item:
            return item
        return None


# Токен вашего бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN, parse_mode='HTML')

# Создаем экземпляр класса Menu
menu = Menu()


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    process_menu("start", msg=message)


# Обработчик нажатий на inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("back_to_"):
        parent_callback = call.data[len("back_to_"):]
        if parent_callback == "menu":
            clear_chat_history(call.message.chat.id)
    else:
        parent_callback = call.data

    if parent_callback.startswith("order_"):
        pass
    process_menu(parent_callback, msg=call.message)


def process_menu(parent_callback, msg=None):
    # Создание клавиатуры и получение текста и изображения:
    if parent_callback == menu.last_menu and parent_callback != 'start':
        return
    else:
        menu.last_menu = parent_callback

    menu_keys = menu.create_menu_keyboard(parent_callback)
    menu_text = menu.item(parent_callback)['text']
    image_url = menu.item(parent_callback)['image_url']
    user_id = msg.chat.id

    send_or_change_menu_msg(user_id, menu_text, menu_keys, image_url, msg)

    if menu.item(parent_callback)['parent_menu'] == 'menu':
        print(parent_callback)
        view_category_dishes_menu(parent_callback, user_id)


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
                bot.send_message(user_id, text=menu_text, reply_markup=menu_keys)
                bot.delete_message(chat_id=user_id, message_id=old_msg.message_id)

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


def save_message_id(user_id, message_id, id):
    """Сохраняет ID сообщения, отправленного ботом, с привязкой к идентификатору."""

    # Проверяем, есть ли уже записи для данного пользователя
    if user_id not in sent_messages:
        sent_messages[user_id] = {}  # Инициализируем словарь для конкретного пользователя

    # Сохраняем id под конкретным message_id
    sent_messages[user_id][message_id] = id


def clear_chat_history(user_id):
    """Удаляет все сообщения, отправленные ботом в данном чате."""
    if user_id in sent_messages:
        # Получаем список message_id для удаления
        message_ids = list(sent_messages[user_id].keys())

        for message_id in message_ids:
            try:
                bot.delete_message(user_id, message_id)
                time.sleep(0.05)  # Задержка, чтобы избежать лимитов API
            except Exception as e:
                print(f"Не удалось удалить сообщение {message_id}: {e}")

        # Очистка словаря сообщений после их удаления
        sent_messages[user_id] = {}


def send_new_message(user_id, image_url, msg_text, markup_keys=None, id=None):
    """Отправка сообщения - только текст или текст/картинка + markup_keysб
    Сохраняет ID сообщения, отправленного ботом, с привязкой к идентификатору"""
    try:
        with open(image_url, 'rb') as photo:
            msg = bot.send_photo(
                user_id,
                photo,
                caption=msg_text,
                reply_markup=markup_keys)
        save_message_id(user_id, msg.message_id, id)
    except (TypeError, FileNotFoundError):
        msg = bot.send_message(
            user_id,
            text=msg_text,
            reply_markup=markup_keys
        )
        save_message_id(user_id, msg.message_id, id)


def view_category_dishes_menu(parent_callback, user_id):
    # Получаем список блюд из временной базы данных
    dishes_list = temp_db.get_dishes_by_menu_callback(parent_callback)

    # Если список блюд пуст, отправляем сообщение об этом
    if not dishes_list:
        return

    for dish in dishes_list:
        # Создаем разметку с кнопкой для каждого изображения
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text=f"Выбрать", callback_data=f"order_{dish['id']}")
        markup.add(button)

        # Отправляем изображение с подписью и кнопкой
        dish_message = f"<b>{dish['name']}</b>\nЦена: {dish['price']} руб."

        # отправим собщение в бот
        send_new_message(user_id, dish['image_url'], dish_message, markup, dish['id'])


bot.polling()
