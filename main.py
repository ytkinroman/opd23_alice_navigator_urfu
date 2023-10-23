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
        response["response"]["text"] = "Первое сообщение"
    else:
        if req["request"]["original_utterance"]:
            aua = (req["request"]["nlu"]["tokens"][0])
            try:
                with sqlite3.connect("database.db") as db:
                    cursor = db.cursor()
                    query = f""" SELECT * FROM testing WHERE au = '{aua}' """
                    cursor.execute(query)
                    res = cursor.fetchone()  # Картеж с данными из базы данных.
                    text = res[1]
                    response["response"]["text"] = text
            except TypeError:
                text = "Что-то не так..."
                response["response"]["text"] = text
    return json.dumps(response)


if __name__ == "__main__":
    app.run()
