from app.automata_learning.white_box.smart_teacher import smart_teacher_learning
from app.automata_learning.white_box.normal_teacher import normal_teacher_learning


def white_box_learning(learning_id, request_data):
    if request_data["teacherType"] == "smartTeacher":
        smart_teacher_learning(learning_id, request_data)
    elif request_data["teacherType"] == "normalTeacher":
        normal_teacher_learning(learning_id, request_data)
