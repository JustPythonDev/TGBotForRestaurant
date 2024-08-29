def payment_menu_start(callback, user_id):
    if callback == 'payment':
        return view_payment_data(user_id)
    elif callback.startswith("payment_cash"):
        return process_cash_payment(user_id)
    elif callback.startswith("payment_card"):
        return process_card_payment(user_id)


def view_payment_data(user_id):
    session = db.get_session()
    total_amount = session.query(Card.total_amount).filter_by(user_id=user_id).scalar() or 0

    if total_amount == 0:
        return [{
            'message': 'Корзина пуста. Сформируйте заказ',
            'image_url': None,
            'markup': None,
            'buttons': None,
            'id': None
        }]

    payment_message = f'Сумма заказа - {total_amount} руб.'
    payment_buttons = [
        {'text': 'Наличные', 'callback_data': 'payment_cash'},
        {'text': 'Онлайн', 'callback_data': 'payment_card'}
    ]
    return [{
        'message': payment_message,
        'image_url': None,
        'markup': None,
        'buttons': payment_buttons,
        'id': None
    }]


def process_card_payment(user_id):
    session = db.get_session()
    total_amount = session.query(Card.total_amount).filter_by(user_id=user_id).scalar() or 0
    session.close()

    session = db.get_session()
    create_order(user_id, payment_method='card')
    session.commit()
    session.close()

    session = db.get_session()
    session.query(Card).filter_by(user_id=user_id).delete()
    session.commit()
    session.close()

    payment_message = f'Заказ на сумму {total_amount} оплачен и принят к исполнению.'
    return [{
        'message': payment_message,
        'image_url': None,
        'markup': None,
        'buttons': None,
        'id': None
    }]


def process_cash_payment(user_id):
    session = db.get_session()
    total_amount = session.query(Card.total_amount).filter_by(user_id=user_id).scalar() or 0
    session.close()

    session = db.get_session()
    create_order(user_id, payment_method='cash')
    session.commit()
    session.close()

    session = db.get_session()
    session.query(Card).filter_by(user_id=user_id).delete()
    session.commit()
    session.close()

    payment_message = f'Заказ на сумму {total_amount} принят к исполнению, оплата наличными курьеру'
    return [{
        'message': payment_message,
        'image_url': None,
        'markup': None,
        'buttons': None,
        'id': None
    }]

def create_order(user_id, payment_method):
    session = db.get_session()
    card_items = session.query(Card).filter_by(user_id=user_id).all()

    for item in card_items:
        payment_status = 'Оплачен' if payment_method == 'card' else 'Не оплачен'
        new_order = Orders(
            user_id=item.user_id,
            total_amount=item.total_amount,
            payment_status=payment_status,
            delivery_address=item.delivery_address,
            order_date=datetime.now()
        )
        session.add(new_order)

    session.commit()
    session.close()