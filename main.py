import json
import sqlite3
from flask import Flask, request

app = Flask(__name__)


def symbols_classroom(classroom):
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
    elif len(characters) == len(numbers) == 3:
        result = list(characters + numbers + characters)
    else:
        result = list(characters + numbers)
    return result


def get_message_p1(t):
    r = f"Аудитория \"{t[0].upper()}-{t[2]}\" – {t[1]}. Находится по адресу: {t[6]}."
    return r


def get_message_p2(t):
    if t[5] == "цокольный":
        r = f" Cпуститесь на {t[5]} этаж."
        return r
    elif t[5] == "первый":
        return ""
    else:
        r = f" Поднимитесь по лестнице на {t[5]} этаж."
        return r


def get_message_p3(t):
    if not t[4] is None:
        r = f" Пройдите в {t[4]} крыло."
        return r
    else:
        return ""


def get_message_p4(t):
    if not t[8] is None:
        return " " + t[8]
    else:
        return ""


def get_message(t):
    """
    цкйцвцувц
    :return: string
    """
    return get_message_p1(t) + get_message_p4(t) + get_message_p2(t) + get_message_p3(t)


@app.route("/alice-webhook", methods=["POST"])
def main():
    req = request.json
    response = {
        "version": request.json["version"],
        "session": request.json["session"],
        "response": {
            "end_session": False
        }
    }
    if req["session"]["new"]:
        response["response"]["text"] = "Я помогу найти тебе аудиторию. Какую аудиторию ты ищешь?"
    else:
        if req["request"]["original_utterance"]:
            #m = req["request"]["original_utterance"]
            m = ' '.join(req["request"]["nlu"]["tokens"])
            l = symbols_classroom(m)
            c = l[0].lower()  # Корпус.
            au = l[1]  # Аудитория.
            # asymb = l[1] # Символ аудитории если есть.
            try:
                with sqlite3.connect("db.db") as db:
                    cursor = db.cursor()
                    query = f""" SELECT * FROM test WHERE c = '{c}' AND au = '{au}' """
                    cursor.execute(query)
                    res = cursor.fetchone()  # Картеж с данными из базы данных.
                    if res is None:
                        text = text = "Аудитория не найдена..."
                        response["response"]["text"] = text
                    else:
                        t = res
                        text = get_message(t)
                        URL = t[7]
                        img001 = ["997614/8ff2a16ed346c7665978", "Тест пикча"]
                        ['respose']['card'] = { "type": "BigImage", "image_id": img, "title": title }
                        response = {
                            'response': {
                                'text': text,
                                "сard": {
                                    "type": "BigImage",
                                    "image_id": img001[0],
                                    "title": img001[1],
                                }
                                'buttons':
                                    {
                                        'title': 'Построить маршрут',
                                        'payload': {},
                                        'url': URL
                                    }
                                ,
                                'end_session': False
                            },
                            "version": request.json["version"],
                            "session": request.json["session"],
                        }
            except TypeError:
                text = "Что-то пошло не так..."
                response["response"]["text"] = text
    return json.dumps(response)


if __name__ == "__main__":
    app.run()
