import telebot
import json
import config
import random
import datetime

from telebot import apihelper
from telebot import types

if config.PROXY_URL:
    apihelper.proxy = {'https': config.PROXY_URL}

bot = telebot.TeleBot(config.TOKEN)

markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
item1 = types.KeyboardButton("✏️ Написать запрос")
item2 = types.KeyboardButton("✉️ Мои запросы")
markup_main.row(item1)
markup_main.row(item2)

markup_support_panel = types.InlineKeyboardMarkup(row_width=2)
item1 = types.InlineKeyboardButton("✉️ Текущие запросы", callback_data='cur_requests')
item2 = types.InlineKeyboardButton("🗂 История", callback_data='all_history')
markup_support_panel.add(item1)
markup_support_panel.row(item2)

markup_admin_panel = types.InlineKeyboardMarkup(row_width=2)
item1 = types.InlineKeyboardButton("✅ Добавить агента поддержки", callback_data='add_agent')
item2 = types.InlineKeyboardButton("❌ Удалить агента поддержки", callback_data='del_agent')
item3 = types.InlineKeyboardButton("🔑 Одноразовые пароли", callback_data='all_pass')
item4 = types.InlineKeyboardButton("🎲 Сгенерировать одноразовые пароли", callback_data='gen_pass')
item5 = types.InlineKeyboardButton("⛔️ Выключить бота", callback_data='stop_bot')
markup_admin_panel.add(item1, item2, item3)
markup_admin_panel.row(item4)
markup_admin_panel.row(item5)


@bot.message_handler(commands=['start'])
def start_text(message):
    bot.send_message(message.chat.id, 'Привет! Это бот для технической поддержки пользователей. Если у тебя есть какой-либо вопрос или проблема - нажми на кнопку <b>Написать запрос</b> и наши сотрудники в скором времени тебе ответят.', parse_mode='html', reply_markup=markup_main)


@bot.message_handler(commands=['support'])
def check_support_panel(message):
    support_id = str(message.from_user.id)
    with open('base_support.json', 'r') as file:
        json_support_data = json.load(file)

    if support_id in json_support_data: 
        bot.send_message(message.chat.id, 'Выберите раздел технической панели:', parse_mode='html', reply_markup=markup_support_panel)
    else:
        def get_password_message(message):
            with open('pass.json', 'r') as file:
                json_pass_data = json.load(file)

            password = message.text
            if password in json_pass_data:
                with open('pass.json', 'r') as file:
                    json_pass_data = json.load(file)
                json_pass_data.remove(password)
                with open('pass.json', 'w') as file:
                    json.dump(json_pass_data, file, ensure_ascii=False)

                bot.send_message(message.chat.id, 'Выберите раздел технической панели:', parse_mode='html', reply_markup=markup_support_panel)

                with open('base_support.json', 'w') as file:
                    json_support_data.append(str(message.from_user.id))
                    json.dump(json_support_data, file, ensure_ascii=False)

            elif message.text.lower() == 'отмена':
                bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup_main)
            else:
                send_message = bot.send_message(message.chat.id, 'Неверный пароль. Попробуй ещё раз.\nЧтобы отменить действие, отправьте слово Отмена.', reply_markup=markup_main)
                bot.register_next_step_handler(send_message, get_password_message)

        send_message = bot.send_message(message.chat.id, 'Тебя нет в базе. Отправьте одноразовый пароль доступа.\nЧтобы отменить действие, отправьте слово Отмена.', reply_markup=markup_main)
        bot.register_next_step_handler(send_message, get_password_message)

@bot.message_handler(commands=['admin'])
def check_admin(message):
    if str(message.from_user.id) == config.ADMIN_ID:
        bot.send_message(message.chat.id, 'Выберите раздел админ панели:', reply_markup=markup_admin_panel)
    else:
        bot.send_message(message.chat.id, 'Эта команда доступна только администратору.')

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == '✏️ Написать запрос':
        send_message_request = bot.send_message(message.chat.id, 'Введите свой запрос и наши сотрудники скоро с вами свяжутся.\nЧтобы отменить действие, отправьте слово Отмена.', reply_markup=markup_main)
        bot.register_next_step_handler(send_message_request, get_request)

    if message.text == '✉️ Мои запросы':
        id_user = message.from_user.id

        try:
            all_request_history = json.load(open('requests.json'))
        except:
            all_request_history = []

        my_req_markup = types.InlineKeyboardMarkup(row_width=2)

        if str(all_request_history) != '[]':
            for all_data in all_request_history:
                for user_id in all_data:
                    if str(user_id) == str(id_user):                        
                        for req_user in all_data[user_id]:
                            for req_id in req_user:
                                for item in req_user[req_id][0]:
                                    if req_user[req_id][0][item]['status'] == 'Не отвечено':
                                        if int(item) == 1:
                                            req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ⏳', callback_data='ID:' + 'send' + req_id)
                                            my_req_markup.row(req_id)
                                    elif req_user[req_id][0][item]['status'] == 'Отвечено':
                                        if int(item) == 1:
                                            req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ⚠️', callback_data='ID:' + 'wait' + req_id)
                                            my_req_markup.row(req_id)
                                    elif req_user[req_id][0][item]['status'] == 'Завершено':
                                        if int(item) == 1:
                                            req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ✅', callback_data='ID:' + 'done' + req_id)
                                            my_req_markup.row(req_id)

        bot.send_message(message.chat.id, '⏳ Ожидает ответа от технической поддержки\n\n⚠️ Ожидает ответа от пользователя\n\n✅ Завершено\n\nЧтобы прочитать, либо дополнить обращение - нажмите на запрос', reply_markup=my_req_markup)

def get_request(message):
    id_user = message.from_user.id
    if message.text.lower() != 'отмена':
        request = message.text
        try:
            all_request_data = json.load(open('requests.json'))
        except:
            all_request_data = []
        dt = datetime.datetime.now()
        date_now = dt.strftime('%d.%m.%Y %H:%M:%S')

        if str(all_request_data) != '[]':
            for all_data in all_request_data:
                for user_id in all_data:
                    for req_user in all_data[user_id]:
                        for req_id in req_user:
                            break
                        break
                    break
        else:
            req_id = 0

        all_request_data.append({id_user: [{str(int(req_id)+1): [{"1": {"time": str(date_now),"text": str(request), "status": "Не отвечено", "from": "user"}}]}]})
        with open('requests.json', 'w') as file:
            json.dump(all_request_data, file, indent=2, ensure_ascii=False)
        new_req = int(req_id) + 1
        bot.send_message(message.chat.id, 'Ваш запрос под ID {} создан. Посмотреть текущие запросы можно нажав кнопку <b>Мои текущие запросы</b>'.format(new_req), parse_mode='html', reply_markup=markup_main)
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup_main)

def take_req_message(message, req_write_id):
    markup_user = types.InlineKeyboardMarkup(row_width=1)
    back_user_item = types.InlineKeyboardButton("Назад", callback_data='back_user_req')
    markup_user.add(back_user_item)

    new_request = str(message.text)
    id_user = message.from_user.id
    id_req = req_write_id

    if new_request.lower() != 'отмена':
        dt = datetime.datetime.now()
        date_now = dt.strftime('%d.%m.%Y %H:%M:%S')

        try:
            all_request_history = json.load(open('requests.json'))
        except:
            all_request_history = []

        if str(all_request_history) != '[]':
            for all_data in all_request_history:
                for user_id in all_data:                    
                    if user_id == str(id_user):
                        for req_user in all_data[user_id]:
                            for req_id in req_user:
                                if str(req_id) == id_req:
                                    for item in req_user[req_id][0]:
                                        pass
                                break
                            break
                        break
                    break

        if str(all_request_history) != '[]':
            for all_data in all_request_history:
                for user_id in all_data:
                    if user_id == str(id_user):
                        for req_user in all_data[user_id]:
                            for req_id in req_user:
                                if str(req_id) == id_req:
                                    try:
                                        req_user[req_id][0]['1']['status'] = 'Не отвечено'
                                    except Exception:
                                        pass
                                break
                            break
                        break
                    break

        all_request_history.append({id_user: [{str(int(id_req)): [{int(item)+1: {"time": str(date_now),"text": str(new_request), "status": "Не отвечено", "from": "user"}}]}]})

        with open('requests.json', 'w') as file:
           json.dump(all_request_history, file, indent=2, ensure_ascii=False)

        bot.send_message(message.chat.id, 'Ваша заявка успешно дополнена! Ожидайте ответа от наших сотрудников поддержки.', reply_markup=markup_user)

    elif new_request.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup_user)

    

def take_sup_message(message, req_write_id, to_id):
    markup_sup = types.InlineKeyboardMarkup(row_width=1)
    back_sup_item = types.InlineKeyboardButton("Назад", callback_data='cur_requests')
    markup_sup.add(back_sup_item)

    new_request = str(message.text)
    id_req = req_write_id
    to_id_write = to_id

    if new_request.lower() != 'отмена':
        dt = datetime.datetime.now()
        date_now = dt.strftime('%d.%m.%Y %H:%M:%S')

        try:
            all_request_history = json.load(open('requests.json'))
        except:
            all_request_history = []

        if str(all_request_history) != '[]':
            for all_data in all_request_history:
                for user_id in all_data:          
                    if str(user_id) == str(to_id_write):           
                        for req_user in all_data[user_id]:
                            for req_id in req_user:
                                if str(req_id) == id_req:
                                    for item in req_user[req_id][0]:
                                        pass
                                break
                            break
                        break

        if str(all_request_history) != '[]':
            for all_data in all_request_history:
                for user_id in all_data:
                    if user_id == str(to_id_write):
                        for req_user in all_data[user_id]:
                            for req_id in req_user:
                                if str(req_id) == id_req:
                                    try:
                                        req_user[req_id][0]['1']['status'] = 'Отвечено'
                                    except Exception:
                                        pass
                                break
                            break
                        break

        all_request_history.append({to_id_write: [{str(int(id_req)): [{int(item)+1: {"time": str(date_now),"text": str(new_request), "status": "Не отвечено", "from": "support"}}]}]})
        with open('requests.json', 'w') as file:
           json.dump(all_request_history, file, indent=2, ensure_ascii=False)
        bot.send_message(message.chat.id, 'Запрос успешно дополнен!', reply_markup=markup_sup)
        text_to_user = '⚠️ Получен новый ответ на ваш запрос!\n\n🧑‍💻 Ответ агента поддержки\n' +  str(date_now) + '\n' + str(new_request)
        bot.send_message(to_id_write, text_to_user, reply_markup=markup_main)

    elif new_request.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup_sup)
                
def take_agent_message(message):
    agent_text = message.text

    if agent_text.lower() != 'отмена':
        with open('base_support.json', 'r') as file:
            json_agent_data = json.load(file)
        json_agent_data.append(agent_text)
        with open('base_support.json', 'w') as file:
            json.dump(json_agent_data, file, ensure_ascii=False)
        bot.send_message(message.chat.id, 'Агент успешно добавлен\n\nВыберите раздел админ панели:', reply_markup=markup_admin_panel)

    elif agent_text.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup_admin_panel)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    id_user = str(call.message.chat.id)

    back_markup_admin = types.InlineKeyboardMarkup(row_width=1)
    back_admin_item = types.InlineKeyboardButton("Назад", callback_data='back_admin')
    back_markup_admin.add(back_admin_item)

    markup_user = types.InlineKeyboardMarkup(row_width=1)
    back_user_item = types.InlineKeyboardButton("Назад", callback_data='back_user_req')
    markup_user.add(back_user_item)

    if call.message:
        if call.data == 'back_user_req':
            id_user = call.message.chat.id

            try:
                all_request_history = json.load(open('requests.json'))
            except:
                all_request_history = []

            my_req_markup = types.InlineKeyboardMarkup(row_width=2)
            if str(all_request_history) != '[]':
                for all_data in all_request_history:
                    for user_id in all_data:
                        if str(user_id) == str(id_user):                        
                            for req_user in all_data[user_id]:
                                for req_id in req_user:
                                    for item in req_user[req_id][0]:
                                        if req_user[req_id][0][item]['status'] == 'Не отвечено':
                                            if int(item) == 1:
                                                req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ⏳', callback_data='ID:' + 'send' + req_id)
                                                my_req_markup.row(req_id)
                                                break
                                        elif req_user[req_id][0][item]['status'] == 'Отвечено':
                                            if int(item) == 1:
                                                req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ⚠️', callback_data='ID:' + 'wait' + req_id)
                                                my_req_markup.row(req_id)
                                                break
                                        elif req_user[req_id][0][item]['status'] == 'Завершено':
                                            if int(item) == 1:
                                                req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ✅', callback_data='ID:' + 'done' + req_id)
                                                my_req_markup.row(req_id)
                                                break
                                    break
                                break
                            break
                        break
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='⏳ Ожидает ответа от технической поддержки\n\n⚠️ Ожидает ответа от пользователя\n\n✅ Завершено\n\nЧтобы прочитать, либо дополнить обращение - нажмите на запрос', reply_markup=my_req_markup)

        if 'ID:' in call.data:
            call_status = call.data[3:7]
            call_req = call.data[7:] # DELETE ID:

            try:
                all_request_history = json.load(open('requests.json'))
            except:
                all_request_history = []

            text_req = ''
            if str(all_request_history) != '[]':
                for all_data in all_request_history:
                    for user_id in all_data:
                        if user_id == id_user:
                            for req_user in all_data[user_id]:
                                for req_id in req_user:
                                    if str(req_id) == call_req:
                                        for item in req_user[req_id][0]:
                                            if req_user[req_id][0][item]['from'] == 'user':
                                                text_req += ('👤 Ваше сообщение ' + '\n' + req_user[req_id][0][item]['time'] + '\n' + req_user[req_id][0][item]['text'] + '\n\n')
                                            elif 'support' in req_user[req_id][0][item]['from']:
                                                text_req += ('🧑‍💻 Ответ агента поддержки ' + '\n' + req_user[req_id][0][item]['time'] + '\n' + req_user[req_id][0][item]['text'] + '\n\n')
                                            break
                                        req_num = req_id
                                        break
                                    break
                                break
                            break
                        break

            text_req = text_req[:-2] # DELETE LAST \n\n


            if call_status == 'send':
                markup_user = types.InlineKeyboardMarkup(row_width=1)
                back_user_item = types.InlineKeyboardButton("Назад", callback_data='back_user_req')
                write_user_item = types.InlineKeyboardButton("Ответить", callback_data='add_user_req' + req_num)
                complete_user_item = types.InlineKeyboardButton("Завершить запрос", callback_data='comp_user_req' + req_num)
                markup_user.add(write_user_item, complete_user_item, back_user_item)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_req, reply_markup=markup_user)
            elif call_status == 'wait':
                markup_user = types.InlineKeyboardMarkup(row_width=1)
                back_user_item = types.InlineKeyboardButton("Назад", callback_data='back_user_req')
                write_user_item = types.InlineKeyboardButton("Ответить", callback_data='add_user_req' + req_num)
                complete_user_item = types.InlineKeyboardButton("Завершить запрос", callback_data='comp_user_req' + req_num)
                markup_user.add(write_user_item, complete_user_item, back_user_item)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_req, reply_markup=markup_user)
            elif call_status == 'done':
                markup_user = types.InlineKeyboardMarkup(row_width=1)
                back_user_item = types.InlineKeyboardButton("Назад", callback_data='back_user_req')
                markup_user.add(back_user_item)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_req, reply_markup=markup_user)

        if 'add_user_req' in call.data:
            req_write_id = call.data[12:]
            get_req_message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Чтобы дополнить ваш запрос - отправьте свое сообщение ниже.\nЧтобы отменить действие, отправьте слово Отмена.')

            bot.register_next_step_handler(get_req_message, take_req_message, req_write_id)

        if 'comp_user_req' in call.data:
            req_done_id = call.data[13:]
            confirm_done = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Да", callback_data='true_done_req' + req_done_id)
            item2 = types.InlineKeyboardButton("Нет", callback_data='ID:'+'wait' + req_done_id)
            confirm_done.add(item1)
            confirm_done.row(item2)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы точно хотите завершить запрос?", reply_markup=confirm_done)   

        if 'true_done_req' in call.data:
            req_true_done = call.data[13:]

            try:
                all_request_history = json.load(open('requests.json'))
            except:
                all_request_history = []

            if str(all_request_history) != '[]':
                for all_data in all_request_history:
                    for user_id in all_data:
                        if user_id == str(id_user):
                            for req_user in all_data[user_id]:
                                for req_id in req_user:
                                    if str(req_id) == str(req_true_done):
                                        try:
                                            req_user[req_id][0]['1']['status'] = 'Завершено'
                                        except Exception:
                                            pass
                                    break
                                break
                            break
                        break

            with open('requests.json', 'w') as file:
                json.dump(all_request_history, file, indent=2, ensure_ascii=False)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Завершено", reply_markup=markup_user) 


 ##       SUPPORT
        if call.data == 'back_sup_panel':
            support_id = str(call.message.chat.id)
            with open('base_support.json', 'r') as file:
                json_support_data = json.load(file)

            if support_id in json_support_data: 
                markup_back_panel = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton("✉️ Текущие запросы", callback_data='cur_requests')
                item2 = types.InlineKeyboardButton("🗂 История", callback_data='all_history')
                markup_back_panel.add(item1)
                markup_back_panel.row(item2)

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите раздел технической панели:', parse_mode='html', reply_markup=markup_back_panel)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Тебя нет в базе.', reply_markup=markup_main)

        if call.data == 'cur_requests':
            try:
                all_request_history = json.load(open('requests.json'))
            except:
                all_request_history = []

            sup_req_markup = types.InlineKeyboardMarkup(row_width=2)
            if str(all_request_history) != '[]':
                for all_data in all_request_history:
                    for user_id in all_data:
                        for req_user in all_data[user_id]:
                            for req_id in req_user:
                                for item in req_user[req_id][0]:
                                    if req_user[req_id][0][item]['status'] == 'Не отвечено':
                                        if int(item) == 1:
                                            req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ⏳', callback_data='wrsupID:' + 'send' + req_id)
                                            sup_req_markup.row(req_id)
                                            break
                                        break
                                    break
                                break
                            break
                        break

            back_sup_item = types.InlineKeyboardButton('Назад', callback_data='back_sup_panel')
            sup_req_markup.row(back_sup_item)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на запрос, чтобы ответить на него.', reply_markup=sup_req_markup)

        if 'wrsupID:' in call.data:
            call_status = call.data[8:12]
            call_req = call.data[12:] # DELETE ID:
            try:
                all_request_history = json.load(open('requests.json'))
            except:
                all_request_history = []

            text_req = ''
            if str(all_request_history) != '[]':
                for all_data in all_request_history:
                    for user_id in all_data:
                        for req_user in all_data[user_id]:
                            for req_id in req_user:
                                if str(req_id) == call_req:
                                    for item in req_user[req_id][0]:
                                        if req_user[req_id][0][item]['from'] == 'user':
                                            text_req += ('👤 Cообщение пользователя' + '\n' + req_user[req_id][0][item]['time'] + '\n' + req_user[req_id][0][item]['text'] + '\n\n')
                                        elif 'support' in req_user[req_id][0][item]['from']:
                                            text_req += ('🧑‍💻 Ответ агента поддержки ' + '\n' + req_user[req_id][0][item]['time'] + '\n' + req_user[req_id][0][item]['text'] + '\n\n')
                                        break
                                    req_num = req_id
                                    to_id_write = user_id
                                    break
                                break
                            break
                        break

            text_req = text_req[:-2] # DELETE LAST \n\n


            if call_status == 'send':
                markup_sup_wr = types.InlineKeyboardMarkup(row_width=1)
                back_sup_wr_item = types.InlineKeyboardButton("Назад", callback_data='cur_requests')
                write_sup_wr_item = types.InlineKeyboardButton("Ответить", callback_data=to_id_write + ':add_sup_req:' + req_num)
                markup_sup_wr.add(write_sup_wr_item, back_sup_wr_item)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_req, reply_markup=markup_sup_wr)

        if 'add_sup_req' in call.data:
            parts = call.data.rsplit(':', 2)
            to_id = parts[0]
            req_write_id = parts[2]
            get_req_message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Чтобы ответить на запрос - отправьте свое сообщение ниже.\nЧтобы отменить действие, отправьте слово Отмена.')

            bot.register_next_step_handler(get_req_message, take_sup_message, req_write_id, to_id)

        if call.data == 'all_history':
            try:
                all_request_history = json.load(open('requests.json'))
            except:
                all_request_history = []

            sup_req_markup = types.InlineKeyboardMarkup(row_width=2)
            if str(all_request_history) != '[]':
                for all_data in all_request_history:
                    for user_id in all_data:
                        for req_user in all_data[user_id]:
                            for req_id in req_user:
                                for item in req_user[req_id][0]:
                                    if req_user[req_id][0][item]['status'] == 'Не отвечено':
                                        if int(item) == 1:
                                            req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ⏳', callback_data='supID:' + 'send' + req_id)
                                            sup_req_markup.row(req_id)
                                    elif req_user[req_id][0][item]['status'] == 'Отвечено':
                                        if int(item) == 1:
                                            req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ⚠️', callback_data='supID:' + 'wait' + req_id)
                                            sup_req_markup.row(req_id)
                                    elif req_user[req_id][0][item]['status'] == 'Завершено':
                                        if int(item) == 1:
                                            req_id = types.InlineKeyboardButton('ID: ' + str(req_id) + ' Статус: ✅', callback_data='supID:' + 'done' + req_id)
                                            sup_req_markup.row(req_id)

                                break
                            break
                        break

            back_sup_item = types.InlineKeyboardButton('Назад', callback_data='back_sup_panel')
            sup_req_markup.row(back_sup_item)
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='⏳ Ожидает ответа от технической поддержки\n\n⚠️ Ожидает ответа от пользователя\n\n✅ Завершено\n\nЧтобы прочитать - нажмите на запрос.', reply_markup=sup_req_markup)

        if 'supID:' in call.data:
            call_status = call.data[6:10]
            call_req = call.data[10:] # DELETE ID:

            try:
                all_request_history = json.load(open('requests.json'))
            except:
                all_request_history = []

            text_req = ''
            if str(all_request_history) != '[]':
                for all_data in all_request_history:
                    for user_id in all_data:
                        for req_user in all_data[user_id]:
                            for req_id in req_user:
                                if str(req_id) == call_req:
                                    for item in req_user[req_id][0]:
                                        if req_user[req_id][0][item]['from'] == 'user':
                                            text_req += ('👤 Cообщение пользователя ' + '\n' + req_user[req_id][0][item]['time'] + '\n' + req_user[req_id][0][item]['text'] + '\n\n')
                                        elif 'support' in req_user[req_id][0][item]['from']:
                                            text_req += ('🧑‍💻 Ответ агента поддержки ' + '\n' + req_user[req_id][0][item]['time'] + '\n' + req_user[req_id][0][item]['text'] + '\n\n')
                                        break
                                    req_num = req_id
                                    break
                                break
                            break
                        break

            text_req = text_req[:-2] # DELETE LAST \n\n


            if call_status == 'send':
                markup_sup = types.InlineKeyboardMarkup(row_width=1)
                back_sup_item = types.InlineKeyboardButton("Назад", callback_data='all_history')
                markup_sup.add(back_sup_item)

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_req, reply_markup=markup_sup)
            elif call_status == 'wait':
                markup_sup = types.InlineKeyboardMarkup(row_width=1)
                back_sup_item = types.InlineKeyboardButton("Назад", callback_data='all_history')
                markup_sup.add(back_sup_item)

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_req, reply_markup=markup_sup)
            elif call_status == 'done':
                markup_sup = types.InlineKeyboardMarkup(row_width=1)
                back_sup_item = types.InlineKeyboardButton("Назад", callback_data='all_history')
                markup_sup.add(back_sup_item)
    
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_req, reply_markup=markup_sup)



 ## ADMIN
        if call.data == 'back_admin':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите раздел админ панели:', reply_markup=markup_admin_panel)

        if call.data == 'del_agent':
            all_sup_markup = types.InlineKeyboardMarkup(row_width=1)
            with open('base_support.json', 'r') as file:
                json_sup_data = json.load(file)

                for support in json_sup_data:
                    support = types.InlineKeyboardButton(support, callback_data='support:' + support)
                    all_sup_markup.add(support)
                all_sup_markup.add(back_admin_item)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Нажмите на агента поддержки, чтобы удалить его\nВсе агенты:", reply_markup=all_sup_markup)

        if call.data == 'add_agent':

            get_agent_message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Чтобы добавить агента поддержки - введите его ID Telegram.\nЧтобы отменить действие, отправьте слово Отмена.')
            bot.register_next_step_handler(get_agent_message, take_agent_message)

        if 'support:' in call.data:
            call_sup = call.data[8:]
            with open('base_support.json', 'r') as file:
                json_sup_data = json.load(file)
            json_sup_data.remove(call_sup)
            with open('base_support.json', 'w') as file:
                json.dump(json_sup_data, file, ensure_ascii=False)
            all_sup_markup = types.InlineKeyboardMarkup(row_width=1)
            with open('base_support.json', 'r') as file:
                json_sup_data = json.load(file)

                for support in json_sup_data:
                    support = types.InlineKeyboardButton(support, callback_data='support:' + support)
                    all_sup_markup.add(support)
                all_sup_markup.add(back_admin_item)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Нажмите на пароль, чтобы удалить его\nВсе пароли:", reply_markup=all_sup_markup)        

        if call.data == 'all_pass':
            all_pass_markup = types.InlineKeyboardMarkup(row_width=1)
            with open('pass.json', 'r') as file:
                json_pass_data = json.load(file)
                for password in json_pass_data:
                    password = types.InlineKeyboardButton(password, callback_data='password:' + password)
                    all_pass_markup.add(password)
                all_pass_markup.add(back_admin_item)
                
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Нажмите на пароль, чтобы удалить его\nВсе пароли:", reply_markup=all_pass_markup)

        if 'password:' in call.data:
            call_pass = call.data[9:]
            with open('pass.json', 'r') as file:
                json_pass_data = json.load(file)
            json_pass_data.remove(call_pass)
            with open('pass.json', 'w') as file:
                json.dump(json_pass_data, file, ensure_ascii=False)
            all_pass_markup = types.InlineKeyboardMarkup(row_width=1)
            with open('pass.json', 'r') as file:
                json_pass_data = json.load(file)
                for password in json_pass_data:
                    password = types.InlineKeyboardButton(password, callback_data='password:' + password)
                    all_pass_markup.add(password)
                all_pass_markup.add(back_admin_item)

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Нажмите на пароль, чтобы удалить его\nВсе пароли:", reply_markup=all_pass_markup)            
                    
        if call.data == 'gen_pass':
            chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
            number = 10 # число сгенированных паролей
            length = 15 # количество символов в пароле
            pass_data = []
            for n in range(number):
                password = ''
                for i in range(length):
                    password += random.choice(chars)
                pass_data.append(str(password))
                with open('pass.json', 'w') as file:
                    json.dump(pass_data, file, ensure_ascii=False)
                    
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Сгенерировано " + str(number) + " паролей", reply_markup=back_markup_admin)  

        if call.data == 'stop_bot':
            confirm_stop = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Да", callback_data='true_stop')
            item2 = types.InlineKeyboardButton("Нет", callback_data='back_admin')
            confirm_stop.add(item1)
            confirm_stop.row(item2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы точно хотите отключить бота?", reply_markup=confirm_stop)            

        if call.data == 'true_stop':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Бот оключен.')
            bot.stop_polling()


bot.polling(none_stop=True)