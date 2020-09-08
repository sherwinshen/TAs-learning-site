# request_data = {
#     "boxType": 'blackBox' or 'whiteBox',
#     "teacherType": 'smartTeacher' or 'normalTeacher',
#     "upperGuard": 10,
#     "delta": 0.01,
#     "epsilon": 0.01,
#     "model": .....
# }

from app.automata_learning.black_box import black_box_learning
from app.automata_learning.white_box import white_box_learning


def automata_learning(learning_id, request_data):
    if request_data["boxType"] == "blackBox":
        black_box_learning(learning_id, request_data)
    elif request_data["boxType"] == "whiteBox":
        white_box_learning(learning_id, request_data)
