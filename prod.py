## Код функции для встраивания в работаюший сервис
# На вход принимает группу, список пар, все нужные параметры
# На выход отдаёт путь к файлу
#
#Это должна быть хорошая функция, которая узко выполняет задачу свою.
#
#Использовать аннотации
#Никакого обращения к апи не нужно в функции делать, данные будут идти внешне, а в функцию подавать готовые.
#Модели данных пока любые используй, хоть те же датаклассы.

import time
import os
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class ScheduleEvent:
    day: str
    time_range: str
    discipline: str
    lecture_type: str
    lecturer: str
    room: str

@dataclass
class ScheduleData:
    events: List[ScheduleEvent]

def generate_ical_file(group_name: str, week_number: int, schedule_data: ScheduleData) -> str:
    header = 'BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n'
    
    ##Вариант функции, которая сохранит файл в директории iCals, находящейся в той же директории, что и скрипт
    '''
    ical_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iCals')

    # Создаем директорию 'iCals', если её нет
    os.makedirs(ical_directory, exist_ok=True)
    ical_file_path = os.path.join(ical_directory, f'Расписание_занятий_для_группы_{group_name}_на_{week_number}-ю_неделю.ics')
    '''

    ##Вариант функции, которая сохранит файл в той же директории, что и скрипт   
    ical_file_path = os.path.join(os.getcwd(), f'Расписание_занятий_для_группы_{group_name}_на_{week_number}-ю_неделю.ics')

    with open(ical_file_path, 'w') as file:
        file.write(header)

        for event in schedule_data.events:
            day, time_range, discipline, lecture_type, lecturer, room = asdict(event).values()

            # Форматируем переменные
            summary = f"SUMMARY:{room} {discipline} {lecture_type} {lecturer}"
            dt_start = f"DTSTART:{day.split()[1].split('.')[2]}{day.split()[1].split('.')[1]}{day.split()[1].split('.')[0]}T{time_range.split('-')[0].replace(':', '')}00"
            dt_end = f"DTEND:{day.split()[1].split('.')[2]}{day.split()[1].split('.')[1]}{day.split()[1].split('.')[0]}T{time_range.split('-')[1].replace(':', '')}00"

            # Выводим результат
            csv_line = f'\nBEGIN:VEVENT\n{summary}\n{dt_start}\n{dt_end}\nEND:VEVENT\n'
            file.write(csv_line)

        footer = '\nEND:VCALENDAR\n'
        file.write(footer)

    print(f'Файл "{ical_file_path}" сформирован')
    return ical_file_path

def delete_file(file_path: str):
    try:
        os.remove(file_path)
        print(f'Файл "{file_path}" удален')
    except FileNotFoundError:
        print(f'Файл "{file_path}" не найден')
    except Exception as e:
        print(f'Произошла ошибка при удалении файла "{file_path}": {e}')

def integrate_into_service(input_semester: str, input_group_name: str, week_number: int, schedule_data: ScheduleData) -> str:
    ical_file_path = generate_ical_file(input_group_name, week_number, schedule_data)
    return ical_file_path



# Пример использования:
# schedule_data - это данные о расписании полученные от материнской функции
#schedule_data = get_schedule_data(input_group_name, semester_id, week_number)  # Ваша функция для получения расписания. Ну типа главная функция, которая парсит апи

## <-- Начало тестовых данных --> ##
schedule_data = ScheduleData(events=[
    ScheduleEvent(day="Понедельник 01.01.2023", time_range="10:00-11:30", discipline="Математика", lecture_type="Лекция", lecturer="Иванов И.И.", room="Ауд. 101"),
    ScheduleEvent(day="Понедельник 01.01.2023", time_range="12:00-13:30", discipline="Физика", lecture_type="Практика", lecturer="Петров П.П.", room="Ауд. 102"),
    ScheduleEvent(day="Вторник 02.01.2023", time_range="09:00-10:30", discipline="Химия", lecture_type="Лекция", lecturer="Сидоров С.С.", room="Ауд. 103"),
    ScheduleEvent(day="Среда 03.01.2023", time_range="14:00-15:30", discipline="Информатика", lecture_type="Семинар", lecturer="Кузнецов К.К.", room="Ауд. 104"),
    ScheduleEvent(day="Четверг 04.01.2023", time_range="16:00-17:30", discipline="Литература", lecture_type="Лекция", lecturer="Антонов А.А.", room="Ауд. 105"),
])

input_semester_name, input_group_name, input_week_number = 'Осенний семестр 2023/2024', 'МО-226Б', 15
## <-- Конец тестовых данных --> ##

ical_file_path = integrate_into_service(input_semester_name, input_group_name, input_week_number, schedule_data)

time.sleep(10)

delete_file(ical_file_path)