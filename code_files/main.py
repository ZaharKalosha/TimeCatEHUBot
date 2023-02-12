import numpy as np
import schedule

from code_files.assistant import *
from code_files.functions import *
from code_files.work_with_google_sheets import *

'''Initialization'''

# telegram bot
bot = telebot.TeleBot('5951740364:AAEvXmHPJ_fhwVxOh5SrsBC08pDrpFuPnEY')

# Admin and owner's chat log
ADMIN_CHAT_ID = 5934594152
OWNER_ID = 5934594152  # ADMIN_CHAT_ID but without ligs

# users database
# TODO: add SQL/dumps
# users_dict description - {chat_id: ['login', 'pasword', 0, auth_flag, course, specialty, settings[]]
# np.save('../data_files/users_database.npy',
#         {OWNER_ID: ['None', 'None', 0, True, -1, 'None', ['🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл']]})
#  adding an object to the database (uncomment at the first start, otherwise there will be an error)
users_dict = np.load('../data_files/users_database.npy', allow_pickle=True, fix_imports=True).item()
users_dict = dict(users_dict)

# sheets database
# np.save('../data_files/sheets.npy', {'specialty': ['empty_url', 'empty_url', 'empty_url', 'empty_url', 'empty_url']})
#  adding an object to the database (uncomment at the first start, otherwise there will be an error)
spread_sheets_list = np.load('../data_files/sheets.npy', allow_pickle=True, fix_imports=True).item()
spread_sheets_list = dict(spread_sheets_list)

# cooldown info
cooldown = {}
requests_count = {}
requests_what_cat_are_you_today = {}

# list of logs
to_send_logs = []
settings_flag_ = [-1]


def update_database():
    np.save('../data_files/users_database.npy', users_dict)


def update_sheets_database():
    np.save('../data_files/sheets.npy', spread_sheets_list)


def clear_cooldown():
    global cooldown, requests_count
    cooldown = {}
    requests_count = {}
    schedule.every().day.at("00:00").do(clear_cooldown)


''' Bot events '''


@bot.message_handler(commands=['start'])
def start(call):
    # welcome_sticker = open('../additional_files/welcome.tgs', 'rb')
    # bot.send_sticker(call.chat.id, welcome_sticker)
    mess = '👋🏼 Привет! Я рад что ты с нами!' \
           '\n\n' \
           'Быстренько познакомлю тебя с функционалом бота:' \
           '\n\n' \
           '📒 Расписание – раздел, где ты можешь выбрать расписание своей группы и быть в курсе об всех изменениях ' \
           'и парах (для отображения расписания, вам нужно будет подтвердить свой статус студента ЕГУ ' \
           'через авторизацию через Moodle);' \
           '\n\n' \
           '🐈 Ассистент Пушистик – принесёт вам неповторимый опыт, поможет поднять настроение и отвлечься от учебы :З' \
           '\n\n' \
           '⚙️ Настройки Уведомлений – гибко адаптируйте уведомления расписания под себя. ' \
           'Так вы не упустите ни перестановки, ни изменений в расписании, ни неожиданных ранних пар;' \
           '\n\n' \
           '⚙️ Настройки Ассистента – персонализируй Пушистика под себя и свои интересы.' \
           '\n\n' \
           'Просмотреть все возможности и функционал бота ты можешь введя команду /help'
    bot.send_message(call.from_user.id, mess, parse_mode='html')
    mess = '⬇️ Снизу находятся кнопки навигации по боту и список команд'
    bot.send_message(call.from_user.id, mess, parse_mode='html', reply_markup=main_menu_reply_buttons)
    return


@bot.message_handler(commands=['timetable'])
def timetable(call):
    if not users_dict[call.from_user.id][3]:
        moodle_authentication(call)
    elif users_dict[call.from_user.id][4] == -1 or users_dict[call.from_user.id][5] == 'None':
        course_selection(call)

    if users_dict[call.from_user.id][3] \
            and users_dict[call.from_user.id][4] > 0 \
            and users_dict[call.from_user.id][5] != 'None':
        if requests_count[call.from_user.id] > 50:
            bot.send_message(call.from_user.id,
                             'Слишком много запросов(>50) за день. Если возникла какая-то ошибка, напишите '
                             '@Zahar_i4', reply_markup=main_menu_buttons)
            return
        bot.send_message(call.from_user.id,
                         'Получение расписания. Если бот долго не отвечает, попробуйте запросить расписание ещё '
                         'раз')
        for i in spread_sheets_list:
            if i == users_dict[call.from_user.id][5]:
                if i[users_dict[call.from_user.id][4] - 1] != 'empty_url':
                    getting_of_schedule(call, getting_of_week(get_number_of_week()))
                    return
        bot.send_message(call.from_user.id,
                         'Расписание для текущих настроек курса и факультеета отсутствует, напишите @Zahar_i4')
    return


def course_selection(call):
    s1 = 'Укажите свой курс:'
    bot.send_message(call.from_user.id, s1, reply_markup=course_selection_buttons)


def speciality_selection(call):
    s1 = 'Укажите свой факультет:'
    bot.send_message(call.from_user.id, s1, reply_markup=specialty_selection_buttons)


def timetable_recall(call):
    update_database()
    s1 = "⏳ Расписание загружается...."
    bot.send_message(call.from_user.id, s1)
    timetable(call)


@bot.message_handler(commands=['today'])
def today(call):
    if get_number_of_day() == 7:
        bot.send_message(call.from_user.id, 'Ой, а сегодня выходной) 🎉')
        return
    head = range_to_head_message(
        get_range(
            spread_sheets_list[users_dict[call.from_user.id][5]][users_dict[call.from_user.id][4] - 1],
            SAMPLE_RANGE_NAME),
        get_number_of_day(),
        getting_of_week(get_number_of_week()))
    body = range_to_day_massage(
        get_range(
            spread_sheets_list[users_dict[call.from_user.id][5]][users_dict[call.from_user.id][4] - 1],
            SAMPLE_RANGE_NAME),
        get_number_of_day(),
        getting_of_week(get_number_of_week()))
    bot.send_message(call.from_user.id, head + body, parse_mode='html',
                     reply_markup=schedule_output_setting_buttons)
    return


@bot.message_handler(commands=['tomorrow'])
def tomorrow(call):
    if (get_number_of_day() + 1) % 7 == 0:
        bot.send_message(call.from_user.id, 'Ой, а завтра выходной) 🎉')
        return
    next_week_flag = 0
    if get_number_of_day() + 1 > 7:
        next_week_flag = 1
    head = range_to_head_message(
        get_range(
            spread_sheets_list[users_dict[call.from_user.id][5]][users_dict[call.from_user.id][4] - 1],
            SAMPLE_RANGE_NAME),
        get_number_of_day() + 1,
        getting_of_week(get_number_of_week() + next_week_flag))
    body = range_to_day_massage(
        get_range(
            spread_sheets_list[users_dict[call.from_user.id][5]][users_dict[call.from_user.id][4] - 1],
            SAMPLE_RANGE_NAME),
        get_number_of_day() + 1,
        getting_of_week(get_number_of_week() + next_week_flag))
    bot.send_message(call.from_user.id, head + body, parse_mode='html',
                     reply_markup=schedule_output_setting_buttons)
    return


@bot.message_handler(commands=['faq'])
def faq(call):
    will_be_soon(call)


@bot.message_handler(commands=['assistant'])
def assistant(call):
    assistant_greeting(call)


@bot.message_handler(commands=['settings'])
def settings(call):
    # '🟢 вкл' '🔴 откл'
    s1 = f'🔔 Уведомления | статус' \
         f'\n\n' \
         f'√ Правки в расписании — {users_dict[call.from_user.id][6][0]}' \
         f'\n' \
         f'√ Отменённые пары — {users_dict[call.from_user.id][6][1]}' \
         f'\n' \
         f'√ О парах на завтра — {users_dict[call.from_user.id][6][2]}' \
         f'\n' \
         f'√ Начало пар в 8:30 — {users_dict[call.from_user.id][6][3]}' \
         f'\n' \
         f'√ Новые недели — {users_dict[call.from_user.id][6][4]}' \
         f'\n\n' \
         f'Выбери настройку:'

    bot.send_message(call.from_user.id, s1, reply_markup=notification_settings_buttons)
    return


@bot.message_handler(commands=['reset_timetable'])
def reset_timetable(call):
    s1 = 'Укажите свой курс:'
    bot.send_message(call.from_user.id, s1, reply_markup=course_selection_buttons)
    return


@bot.message_handler(commands=['assistant_settings'])
def assistant_settings(call):
    assistant_presets(call)


@bot.message_handler(commands=['help'])
def information(call):
    s1 = '/start - 🔁  Перезапуск бота' \
         '\n' \
         '/timetable - 📒 Расписание' \
         '\n' \
         '/today - 📆 Расписание на сегодня' \
         '\n' \
         '/tomorrow - 📆 Расписание на завтра' \
         '\n' \
         '/vacancy - 💼 Вакансии' \
         '\n' \
         '/faq - 📖 База знаний EHU' \
         '\n' \
         '/assistant - 🐈 Ассистент Пушистик' \
         '\n' \
         '/settings - ⚙️ Настройки уведомлений' \
         '\n' \
         '/reset_timetable - ⚙️ Сбрасывает настройки группы и курса для расписания' \
         '\n' \
         '/assistantsettings - ⚙️ Настройки ассистента' \
         '\n' \
         '/help - ❔ Гид по боту ' \
         '\n' \
         '/report -  📣 Сообщить о проблеме' \
         '\n' \
         '/moodle_authentication - ✅ Moodle-аутентификация' \
         '\n' \
         '/find_out_details - ❓ Узнать свои данные'

    s2 = 'По всем вопросам и предложениям: @Zahar_i4'
    bot.send_message(call.from_user.id, s1)
    bot.send_message(call.from_user.id, s2)
    return


@bot.message_handler(commands=['report'])
def report(call):
    s1 = '❓ТаймКот ЕГУ: открытый бета-тест. ' \
         + '\n' \
         + '\n' \
         + 'Бот активно развивается и обрастает новым контентом. ' \
         + '\n' \
         + '\n' \
         + 'Вы можете помочь нашему проекту, ' \
           'если поделитесь своим впечатлением и опытом использования мобильного расписания! ' \
         + '\n' \
         + '\n' \
         + 'Напишите любому из нас в личные сообщения свои отзывы о боте/предложения новых идей/сообщения об ошибках. ' \
           'Мы будем вам очень благодарны! ' \
         + '\n' \
         + '\n' \
         + '👥 Создатели: ' \
         + '\n' \
         + '@daniel_warsz — Founder ' \
         + '\n' \
         + '@Zahar_i4 — Developer ' \
         + '\n' \
         + '\n' \
         + 'TimeCat EHU | version 0.2'

    bot.send_message(call.from_user.id, s1)
    return


@bot.message_handler(commands=['moodle_authentication'])
def moodle_authentication(call):
    s1 = '👀 Для просмотра расписания вам нужно подтвердить статус студента ЕГУ через свой Moodle.' \
         '\n\n ' \
         'P.S. Бот не хранит никаких данных, кроме "галочки", что вы подтвержденный студент'
    bot.send_message(call.from_user.id, s1)
    moodle_getting_of_login(call)
    return


def moodle_getting_of_login(call):
    s1 = '✍🏼 Введите свой Moodle логин:'
    bot.send_message(call.from_user.id, s1)

    # next call will be login
    # noinspection PyTypeChecker
    users_dict[call.from_user.id][2] = 1
    return


def moodle_getting_of_password(call):
    s1 = '✍🏼 Введите свой пароль:'
    bot.send_message(call.from_user.id, s1)

    # next call will be password
    # noinspection PyTypeChecker
    users_dict[call.from_user.id][2] = 2
    return


@bot.message_handler(commands=['find_out_details'])
def find_out_details(call):
    login = users_dict[call.from_user.id][0]
    password = users_dict[call.from_user.id][1]
    authorization_flag = users_dict[call.from_user.id][3]
    year = users_dict[call.from_user.id][4]
    group = users_dict[call.from_user.id][5]
    bot.send_message(call.from_user.id,
                     f'Логин: {login}. Пароль: {password}. '
                     f'Успешность авторизации: {authorization_flag}. '
                     f'Курс: {year}. Направление: {group}.')
    # To find out the ID for adding an admin
    bot.send_message(call.from_user.id, f'Id вашего чата: {call.from_user.id}')
    return


def check_auth(message):
    bot.send_message(ADMIN_CHAT_ID, f'Upd {message.from_user.id}')
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, 'Данные успешно обновлены!')
    bot.send_message(message.chat.id, '⏳ Проверяю данные от Moodle....')
    trial_authentication_result = auth_moodle(users_dict[message.from_user.id][0],
                                              users_dict[message.from_user.id][1])

    if trial_authentication_result:
        bot.send_message(message.chat.id, '✅ Вы успешно подтвердили свой Moodle! '
                                          '\n\n'
                                          'Доступ к расписанию открыт')
        users_dict.update({message.from_user.id: ['None', 'None', 0, True, -1, 'None',
                                                  ['🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл']]})
    else:
        bot.send_message(message.chat.id, '😞 Мне не удалось проверить вас... '
                                          '\n\n'
                                          'Скорее всего, вы некорректно указали свои Moodle-данные',
                         reply_markup=relogining)
        users_dict.update({message.from_user.id: ['None', 'None', 0, False, -1, 'None',
                                                  ['🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл']]})
        bot.send_message(message.chat.id, '')
    return


def getting_of_schedule(call, week):
    bot.send_message(call.from_user.id, 'Рассписание загружается...')
    next_week_flag = 0
    if get_number_of_day() == 7:
        next_week_flag = 1

    if week + next_week_flag >= 4:
        bot.send_message(call.from_user.id, "Следующая неделя еще не загружена(",
                         reply_markup=schedule_output_setting_buttons, parse_mode='html')
        return
    head = range_to_head_message(
        get_range(
            spread_sheets_list[users_dict[call.from_user.id][5]][users_dict[call.from_user.id][4] - 1],
            SAMPLE_RANGE_NAME),
        get_number_of_day(),
        week + next_week_flag)
    mess = ['', '', '', '', '', '']

    for i in range(1, 7):
        mess[i - 1] = range_to_day_massage(
            get_range(spread_sheets_list[users_dict[call.from_user.id][5]][users_dict[call.from_user.id][4] - 1],
                      SAMPLE_RANGE_NAME), i, week + next_week_flag)
    out = ''
    for j in range(0, 6):
        out += mess[j]
    bot.send_message(call.from_user.id, head + out, reply_markup=schedule_output_setting_buttons, parse_mode='html')
    update_sheets_database()
    return


def other_format(call):
    bot.send_message(call.from_user.id, '📍 Выберите удобный формат расписания:',
                     reply_markup=schedule_output_period_setting_buttons)


@bot.message_handler(commands=['vacancy'])
def vacancy(call):
    message = 'Проект ТаймКот ищет: ' \
              + '\n' \
              + '\n' \
              + '👤 Контент-менеджера — ' \
              + '\n' \
              + 'дополнение ассистента Пушистика новым контентом: новыми мемами, котиками дня, фильмами,' \
                ' а также поиском контента для нового раздела. ' \
              + '\n' \
              + '\n' \
              + '👤 Дизайнера — ' \
              + '\n' \
              + 'Пушистик остро нуждается в дизайнере, который создаст фирменный стиль бота, создаст и нарисует котика Пушистика и создаст с ним аватарку и обложки для разделов. ' \
              + '\n' \
              + '\n' \
              + 'Если вы желаете принять участие в развитии проекта в данных направлениях – пишите мне: @daniel_warsz ' \
              + '\n' \
              + '\n' \
              + 'P.S. Проект официально зарегистрирован в ЕГУ, он подходит для подачи на конкурс портфолио'
    bot.send_message(call.from_user.id, message, reply_markup=vacancy_link_button)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.from_user.id not in users_dict:
        users_dict.update({call.from_user.id: ['None',
                                               'None',
                                               0,
                                               False,
                                               -1,
                                               'None',
                                               ['🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл']]})

    if call.data == "get_schedule":
        timetable(call)
    elif call.data == "assistant_fluffy":
        assistant(call)
    elif call.data == "notification_settings":
        settings(call)
    elif call.data == "assistant_settings":
        assistant_settings(call)

    elif call.data == "schedule_presets":
        settings_flag_[0] = 0
        bot.send_message(call.from_user.id,
                         "⏰ Бот будет сообщать вам об всех изменениях и перестановках в расписании",
                         reply_markup=on_off_buttons)
    elif call.data == "canceled_classes":
        settings_flag_[0] = 1
        bot.send_message(call.from_user.id, "⏰ Бот будет сообщать вам об всех отмененных парах",
                         reply_markup=on_off_buttons)
    elif call.data == "tomorrow's_classes":
        settings_flag_[0] = 2
        bot.send_message(call.from_user.id, "⏰ В 20:00 бот будет присылать ваше расписание на завтра",
                         reply_markup=on_off_buttons)
    elif call.data == "start_of_classes":
        settings_flag_[0] = 3
        bot.send_message(call.from_user.id, "⏰ В 19:00 бот будет напоминать вам о завтрашних ранних парах",
                         reply_markup=on_off_buttons)
    elif call.data == "new_weeks":
        settings_flag_[0] = 4
        bot.send_message(call.from_user.id, "⏰ Бот будет сообщать вам о появлении расписания на новые недели",
                         reply_markup=on_off_buttons)

    elif call.data == "relogining":
        moodle_getting_of_login(call)

    elif call.data == "on":
        users_dict[call.from_user.id][6][settings_flag_[0]] = '🟢 вкл'
        bot.send_message(call.from_user.id, "✔️ Настройки сохранены",
                         reply_markup=notification_settings_buttons)
        settings(call)
    elif call.data == "off":
        users_dict[call.from_user.id][6][settings_flag_[0]] = '🔴 откл'
        bot.send_message(call.from_user.id, "✔️ Настройки сохранены",
                         reply_markup=notification_settings_buttons)
        settings(call)

    elif call.data == "first_year":
        users_dict[call.from_user.id][4] = 1
        speciality_selection(call)
    elif call.data == "second_year":
        users_dict[call.from_user.id][4] = 2
        speciality_selection(call)
    elif call.data == "third_year":
        users_dict[call.from_user.id][4] = 3
        speciality_selection(call)
    elif call.data == "fourth_year":
        users_dict[call.from_user.id][4] = 4
        speciality_selection(call)
    elif call.data == "fifth_year":
        users_dict[call.from_user.id][4] = 5
        speciality_selection(call)

    elif call.data == "media":
        users_dict[call.from_user.id][5] = "media"
        timetable_recall(call)
    elif call.data == "design":
        users_dict[call.from_user.id][5] = "design"
        timetable_recall(call)
    elif call.data == "theater":
        users_dict[call.from_user.id][5] = "theater"
        timetable_recall(call)
    elif call.data == "policy":
        users_dict[call.from_user.id][5] = "policy"
        timetable_recall(call)
    elif call.data == "heritage":
        users_dict[call.from_user.id][5] = "heritage"
        timetable_recall(call)
    elif call.data == "law":
        users_dict[call.from_user.id][5] = "law"
        timetable_recall(call)

    elif call.data == "back":
        if spread_sheets_list[users_dict[call.from_user.id][5]][users_dict[call.from_user.id][4] - 1] != 'empty_url':
            if getting_of_week(get_number_of_week() - 1) <= getting_of_week(get_number_of_week()):
                for i in spread_sheets_list:
                    if i == users_dict[call.from_user.id][5]:
                        if i[users_dict[call.from_user.id][4] - 1] != 'empty_url':
                            getting_of_schedule(call, getting_of_week(get_number_of_week()))
                            return
            else:
                bot.send_message(call.from_user.id, 'Желаемая неделя уже устарела(')
            return
    elif call.data == "nothing":
        return
    elif call.data == "forward":
        if spread_sheets_list[users_dict[call.from_user.id][5]][users_dict[call.from_user.id][4] - 1] != 'empty_url':
            if getting_of_week(get_number_of_week() + 1) >= getting_of_week(get_number_of_week()):
                getting_of_schedule(call, getting_of_week(get_number_of_week() + 1))
            else:
                bot.send_message(call.from_user.id, 'Желаемая неделя еще не существует в рассписанииl')
            return
    elif call.data == "other_format":
        other_format(call)

    elif call.data == "today":
        today(call)
    elif call.data == "tomorrow":
        tomorrow(call)
    elif call.data == "week":
        timetable(call)

    callback_query2(call)

    update_database()
    update_sheets_database()


def will_be_soon(call):
    s1 = '🛠 Раздел находится в разработке.Совсем скоро он появится:)'
    bot.send_message(call.from_user.id, s1)
    return


@bot.message_handler(content_types=["text"])
def get_user_text(message):
    formatted_message = str(message.text).lower()

    # adding new users
    if message.from_user.id not in users_dict:
        users_dict.update({message.from_user.id: ['None',
                                                  'None',
                                                  0,
                                                  False,
                                                  -1,
                                                  'None',
                                                  ['🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл', '🔴 откл']]})

    # chat checking
    if message.from_user.id != message.chat.id:
        bot.send_message(message.chat.id, 'Бот не доступен для использования в чатах. Используйте личные сообщения')

    # logs
    global to_send_logs
    if to_send_logs:
        for log in to_send_logs:
            if str(log):
                bot.send_message(ADMIN_CHAT_ID, str(log))
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
    if message.from_user.id == OWNER_ID or message.from_user.id == ADMIN_CHAT_ID:
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
                    bot.send_message(message.chat.id, e)
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
                        requests_what_cat_are_you_today[int(reset_id)] = 0
                        bot.send_message(message.chat.id, f'Сброшен {reset_id}')
                        return

        elif formatted_message == 'новая таблица':
            s1 = 'Введите name, year и spreadsheet_id вводятся с новой строки.'
            bot.send_message(message.chat.id, s1)
            # next call will be name spreadsheet_id
            # noinspection PyTypeChecker
            users_dict[message.from_user.id][2] = 4
            return

        # name, course, spreadsheet_id
        elif users_dict[message.from_user.id][2] == 4:
            users_dict[message.from_user.id][2] = 0
            if len(formatted_message.split('\n')) == 3:
                # TODO
                name, year, spreadsheet_id = message.text.split('\n')
                # list_of_ids
                # spread_sheets_list.update({name: [spreadsheet_id]})
                # log = '{} - {}:{} - {} {} - @{}'.format(str(get_time().strftime("%B %d, %Y. %H:%M")), name,
                #                                         spreadsheet_id,
                #                                         call.from_user.first_name, call.from_user.last_name,
                #                                         call.from_user.username)
                # bot.send_message(ADMIN_CHAT_ID, log)
                if name not in spread_sheets_list:
                    spread_sheets_list.update({name: ['empty_url', 'empty_url', 'empty_url', 'empty_url', 'empty_url']})
                spread_sheets_list[name][int(year) - 1] = spreadsheet_id
                bot.send_message(ADMIN_CHAT_ID, 'Upd sheets')
                update_sheets_database()
                bot.send_message(message.chat.id, 'Данные таблиц успешно обновлены!')


            else:
                bot.send_message(message.chat.id,
                                 'Неверный формат. Попробуйте ещё-раз. name,'
                                 ' course и spreadsheet_id вводятся с новой строки')

            update_sheets_database()
            return
    # bans
    if users_dict[message.from_user.id][2] == -1:
        bot.send_message(message.chat.id,
                         'Вы были заблокированы. Для подробностей обращайтесь к @Zahar_i4')
        return

    # main commands
    if formatted_message == '📒 расписание':
        timetable(message)

    elif formatted_message == '🐈 ассистент пушистик':
        assistant(message)

    elif formatted_message == '⚙️ настр. увед.':
        settings(message)

    elif formatted_message == '⚙️ настр. ассистента':
        assistant_settings(message)

    # login, password
    elif users_dict[message.from_user.id][2] == 1:
        users_dict[message.from_user.id][0] = message.text
        bot.delete_message(message.chat.id, message.message_id)
        moodle_getting_of_password(message)
    elif users_dict[message.from_user.id][2] == 2:
        users_dict[message.from_user.id][1] = message.text
        check_auth(message)

    else:
        bot.send_message(message.chat.id,
                         'Я тебя не понимаю :( Если ты считаешь, что я должен тебе отвечать на такие сообщения, напиши '
                         '@Zahar_i4')

    update_database()


bot.polling(none_stop=True)
