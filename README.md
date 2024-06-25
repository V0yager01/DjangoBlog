# DjangoBlog
## Описание
Сайт микроблогов, на котором люди делятся своими мыслями. Реализована возможность
публиковать, редактировать, комментировать и удалять посты. Публикации можно
сортировать по категориям.

## Запуск проекта
### Клонирование
Клонируйте репозиторий
```
git clone git@github.com:V0yager01/DjangoBlog.git
```
### Подготовка виртуального окружения
Создаем и включаем окружение для проекта
```
python -m venv venv
source venv/Scripts/activate
```
### Установка зависимостей
```
cd DjangoBlog/
pip install -r requirements.txt
```
### Подготовка Django
Выполням миграцию
```
cd blogicum/
python manage.py migrate
```
### Запуск
```
python manage.py runserver
```

## Технологии:
* Python
* Django
* HTML
* CSS
* Bootstrap5