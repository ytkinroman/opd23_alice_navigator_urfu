import json
import sqlite3
from flask import Flask, request


app = Flask(__name__)


@app.route("/", methods=["POST"])
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
                    query = f""" SELECT * FROM test WHERE c = '{c}' AND au = '{au}' OR aua = '{au}' """
                    cursor.execute(query)
                    res = cursor.fetchone()  # Картеж с данными из базы данных.
                    if res == None:
                        text = text = "Не найдено..."
                        response["response"]["text"] = text
                    else:
                        text = str(res)
                        response["response"]["text"] = text
            except TypeError:
                text = "Что-то не так..."
                response["response"]["text"] = text
    return json.dumps(response)


if __name__ == "__main__":
    app.run()
