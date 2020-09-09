# request_data = {
#     "boxType": 'blackBox' or 'whiteBox',
#     "teacherType": 'smartTeacher' or 'normalTeacher',
#     "upperGuard": 10,
#     "delta": 0.01,
#     "epsilon": 0.01,
#     "model": .....
# }

from app.automata_learning.white_box.smart_teacher import white_smart_learning
from app.automata_learning.white_box.normal_teacher import white_normal_learning
from app.automata_learning.black_box.pac_learning.smart_teacher import black_smart_pac_learning
from app.automata_learning.black_box.pac_learning.normal_teacher import black_normal_pac_learning


def automata_learning(learning_id, request_data):
    if request_data["boxType"] == "blackBox":
        if request_data["teacherType"] == "smartTeacher":
            black_smart_pac_learning(learning_id, request_data)
        elif request_data["teacherType"] == "normalTeacher":
            black_normal_pac_learning(learning_id, request_data)
    elif request_data["boxType"] == "whiteBox":
        if request_data["teacherType"] == "smartTeacher":
            white_smart_learning(learning_id, request_data)
        elif request_data["teacherType"] == "normalTeacher":
            white_normal_learning(learning_id, request_data)
    return True
