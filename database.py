from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from config import DATABASE_NAME  # Импортируете путь к базе данных

# Базовый класс для декларативных классов
Base = declarative_base()

# Определение классов для таблиц
class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    dishes = relationship("Dishes", back_populates="menu")

class Dishes(Base):
    __tablename__ = 'dishes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String)
    menu_id = Column(Integer, ForeignKey('menu.id'))

    menu = relationship("Menu", back_populates="dishes")
    cart_items = relationship("Cart", back_populates="dish")
    reviews = relationship("Reviews", back_populates="dish")

class Cart(Base):
    __tablename__ = 'cart'
    user_id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey('dishes.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    dish = relationship("Dishes", back_populates="cart_items")

class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String, nullable=False)
    delivery_address = Column(Text, nullable=False)
    order_date = Column(String, nullable=False)

class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    dish_id = Column(Integer, ForeignKey('dishes.id'))
    review_text = Column(Text)
    rating = Column(Integer)
    review_date = Column(String, nullable=False)

    dish = relationship("Dishes", back_populates="reviews")

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, unique=True, nullable=False)

# Настройка подключения к базе данных
engine = create_engine(f'sqlite:///{DATABASE_NAME}')  # Использование переменной DATABASE_NAME

# Создание всех таблиц в базе данных
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

# Функции для работы с базой данных

def create_connection():
    return session

def create_tables():
    Base.metadata.create_all(engine)

def insert_test_data():
    # Пример добавления тестовых данных
    new_user = Users(telegram_user_id=123456)
    session.add(new_user)
    session.commit()

def get_menu():
    return session.query(Menu).all()

def add_order(user_id, total_amount, payment_status, delivery_address, order_date):
    new_order = Orders(
        user_id=user_id,
        total_amount=total_amount,
        payment_status=payment_status,
        delivery_address=delivery_address,
        order_date=order_date
    )
    session.add(new_order)
    session.commit()

def update_order_payment_status(order_id, new_status):
    order = session.query(Orders).filter_by(id=order_id).first()
    if order:
        order.payment_status = new_status
        session.commit()

def get_order_status(order_id):
    return session.query(Orders).filter_by(id=order_id).first()

def add_feedback(user_id, dish_id, review_text, rating, review_date):
    new_review = Reviews(
        user_id=user_id,
        dish_id=dish_id,
        review_text=review_text,
        rating=rating,
        review_date=review_date
    )
    session.add(new_review)
    session.commit()

# Здесь можно добавить другие функции для работы с базой данных
