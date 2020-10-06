from flask import Flask, request
from flask_cors import CORS

import json
import uuid
import time
from concurrent.futures import ThreadPoolExecutor
from app.data_storage.init import new_cache, delete_cache
from app.automata_learning.main import automata_learning

app = Flask(__name__)
CORS(app, supports_credentials=True)

executor = ThreadPoolExecutor()


@app.route("/api/learning", methods=["POST"])
def learning():
    learning_id = str(uuid.uuid1())
    new_cache(learning_id)
    request_data = json.loads(request.get_data(as_text=True))
    executor.submit(automata_learning, learning_id, request_data, time.time())
    return {"code": 1, "id": learning_id}


@app.route("/api/processing", methods=["POST"])
def get_process():
    request_data = json.loads(request.get_data(as_text=True))
    learning_id = request_data["id"]
    lastModified = request_data["lastModified"]
    path = "./cache/" + learning_id + ".json"
    with open(path, "r") as f:
        new_dict = json.load(f)
        f.close()

    def getMiddleModels(modelList):
        if len(modelList) <= 6:
            return False, modelList
        else:
            return True, modelList[0:2] + modelList[-3:]

    if new_dict["isFinished"]:
        ifOmit, middleModels = getMiddleModels(new_dict["middleModels"])
        return {"code": 1, "middleModels": middleModels, "lastModified": new_dict["lastModified"], "ifOmit": ifOmit}
    elif lastModified == new_dict["lastModified"]:
        return {"code": 2}
    else:
        ifOmit, middleModels = getMiddleModels(new_dict["middleModels"])
        return {"code": 0, "middleModels": middleModels, "lastModified": new_dict["lastModified"], "ifOmit": ifOmit}


@app.route("/api/result", methods=["POST"])
def get_result():
    request_data = json.loads(request.get_data(as_text=True))
    learning_id = request_data["id"]
    path = "./cache/" + learning_id + ".json"
    with open(path, "r") as f:
        new_dict = json.load(f)
        f.close()
    if new_dict["result"]["result"] == 'success':
        return {
            "code": 0,
            "result": new_dict["result"],
            "learnedModel": new_dict["model"]
        }
    else:
        return {
            "code": 1,
            "result": new_dict["result"]
        }


@app.route("/api/delete", methods=["POST"])
def delete_file():
    request_data = json.loads(request.get_data(as_text=True))
    learning_id = request_data["id"]
    delete_cache(learning_id)
    return {"code": 0, "msg": "Delete success!"}


@app.route("/api/getResult", methods=["POST"])
def download_result():
    request_data = json.loads(request.get_data(as_text=True))
    learning_id = request_data["id"]
    path = "./cache/" + learning_id + ".json"
    with open(path, "r") as f:
        new_dict = json.load(f)
        f.close()
    del new_dict["middleModels"]
    return {"code": 0, "data": new_dict}


@app.route("/api/getMiddle", methods=["POST"])
def download_middle():
    request_data = json.loads(request.get_data(as_text=True))
    learning_id = request_data["id"]
    path = "./cache/" + learning_id + ".json"
    with open(path, "r") as f:
        new_dict = json.load(f)
        f.close()
    return {"code": 0, "data": new_dict["middleModels"]}


@app.route("/api/test", methods=["GET"])
def test():
    return {"msg": "test success!"}


if __name__ == "__main__":
    app.run()
