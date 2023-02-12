import random

from code_files.work_with_google_sheets import *
from code_files.templates import *

bot = telebot.TeleBot('5951740364:AAEvXmHPJ_fhwVxOh5SrsBC08pDrpFuPnEY')

# https://drive.google.com/drive/folders/1d2PB53IA4RaQ8Q2KsGSasS7lwsJFqQkU
FILMS_SPREADSHEET_ID = '1fyDQUDUPqpce3lj0-ieuX_ZRd6QITOYEvAbVGEm_BHE'
FILMS_RANGE_NAME = "Movies!A2:D50"

requests_what_cat_are_you_today = {}


def assistant_greeting(call):
    message = '😸 Мяу-мяу привет!' \
              + '\n' \
              + 'Меня зовут Пушистик - я твой верный ассистент!' \
              + '\n' \
              + '\n' \
              + 'Я смогу поднять тебе настроение, рассмешить, умилить, посоветовать фильм на выходные. ' \
                'И если у тебя появится какой-либо вопрос по поводу учебы или жизни в Литве - ' \
                'я с удовольствием на него отвечу :з' \
              + '\n' \
              + '\n' \
              + 'Выбери кнопочку:'
    bot.send_message(call.from_user.id, message, reply_markup=assistant_menu_buttons)


def assistant_presets(call):
    message = '🍥 Рассылка котиков готова!' + '\n' \
              + 'Пушистик не позволит тебе загрустить перед учебой!' \
              + '\n' \
              + '\n' \
              + 'Ассистент подготовил для тебя несколько милых рассылок, ' \
                'которые смогут поднять тебе настроение в любое время.' \
              + '\n' \
              + '\n' \
              + 'Выбери рассылочку:'
    bot.send_message(call.from_user.id, message, reply_markup=assistant_settings_buttons)


@bot.callback_query_handler(func=lambda call: True)
def callback_query2(call):
    if call.data == "what_cat_are_you_today":
        what_cat_are_you_today(call)
    if call.data == "funny_from_fluffy":
        funny_from_fluffy(call)
    if call.data == "film_from_fluffy":
        film_from_fluffy(call)
    if call.data == "knowledge_base":
        knowledge_base(call)
    if call.data == "come_back_home":
        come_back_home(call)
    if call.data == "return_to_assistant":
        assistant_greeting(call)
    if call.data == "next_film":
        film_from_fluffy(call)
    if call.data == "good":
        message = '😽 Пушистик очень рад!' \
                  + '\n' \
                  + '\n' \
                  + ' У меня остались ещё фильмы для тебя.' \
                  + '\n' \
                  + ' А также, я обновляю и дополняю свой списочек фильмов каждую неделю. )'
        bot.send_message(call.from_user.id, message, reply_markup=another_film_button)
    if call.data == "bead":
        message = '😿 Мне очень жаль...' \
                  + '\n' \
                  + '\n' \
                  + ' Давай я поищу ещё какой-нибудь фильм для тебя'
        bot.send_message(call.from_user.id, message, reply_markup=another_film_button)


def what_cat_are_you_today(call):
    random_number = random.randint(1, 8)

    if call.from_user.id not in requests_what_cat_are_you_today:
        requests_what_cat_are_you_today[call.from_user.id] = random_number
    link = f'../additional_files/cats/a-kakoi-ty-kotik-images-big ({random_number}).jpg'
    photo = open(link, "rb")
    if requests_what_cat_are_you_today[call.from_user.id] > 0:
        bot.send_message(call.from_user.id, 'И сегодня ты...')
        link = f'../additional_files/cats/a-kakoi-ty-kotik-images-big ' \
               f'({requests_what_cat_are_you_today[call.from_user.id]}).jpg'
        photo = open(link, "rb")
        bot.send_photo(call.from_user.id, photo)
        bot.send_message(call.from_user.id, 'Приходите за новым котиком завтра)', reply_markup=main_menu_buttons)
        return

    bot.send_message(call.from_user.id, 'Вжжжж загружаю Какой котик ты сегодня....')
    bot.send_message(call.from_user.id, 'И сегодня ты...')
    bot.send_photo(call.from_user.id, photo)
    bot.send_message(call.from_user.id, 'Приходи завтра и узнай какой ты новый котик :з',
                     reply_markup=return_to_assistant_button)
    return


def funny_from_fluffy(call):
    random_number = random.randint(1, 11)
    link = f'../additional_files/mems/{random_number}.jpg'
    photo = open(link, "rb")
    bot.send_message(call.from_user.id, 'Вжжжж загружаю мемчик....')
    bot.send_photo(call.from_user.id, photo, reply_markup=after_meme_button)
    return


def film_from_fluffy(call):
    random_number = random.randint(0, 9)
    # random_number = 7
    films_matrix = get_range(FILMS_SPREADSHEET_ID, FILMS_RANGE_NAME)
    if not films_matrix[random_number]:
        bot.send_message(call.from_user.id, "there is no list of films, write @Zahar_i4",
                         reply_markup=return_to_assistant_button)
        return
    if not len(films_matrix[random_number]) == 4:
        bot.send_message(call.from_user.id,
                         f"The table is not correct, the line is {random_number + 2}, write @Zahar_i4",
                         reply_markup=return_to_assistant_button)
        return
    link = f'../additional_files/films/{films_matrix[random_number][0]}'
    film = films_matrix[random_number][1]
    genre = films_matrix[random_number][2]
    description = films_matrix[random_number][3]
    photo = open(link, "rb")
    message = 'Пушистик посмотрел свой списочек и специально для тебя рекомендует: ' \
              + '\n' \
              + '\n' \
              + f'🎞️ Фильм: <b>{film}</b>' \
              + '\n' \
              + f'📺 Жанр: {genre}' \
              + '\n' \
              + '\n' \
              + f'Описание: \n <i>{description}</i>' \
              + '\n' \
              + '\n' \
              + 'Как тебе рекомендация пушистика? :з'
    # print(len(message))
    bot.send_photo(call.from_user.id, photo, caption=message, parse_mode='html', reply_markup=film_review_button)
    return


def knowledge_base(call):
    message = '⚙️ Данный раздел ещё на стадии разработки...' \
              + '\n' \
              + '\n' \
              + 'Пушистик собирает все статьи из GO EHU, ' \
                'чтобы представить вам самую актуальную и большую базу знаний, ' \
                'которая включает важные темы и статьи от учёбы в университете, ' \
                'до повседневной жизни в Литве.' \
              + '\n' \
              + '\n' \
              + 'В данном разделе вы сможете получить всю необходимую точечную информацию, ' \
                'которая понадобится вам при учебе в Европе.'
    bot.send_message(call.from_user.id, message, reply_markup=return_to_assistant_button)


def come_back_home(call):
    message = '🏠 Вы на главной странице бота' \
              + '\n' \
              + 'Выберите раздел:' \
              + '\n' \
              + '\n' \
              + '\n' \
              + '📒 Расписание – раздел, где ты можешь выбрать расписание своей группы ' \
                'и быть в курсе об всех изменениях и парах (для отображения расписания, ' \
                'вам нужно будет подтвердить свой статус студента ЕГУ через авторизацию через Moodle);' \
              + '\n' \
              + '\n' \
              + '🐈 Ассистент Пушистик – принесёт вам неповторимый опыт, ' \
                'поможет поднять настроение и отвлечься от учебы :З' \
              + '\n' \
              + '\n' \
              + '⚙️ Настройки Уведомлений – гибко адаптируйте уведомления расписания под себя. ' \
                'Так вы не упустите ни перестановки, ни изменений в расписании, ни неожиданных ранних пар;' \
              + '\n' \
              + '\n' \
              + '⚙️ Настройки Ассистента – персонализируй Пушистика под себя и свои интересы. ' \
                'Просмотреть все возможности и функционал бота твы можете введя команду /help'
    bot.send_message(call.from_user.id, message, reply_markup=main_menu_buttons)
