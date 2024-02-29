from flask import Flask, request
import json
import sqlite3

app = Flask(__name__)


def get_data_from_database(corpus, auditorium, database="db.db", table="test"):
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



def check_for_digits(tokens):
    for i in range(1, len(tokens)):
        if tokens[i].isdigit():
            return (tokens[i], tokens[i - 1])
    return None, None



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
        response["response"]["text"] = "Привет! Я помогу найти тебе аудиторию. Какую аудиторию ты ищешь?"
    else:
        if req["request"]["original_utterance"]:
            tokens = req["request"]["nlu"]["tokens"]
            rout_url = None
            s = []
            for token in tokens:
                s.append(token.lower())
            au, cor = check_for_digits(tokens)
            if au and cor:
                res = get_data_from_database(str(cor), str(au))
                if res is None:
                    text = "Аудитория не найдена в базе данных..."
                    response["response"]["text"] = text
                else:
                    t = res
                    text = get_message(t)
                    rout_url = t[7]
            else:
                text = "Аудитория в тексте не найдена..."
            if rout_url:
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
            else:
                response = {
                    'response': {
                        'text': text,
                        'end_session': False
                    },
                    'version': request.json["version"],
                    'session': request.json["session"],
                }
    return json.dumps(response)



if __name__ == "__main__":
    app.run()
