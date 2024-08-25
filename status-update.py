import sqlite3
import threading
import time
from datetime import datetime

# Функция для подключения к базе данных SQLite
def get_db_connection():
    conn = sqlite3.connect('data/food_ordering_system.db')
    conn.row_factory = sqlite3.Row
    return conn

# Функция для получения текущего статуса заказа
def get_current_status(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM orders WHERE id = ?', (order_id,))
    status = cursor.fetchone()['status']
    conn.close()
    return status

# Функция для обновления статуса заказа
def update_order_status(order_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE orders
        SET status = ?
        WHERE id = ?
    ''', (new_status, order_id))
    conn.commit()
    conn.close()
    print(f"Order {order_id} status updated to '{new_status}'.")

# Функция для обработки обновления статусов заказа
def process_order(order_id):
    # Установить начальный статус
    update_order_status(order_id, 'Оформлен')

    # Через 3 минуты статус меняется на «В работе»
    time.sleep(3 * 60)
    if get_current_status(order_id) == 'Доставлен':
        return
    update_order_status(order_id, 'В работе')

    # Через 25 минут после оформления заказа статус меняется на «Готов к выдаче»
    time.sleep(22 * 60)  # (25 - 3) минут
    if get_current_status(order_id) == 'Доставлен':
        return
    update_order_status(order_id, 'Готов к выдаче')

    # Через 30 минут после оформления заказа статус меняется на «В пути»
    time.sleep(5 * 60)  # (30 - 25) минут
    if get_current_status(order_id) == 'Доставлен':
        return
    update_order_status(order_id, 'В пути')

    # Через 50 минут после оформления заказа статус меняется на «Доставлен»
    time.sleep(20 * 60)  # (50 - 30) минут
    if get_current_status(order_id) == 'Доставлен':
        return
    update_order_status(order_id, 'Доставлен')

    # Запуск процесса обновления статусов заказа
    threading.Thread(target=process_order, args=(order_id,)).start()
    print(f"Order {order_id} added and processing started.")
