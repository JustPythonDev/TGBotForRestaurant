# Проект "Система заказа еды" (TGBotForRestaurant)
Данный проект создан в рамках курса по Python от Zerocoder для тренировки навыков командной работы
## Техническое задание для проекта "Система заказа еды"
### Общее описание проекта
Разработка чат-бота для мессенджера Telegram, который позволит пользователям делать заказы в ресторанах и кафе, используя интерфейс мессенджера.
### Ключевые технологии
Платформа: Telegram
Основной стек технологий: Python, библиотека telebot, SQL (SQLite) для хранения данных.
### Основные функциональные требования
**Отображение меню:**
- Возможность просмотреть текущее меню ресторана, включая категории блюд.
  
**Оформление заказа:**
- Возможность выбора блюд из меню и добавления их в корзину.
- Указание количества каждого блюда.
- Предоставление окончательной стоимости заказа.
  
**Управление заказами:**
- Отслеживание статуса заказа.
  
**Оплата:**
- Выбор способа оплаты: картой онлайн или наличными при получении.
  
**Обратная связь:**
- Возможность оставлять отзывы о блюдах и обслуживании.
- Рейтинг блюд и сервиса.
### Этапы и сроки разработки
1. Подготовка и анализ: Изучение API Telegram, проектирование базы данных.
2. Разработка: Реализация функционала бота, настройка серверной логики и базы данных.
3. Тестирование: Отладка, тестирование функционала.
4. Поддержка и обновление: Регулярное обновление софта, исправление возникающих ошибок, обновление контента меню

# Структура файлов проекта
## Служебные файлы
amvera.yml – служебный файл для хостинга бота<br>
requirements.txt – служебный файл для разворачивания проекта (содержит ссылки на требуемые сторонние библиотеки)<br>
config.py – файл с настройкой констант<br>
README.md

## Файлы БД
data/food_ordering_system.db – файл БД

create_dictionary_data.py – добавление справочных данных в БД, делается однократно при создании проекта<br>
creation_table.py – создание структуры БД, делается однократно при создании проекта

## Основные файлы
bot.py – основной файл с логикой работы с ботом: создание сообщений, callback_query_handler<br>
db_library.py – файл с методами доступа к данным БД

## Файлы для логики отдельных процессов:
cart.py - Корзина<br>
dish_menu.py – Меню кафе<br>
payment.py - Оплата<br>
status.py – Статус заказа<br>
review.py – Рейтинг<br>