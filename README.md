![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)


# Социальная сеть YaTube.

Социальная сеть с возможностью создания, просмотра, редактирования и удаления (CRUD) записей. Реализован механизм подписки на понравившихся авторов и отслеживание их записей. Покрытие тестами. Возможность добавления изображений.

* Инструментарий:
  * Django 2.2
  * Python 3.8
  * Django Unittest
  * Django debug toolbar
  * PostgreSQL
  * Django ORM

* Запуск:
  * Установка зависимостей:
    * `pip install -r requirements.txt`
  * Применение миграций:
    * `python manage.py makemigrations`
    * `python manage.py migrate`
  * Создание администратора:
    * `python manage.py createsuperuser`
  * Запуск приложения:
    * `python manage.py runserver`
