import json
import os
import time


# 新建数据缓存（文件）
def new_cache(cache_id):
    json_text = {
        "createTime": time.time(),
        "lastModified": time.time(),
        "isFinished": False,
        "middleModels": []
    }
    json_data = json.dumps(json_text, indent=4)
    f = open('./cache/' + cache_id + '.json', 'w')
    f.write(json_data)
    f.close()


# 删除数据缓存（文件）
def delete_cache(cache_id):
    path = './cache/' + cache_id + '.json'
    if os.path.exists(path):  # 如果文件存在
        os.remove(path)


# 更新数据缓存（文件）
def update_cache(cache_id, values):
    path = './cache/' + cache_id + '.json'
    with open(path, "r") as f:
        new_dict = json.load(f)
        f.close()
    for key in values:
        if key == 'middleModels':
            new_dict['middleModels'].append(values['middleModels'])
        else:
            new_dict[key] = values[key]
    new_dict['lastModified'] = time.time()
    with open(path, "w") as f:
        new_dict = json.dumps(new_dict, indent=4)
        f.write(new_dict)
        f.close()
