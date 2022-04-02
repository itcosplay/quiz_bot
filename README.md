# бот - викторина
Бот реализованный для vk и telegram.

vk: [работает в сообществе](https://vk.com/club166280211)  
найти в telegram: @pi_tasty_bot

Возможности бота:
- Позволяет проводить викторины;
- Подсчитывает колличество правильных ответов.

## Необходимое окружение
|переменная|описание|тип
|----------|--------|--------------
|`TG_BOT_TOKEN`|Токен для бота [telegram](https://core.telegram.org/bots#6-botfather)|string
|`REDIS_HOST`|Хост бд [Redis](http://redislabs.com/)|string
|`REDIS_PORT`|Порт бд [Redis](http://redislabs.com/)|string
|`REDIS_PASSWORD`|Пароль бд [Redis](http://redislabs.com/)|string
|`VK_GROUP_TOKEN`|Токен вашей [группы vk](https://pechenek.net/social-networks/vk/api-vk-poluchaem-klyuch-dostupa-token-gruppy/)|string

Все переменные окружения должны храниться в файле .env в корне проекта.

## Как установить
* Клонируем репозиторий
* Добавляем файл .env с необходимыми переменными
* Создаем виртуальное окружение
* Устанавливаем зависимости
```
pip install -r requirements.txt
```

## Запуск
Запуск бота в telegram:
```
python tg_bot.py
```

Запуск бота в vk:
```
python vk_bot.py
```


## Загрузка вопросов в БД
Сохраните в корне проекта папку с названием `questions`. В папку положите txt файлы с воросами.
Структура файла с фопросами:
```
Вопрос:
Текст вопроса

Ответ:
Ответ на вопрос


Вопрос:
Текст вопроса

Ответ:
Ответ на вопрос
```
Запустите скрипт:
```
python upload_questions.py
```

## Цели проекта
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
