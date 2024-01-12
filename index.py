import time
import requests
from bs4 import BeautifulSoup
import json
import os
from colorama import Fore, Back, Style, init

init(autoreset=True)  # Инициализация colorama

# Получаем путь к текущему скрипту
script_dir = os.path.dirname(os.path.abspath(__file__))

# Формируем путь к корневой директории Script
root_dir = os.path.abspath(os.path.join(script_dir))

# Устанавливаем текущую рабочую директорию
os.chdir(root_dir)

current_directory = os.getcwd()
formatted_line = f"{Fore.WHITE}{Back.GREEN}Текущая рабочая директория:{Style.RESET_ALL} {Fore.YELLOW}{current_directory}{Style.RESET_ALL}"

print(formatted_line)

def get_calendar_object(group_id, semester_id, week_number):
    URL = f'https://isu.uust.ru/api/new_schedule_api/?schedule_semestr_id={semester_id}&WhatShow=1&student_group_id={group_id}&weeks={week_number}'

    try:
        response = requests.get(URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Найдем таблицу
        table = soup.find('table')

        # Проверим, что таблица найдена
        if not table:
            raise ValueError("Таблица не найдена.")

        # Создадим пустой список для хранения данных
        schedule_data = []
        current_day = None  # Переменная для хранения текущего дня

        # Найдем все строки в теле таблицы
        rows = table.find_all('tr')

        # Проитерируемся по строкам и получим данные
        for row in rows:
            columns = row.find_all(['td', 'th'])
            row_data = [column.get_text(strip=True) for column in columns]

            # Если строка представляет собой заголовок дня, сохраняем текущий день
            if 'dayheader' in row.get('class', []):
                current_day = row_data[0]

            # Если дата и время указаны, добавим текущий день к строке
            elif row_data[0] and row_data[1]:
                row_data[0] = f"{current_day} {row_data[0]}"

            schedule_data.append(row_data)

        # Преобразуем в JSON
        json_data = json.dumps(schedule_data, ensure_ascii=False, indent=2)

        # Преобразование строки в объект
        json_data1 = json.loads(json_data)

        current_date = None

        # Проходим по всем элементам и заполняем даты
        for row in json_data1:
            if len(row) > 1 and row[0] != "":
                current_date = row[0]
            elif current_date:
                row.insert(0, current_date)

        # Преобразование объекта обратно в строку
        updated_json_data_str = json.dumps(json_data1, ensure_ascii=False, indent=2)

        # Функция для удаления элементов с "Нет информации"
        def filter_none_info(row):
            return "Нет информации" not in row

        # Фильтрация данных
        filtered_data = list(filter(filter_none_info, json_data1))

        # Преобразование объекта обратно в строку
        filtered_json_data_str = json.dumps(filtered_data, ensure_ascii=False, indent=2)

        # Функция для удаления пустого поля с индексом 1
        def remove_empty_second_field(row):
            if len(row) > 1 and row[1] == "":
                row.pop(1)
            return row

        # Преобразование каждой строки и удаление первого элемента
        filtered_data = [remove_empty_second_field(row) for row in filtered_data][1:]

        # Преобразование объекта обратно в строку
        filtered_json_data_str = json.dumps(filtered_data, ensure_ascii=False, indent=2)

        if filtered_json_data_str:
            return filtered_json_data_str
        else:
            raise ValueError("{Fore.RED}Ни одного занятия не найдено.")

    except requests.RequestException as e:
        print(f"{Fore.RED}Ошибка при выполнении запроса: {e}")
    except Exception as e:
        print(f"{Fore.RED}Произошла ошибка: {e}")

def get_group_id(input_group_name, semester_id):
    URL = f'https://isu.uust.ru/api/new_schedule_api/?schedule_semestr_id={semester_id}&WhatShow=1'

    try:
        response = requests.get(URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим нужный div по классу
        div_element = soup.find('div', class_='col-lg-3')

        # Получаем текст из найденного элемента
        text_content = div_element.get_text(strip=True)

        print(f'{Fore.BLUE}{Back.WHITE}{text_content}')

        groups_dict = {}
        select_tag = soup.find('select', {'name': 'student_group_id'})
        if select_tag:
            options = select_tag.find_all('option')
            for option in options:
                value = option['value']
                text = option.get_text(strip=True)
                groups_dict[value] = text

        matching_group_id = next((group_id for group_id, group_text in groups_dict.items() if input_group_name in group_text), None)

        if matching_group_id:
            return matching_group_id
        else:
            raise ValueError(f"{Fore.RED}Группа '{input_group_name}' не найдена в словаре.")
    except requests.RequestException as e:
        print(f"{Fore.RED}Ошибка при запросе к {URL}: {e}")
        return None
    except Exception as e:
        print(f"{Fore.RED}Произошла неизвестная ошибка: {e}")
        return None

def get_semester_id(input_semester):
    URL = f'https://isu.ugatu.su/api/new_schedule_api'

    try:
        response = requests.get(URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        semesters_dict = {}

        select_tag = soup.find('select', {'name': 'schedule_semestr_id'})
        if select_tag:
            options = select_tag.find_all('option')
            for option in options:
                value = option['value']
                text = option.get_text(strip=True)
                semesters_dict[value] = text

        matching_semester_id = next((semester_id for semester_id, semester_text in semesters_dict.items() if input_semester in semester_text), None)

        if matching_semester_id:
            return matching_semester_id
        else:
            raise ValueError(f"Семестр '{input_semester}' не найден в словаре.")
    except requests.RequestException as e:
        print(f"Ошибка при запросе к {URL}: {e}")
        return None
    except Exception as e:
        print(f"Произошла неизвестная ошибка: {e}")
        return None

def export_object_to_ical(input_group_name, week_number, calendar_object):
    open_file(input_group_name, week_number)

    # Преобразование строки в объект
    schedule_data = json.loads(calendar_object)

    for event in schedule_data:
        day, time_range, discipline, lecture_type, lecturer, room, _ = event

        # Форматируем переменные
        summary = f"SUMMARY:{room} {discipline} {lecture_type} {lecturer}"
        dt_start = f"DTSTART:{day.split()[1].split('.')[2]}{day.split()[1].split('.')[1]}{day.split()[1].split('.')[0]}T{time_range.split('-')[0].replace(':', '')}00"
        dt_end = f"DTEND:{day.split()[1].split('.')[2]}{day.split()[1].split('.')[1]}{day.split()[1].split('.')[0]}T{time_range.split('-')[1].replace(':', '')}00"

        # Выводим результат
        add_lesson(input_group_name, summary, dt_start, dt_end, week_number)
    close_file(input_group_name, week_number)


def open_file(group_name, week_number):
    header = 'BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n'
    with open(os.path.join(root_dir, f'Расписание_занятий_для_группы_{group_name}_на_{week_number}-ю_неделю.ics'), 'w') as file:
        file.write(header)


def close_file(group_name, week_number):
    footer = '\nEND:VCALENDAR\n'
    with open(os.path.join(root_dir, f'Расписание_занятий_для_группы_{group_name}_на_{week_number}-ю_неделю.ics'), 'a') as file:
        file.write(footer)
    print(f'{Fore.GREEN}Файл "Расписание_занятий_для_группы_{group_name}_на_{week_number}-ю_неделю.ics" сформирован')


def add_lesson(group_name, SUMMARY, DTSTART, DTEND, week_number):
    csv_line = f'\nBEGIN:VEVENT\n{SUMMARY}\n{DTSTART}\n{DTEND}\nEND:VEVENT\n'
    with open(os.path.join(root_dir, f'Расписание_занятий_для_группы_{group_name}_на_{week_number}-ю_неделю.ics'), 'a') as file:
        file.write(csv_line)


def main():
    try:
        start_time = time.time()
        print(f"{Fore.GREEN}Спасибо, что выбрали мой скрипт для создания файла-календаря с расписанием в УУНиТ.")
        print("Перед использованием скрипта убедитесь, что у Вас выключен VPN")

        input_semester = input(f"{Fore.YELLOW}Введите семестр в формате \"Осенний семестр 2023/2024\": ")
        semester_id = get_semester_id(input_semester)

        input_group_name = input(f"{Fore.YELLOW}Введите номер группы в формате \"МО-226Б\": ")
        group_id = get_group_id(input_group_name, semester_id)
        
        week_number = int(input(f"{Fore.YELLOW}Введите номер недели: "))
        calendar_object = get_calendar_object(group_id, semester_id, week_number)

        if calendar_object:
            export_object_to_ical(input_group_name, week_number, calendar_object)

            end_time = time.time()
            print(f'{Fore.GREEN}Время выполнения программы: {end_time - start_time:.2f} сек.')

    except ValueError as ve:
        print(f"{Fore.RED}{ve}")


if __name__ == "__main__":
    main()