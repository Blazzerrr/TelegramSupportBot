import config
import core
import telebot
import random
import datetime
import markup
import sys
from telebot import apihelper

if config.PROXY_URL:
    apihelper.proxy = {'https': config.PROXY_URL}

bot = telebot.TeleBot(config.TOKEN, skip_pending=True)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, ' Привет! Это бот для технической поддержки пользователей.\nЕсли у тебя есть какой-либо вопрос или проблема - нажми на кнопку <b>Написать запрос</b> и наши сотрудники скоро с тобой свяжутся!', parse_mode='html', reply_markup=markup.markup_main())


@bot.message_handler(commands=['agent'])
def agent(message):
    user_id = message.from_user.id

    if core.check_agent_status(user_id) == True:
        bot.send_message(message.chat.id, ' Вы авторизованы как Агент поддержки', parse_mode='html', reply_markup=markup.markup_agent())
    else:
        take_password_message = bot.send_message(message.chat.id, '⚠️ Тебя нет в базе. Отправь одноразовый пароль доступа.', reply_markup=markup.markup_cancel())

        bot.register_next_step_handler(take_password_message, get_password_message)


@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id

    if str(user_id) == config.ADMIN_ID:
        bot.send_message(message.chat.id, ' Вы авторизованы как Админ', parse_mode='html', reply_markup=markup.markup_admin())
    else:
        bot.send_message(message.chat.id, ' Эта команда доступна только администратору.')


@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.from_user.id

    if message.text == '✏️ Написать запрос':
        take_new_request = bot.send_message(message.chat.id, 'Введите свой запрос и наши сотрудники скоро с вами свяжутся.', reply_markup=markup.markup_cancel())

        bot.register_next_step_handler(take_new_request, get_new_request)

    elif message.text == '✉️ Мои запросы':
        markup_and_value = markup.markup_reqs(user_id, 'my_reqs', '1')
        markup_req = markup_and_value[0]
        value = markup_and_value[1]

        if value == 0:
            bot.send_message(message.chat.id, '⚠️ Запросы не обнаружены.', reply_markup=markup.markup_main())
        else:
            bot.send_message(message.chat.id, 'Ваши запросы:', reply_markup=markup_req)


def get_password_message(message):
    password = message.text

    if password == None:
        take_password_message = bot.send_message(message.chat.id, '⚠️ Ты не ввел пароль. Попробуй еще раз.', reply_markup=markup.markup_cancel())

        bot.register_next_step_handler(take_password_message, get_password_message)

    elif password.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup.markup_main())
        return

    else:
        if core.valid_password(password) == True:
            core.add_agent(user_id)
            bot.send_message(message.chat.id, ' Вы авторизованы как Агент поддержки', parse_mode='html', reply_markup=markup.markup_agent())
            bot.send```
