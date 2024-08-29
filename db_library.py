from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, declarative_base, Session
from datetime import datetime, timedelta

from config import DATABASE_NAME

# Базовый класс
Base = declarative_base()

class Database:
    """Класс для управления подключением к базе данных и сессией."""

    def __init__(self, db_url=f'sqlite:///{DATABASE_NAME}'):
        """Инициализация соединения с базой данных."""
        self.engine = create_engine(db_url)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.SessionFactory)

    def get_session(self) -> Session:
        """Получение новой сессии."""
        return self.Session()

    def close(self):
        """Закрытие всех сессий."""
        self.Session.remove()


# Экземпляр класса Database для использования в модуле
db = Database()


def with_session(func):
    """Декоратор для управления сессией. Автоматически открывает и закрывает сессию."""

    def wrapper(*args, **kwargs):
        session = db.get_session()
        try:
            result = func(*args, session=session, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    return wrapper


class MenuItems(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    text = Column(String, nullable=False)
    image_url = Column(String)
    callback = Column(String, unique=True, nullable=False)
    parent_menu = Column(String, ForeignKey('menu_items.callback'))
    order_by = Column(Integer, nullable=False)

    @classmethod
    @with_session
    def get_menu_item_data(cls, callback_value: str, session: Session) -> dict:
        """
        Возвращает значения всех полей строки по значению callback.
        """
        item = session.query(cls).filter_by(callback=callback_value).first()
        if item:
            return {
                'id': item.id,
                'name': item.name,
                'text': item.text,
                'image_url': item.image_url,
                'callback': item.callback,
                'parent_menu': item.parent_menu,
                'order_by': item.order_by
            }
        else:
            return {
                'id': None,
                'name': None,
                'text': None,
                'image_url': None,
                'callback': None,
                'parent_menu': None,
                'order_by': None
            }

    @classmethod
    @with_session
    def get_menu_items_by_parent(cls, parent_callback: str, session: Session) -> list:
        items = session.query(cls).filter_by(parent_menu=parent_callback).order_by(cls.order_by).all()
        # Возвращаем список словарей, каждый из которых представляет элемент меню
        return [{
            'id': item.id,
            'name': item.name,
            'text': item.text,
            'image_url': item.image_url,
            'callback': item.callback,
            'parent_menu': item.parent_menu,
            'order_by': item.order_by
        } for item in items]

    @classmethod
    @with_session
    def check_is_menu_callback(cls, callback_value: str, session: Session) -> dict:
        """
        Проверяет есть ли записи с таким callback
        """
        item = session.query(cls).filter_by(callback=callback_value).order_by(cls.order_by).first()
        if item:
            return True
        else:
            return False

class DishesCategories(Base):
    __tablename__ = 'dishes_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    menu_item_callback = Column(String, ForeignKey('menu_items.callback'))

    menu_item = relationship("MenuItems", backref="dishes_categories")


class Dishes(Base):
    __tablename__ = 'dishes'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String)
    dishes_category = Column(Integer, ForeignKey('dishes_categories.menu_item_callback'))

    category = relationship("DishesCategories", backref="dishes")
    cart_items = relationship("Cart", back_populates="dish")
    # reviews = relationship("Reviews", back_populates="dish")

    @classmethod
    @with_session
    def get_dishes_by_menu_callback(cls, callback_value: str, session: Session) -> list:
        """
        Возвращает список блюд, связанных с категорией, соответствующей значению callback.
        """
        # category = session.query(cls).filter_by(menu_item_callback=callback_value).first()
        # if category:
        dishes = session.query(cls).filter_by(dishes_category=callback_value).order_by(cls.id).all()
        return [{
            'id': dish.id,
            'name': dish.name,
            'description': dish.description,
            'price': dish.price,
            'image_url': dish.image_url,
            'dishes_category': dish.dishes_category
        } for dish in dishes]


class Orders(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String, nullable=False)
    delivery_address = Column(Text, nullable=False)
    order_date = Column(DateTime, nullable=False)

    @classmethod
    @with_session
    def get_orders_by_user_id(cls, user_id: int, session: Session) -> list:
        """
        Возвращает список заказов для пользователя user_id за текущий день с вычисляемым статусом заказа.

        :param user_id: Идентификатор пользователя.
        :param session: Текущая сессия базы данных.
        :return: Список заказов с полями total_amount, payment_status, order_date, order_status.
        """
        # Устанавливаем начало сегодняшнего дня
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Получаем заказы для указанного пользователя, сделанные сегодня
        orders = session.query(cls).filter_by(user_id=user_id).filter(cls.order_date >= today_start).all()

        result = []
        for order in orders:
            # Вычисляем время, прошедшее с момента заказа
            elapsed_time = datetime.now() - order.order_date

            # Определяем статус заказа на основе времени
            if elapsed_time < timedelta(minutes=30):
                order_status = "в работе"
            elif timedelta(minutes=30) <= elapsed_time < timedelta(hours=2):
                order_status = "в пути"
            else:
                order_status = "доставлен"

            # Формируем результат в виде списка словарей
            result.append({
                'id': order.id,
                'total_amount': order.total_amount,
                'payment_status': order.payment_status,
                'order_date': order.order_date,
                'order_status': order_status
            })

        return result

    @classmethod
    @with_session
    def create_order_from_cart(cls, user_id: int, payment_status: str, delivery_address: str = "", session: Session = None) -> int:
        """
        Создает новый заказ на основе содержимого корзины пользователя и очищает корзину.
        """
        # Вычисляем общую сумму заказа
        total = Cart.get_cart_total_amount(user_id)

        if not total:
            raise ValueError("Корзина пуста. Невозможно создать заказ.")

        # Создаем новый заказ
        new_order = cls(
            user_id=user_id,
            total_amount=total,
            payment_status=payment_status,
            delivery_address=None,
            order_date=datetime.now()
        )
        session.add(new_order)
        session.flush()  # Выполняем промежуточный коммит, чтобы получить order_id

        # Получаем ID нового заказа
        order_id = new_order.id

        # Очищаем корзину после создания заказа
        session.query(Cart).filter_by(user_id=user_id).delete()

        return order_id

class Cart(Base):
    __tablename__ = 'cart'
    user_id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey('dishes.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    dish = relationship("Dishes", back_populates="cart_items")

    @classmethod
    @with_session
    def add_dish_to_cart(cls, user_id: int, dish_id: int, session: Session):
        """Добавляет новую запись в корзину."""
        quantity = 1
        cart_item = session.query(cls).filter_by(user_id=user_id, dish_id=dish_id).first()

        if cart_item:
            cart_item.quantity += 1
            return True
        else:
            new_cart_item = cls(user_id=user_id, dish_id=dish_id, quantity=quantity)
            if new_cart_item:
                session.add(new_cart_item)
                return True
        return False

    @classmethod
    @with_session
    def remove_dish_from_cart(cls, user_id: int, dish_id: int, session: Session):
        """Удаляет позицию из корзины."""
        cart_item = session.query(cls).filter_by(user_id=user_id, dish_id=dish_id).first()

        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                session.delete(cart_item)
            return True
        return False
    @classmethod
    @with_session
    def get_cart_total_amount(cls, user_id: int, session: Session) -> float:
        """
        Подсчитывает общую сумму заказа в корзине для данного пользователя.
        """
        total = session.query(
            func.sum(Dishes.price * cls.quantity)
        ).select_from(cls).join(Dishes, cls.dish_id == Dishes.id).filter(cls.user_id == user_id).scalar()

        return total if total is not None else 0.0

    @classmethod
    @with_session
    def get_cart_dishes(cls, user_id: int, session: Session) -> list:
        """
        Возвращает информацию обо всех товарах в корзине для данного пользователя.
        """
        # Запрос на получение данных о блюдах в корзине
        cart_items = session.query(
            Dishes.name,
            Dishes.image_url,
            Dishes.price,
            cls.quantity,
            (Dishes.price * cls.quantity).label('dish_total')
        ).join(Dishes, cls.dish_id == Dishes.id).filter(cls.user_id == user_id).all()

        # Формируем список словарей с нужной информацией
        return [
            {
                'name': item.name,
                'image_url': item.image_url,
                'price': item.price,
                'quantity': item.quantity,
                'dish_total': item.dish_total
            }
            for item in cart_items
        ]




if __name__ == "__main__":
    # Примеры использования
    # item = MenuItems.get_menu_item_data("menu")
    # print(item)
    #
    # items = MenuItems.get_menu_items_by_parent("menu")
    # print(items)
    #
    # items = Dishes.get_dishes_by_menu_callback("appetizers")
    # print(items)
    items = Cart.get_cart_dishes(1295753599)
    print(items)
    # items = Cart.remove_dish_from_cart(1, 1)
    # print(items)