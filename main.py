from fastapi import FastAPI
from uvicorn import run as uvicorn_run
from pydantic import BaseModel
import json
from subprocess import Popen
from time import sleep


class Interfaces(BaseModel):
    screen: dict
    payments: dict
    account_linking: dict


class User(BaseModel):
    user_id: str


class Application(BaseModel):
    application_id: str


class Nlu(BaseModel):
    tokens: list
    entities: list
    intents: dict


class Markup(BaseModel):
    dangerous_context: bool


class Meta(BaseModel):
    locale: str
    timezone: str
    client_id: str
    interfaces: Interfaces


class Session(BaseModel):
    message_id: int
    session_id: str
    skill_id: str
    user: User
    application: Application
    user_id: str
    new: bool


class Request(BaseModel):
    command: str
    original_utterance: str
    nlu: Nlu
    markup: Markup
    type: str


class Data(BaseModel):
    meta: Meta
    session: Session
    request: Request
    # state: State
    version: str


app = FastAPI()


MENU = 'Привет, я ваш помощник по расписанию.\n' \
    'Здесь вы можете узнать расписание интересующей вас группы.\n\n' \
    'Список команд:\n' \
    '🔵 "Запомнить меня" - команда позволит сохранить вашу группу для ' \
    'быстрого доступа к расписанию.\n' \
    '🔵 "Мое расписание" - команда для открытия своего расписания.\n' \
    '🔵 "Расписание" - команда для открытия расписания.\n' \
    '🔵 "Стоп" - команда закрывает навык.\n' \
    '🔵 "Вернуться" - команда позволяет вернуться к меню.'
MENU_TTS = 'Привет, я ваш помощник по расписанию. ' \
    'Список команд: "Запомнить меня", "Мое расписание", "Расписание", ' \
    '"Стоп", "Вернуться".'

COMMANDS = 'Список команд:\n' \
    '🔵 "Запомнить меня" - команда позволит сохранить вашу группу для ' \
    'быстрого доступа к расписанию.\n' \
    '🔵 "Мое расписание" - команда для открытия своего расписания.\n' \
    '🔵 "Расписание" - команда для открытия расписания.\n' \
    '🔵 "Стоп" - команда закрывает навык.\n' \
    '🔵 "Вернуться" - команда позволяет вернуться к меню.'
COMMANDS_TTS = 'Список команд: "Запомнить меня", "Мое расписание", ' \
    '"Расписание", "Стоп", "Вернуться".'

REQUEST_GROUP_ID = 'Введите номер группы.'

GROUP_SAVED = 'Сохранено ✔️\n\n' \
    'Список команд:\n' \
    '🔵 "Запомнить меня" - команда позволит сохранить вашу группу для ' \
    'быстрого доступа к расписанию.\n' \
    '🔵 "Мое расписание" - команда для открытия своего расписания.\n' \
    '🔵 "Расписание" - команда для открытия расписания.\n' \
    '🔵 "Стоп" - команда закрывает навык.'
GROUP_SAVED_TTS = 'Сохранено. ' \
    'Список команд: "Запомнить меня", "Мое расписание", "Расписание", ' \
    '"Стоп", "Вернуться".'

WHICH_SPECIFIC_GROUP = 'Расписание какой группы вас интересует?'

NOT_REGISTRED = 'Вы не зарегестрированы в нашей базе данных, пройдите ' \
    'регистрацию, чтобы воспользоваться этой функцией.\n\n' \
    'Список команд:\n' \
    '🔵 "Запомнить меня" - команда позволит сохранить вашу' \
    ' группу для быстрого доступа к расписанию.\n' \
    '🔵 "Меню" - команда возвращает в меню.'
NOT_REGISTRED_TTS = 'Вы не зарегестрированы в нашей базе данных, пройдите ' \
    'регистрацию, чтобы воспользоваться этой функцией.' \
    'Список команд: "Запомнить меня", "Меню".'

CHOOSE_DAY = 'Выберите день:\n' \
    '🔵 "Понедельник"\n' \
    '🔵 "Вторник"\n' \
    '🔵 "Среда"\n' \
    '🔵 "Четверг"\n' \
    '🔵 "Пятница"\n' \
    '🔵 "Суббота"'
CHOOSE_DAY_TTS = 'Выберите день.'

NOT_IN_TIME = 'Сервер не успел обновить информацию вовермя.\n\n' \
    'Выберите день:\n' \
    '🔵 "Понедельник"\n' \
    '🔵 "Вторник"\n' \
    '🔵 "Среда"\n' \
    '🔵 "Четверг"\n' \
    '🔵 "Пятница"\n' \
    '🔵 "Суббота"'
NOT_IN_TIME_TTS = 'Сервер не успел обновить информацию вовермя. Выберите день.'

WRONG_GROUP = 'Такой группы не было найдено.\n' \
    'Используйте команду "Вернуться" или повторите запрос.'
WRONG_GROUP_TTS = 'Такой группы не было найдено. ' \
    'Используйте команду "Вернуться" или повторите запрос.'

WRONG_COMMAND = 'Команда не распознана.\n\n'
WRONG_COMMAND_TTS = 'Команда не распознана. '

DAYS = ['1', '2', '3', '4', '5', '6']


def response_by_str(request: Data, text: str, tts: str):
    return {
        'version': request.version,
        'session': request.session,
        'response': {
            'tts': tts,
            'text': text,
            'end_session': 'false'
        },
    }


def end_session_response(request: Data):
    return {
        'version': request.version,
        'session': request.session,
        'response': {
            'tts': 'Выход',
            'text': 'Выход...',
            'end_session': 'true'
        },
    }


def search_obj(obj_list: list, id_name: str, id: str) -> int:
    for i in range(len(obj_list)):
        if obj_list[i][id_name] == id:
            return i
    return -1


def return_user_obj() -> dict:
    return {
        'user_id': '',
        'group_id': '',
        'session_state': ['', '']
    }


def open_file() -> object:
    with open('data/users.json', 'r') as file:
        users: object = json.loads(file.read())
    return users


def update_users(users: object):
    with open('data/users.json', 'w') as file:
        file.write(json.dumps(users))


def update_group(group_id: str):
    Popen(['python', 'schedule.py', group_id])


def change_session_state(users: object, user_index: int, new: list[str]):
    users['users'][user_index]['session_state'] = new


def day_number(day_str: str) -> int:
    days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']
    number = 1
    for day in days:
        if day == day_str:
            return number
        number += 1
    return -1


def get_group_day_schedule(group_id: str, day: int) -> str:
    with open('data/groups.json', 'r') as file:
        groups: object = json.loads(file.read())

    group_index: int = -1
    for i in range(len(groups['groups'])):
        if groups['groups'][i]['group_id'] == group_id:
            group_index = i

    group = groups['groups'][group_index][str(day)]
    text: str = ''

    orders = ['🌒 1 пара (8:50-10:25):\n', '🌓 2 пара (10:40-12:15):\n', '🌔 3 пара (13:15-14:50):\n',
              '🌕 4 пара (15:00-16:35):\n', '🌖 5 пара (16:45-18:20):\n', '🌗 6 пара (18:30-20:05):\n', '🌘 7 пара (20:15-21:50):\n']

    order = 1
    while order <= 7:
        order_str = str(order)
        if group[order_str] is None:
            order += 1
            continue
        text += orders[order - 1]

        auditoriums = group[order_str]["auditoriums"]
        if len(auditoriums) > 47:
            auditoriums = auditoriums[:44] + '...'

        teachers = group[order_str]["teacher"]
        if len(teachers) > 47:
            teachers = teachers[:44] + '...'

        text += f'Предмет: {group[order_str]["discipline"]}\n' \
            f'Тип: {group[order_str]["kind"]}\n' \
            f'Аудитория: {auditoriums}\n' \
            f'Преподаватели: {teachers}\n'
        order += 1

    if text == '':
        text = 'Выходные!\n'

    text += '\n' \
        'Список команд:\n' \
        '🔵 "Другой день" - команда вернёт вас к выбору дня.\n' \
        '🔵 "Меню" - команда возвращает в меню.'
    return text


@app.post('/')
def get_request(request: Data):
    users: object = open_file()
    # with open('data.txt', 'a') as file:
    #     file.write('{}\n'.format(json.dumps(users)))

    user: dict = {
        'id': request.session.user_id,
        'index': -1,
        'text': request.request.original_utterance,
        'command': request.request.command
    }
    user['index'] = search_obj(users['users'], 'user_id', user['id'])
    text: str = ''
    tts: str = ''

    # Опредеяем session_state. Если пользоватеваля не существует - создать
    if user['index'] == -1:
        users['users'].append(return_user_obj())
        user['index'] = len(users['users']) - 1
        users['users'][user['index']]['user_id'] = user['id']
        session_state = ['menu', '']
        change_session_state(users, user['index'],
                             session_state)
    else:
        session_state = users['users'][user['index']]['session_state']

    if user['command'] == 'вернуться':
        text = MENU
        tts = MENU_TTS
        change_session_state(users, user['index'],
                             ['menu_option', ''])
        update_users(users)
        return response_by_str(request, text, tts)

    if request.session.new or session_state[0] == 'menu':
        text = MENU
        tts = MENU_TTS
        change_session_state(users, user['index'],
                             ['menu_option', ''])
        if users['users'][user['index']]['group_id'] != '':
            update_group(users['users'][user['index']]['group_id'])
        update_users(users)
        return response_by_str(request, text, tts)

    if session_state[0] == 'menu_option':
        if user['command'] == 'запомнить меня':
            text = REQUEST_GROUP_ID
            change_session_state(users, user['index'],
                                 ['change_own_group', ''])
        elif user['command'] == 'мое расписание':
            if (users['users'][user['index']]['group_id'] == ''):
                text = NOT_REGISTRED
                tts = NOT_REGISTRED_TTS
                change_session_state(users, user['index'],
                                     ['not_registred', ''])
            else:
                text = CHOOSE_DAY
                tts = CHOOSE_DAY_TTS
                change_session_state(users, user['index'],
                                     ['choose_day', users['users']
                                      [user['index']]['group_id']])
                update_group(users['users'][user['index']]['group_id'])
                sleep(0.75)
                with open('data/update_state', 'r') as state:
                    if state.read() == '-1':
                        text = WRONG_COMMAND + CHOOSE_DAY
                        tts = WRONG_COMMAND_TTS + CHOOSE_DAY_TTS
                        with open('data/update_state', 'w') as state:
                            state.write('0')
                sleep(2.25)
        elif user['command'] == 'расписание':
            text = WHICH_SPECIFIC_GROUP
            change_session_state(users, user['index'],
                                 ['choose_group', ''])
        elif user['command'] == 'стоп':
            return end_session_response(request)
        else:
            text = WRONG_COMMAND + COMMANDS
            tts = WRONG_COMMAND_TTS + COMMANDS_TTS

    if session_state[0] == 'change_own_group':
        users['users'][user['index']]['group_id'] = user['text']
        update_group(user['text'])
        sleep(0.75)
        with open('data/update_state', 'r') as state:
            if state.read() == '-1':
                text = WRONG_GROUP
                tts = WRONG_GROUP_TTS
                with open('data/update_state', 'w') as state:
                    state.write('0')
            else:
                text = GROUP_SAVED
                tts = GROUP_SAVED_TTS
                change_session_state(users, user['index'],
                                     ['menu_option', ''])

    if session_state[0] == 'not_registred':
        if user['command'] == 'запомнить меня':
            text = REQUEST_GROUP_ID
            change_session_state(users, user['index'],
                                 ['change_own_group', ''])
        elif user['command'] == 'меню':
            text = COMMANDS
            tts = COMMANDS_TTS
            change_session_state(users, user['index'],
                                 ['menu_option', ''])
        else:
            text = WRONG_COMMAND + COMMANDS
            tts = WRONG_COMMAND_TTS + COMMANDS_TTS

    if session_state[0] == 'choose_day':
        is_updating = '1'
        time_elapsed = 0
        while is_updating == '1' and time_elapsed < 3:
            with open('data/update_state', 'r') as state:
                is_updating = state.read()
            sleep(1)
            time_elapsed += 1

        if time_elapsed == 3 and is_updating == '1':
            text = NOT_IN_TIME
            tts = NOT_IN_TIME_TTS
        else:
            day = day_number(user['command'])
            if day == -1:
                text = WRONG_COMMAND + CHOOSE_DAY
                tts = WRONG_COMMAND_TTS + CHOOSE_DAY_TTS
            else:
                text = get_group_day_schedule(
                    session_state[1], day)
                change_session_state(users, user['index'],
                                     ['day_shown', ''])

    if session_state[0] == 'day_shown':
        if user['command'] == 'другой день':
            text = CHOOSE_DAY
            tts = CHOOSE_DAY_TTS
            change_session_state(users, user['index'],
                                 ['choose_day', users['users']
                                  [user['index']]['group_id']])
        elif user['command'] == 'меню':
            text = COMMANDS
            tts = COMMANDS_TTS
            change_session_state(users, user['index'],
                                 ['menu_option', ''])
        else:
            text = WRONG_COMMAND + 'Список команд:\n' \
                '🔵 "Другой день" - команда вернёт вас к выбору дня.\n' \
                '🔵 "Меню" - команда возвращает в меню.'
            tts = WRONG_COMMAND_TTS + 'Список команд: "Другой день", "Меню"'

    if session_state[0] == 'choose_group':
        text = CHOOSE_DAY
        tts = CHOOSE_DAY_TTS
        group_id = user['text']

        update_group(group_id)
        sleep(0.75)
        with open('data/update_state', 'r') as state:
            if state.read() == '-1':
                text = WRONG_GROUP
                tts = WRONG_GROUP_TTS
                with open('data/update_state', 'w') as state:
                    state.write('0')
            else:
                sleep(2.25)
                change_session_state(users, user['index'],
                                     ['choose_day', group_id])

    if tts == '':
        tts = text

    update_users(users)
    return response_by_str(request, text, tts)


if __name__ == '__main__':
    uvicorn_run('main:app', reload=True)
