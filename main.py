"""

    Fuck it.

"""
import json
import sqlite3
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    # Получаем запрос.
    req = request.json

    # Создаём ответ.
    response = {
        "version": request.json["version"],
        "session": request.json["session"],
        "response": {
            "end_session": False
        }
    }
    # Заполняем необходимую информацию.
    if req["session"]["new"]:
        response["response"]["text"] = "Я помогу найти тебе аудиторию. Какую аудиторию ты ищешь?"
    else:
        if req["request"]["original_utterance"]:
            # Инициализация.
            c = (req["request"]["nlu"]["tokens"][0])  # Корпус.
            au = (req["request"]["nlu"]["tokens"][1]) # Аудитория.
            # Обрабатываем.
            try:
                with sqlite3.connect("database.db") as db:
                    cursor = db.cursor()
                    query = f""" SELECT * FROM testing WHERE c = '{c}' AND au = '{au}' OR aua = '{au}' """
                    cursor.execute(query)
                    res = cursor.fetchone() # Картеж с данными из базы данных.
                    response["response"]["text"] = res
            except TypeError:
                text = "Корпус не найден..."
                response["response"]["text"] = text
    return json.dumps(response) # Отправляем ответ.


if __name__ == "__main__":
    app.run()
