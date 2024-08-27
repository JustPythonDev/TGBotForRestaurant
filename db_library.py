from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, Session, relationship
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
            return None

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

    # @classmethod
    # @with_session
    # def create_menu_item(cls, name: str, text: str, image_url: str, callback: str, parent_menu: str, order_by: int, session: Session):
    #     """
    #     Создает новый элемент меню и сохраняет его в базе данных.
    #     """
    #     new_item = cls(
    #         name=name,
    #         text=text,
    #         image_url=image_url,
    #         callback=callback,
    #         parent_menu=parent_menu,
    #         order_by=order_by
    #     )
    #     session.add(new_item)
    #     session.commit()

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
    # cart_items = relationship("Cart", back_populates="dish")
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
        # return []




if __name__ == "__main__":
    # Примеры использования
    item = MenuItems.get_menu_item_data("menu")
    print(item)

    items = MenuItems.get_menu_items_by_parent("menu")
    print(items)

    items = Dishes.get_dishes_by_menu_callback("appetizers")
    print(items)
