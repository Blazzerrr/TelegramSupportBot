# Telegram Support Bot

Telegram Бот для технической поддержки пользователей.
Имеется три панели:
1. Основная - она предназначена для пользователей, которые будут создавать и просматривать все свои запросы.
2. Панель для сотрудников технической поддержки, доступ к которой можно получить введя пароль выданный администратором, либо через админ-панель. Можно просматривать и отвечать на все текущие запросы пользователей.
3. Админ-панель - нужна для добавления и удаления сотрудников поддержки, генерации/удаления паролей доступа, а также отключения бота без взаимодействия с кодом.

## Скриншот
[Screenshot](https://github.com/Blazzerrr/TelegramSupportBot/blob/master/image.png) 

## Запуск
В файле config.py указать Telegram Token, Telegram ID главного администратора и при необходимости прокси-сервер.

```bash
cd Telegram Support Bot
python bot.py
```

## Requirements
- telebot
- json
- random
- datetime

## Author
Blazzerrr

You can contact me at Telegram
[@blazzzerrr](https://t.me/blazzzerrr) 
