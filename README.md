# Social media project where people can register, create and browse groups, create posts with media, leave comments and follow other users.

## Yatube Project Enhancements
Custom error pages have been added to the project:
 - 404 page_not_found
 - 403 permission_denied_view
A test has been written to verify that the 404 page serves a custom template.
Images for posts have been displayed using sorl-thumbnail:
 - in the main page template,
 - in the author profile template,
 - in the group page template,
 - on the individual post page.
Tests have been written to check:
when displaying a post with an image, the image is passed in the context dictionary
 - to the main page,
 - to the profile page,
 - to the group page,
 - to the individual post page;
when a post with an image is sent through the PostForm, a record is created in the database;

A commenting system for posts has been implemented. A comment submission form is displayed below the post text on the post page, followed by a list of comments. Only registered users can comment. The functionality of the module has been tested.

The list of posts on the main page of the site is stored in the cache and updated every 20 seconds.
A test has been written to check the caching of the main page. The logic of the test is: when a post is deleted from the database, it remains in the response.content of the main page until the cache is forcefully cleared.

The project is implemented using the Django Framework.

### How to start the project:

Clone the repository and go to it via the command line:

```
git clone https://github.com/Marikalis/hw05_final
```

```
cd hw05_final
```

Create and activate a virtual environment:

```
python3 -m venv env
```

```
source env/bin/activate
```

Install dependencies from the requirements.txt file:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Perform migrations:

```
python3 manage.py migrate
```

Start the project:

```
python3 manage.py runserver
```

=============================================

## Улучшение проекта Yatube
В проект добавлены кастомные страницы ошибок:
 - 404 page_not_found
 - 403 permission_denied_view
Написан тест, проверяющий, что страница 404 отдает кастомный шаблон.
С помощью sorl-thumbnail выведены иллюстрации к постам:
 - в шаблон главной страницы,
 - в шаблон профайла автора,
 - в шаблон страницы группы,
 - на отдельную страницу поста.
Написаны тесты, которые проверяют:
при выводе поста с картинкой изображение передаётся в словаре context
 - на главную страницу,
 - на страницу профайла,
 - на страницу группы,
 - на отдельную страницу поста;
при отправке поста с картинкой через форму PostForm создаётся запись в базе данных;

Написана система комментирования записей. На странице поста под текстом записи выводится форма для отправки комментария, а ниже — список комментариев. Комментировать могут только авторизованные пользователи. Работоспособность модуля протестирована.

Список постов на главной странице сайта хранится в кэше и обновляется раз в 20 секунд.
Написан тест для проверки кеширования главной страницы. Логика теста: при удалении записи из базы, она остаётся в response.content главной страницы до тех пор, пока кэш не будет очищен принудительно.

Проект реализован на Django Framework.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Marikalis/hw05_final
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
