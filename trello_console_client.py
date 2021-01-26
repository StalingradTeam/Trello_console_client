"""trello.com api manage client"""

import sys
import requests

token_key = str(input("token_key:"))
api_key = str(input("api_key:"))
board_id = str(input("board_id:"))

auth_params = {
    'key': str(api_key),
    'token': str(token_key),
}

base_url = "https://api.trello.com/1/{}"


#Добавляем рядом с названием колонки цифру - количество задач в ней
def read():
    #Парсим данные колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    #Выведем название колонок и заданий
    for column in column_data:
        #Получаем данные задач в колонке
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(column['name'] + " - " + str((len(task_data))))
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'] + ":     " + task['id'])


def get_task_duplicates(task_name):
    #Получаем данные колонок
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    #Создаем список колонок с дублями
    duplicate_tasks = []
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == task_name:
                duplicate_tasks.append(task)
    return duplicate_tasks


def move(name, column_name):
    duplicate_tasks = get_task_duplicates(name)
    if len(duplicate_tasks) > 1:
        print("Задач с этим названием несколько:")
        for index, task in enumerate(duplicate_tasks):
            task_column_name = requests.get(base_url.format('lists') + '/' + task['idList'], params=auth_params).json()['name']
            print("Задача номер{}\tid: {}\tРасположена в колонке: {}\t ".format(index, task['id'], task_column_name))
        task_id = input("Введите ID задачи, которую необходимо переместить: ")
    else:
        task_id = duplicate_tasks[0]['id']

    #Получаем ID колонки для перемещаемой задачи
    column_id = column_check(column_name)
    if column_id is None:
        column_id = add(column_name)['id']
    #Перемещаем:
    requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column_id, **auth_params})

#Создаем колонки
def add(column_name):
    return requests.post(base_url.format('boards') + '/' + board_id + '/lists',
                         data={'name': column_name, 'idBoard': board_id, **auth_params}).json()


def column_check(column_name):
    column_id = None
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    for column in column_data:
        if column['name'] == column_name:
            column_id = column['id']
            return column_id
    return column_id


def create(name, column_name):
    column_id = column_check(column_name)
    if column_id is None:
        column_id = add(column_name)['id']

    requests.post(base_url.format('cards'), data={'name': name, 'idList': column_id, **auth_params})


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'add':
        add(sys.argv[2])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])