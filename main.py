import numpy as np
import schedule
import telebot


from functions import *

'''Initialization'''

# telegram bot
bot = telebot.TeleBot('5951740364:AAGDj1J-nrShBTl4nIK5Ep2gYfgUPUmsx84')

# Admin's and owner's chat log
LOG_CHAT_ID = 5934594152
OWNER_ID = 5934594152

# users database
# TODO: add SQL/dumps
users_dict = np.load('bd.npy', allow_pickle=True, fix_imports=True).item()
users_dict = dict(users_dict)


def update_database():
    np.save('bd.npy', users_dict)


# cooldown info
cooldown = {}
requests_count = {}


def clear_cooldown():
    global cooldown, requests_count
    cooldown = {}
    requests_count = {}
    schedule.every().day.at("00:00").do(clear_cooldown)


# templates
keyboard1 = telebot.types.ReplyKeyboardMarkup(True, False)
keyboard1.row('Информация', 'Расписание')
keyboard1.row('Ввести данные', 'Узнать свои данные')

''' Bot events '''


# Welcoming
@bot.message_handler(commands=['start'])
def start(message):
    welcome_sticker = open('additional/welcome.tgs', 'rb')
    bot.send_sticker(message.chat.id, welcome_sticker)
    mess = f'Привет, {message.from_user.first_name}!!!'
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=keyboard1)
    mess = f'Данный бот предназначен для облегчения получения расписания в нашем любимом ЕГУ) ' \
           f'он совсем еще необкатан, так что при возникновении каких либо проблемм пишите @Zahar_i4 ' \
           f'приятного использовния)'
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=keyboard1)
    # bot.send_message(message.chat.id, message.chat.id, reply_markup=keyboard1)


# main commands
to_send_logs = []  # list of logs

@bot.message_handler(content_types=["text"])
def get_user_text(message):
    # bot.send_message(message.chat.id, message, reply_markup=keyboard1)
    # bot.send_message(message.chat.id, {message.from_user.id: ['None', 'None', 0]})
    ### np.save('bd.npy', {message.from_user.id: ['None', 'None', 0]})

    formatted_message = str(message.text).lower()

    # adding new users
    if message.from_user.id not in users_dict:
        users_dict.update({message.from_user.id: ['None', 'None', 0]})

    # chat checking
    if message.from_user.id != message.chat.id:
        bot.send_message(message.chat.id, 'Бот не доступен для использования в чатах. Используйте личные сообщения')

    # logs
    global to_send_logs
    if to_send_logs:
        for log in to_send_logs:
            if str(log):
                bot.send_message(LOG_CHAT_ID, str(log))
        to_send_logs = []

    # cooldown and requests count
    if message.from_user.id in cooldown:
        if datetime.now() < cooldown[message.from_user.id] and (formatted_message == 'расписание'):
            seconds = (cooldown[message.from_user.id] - datetime.now()).total_seconds()
            bot.send_message(message.chat.id, f'Подождите {round(seconds)} секунд перед повторным запросом')
            return
    if message.from_user.id not in requests_count:
        requests_count[message.from_user.id] = 0

    # dev commands
    if message.from_user.id == OWNER_ID:
        if formatted_message == 'пользователи':
            bot.send_message(message.chat.id, f'Использует {len(users_dict) - 1}')
            return
        elif formatted_message[:8] == 'рассылка':
            bot.send_message(message.chat.id, 'Делаю рассылку')
            correct_messages_counter = 0
            messages_counter = 0
            for i in users_dict:
                messages_counter += 1
                try:
                    bot.send_message(i, str(message.text).split('\n')[-1])
                    correct_messages_counter += 1
                except Exception as e:
                    print(e)
            bot.send_message(message.chat.id, f'Конец. Успешно {correct_messages_counter}/{messages_counter}')
            return
        elif formatted_message[:3] == 'бан':
            if len(formatted_message.split(' ')) == 2:
                ban_id = formatted_message[formatted_message.find(' ') + 1:]
                if ban_id.isdigit():
                    if int(ban_id) in users_dict:
                        users_dict[int(ban_id)][2] = -1
                        update_database()
                        bot.send_message(message.chat.id, f'Забанен {ban_id}')
                        return
        elif formatted_message[:5] == 'анбан':
            if len(formatted_message.split(' ')) == 2:
                ban_id = formatted_message[formatted_message.find(' ') + 1:]
                if ban_id.isdigit():
                    if int(ban_id) in users_dict:
                        users_dict[int(ban_id)][2] = 0
                        update_database()
                        bot.send_message(message.chat.id, f'Разбанен {ban_id}')
                        return
        elif formatted_message[:5] == 'сброс':
            if len(formatted_message.split(' ')) == 2:
                reset_id = formatted_message[formatted_message.find(' ') + 1:]
                if reset_id.isdigit():
                    if int(reset_id) in users_dict:
                        requests_count[int(reset_id)] = 0
                        bot.send_message(message.chat.id, f'Сброшен {reset_id}')
                        return

    # bans
    if users_dict[message.from_user.id][2] == -1:
        bot.send_message(message.chat.id, 'Вы были заблокированы. Для подробностей обращайтесь к @Zahar_i4')
        return

    # default commands
    if formatted_message == 'информация':
        s1 = 'Привет! Я бот для получения расписания с moodle.' \
             ' В данный момент я могу получать и отправлять списком твое расписание'
        s2 = 'По всем вопросам и предложениям: @Zahar_i4'
        bot.send_message(message.chat.id, s1)
        bot.send_message(message.chat.id, s2, reply_markup=keyboard1)

    elif formatted_message == 'расписание':
        if users_dict[message.from_user.id][0] != 'None':
            if requests_count[message.from_user.id] > 20:
                bot.send_message(message.chat.id,
                                 'Слишком много запросов(>20) за день. Если возникла какая-то ошибка, напишите @Zahar_i4')
                return
            bot.send_message(message.chat.id,
                             'Получение расписания. Если бот долго не отвечает, попробуйте запросить расписание ещё раз')
            try:
                # timetable = get_timetable(users_dict[message.from_user.id][0], users_dict[message.from_user.id][1])
                trial_authentication_result = auth_moodle(users_dict[message.from_user.id][0], users_dict[message.from_user.id][1])

                if trial_authentication_result == 'Moodle':
                    bot.send_message(message.chat.id, 'Юху ауентификация пройдена')
                elif trial_authentication_result == 'Moodle: Log in to the site':
                    bot.send_message(message.chat.id, 'Упс, бобо')
                cooldown[message.from_user.id] = datetime.now() + timedelta(seconds=10)
                requests_count[message.from_user.id] += 1
            except Exception as e:
                print(e)
                if str(e):
                    bot.send_message(LOG_CHAT_ID, str(e))
                bot.send_message(message.chat.id, 'Ошибка ER. Проверьте введённые данные или напишите @Zahar_i4')
                return
            # bot.send_message(message.chat.id, timetable)
            bot.send_message(LOG_CHAT_ID, f'Получил расписание {message.from_user.id}')
        else:
            bot.send_message(message.chat.id, 'У нас нету ваших логина и пароля :( Попробуйте ввести данные ещё раз',
                             reply_markup=keyboard1)

    elif formatted_message == 'ввести данные':
        s1 = 'Введите логин и пароль через пробел (в логине и пароле нельзя использовать пробел)'
        bot.send_message(message.chat.id, s1, reply_markup=keyboard1)
        # next message will be login:password
        # noinspection PyTypeChecker
        users_dict[message.from_user.id][2] = 1
    elif formatted_message == 'узнать свои данные':
        login, password = users_dict[message.from_user.id][0], users_dict[message.from_user.id][1]
        bot.send_message(message.chat.id, f'Логин: {login}. Пароль:{password}', reply_markup=keyboard1)
    # login, password
    elif users_dict[message.from_user.id][2] == 1:
        if len(formatted_message.split(' ')) == 2:
            login, password = message.text.split(' ')
            users_dict.update({message.from_user.id: [login, password, 0]})
            log = '{} - {}:{} - {} {} - @{}'.format(str(get_time().strftime("%B %d, %Y. %H:%M")), login, password,
                                                    message.from_user.first_name, message.from_user.last_name,
                                                    message.from_user.username)
            bot.send_message(LOG_CHAT_ID, log)
            bot.send_message(LOG_CHAT_ID, 'Upd')
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, 'Данные успешно обновлены', reply_markup=keyboard1)
        else:
            bot.send_message(message.chat.id,
                             'Неверный формат. Попробуйте ещё-раз. Логин и пароль вводятся через пробел',
                             reply_markup=keyboard1)
            bot.delete_message(message.chat.id, message.message_id)
    else:
        bot.send_message(message.chat.id,
                         'Я тебя не понимаю :( Если ты считаешь, что я должен тебе отвечать на такие сообщения, напиши @Zahar_i4')

    update_database()


bot.polling(none_stop=True)
