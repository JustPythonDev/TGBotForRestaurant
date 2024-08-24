from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, Session
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

    def get_session(self):
        """Получение текущей сессии."""
        return self.Session()

    def close(self):
        """Закрытие текущей сессии."""
        self.Session.remove()


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    text = Column(String, nullable=False)
    image_url = Column(String)
    callback = Column(String, unique=True, nullable=False)
    parent_menu = Column(String, ForeignKey('menu_items.callback'))
    order_by = Column(Integer, nullable=False)

    @classmethod
    def get_menu_item_data(cls, session: Session, callback_value: str) -> dict:
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
    def get_menu_items_by_parent(cls, session: Session, parent_callback: str) -> list:
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

if __name__ == "__main__":
    db = Database()
    session = db.get_session()



    # Получение элемента по значению callback
    item = MenuItem.get_menu_item_data(session, "menu")
    print(item)

    # Закрытие сессии
    db.close()