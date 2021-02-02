from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import pickle
import time
import telegram
from random import randint
from constants import *
from https import *
import sqlite3
import requests
from loc_requests import *
import apiai, json

def contacting(update, context):
    print('Контакт получен')
    verification(update, context)


def verification(update, context):
    user_id = update.message.chat_id
    number = update.message.contact.phone_number
    conn = sqlite3.connect('adminfile/database.sqlite')
    cursor = conn.cursor()
    code_in_table = cursor.execute('''
                        select CODE
                        from Users
                        where TELEGRAM_ID = '{}'
                    '''.format(user_id)).fetchall()
    code_in_table = (code_in_table[0][0])
    requests.post(SMS_URL, data={'token': sms_token,
                                 'sms_phone': '{}'.format(number),
                                 'sms_text': '{}'.format(code_in_table)})
    typing(update,context)
    context.bot.send_message(chat_id=user_id, text='Вам на номер телефона пришёл код. Введите его пожалуйста.')
    print('Смс отправлено на номер {}'.format(number))
    print('Код: {}'.format(code_in_table))
    cursor.execute('''
            UPDATE Users
            SET PHONE_NUMBER = {}
            WHERE TELEGRAM_ID ={}'''.format(number, user_id))
    conn.commit()


def typing(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat_id,
                                 action=telegram.ChatAction.TYPING)
    time.sleep(3)

def sending_photo(update, context):
    context.bot.send_chat_action(chat_id=update.callback_query.from_user.id,
                                 action=telegram.ChatAction.UPLOAD_PHOTO)
    time.sleep(2)

def sending_doc(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat_id,
                                 action=telegram.ChatAction.UPLOAD_DOCUMENT)
    time.sleep(2)

def hello(update, context):
    typing(update, context)
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=start_msg)
    name = update.message.from_user.first_name
    user_id = update.message.chat_id
    file = open('adminfile/users.txt', 'rb')
    users = list(pickle.load(file))
    file.close()

    users.append('{} нажал start \n'.format(name))

    file = open('adminfile/users.txt', 'wb')
    pickle.dump(users, file)
    file.close()
    conn = sqlite3.connect('adminfile/database.sqlite')
    x = randint(1000, 10000)
    cursor = conn.cursor()
    table_id = (cursor.execute('''
    select TELEGRAM_ID
    from Users
    where TELEGRAM_ID = '{}'
    '''.format(user_id)).fetchall())
    if len(table_id) == 0:
        cursor.execute('''
                insert into Users values ('{}', '{}', 0, '{}', 0)
                '''.format(int(user_id), str(name), x))
        conn.commit()
    code_stage = cursor.execute('''
                               select CODE_STADIA_ID
                               from Users
                               where TELEGRAM_ID = '{}'
                           '''.format(user_id)).fetchall()
    code_stage = code_stage[0][0]
    print(code_stage)
    if code_stage == 0:
        typing(update, context)
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=next_msg)
        cont_butt = [KeyboardButton(text='Скинуть контакт',callback_data='contact', request_contact=True)]
        context.bot.send_message(chat_id=user_id, text='После этого - весь функционал будет доступен', reply_markup=ReplyKeyboardMarkup([cont_butt], one_time_keyboard=True, resize_keyboard=True))
    else:
        buttons(update, context)

def buttons(update, context):
    typing(update, context)
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=go_msg)
    user_id = update.message.chat_id
    top_buttons_list = [
        InlineKeyboardButton(text='Назови моё имя', callback_data='name')
    ]
    mid_buttons_list = [
        InlineKeyboardButton(text='Хочу в галлерею', callback_data='gallery')
    ]
    bot_buttons_list = [
        InlineKeyboardButton(text='Рандомное число!', callback_data='randomize')
    ]
    bot_bot_buttons_list = [
        InlineKeyboardButton(text='Мой телеграм ID', callback_data='tg_id')
    ]
    context.bot.send_message(chat_id=user_id,
                             text='Чего желаете?',
                             reply_markup=InlineKeyboardMarkup([top_buttons_list, mid_buttons_list, bot_buttons_list, bot_bot_buttons_list]))
    loc_butt = [
        KeyboardButton(text='Узнать свой адрес', request_location=True)
    ]
    typing(update, context)
    context.bot.send_message(chat_id=user_id, text='Кнопки - бывают разные)', reply_markup=ReplyKeyboardMarkup([loc_butt],resize_keyboard=True))

def t_answ(update, context):
    user_id = update.message.chat_id
    name = update.message.from_user.first_name
    user_message = update.message.text
    file = open('adminfile/logs.txt', 'rb')
    logs = list(pickle.load(file))
    file.close()
    logs.append('Получено сообщение {} от: {} \n'.format(user_message,name))
    file = open('adminfile/logs.txt', 'wb')
    pickle.dump(logs, file)
    file.close()
    conn = sqlite3.connect('adminfile/database.sqlite')
    cursor = conn.cursor()
    code_stage = cursor.execute('''
                            select CODE_STADIA_ID
                            from Users
                            where TELEGRAM_ID = '{}'
                        '''.format(user_id)).fetchall()
    code_stage = code_stage[0][0]
    code_in_table = cursor.execute('''
                            select CODE
                            from Users
                            where TELEGRAM_ID = '{}'
                        '''.format(user_id)).fetchall()
    code_in_table = (code_in_table[0][0])
    if len(user_message) == 4 and user_message.isalnum and code_stage == 0 :
        if int(user_message) == int(code_in_table):
            context.bot.send_message(chat_id=user_id, text='Супер! Наслаждайтесь полным функционалом!')
            cursor.execute('''
                                    UPDATE Users
                                    SET CODE_STADIA_ID = 1
                                    WHERE TELEGRAM_ID ={}'''.format(user_id))
            conn.commit()
            time.sleep(3)
            try:
                for id in range((update.message.message_id-50), update.message.message_id):
                    context.bot.delete_message(chat_id=user_id, message_id=id)
            except:
                print('Не получилось(')
            buttons(update, context)
        elif int(user_message) != int(code_in_table):
            context.bot.send_message(chat_id=user_id, text='Код неверный. Перепроверьте код.')


def checking(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text=check_msg)


def p_answ(update, context):
    user_id = update.message.chat_id
    photo_id = update.message.photo[-1].file_id
    file = context.bot.getFile(photo_id)
    x = ('photos/'+ str(user_id) + str(randint(0, 999)) + str(randint(0, 999)) + '.jpg')
    file.download(x)
    file.close()
    typing(update, context)
    context.bot.send_message(text='Фотка получена',
                             chat_id=update.message.chat_id)


def buttons_pht (update, context):
    user_id = update.callback_query.from_user.id

    top_buttons_list = [
        InlineKeyboardButton(text=frst_pht, callback_data='pht1'),
    InlineKeyboardButton(text=scnd_pht, callback_data='pht2')]
    mid_buttons_list = [
        InlineKeyboardButton(text=thrd_pht, callback_data='pht3'),
        InlineKeyboardButton(text=frt_pht, callback_data='pht4')]
    bot_buttons_list = [
        InlineKeyboardButton(text=fift_pht, callback_data='pht5')
    ]
    context.bot.send_message(
        text=cho_pht,
        chat_id=user_id,
        reply_markup=InlineKeyboardMarkup([top_buttons_list,mid_buttons_list, bot_buttons_list]))

def pht1(update, context):
    sending_photo(update, context)
    context.bot.send_photo(chat_id=update.callback_query.from_user.id,
                           photo=h_pht_1,
                             caption=frst_pht)

def pht2(update, context):
    sending_photo(update, context)
    context.bot.send_photo(chat_id=update.callback_query.from_user.id,
                           photo=h_pht_2,
                           caption=nar_pht)
def pht3(update, context):
    sending_photo(update, context)
    context.bot.send_photo(chat_id=update.callback_query.from_user.id,
                           photo=h_pht_3,
                             caption=cat_pht)

def pht4(update, context):
    sending_photo(update, context)
    context.bot.send_photo(chat_id=update.callback_query.from_user.id,
                           photo=h_pht_4,
                           caption=tas_pht)
def pht5(update, context):
    sending_photo(update, context)
    context.bot.send_photo(chat_id=update.callback_query.from_user.id,
                           photo=h_pht_5,
                           caption=prpd_pht)

def name(update, context):
    name = update.callback_query.from_user.first_name
    user_id = update.callback_query.from_user.id
    context.bot.send_message(chat_id=user_id,
                             text=('Ваше имя: {}'.format(name)))

def randomize(update, context):
    user_id = update.callback_query.from_user.id
    top_buttons_list = [
        InlineKeyboardButton(text='0 - 10', callback_data='rand1')]
    mid_buttons_list = [
        InlineKeyboardButton(text='0 - 50', callback_data='rand2')]
    bot_buttons_list = [
        InlineKeyboardButton(text='0 - 100', callback_data='rand3')]
    context.bot.send_message(
        text=rand_tex,
        chat_id=user_id,
        reply_markup=InlineKeyboardMarkup([top_buttons_list, mid_buttons_list, bot_buttons_list]))
def rand1(update, context):
    user_id = update.callback_query.from_user.id
    x = randint(0, 11)
    context.bot.send_message(chat_id=user_id,
                             text=rand_tex + str(x))
def rand2(update, context):
    user_id = update.callback_query.from_user.id
    x = randint(0, 51)
    context.bot.send_message(chat_id=user_id,
                             text=rand_tex + str(x))
def rand3(update, context):
    user_id = update.callback_query.from_user.id
    x = randint(0, 101)
    context.bot.send_message(chat_id=user_id,
                             text=rand_tex + str(x))

def admin(update, context):
    chat_id = update.message.chat_id
    name = update.message.from_user.first_name
    typing(update, context)
    context.bot.send_message(chat_id=chat_id,
                             text='А ты хорош {}'.format(name))
    sending_doc(update, context)
    file = open('adminfile/logs.txt', 'rb')
    context.bot.send_document(chat_id=chat_id,
                              document=file)
    file.close()
    file = open('adminfile/users.txt', 'rb')
    context.bot.send_document(chat_id=chat_id,
                              document=file)

def your_id(update, context):
    context.bot.send_photo(photo=QR_URL.format(update.callback_query.from_user.id),
                           chat_id=update.callback_query.from_user.id)

def location(update, context):
    message = update.message
    current_position = (message.location.longitude, message.location.latitude)
    coords = f"{current_position[0]},{current_position[1]}"
    address_str = get_address_from_coords(coords)
    update.message.reply_text(address_str)