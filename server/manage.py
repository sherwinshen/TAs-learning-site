from flask import Flask, request
from flask_cors import CORS

import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from app.data_storage import new_cache, delete_cache
from app.automata_learning import automata_learning

app = Flask(__name__)
CORS(app, supports_credentials=True)

executor = ThreadPoolExecutor()


@app.route("/learning", methods=["POST"])
def learning():
    learning_id = str(uuid.uuid1())
    new_cache(learning_id)
    request_data = json.loads(request.get_data(as_text=True))
    executor.submit(automata_learning, learning_id, request_data)
    return {"code": 1, "id": learning_id}


@app.route("/processing", methods=["POST"])
def get_process():
    request_data = json.loads(request.get_data(as_text=True))
    learning_id = request_data["id"]
    lastModified = request_data["lastModified"]
    path = "./cache/" + learning_id + ".json"
    with open(path, "r") as f:
        new_dict = json.load(f)
        f.close()
    if new_dict["isFinished"]:
        return {"code": 1, "middleModels": new_dict["middleModels"], "lastModified": new_dict["lastModified"]}
    elif lastModified == new_dict["lastModified"]:
        return {"code": 2}
    else:
        return {"code": 0, "middleModels": new_dict["middleModels"], "lastModified": new_dict["lastModified"]}


@app.route("/result", methods=["POST"])
def get_result():
    request_data = json.loads(request.get_data(as_text=True))
    learning_id = request_data["id"]
    path = "./cache/" + learning_id + ".json"
    with open(path, "r") as f:
        new_dict = json.load(f)
        f.close()
    return {
        "result":  new_dict["result"],
        "learnedModel": new_dict["model"]
    }


@app.route("/delete", methods=["POST"])
def delete_file():
    request_data = json.loads(request.get_data(as_text=True))
    learning_id = request_data["id"]
    delete_cache(learning_id)
    return {"code": 0, "msg": "Delete success!"}


if __name__ == "__main__":
    app.run(port=5000, debug=True)
