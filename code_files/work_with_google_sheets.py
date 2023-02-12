from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet. TODO: Надо чтоюы авторизацию подтвердил пользователь с таблицей вроде
# https://drive.google.com/drive/u/0/folders/1CCOp5p4X8fVTfSNOtNYAGg_IzUdPfiN9 диск с таблицами

SAMPLE_SPREADSHEET_ID = '1j9hV5vzwCLIWk3JpluVjrM4BSuxRjlKMgNkHoyHOL7o'  # 1 дизайн1
# SAMPLE_SPREADSHEET_ID = '1U2We5j2FNZdfD4QUtamZUJ1WhKW_sLVWp8DSjCh-pUE'  #2 дизайн2 -
# SAMPLE_SPREADSHEET_ID = '1EYM1nQiyZHrziGVyJoZGxpmVwEB-gYqqm0Ytc-JXBDY'  #3 дизайн3
# SAMPLE_SPREADSHEET_ID = '1BdQ5LITcRdrPcKlzrT87OFH8fMZHTvIHSq7x0GNbm7U'  #4 дизайн4
SAMPLE_RANGE_NAME = "Sheet1!A1:M140"

values_range = [[]]


def get_range(sample_spreadsheet_id, sample_range_name):
    global values_range
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../data_files/token.json'):
        creds = Credentials.from_authorized_user_file('../data_files/token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in to an account with rights to read sheets.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file('../data_files/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('../data_files/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().batchGet(spreadsheetId=sample_spreadsheet_id,
                                         ranges=sample_range_name,
                                         valueRenderOption='FORMATTED_VALUE',
                                         dateTimeRenderOption='FORMATTED_STRING').execute()

        values_range = result['valueRanges'][0]['values']

        if not values_range:
            print('No data found.')
            return

    except HttpError as err:
        print(err)

    return values_range


def set_shifts(values, number_of_day, number_of_weak):
    # if number_of_day < 1 or number_of_day > 6:
    #     return 'ERROR! incorrect parameter in range_to_day_massage, write to @Zahar_i4'
    shift_left = 0
    if int(number_of_weak) % 2 == 0:
        shift_left = 7
    shift_down = 0
    if int(number_of_weak) > 2:
        third_or_fourth_week = 1
        i = 0
        while i < 140:
            if values[i]:
                if values[i][0 + shift_left]:
                    if values[i][0 + shift_left] == 'Date' and third_or_fourth_week == 0:
                        break
                if values[i][0 + shift_left] == 'Date':
                    third_or_fourth_week -= 1
            i += 1
        if i == 140:
            return 'ERROR! Something is wrong with the schedule, write to @Zahar_i4'
        shift_down = i - 4
    return [shift_down, shift_left]


# number_of_day = 0 - week, 1 - mon, 2 - tue, ..., 6 - sat.  number_of_weak = 1-4
def range_to_day_massage(values, number_of_day, number_of_weak):
    shifts = set_shifts(values, number_of_day, number_of_weak)
    shift_down = shifts[0]
    shift_left = shifts[1]

    body = ''
    flag = 1
    number_of_day -= 1
    for i in range(3, len(values)):
        if values[i + shift_down]:
            if len(values[i + shift_down]) - shift_left < 0:
                continue
            if number_of_day >= 0 and not values[i + shift_down][0 + shift_left]:
                continue

            if values[i + shift_down][0 + shift_left] == 'Date':
                continue

            if values[i + shift_down][0 + shift_left] and number_of_day > 0:
                number_of_day -= 1
                continue

            if flag != 2:
                body += '———————————————' + '\n' + \
                        f"🔸 {values[i + shift_down][0 + shift_left]}" + '\n' + \
                        '———————————————' + '\n'
                body += '\n'

                n = 8
                j = 0
                while j < n:
                    time = ''
                    room = ''
                    course = ''
                    teacher = ''
                    form = ''
                    if len(values[i + j]) - shift_left < 1:
                        n += 1
                    for k in range(1, min(6, len(values[i + j + shift_down]) - shift_left)):
                        if (len(values[i + j + shift_down]) < 7 or len(values[i + j + shift_down]) == 0) and k == 1:
                            n += 1
                        if not values[i + j + shift_down][1 + shift_left] and k == 1:
                            n += 1
                        if values[i + j + shift_down][k + shift_left]:
                            if k == 1:
                                time = values[i + j + shift_down][k + shift_left]
                            elif k == 2:
                                room = values[i + j + shift_down][k + shift_left]
                            elif k == 3:
                                course = f'<u>{values[i + j + shift_down][k + shift_left]}</u>'
                            elif k == 4:
                                teacher = values[i + j + shift_down][k + shift_left]
                            elif k == 5:
                                form = values[i + j + shift_down][k + shift_left]
                            else:
                                body += values[i + j + shift_down][k + shift_left] + '\n'
                    if room == '' and course == '':
                        j += 1
                        continue
                    if time == '':
                        time = '➕'
                    else:
                        time = '\n' + time
                    if room == '':
                        room = 'Не указано'
                    if course == '':
                        course = 'Не указано'
                    if teacher == '':
                        teacher = 'Не указано'
                    if form == '':
                        form = 'Не указано'
                    body += time + '\n' + course + '\n' + 'аудитория: ' + room + '\n' + 'формат: ' + form
                    j += 1
                    body += '\n'
                number_of_day -= 1
                break

            if number_of_day < 0 and values[i + shift_down][0 + shift_left]:
                break

            continue
    return body


def range_to_head_message(values, number_of_day, number_of_weak):
    shifts = set_shifts(values, number_of_day, number_of_weak)
    shift_down = shifts[0]
    shift_left = shifts[1]

    head = values[1 + shift_down][0 + shift_left] + '\n'
    head += values[2 + shift_down][0 + shift_left] + '\n\n'
    head += '📝Расписание' + '\n'
    return head


def getting_of_week(week):
    int_week = int(week) % 4
    if int_week == 0:
        int_week = 4
    return int_week

# if __name__ == '__main__':
#     print(range_to_head_message(get_range(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME),
#                                 get_number_of_day(),
#                                 getting_of_week(get_number_of_week())))
#     print(range_to_day_massage(get_range(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME),
#                                get_number_of_day(),
#                                getting_of_week(get_number_of_week())))
