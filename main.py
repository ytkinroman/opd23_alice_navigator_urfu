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
            c = (req["request"]["nlu"]["tokens"][0])
            text = (f"Ответ. {c}.")
            response["response"]["text"] = text
    return json.dumps(response)


if __name__ == "__main__":
    app.run()
