from flask import Flask, request
import json
import sqlite3

app = Flask(__name__)


def get_data_from_database(corpus, auditorium, database="db.db", table="test"):
    """
    Получает данные из указанной таблицы базы данных SQLite3 на основе предоставленных параметров корпуса и аудитории.
    Параметры:
    - corpus (str): Идентификатор корпуса.
    - auditorium (str): Идентификатор аудитории.
    - database (str): Имя файла базы данных SQLite3 (по умолчанию "db.db").
    - table (str): Имя таблицы базы данных (по умолчанию "test").
    """
    with sqlite3.connect(database) as db:
        cursor = db.cursor()
        query = f""" SELECT * FROM {table} WHERE c = ? AND au = ? """
        cursor.execute(query, (corpus, auditorium))
        result = cursor.fetchone()  # Картеж строки из базы данных.

        if result is None:
            return None
        else:
            return result


def symbols_classroom(classroom):
    # "р432" --> ["р", 432]
    characters = []
    numbers = []
    current_character = ""
    count = 0

    for element in classroom:
        if element.isalpha():  # проверяет, является ли текущий символ буквой
            if current_character.isdigit():  # проверяет, является ли предыдущий символ числом
                numbers.append(
                    int(current_character))  # добавляет предыдущий символ в список числовых символов, преобразуя его в целое число
                current_character = ""
            current_character += element
        elif element.isdigit():  # проверяет, является ли последний символ числом
            if current_character.isalpha():  # проверяет, является ли предыдущий символ буквой
                characters.append(current_character)  # добавляет последний символ в список буквенных символов
                current_character = ""
            current_character += element

        # Увеличиваем счетчик только для буквенных символов
        if element.isalpha():
            count += 1

    # Проверка последнего элемента, если он есть, то добавляем к текущей строке
    if current_character:
        if current_character.isdigit():
            numbers.append(int(current_character))
        else:
            characters.append(current_character)

    # Проверка на вид строки
    if len(characters) == 2:
        result = list(characters + numbers)
        result[2], result[1] = result[1], result[2]
        result[2] = result[2].lower()
    elif len(characters) == len(numbers) == 3:
        result = list(characters + numbers + characters)
        result[2] = result[2].lower()
    else:
        result = list(characters + numbers)
    result[0] = result[0].lower()
    return result


def get_message_p1(auditorium_data):
    """Формирует строку с информацией о номере и типе аудитории, а также её адрес."""
    result_data = f"Аудитория \"{auditorium_data[0].upper()}-{auditorium_data[2]}\" – {auditorium_data[1]}. Находится по адресу: {auditorium_data[6]}."
    return result_data


def get_message_p2(auditorium_data):
    """Формирует строку о местоположении аудитории на этаже."""
    if auditorium_data[5] == "цокольный":
        result_data = f"Cпуститесь на цокольный этаж."
        return result_data
    elif auditorium_data[5] == "первый":
        return "Первый этаж."
    elif auditorium_data[5] is not None:
        result_data = f"Поднимитесь по лестнице на {auditorium_data[5]} этаж."
        return result_data
    else:
        return ""


def get_message_p3(auditorium_data):
    """Формирует строку о расположении аудитории относительно крыла."""
    if not auditorium_data[4] is None:
        result_data = f"Пройдите в {auditorium_data[4]} крыло."
        return result_data
    else:
        return "Аудитория находится в центральной части."


def get_message_p4(auditorium_data):
    """Формирует строку с дополнительной информацией об аудитории."""
    if not auditorium_data[8] is None:
        return "" + auditorium_data[8]
    else:
        return ""


def get_message(auditorium_data):
    """
    Формирует итоговое сообщение с информацией об аудитории.
    Параметры:
    - auditorium_data (tuple): Кортеж с данными об аудитории.
    Возвращается:
    - str: Итоговое сообщение с информацией об аудитории.
    """
    return f"{get_message_p1(auditorium_data)} {get_message_p3(auditorium_data)} {get_message_p4(auditorium_data)} {get_message_p2(auditorium_data)}"


@app.route("/alice-webhook", methods=["POST"])
def main():
    req = request.json  # Получаем запрос.
    response = {  # Формируем базовый ответ.
        "version": request.json["version"],
        "session": request.json["session"],
        "response": {
            "end_session": False
        }
    }
    if req["session"]["new"]:  # Обработка запроса. Приветствие.
        response["response"]["text"] = "Привет! Я помогу найти тебе аудиторию. Какую аудиторию ты ищешь? (Примечание: Скажите только название аудитории, например И-125, Т-1010)."
    else:
        if req["request"]["original_utterance"]:

            m = ' '.join(req["request"]["nlu"]["tokens"])  # Р-0123      Р 23 Б     С,01      Т-1010 --> [т,1010]
            l = symbols_classroom(m)

            if len(l) < 2: # Для того чтобы Алиса игнорировала случайные значения или запросы
                response["response"]["text"] = "Пожалуйста, укажите название аудитории в формате, например, И-125 или Т-1010."
            else:
                c = l[0].lower()  # Корпус.
                au = str(l[1])  # Аудитория.

                if len(l) > 2 and l[2] in l:
                    a2 = l[2]  # буква кабинета
                    print(au + a2)

                res = get_data_from_database(c, au)

                if res is None:
                    text = "Аудитория не найдена..."
                    response["response"]["text"] = text
                else:
                    t = res
                    text = get_message(t)
                    rout_url = t[7]
                    response = {
                        'response': {
                            'text': text,
                            'buttons': [
                                {
                                    'title': 'Построить маршрут',
                                    'payload': {},
                                    'url': rout_url,
                                    'hide': "true"
                                }
                            ],
                            'end_session': False
                        },
                        'version': request.json["version"],
                        'session': request.json["session"],
                    }
    return json.dumps(response)


if __name__ == "__main__":
    app.run()
