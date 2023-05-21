import requests
import bs4
import re
import json
import sys
import time


def update_groups(data):
    with open('data/groups.json', 'w') as file:
        file.write(json.dumps(data))


def search_obj(obj_list: list, id: str) -> int:
    for i in range(len(obj_list)):
        if obj_list[i]['group_id'] == id:
            return i
    return -1


def get_schedule_by_group(group: str):
    facult = ['yuf', 'rtf', 'rkf', 'fet', 'fsu', 'fvs', 'gf', 'fb', 'ef']
    if type(group[0]) != int:
        return None
    response = requests.get(
        f'https://timetable.tusur.ru/faculties/{facult[int(group[0])]}/groups/{group}')
    lessons = bs4.BeautifulSoup(response.content, 'html.parser')
    lessons = lessons.find_all('tr', {'class': re.compile('lesson')})
    if lessons == []:
        return None
    for i in range(7):
        lessons[i] = lessons[i].find_all('td')
    mas = [{str(i): {'discipline': '',
                     'kind': '',
                     'auditoriums': '',
                     'teacher': ''
                     } for i in range(1, 8)} for j in range(6)]
    for i in range(7):
        for j in range(6):
            data = lessons[i][j].find('div', {'class': 'hidden for_print'})
            if data is None:
                mas[j][str(i+1)] = None
                continue
            data = data.find_all('span')
            mas[j][str(i+1)]['discipline'] = data[0].text
            mas[j][str(i+1)]['kind'] = data[1].text
            mas[j][str(i+1)]['auditoriums'] = data[2].text
            mas[j][str(i+1)]['teacher'] = data[3].text
    return {
        'group_id': group,
        'last_update': int(time.time() / 86400),
        '1': mas[0],
        '2': mas[1],
        '3': mas[2],
        '4': mas[3],
        '5': mas[4],
        '6': mas[5]
    }


with open('data/groups.json', 'r') as file:
    groups = json.loads(file.read())
group_id = sys.argv[1]
print("group_id: {}\n".format(group_id))
group_index = search_obj(groups['groups'], group_id)

if group_index != -1 and ((int(time.time() / 86400) - int(groups['groups'][group_index]["last_update"])) == 0):
    exit()

with open('data/update_state', 'w') as file:
    file.write('1')
schedule = get_schedule_by_group(group_id)
if schedule is None:
    with open('data/update_state', 'w') as file:
        file.write('-1')
    exit()
with open('data/update_state', 'w') as file:
    file.write('0')
if group_index == -1:
    groups['groups'].append(schedule)
else:
    groups['groups'][group_index] = schedule

update_groups(groups)
