# request_data = {
#     "boxType": 'blackBox' or 'whiteBox',
#     "teacherType": 'smartTeacher' or 'normalTeacher',
#     "upperGuard": 10,
#     "delta": 0.01,
#     "epsilon": 0.01,
#     "model": .....
# }

from app.automata_learning.white_box.smart_teacher.main import white_smart_learning
from app.automata_learning.white_box.normal_teacher.main import white_normal_learning
from app.automata_learning.black_box.pac_learning.smart_teacher.main import black_smart_pac_learning
from app.automata_learning.black_box.pac_learning.normal_teacher.main import black_normal_pac_learning


def automata_learning(learning_id, request_data, startTime):
    timeout = request_data['timeout'] * 60
    if request_data["boxType"] == "blackBox":
        # 详见 https://github.com/MrEnvision/pac_learn_DOTAs
        if request_data["teacherType"] == "smartTeacher":
            black_smart_pac_learning(learning_id, request_data, startTime, timeout)
        # 详见 https://github.com/MrEnvision/pac_learn_DOTAs
        elif request_data["teacherType"] == "normalTeacher":
            black_normal_pac_learning(learning_id, request_data, startTime, timeout)
    elif request_data["boxType"] == "whiteBox":
        # 详见 https://github.com/Leslieaj/OTALearning
        if request_data["teacherType"] == "smartTeacher":
            white_smart_learning(learning_id, request_data, startTime, timeout)
        # 详见 https://github.com/Leslieaj/OTALearningNormal
        elif request_data["teacherType"] == "normalTeacher":
            white_normal_learning(learning_id, request_data, startTime, timeout)
    return True
