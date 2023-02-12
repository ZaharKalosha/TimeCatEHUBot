import telebot
from telebot.types import InlineKeyboardButton

from code_files.functions import get_number_of_week

# ReplyKeyboardMarkups

main_menu_reply_buttons = telebot.types.ReplyKeyboardMarkup(True, False)
main_menu_reply_buttons.row('📒 Расписание', '🐈 Ассистент Пушистик')
main_menu_reply_buttons.row('⚙️ Настр. увед.', '⚙️ Настр. ассистента')

# InlineKeyboardMarkups

# MainMarkups
main_menu_buttons = telebot.types.InlineKeyboardMarkup(row_width=2)
main_menu_buttons.add(InlineKeyboardButton('📒 Расписание', callback_data="get_schedule"),
                      InlineKeyboardButton('🐈 Ассистент Пушистик', callback_data="assistant_fluffy"))
main_menu_buttons.add(InlineKeyboardButton('⚙️ Настр. увед.', callback_data="notification_settings"),
                      InlineKeyboardButton('⚙️ Настр. ассистента', callback_data="assistant_settings"))

notification_settings_buttons = telebot.types.InlineKeyboardMarkup(row_width=2)
notification_settings_buttons.row(InlineKeyboardButton('Правки в расписании', callback_data="schedule_presets"), )
notification_settings_buttons.row(InlineKeyboardButton('О парах на завтра', callback_data="tomorrow's_classes"),
                                  InlineKeyboardButton('Начало пар в 8:30', callback_data="start_of_classes"))
notification_settings_buttons.row(InlineKeyboardButton('Новые недели', callback_data="new_weeks"),
                                  InlineKeyboardButton('Отменённые пары', callback_data="canceled_classes"))

on_off_buttons = telebot.types.InlineKeyboardMarkup(row_width=2)
on_off_buttons.row(InlineKeyboardButton('🟢 Включить', callback_data="on"),
                   InlineKeyboardButton('🔴 Выключить', callback_data="off"))

course_selection_buttons = telebot.types.InlineKeyboardMarkup(row_width=5)
course_selection_buttons.row(InlineKeyboardButton('1', callback_data="first_year"),
                             InlineKeyboardButton('2', callback_data="second_year"),
                             InlineKeyboardButton('3', callback_data="third_year"),
                             InlineKeyboardButton('4', callback_data="fourth_year"),
                             InlineKeyboardButton('5', callback_data="fifth_year"))

specialty_selection_buttons = telebot.types.InlineKeyboardMarkup(row_width=3)
specialty_selection_buttons.row(InlineKeyboardButton('Медиа', callback_data="media"),
                                InlineKeyboardButton('Дизайн', callback_data="design"),
                                InlineKeyboardButton('Театр', callback_data="theater"))
specialty_selection_buttons.row(InlineKeyboardButton('Политика', callback_data="policy"),
                                InlineKeyboardButton('Наследие', callback_data="heritage"),
                                InlineKeyboardButton('Право', callback_data="law"))

schedule_output_setting_buttons = telebot.types.InlineKeyboardMarkup(row_width=3)
schedule_output_setting_buttons.row(InlineKeyboardButton('⬅️', callback_data="back"),
                                    InlineKeyboardButton(f'Неделя {get_number_of_week()}', callback_data="nothing"),
                                    InlineKeyboardButton('➡️', callback_data="forward"))
schedule_output_setting_buttons.row(InlineKeyboardButton('🔁 Иной формат', callback_data="other_format"))

schedule_output_period_setting_buttons = telebot.types.InlineKeyboardMarkup(row_width=3)
schedule_output_period_setting_buttons.row(InlineKeyboardButton('На сегодня', callback_data="today"),
                                           InlineKeyboardButton('На завтра', callback_data="tomorrow"),
                                           InlineKeyboardButton('На неделю', callback_data="week"))

relogining = telebot.types.InlineKeyboardMarkup(row_width=1)
relogining.row(InlineKeyboardButton('🔃 Попробовать ещё раз', callback_data="relogining"))

vacancy_link_button = telebot.types.InlineKeyboardMarkup(row_width=1)
vacancy_link_button.row(InlineKeyboardButton('📨 Откликнуться', url="https://t.me/daniel_warsz"))

# AssistantMarkups

assistant_menu_buttons = telebot.types.InlineKeyboardMarkup(row_width=5)
assistant_menu_buttons.add(InlineKeyboardButton('😼 Какой ты котик сегодня', callback_data="what_cat_are_you_today"))
assistant_menu_buttons.add(InlineKeyboardButton('😹 Приколюшка от Пушистика', callback_data="funny_from_fluffy"))
assistant_menu_buttons.add(InlineKeyboardButton('🍿 Фильм от Пушистика', callback_data="film_from_fluffy"))
assistant_menu_buttons.add(InlineKeyboardButton('🗄 База знаний', callback_data="knowledge_base"))
assistant_menu_buttons.add(InlineKeyboardButton('⬅️ Вернуться домой', callback_data="come_back_home"))

after_meme_button = telebot.types.InlineKeyboardMarkup(row_width=2)
after_meme_button.add(InlineKeyboardButton('😹 Ещё один мемчик', callback_data="funny_from_fluffy"))
after_meme_button.add(InlineKeyboardButton('🏠 Вернуться к Ассистенту', callback_data="return_to_assistant"))

another_film_button = telebot.types.InlineKeyboardMarkup(row_width=2)
another_film_button.add(InlineKeyboardButton('👀 Хочу ещё один фильм', callback_data="next_film"))
another_film_button.add(InlineKeyboardButton('🏠 Вернуться к Ассистенту', callback_data="return_to_assistant"))

film_review_button = telebot.types.InlineKeyboardMarkup(row_width=3)
film_review_button.add(InlineKeyboardButton('😊 Очень понравилась!', callback_data="good"))
film_review_button.add(InlineKeyboardButton('😞 Не в моем вкусе...', callback_data="bead"))
film_review_button.add(InlineKeyboardButton('😡 Уже был', callback_data="bead"))

assistant_settings_buttons = telebot.types.InlineKeyboardMarkup(row_width=1)
assistant_settings_buttons.add(InlineKeyboardButton('⚙️ Уведомления пока в разработке. Вы можете предложить свои идеи!',
                                                    callback_data="what_cat_are_you_today"))

return_to_assistant_button = telebot.types.InlineKeyboardMarkup(row_width=1)
return_to_assistant_button.add(InlineKeyboardButton('🏠 Вернуться к Ассистенту', callback_data="return_to_assistant"))
