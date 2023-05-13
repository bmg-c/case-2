from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import json
import subprocess
import time


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


# class State(BaseModel):
#     session: str


class Data(BaseModel):
    meta: Meta
    session: Session
    request: Request
    # state: State
    version: str


app = FastAPI()


START = 'Привет, я ваш помощник по расписанию.\n' \
    'Здесь вы можете узнать расписание интересующей вас группы.\n' \
    'Список команд:\n' \
    '🔵 "Запомнить меня" - команда позволит сохранить вашу группу для ' \
    'быстрого доступа к расписанию.\n' \
    '🔵 "Мое расписание" - команда для открытия своего расписания.\n' \
    '🔵 "Расписание" - команда для открытия расписания.\n' \
    '🔵 "Стоп" - команда закрывает навык.'

COMMANDS = 'Список команд:\n' \
    '🔵 "Запомнить меня" - команда позволит сохранить вашу группу для ' \
    'быстрого доступа к расписанию.\n' \
    '🔵 "Расписание" - команда для открытия расписания.\n' \
    '🔵 "Стоп" - команда закрывает навык.'

REQUEST_GROUP_ID = 'Введите номер группы.'

GROUP_SAVED = 'Сохранено ✔️\n' \
    'Список команд:\n' \
    '🔵 "Запомнить меня" - команда позволит сохранить вашу группу для ' \
    'быстрого доступа к расписанию.\n' \
    '🔵 "Расписание" - команда для открытия расписания.\n' \
    '🔵 "Стоп" - команда закрывает навык.'

WHICH_SPECIFIC_GROUP = 'Расписание какой группы вас интересует?' \

NOT_REGISTRED = 'Вы не зарегестрированы в нашей базе данных, пройдите ' \
    'регистрацию, чтобы воспользоваться этой функцией.\n' \
    '🔵 "Запомнить меня" - команда позволит сохранить вашу' \
    ' группу для быстрого доступа к расписанию.\n' \
    '🔵 "Меню" - команда возвращает в меню.'

CHOOSE_DAY = 'Выберите день:\n' \
    '🔵 "Понедельник"\n' \
    '🔵 "Вторник"\n' \
    '🔵 "Среда"\n' \
    '🔵 "Четверг"\n' \
    '🔵 "Пятница"\n' \
    '🔵 "Суббота"'

f = '🌒 1 пара (8:50-10:25):\n' \
    'Предмет: (данные)\n' \
    'Тип: (данные)\n' \
    'Аудитория: (данные)\n' \
    'Преподаватель: (данные)\n' \
    '🌓 2 пара (10:40-12:15):\n' \
    'Предмет: (данные)\n' \
    'Тип: (данные)\n' \
    'Аудитория: (данные)\n' \
    'Преподаватель: (данные)\n' \
    '🌔 3 пара (13:15-14:50):\n' \
    'Предмет: (данные)\n' \
    'Тип: (данные)\n' \
    'Аудитория: (данные)\n' \
    'Преподаватель: (данные)\n' \
    '🌕 4 пара (15:00-16:35):\n' \
    'Предмет: (данные)\n' \
    'Тип: (данные)\n' \
    'Аудитория: (данные)\n' \
    'Преподаватель: (данные)\n' \
    '🌖 5 пара (16:45-18:20):\n' \
    'Предмет: (данные)\n' \
    'Тип: (данные)\n' \
    'Аудитория: (данные)\n' \
    'Преподаватель: (данные)\n' \
    '🌗 6 пара (18:30-20:05):\n' \
    'Предмет: (данные)\n' \
    'Тип: (данные)\n' \
    'Аудитория: (данные)\n' \
    'Преподаватель: (данные)\n' \
    '🌘 7 пара (20:15-21:50):\n' \
    'Предмет: (данные)\n' \
    'Тип: (данные)\n' \
    'Аудитория: (данные)\n' \
    'Преподаватель: (данные)\n' \
    '\n' \
    'Список команд:\n' \
    '🔵 "Расписание другого дня" - команда вернёт вас к выбору дня.\n' \
    '🔵 "Меню" - команда возвращает в меню.'


def response_by_str(request, text: str):
    return {
        'version': request.version,
        'session': request.session,
        'response': {
            'text': text,
            'end_session': 'false'
        },
    }


def search_obj(obj_list: list, id_name: str, id: str) -> int:
    for i in range(len(obj_list)):
        if obj_list[i][id_name] == id:
            return i
    return -1


def return_user_obj():
    return {
        'user_id': '',
        'group_id': '',
        'session_state': ['', '']
    }


def update_users(users):
    with open('data/users.json', 'w') as file:
        file.write(json.dumps(users))


def update_group(group_id: str):
    subprocess.Popen(['python', 'schedule.py', group_id])


def change_session_state(users, user_index: int, new: list[str]):
    users['users'][user_index]['session_state'] = new
    update_users(users)


@app.post('/')
def get_request(request: Data):
    print("saka")
    with open('data/users.json', 'r') as file:
        users: object = json.loads(file.read())
    with open('data.txt', 'a') as file:
        file.write('{}\n'.format(json.dumps(users)))

    user = {
        'id': request.session.user_id,
        'index': -1,
        'text': request.request.original_utterance,
        'command': request.request.command
    }
    user['index'] = search_obj(users['users'], 'user_id', user['id'])
    text: str = ''

    # Опредеяем session_state. Если юзера не существует - создать
    if user['index'] == -1:
        users['users'].append(return_user_obj())
        user['index'] = len(users['users']) - 1
        users['users'][user['index']]['user_id'] = user['id']
        session_state = ['menu', '']
        change_session_state(users, user['index'],
                             session_state)
    else:
        session_state = users['users'][user['index']]['session_state']

    if request.session.new or session_state[0] == 'menu':
        text = START
        change_session_state(users, user['index'],
                             ['menu_option', ''])
        if users['users'][user['index']]['group_id'] != '':
            update_group(users['users'][user['index']]['group_id'])
        return response_by_str(request, text)

    if session_state[0] == 'menu_option':
        if user['command'] == 'запомнить меня':
            text = REQUEST_GROUP_ID
            change_session_state(users, user['index'],
                                 ['change_own_group', ''])
            return response_by_str(request, text)
        if user['command'] == 'моя группа':
            if (users['users'][user['index']]['group_id'] == ''):
                text = NOT_REGISTRED
                change_session_state(users, user['index'],
                                     ['not_registred', ''])
                return response_by_str(request, text)
            else:
                text = CHOOSE_DAY
                change_session_state(users, user['index'],
                                     ['choose_day', ''])
                return response_by_str(request, text)

    if session_state[0] == 'change_own_group':
        text = GROUP_SAVED
        users['users'][user['index']]['group_id'] = user['text']
        change_session_state(users, user['index'],
                             ['menu_option', ''])
        return response_by_str(request, text)

    if session_state[0] == 'not_registred':
        if user['command'] == 'запомнить меня':
            text = REQUEST_GROUP_ID
            change_session_state(users, user['index'],
                                 ['change_own_group', ''])
            return response_by_str(request, text)
        if user['command'] == 'меню':
            text = START
            change_session_state(users, user['index'],
                                 ['menu_option'])
            return response_by_str(request, text)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
