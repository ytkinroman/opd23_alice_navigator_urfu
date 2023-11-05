import json
import sqlite3
from flask import Flask, request


app = Flask(__name__)


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
            c = (req["request"]["nlu"]["tokens"][0])  # Корпус.
            au = (req["request"]["nlu"]["tokens"][1]) # Аудитория.
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
                            text = f"Аудитория \"{t[0].upper()}-{t[2]}\" – {t[1]}. Находится по адресу: {t[6]}. Вам нужно пройти в {t[4]} крыло и {action} на {t[5]} этаж."
                        elif t[5] == "первый":
                            text = f"Аудитория \"{t[0].upper()}-{t[2]}\" – {t[1]}. Находится по адресу: {t[6]}. Вам нужно пройти в {t[4]} крыло."
                        else:
                            action = "подняться"
                            text = f"Аудитория \"{t[0].upper()}-{t[2]}\" – {t[1]}. Находится по адресу: {t[6]}. Вам нужно пройти в {t[4]} крыло и {action} на {t[5]} этаж."
                        URL = ""
                        urlR = "https://yandex.ru/maps/?rtext=~56.840843,60.651053&rtt=mt"  # Радиофак..
                        urlC = "https://yandex.ru/maps/?rtext=~56.844934,60.650475&rtt=mt"  # Стройфак.
                        urlT = "https://yandex.ru/maps/?rtext=~56.842693,60.655748&rtt=mt"  # Теплофак.
                        if t[0].upper() == "С":
                            URL = urlC
                        elif t[0].upper() == "Р":
                            URL = urlR
                        else:
                            URL = urlT
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
