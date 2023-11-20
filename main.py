import json
import sqlite3
from flask import Flask, request 


app = Flask(__name__)



def symbols_classroom(classroom):
    characters = []
    numbers = []

    current_character = ""

    for char in classroom:
        if char.isalpha():
            if current_character.isdigit():
                numbers.append(current_character)
                current_character = ""
            current_character += char
        elif char.isdigit():
            if current_character.isalpha():
                characters.append(current_character)
                current_character = ""
            current_character += char

    # Проверка, чтобы добавить последний элемент, если он есть
    if current_character:
        if current_character.isdigit():
            numbers.append(current_character)
        else:
            characters.append(current_character)

    result = characters + numbers
    return result


@app.route("/webhook", methods=["POST"])
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
            m = req["request"]["original_utterance"].lower()
            l = symbols_classroom(m)
            c = l[0]  # Корпус.
            au = l[2] # Аудитория.
            asymb = l[1] # Символ аудитории если есть.
            try:
                with sqlite3.connect("database.db") as db:
                    cursor = db.cursor()
                    query = f""" SELECT * FROM test WHERE c = '{c}' AND au = '{au}' """
                    cursor.execute(query)
                    res = cursor.fetchone()  # Картеж с данными из базы данных.
                    if res == None:
                        text = text = "Аудитория не найдена..."
                        response["response"]["text"] = text
                    else:
                        t = res
                        action = ""
                        if t[5] == "цокольный":
                            action = "спуститься"
                            text = f"Аудитория \"{t[0].upper()}-{t[2]}\" – {t[1]}. Находится по адресу: {t[6]}. Вам нужно {action} на {t[5]} этаж и пройти в {t[4]} крыло."
                        elif t[5] == "первый":
                            text = f"Аудитория \"{t[0].upper()}-{t[2]}\" – {t[1]}. Находится по адресу: {t[6]}. Вам нужно пройти в {t[4]} крыло."
                        else:
                            action = "подняться"
                            text = f"Аудитория \"{t[0].upper()}-{t[2]}\" – {t[1]}. Находится по адресу: {t[6]}. Вам нужно {action} на {t[5]} этаж и пройти в {t[4]} крыло."
                        URL = t[7]
                        response = {
                            'response': {
                                'text': text,
                                'buttons': [
                                    {
                                        'title': 'Построить маршрут',
                                        'payload': {},
                                        'url': URL
                                    }
                                ],
                                'end_session': False
                            },
                            "version": request.json["version"],
                            "session": request.json["session"],
                        }
                        
            except TypeError:
                text = "Что-то не так..."
                response["response"]["text"] = text
    return json.dumps(response)


if __name__ == "__main__":
    app.run()
