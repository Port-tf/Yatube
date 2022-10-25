# Социальная сеть для публикации блогов.
### Описание:
Пользователи могут создавать свои страницы, делать записиб редактировать и прикреплять к ним изображения. Если зайти на страницу пользователя, то можно посмотреть все записи автора, подписаться на него, и оставлять комментарии. Есть возможность модерировать записи и блокировать пользователей, реализовано через админ-панель.

Так же проект покрыт тестами для проверки работоспобности:
- Тесты полей модели Post, Group, Follow, Comments verbose_name, help_text и метод str.
- Тесты всех URLs проекта(использован subTest) на обращение к нужному html-шаблону и хардурлу.
- Тесты всех view-функций на правильность словарей context.
- Тесты проверяющие, что если при создании поста или комментария создаётся запись в базе данных.
- Тесты на корректность работы пагинации.
Все тесты написаны для авторизированного и анонимного пользователя.\
При написании тестов использовалась библиотека Unittest, и методы setUp и setUpClass.\

# Стек технологий
Python 3.9.13\
Django 2.2.19\
SQLite

# Запуск проекта
### Создание и активация виртуального окружения:
```
python3 -m venv venv
source venv/Scripts/activate
```
### Установка зависимостей из файла requirements.txt:
```
pip install -r requirements.txt
```
### Применить миграции:
```
python manage.py migrate
```
### Запустить проект:
```
python3 manage.py runserver
```

### Запуск тестов:
```
python3 manage.py test 
```
