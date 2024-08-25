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
        # Создаем экземпляр базы данных и получаем сессию
        self.db = Database()
        self.session = self.db.get_session()
        self.last_menu = ""

    def create_menu_keyboard(self, parent_callback):
        # Создание клавиатуры для текущего уровня меню
        markup = types.InlineKeyboardMarkup()

        # Получение элементов меню из базы данных
        filtered_menu = MenuItem.get_menu_items_by_parent(self.session, parent_callback)
        self.db.close()

        for item in filtered_menu:
            button = types.InlineKeyboardButton(item["name"], callback_data=item["callback"])
            markup.add(button)

        # Если это не главное меню, добавляем кнопку для возврата
        if parent_callback is not None and parent_callback != "start":
            parent_of_parent = self.item(parent_callback)['parent_menu']
            self.db.close()
            if parent_of_parent is None:
                parent_of_parent = "start"
            back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_" + parent_of_parent)
            markup.add(back_button)

        return markup

    def item(self, callback):
        # Получение текста для меню на основе callback
        item = MenuItem.get_menu_item_data(self.session, callback)
        self.db.close()
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

    send_new_msg(menu_text, menu_keys, image_url, msg)

    if menu.item(parent_callback)['parent_menu'] == 'menu':
        print(parent_callback)
        view_menu_category_dishes(parent_callback, msg.chat.id)


def send_new_msg(menu_text, menu_keys=None, image_url=None, old_msg=None):
    user_id = old_msg.chat.id
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
            elif old_msg.text:
                bot.edit_message_text(text=menu_text,
                                      chat_id=user_id,
                                      message_id=old_msg.message_id,
                                      reply_markup=menu_keys)
            else:
                bot.send_message(user_id, text=menu_text, reply_markup=menu_keys)

           # bot.delete_message(chat_id=user_id, message_id=old_msg.message_id)
        elif image_media:
            with open(image_url, 'rb') as photo:
                bot.send_photo(
                    user_id,
                    image_media.media,
                    caption=menu_text,
                    reply_markup=menu_keys
                )

            if old_msg.text:
                bot.delete_message(chat_id=user_id, message_id=old_msg.message_id)
        elif old_msg.text:
            # Если картинки нет, просто редактируем текст
            bot.edit_message_text(text=menu_text,
                                  chat_id=user_id,
                                  message_id=old_msg.message_id,
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


def save_message_id(user_id, message_id):
    """Сохраняет ID сообщения, отправленного ботом."""
    if user_id not in sent_messages:
        sent_messages[user_id] = []
    sent_messages[user_id].append(message_id)


def clear_chat_history(user_id):
    """Удаляет все сообщения, отправленные ботом в данном чате."""
    if user_id in sent_messages:
        for message_id in sent_messages[user_id]:
            try:
                bot.delete_message(user_id, message_id)
                time.sleep(0.1)  # Задержка, чтобы избежать лимитов API
            except Exception as e:
                print(f"Не удалось удалить сообщение {message_id}: {e}")

        # Очистка списка сообщений после их удаления
        sent_messages[user_id] = []


def view_menu_category_dishes(parent_callback, user_id):
    # Получаем список блюд из временной базы данных
    dishes_list = temp_db.get_dishes_by_menu_callback(parent_callback)

    # Если список блюд пуст, отправляем сообщение об этом
    if not dishes_list:
        # bot.send_message(user_id, text="Блюда в данной категории отсутствуют.")
        return

    for dish in dishes_list:
        # Создаем разметку с кнопкой для каждого изображения
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text=f"Заказать {dish['name']}", callback_data=f"order_{dish['id']}")
        markup.add(button)

        # Отправляем изображение с подписью и кнопкой
        dish_message = f"<b>{dish['name']}</b>\nЦена: {dish['price']} руб."
        try:
            with open(dish['image_url'], 'rb') as photo:
                msg = bot.send_photo(
                    user_id,
                    photo,
                    caption=dish_message,
                    reply_markup=markup)
        except (TypeError, FileNotFoundError):
            msg = bot.send_message(
                user_id,
                text=dish_message,
                reply_markup=markup
            )
        save_message_id(user_id, msg.message_id)


bot.polling()
