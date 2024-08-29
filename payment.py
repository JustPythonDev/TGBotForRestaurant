# Изменить в файле 'create_dictionary_data.py':
# ('💵 Оплата заказа', 'Корзина пуста. Сформируйте заказ', 'payment', 'start', 3, 'img/payment.jpg')

# ЗДЕСЬ ДВА СЦЕНАРИЯ для 'Оплата заказа'. Нужно где-то 'name' изменить?

# Добавить в файл 'create_dictionary_data.py':
#('Оплата заказа', f'Сумма заказа - {total_amount}\nДля заказа выберите способ оплаты', 'payment', 'start', 3, 'img/payment.jpg'),
# (кнопки)
# ('Наличные', f'Заказ на сумму {total_amount} принят.\n Оплата курьеру. Спасибо', 'payment_cash', 'payment', 1, 'img/payment.jpg'),
# ('Онлайн', f'Заказ на сумму {total_amount} оплачен и принят в работу. Спасибо', 'payment_online', 'payment', 2, 'img/payment.jpg'),
# ('↩️ Назад', None, 'back_to_start', 'payment', 3, None),


def check_total_amount_and_show_menu(user_id):

 try:
  # Запрашиваем сумму total_amount из таблицы Card для данного пользователя
  total_amount = session.query(Card.total_amount).filter_by(user_id=user_id).scalar() or 0

  if total_amount == 0:
   # Меню, если корзина пуста
   menu = [
    ('Оплата заказа', 'Корзина пуста. Сформируйте заказ', 'payment', 'start', 3, 'img/payment.jpg')
   ]
  else:
   # Меню (с тремя кнопками), если сумма больше 0
   menu = [
    ('Оплата заказа', f'Сумма заказа - {total_amount}\nДля заказа выберите способ оплаты', 'payment', 'start', 3,
     'img/payment.jpg'),
    ('Наличные', f'Заказ на сумму {total_amount} принят.\n Оплата курьеру. Спасибо', 'payment_cash', 'payment', 1,
     'img/payment.jpg'),
    ('Онлайн', f'Заказ на сумму {total_amount} оплачен и принят в работу. Спасибо', 'payment_online', 'payment', 2,
     'img/payment.jpg'),
    ('Назад', None, 'back_to_start', 'payment', 3, None)
   ]

  return menu

 finally:
  session.close()


def handle_payment(user_id, payment_method):
 session = db.get_session()

 try:
  # Получаем данные заказа из таблицы Card
  card_items = session.query(Card).filter_by(user_id=user_id).all()

  if not card_items:
   return "Корзина пуста. Сформируйте заказ."

  # Создаем новую запись в таблице Orders
  for item in card_items:
   new_order = Orders(
    user_id=item.user_id,
    total_amount=item.total_amount,
    payment_status='Оплачен' if payment_method == 'payment_online' else 'Не оплачен',
    delivery_address=item.delivery_address,
    order_date=datetime.now()
   )
   session.add(new_order)

  # Удаляем заказ из таблицы Card
  session.query(Card).filter_by(user_id=user_id).delete()

  # Фиксируем изменения
  session.commit()

  if payment_method == 'payment_cash':
   return f"Заказ на сумму {total_amount} принят.\n Оплата курьеру. Спасибо"
  elif payment_method == 'payment_online':
   return f"Заказ на сумму {total_amount} оплачен и принят в работу. Спасибо"

 except Exception as e:
  session.rollback()
  raise e

 finally:
  session.close()

