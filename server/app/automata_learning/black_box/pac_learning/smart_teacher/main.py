import time
import copy
from app.data_storage.init import update_cache
from app.automata_learning.black_box.pac_learning.smart_teacher.system import build_system
import app.automata_learning.black_box.pac_learning.smart_teacher.obsTable as obsTable
from app.automata_learning.black_box.pac_learning.smart_teacher.teacher import EQs
from app.automata_learning.black_box.pac_learning.smart_teacher.hypothesis import struct_discreteOTA, struct_hypothesisOTA, remove_sink_state
from app.automata_learning.black_box.pac_learning.smart_teacher.comparator import model_compare

from app.automata_learning.black_box.pac_learning.smart_teacher.validate import validate


def black_smart_pac_learning(learning_id, request_data, startTime, timeout, debug_flag=False):
    # build target system
    system = build_system(request_data['model'])

    actions = request_data["model"]["inputs"]
    upper_guard = request_data["upperGuard"]
    epsilon = request_data["epsilon"]  # accuracy
    delta = request_data["delta"]  # confidence
    state_num = len(request_data["model"]["states"])

    # pac learning OTA
    startLearning = time.time()
    if debug_flag:
        print("********** start learning *************")

    ### init Table
    table = obsTable.initTable(actions, system)
    if debug_flag:
        print("***************** init-Table_1 is as follow *******************")
        table.show()

    ### learning start
    equivalent = False
    learned_system = None  # learned model
    table_num = 1  # number of table

    while not equivalent and time.time() - startTime <= timeout:
        prepared = table.is_prepared()
        while not prepared:
            # make closed
            closed_flag, close_move = table.is_closed()
            if not closed_flag:
                table = obsTable.make_closed(table, actions, close_move, system)

                table_num = table_num + 1
                if debug_flag:
                    print("***************** closed-Table_" + str(table_num) + " is as follow *******************")
                    table.show()
            # make consistent
            consistent_flag, consistent_add = table.is_consistent()
            if not consistent_flag:
                consistent_flag, consistent_add = table.is_consistent()
                table = obsTable.make_consistent(table, consistent_add, system)
                table_num = table_num + 1
                if debug_flag:
                    print("***************** consistent-Table_" + str(table_num) + " is as follow *******************")
                    table.show()
            prepared = table.is_prepared()

        ### build hypothesis
        # Discrete OTA
        discreteOTA = struct_discreteOTA(table, actions)
        if debug_flag:
            print("***************** discreteOTA_" + str(system.eq_num + 1) + " is as follow. *******************")
            discreteOTA.show_discreteOTA()
        # Hypothesis OTA
        hypothesisOTA = struct_hypothesisOTA(discreteOTA)
        if debug_flag:
            print("***************** Hypothesis_" + str(system.eq_num + 1) + " is as follow. *******************")
            hypothesisOTA.show_OTA()

        # 添加到 middleModels
        addMiddleModels(learning_id, remove_sink_state(copy.deepcopy(hypothesisOTA).build_simple_hypothesis()))

        ### comparator
        ctx_flag, ctx = model_compare(learned_system, hypothesisOTA, upper_guard, system)
        if ctx_flag:
            ### EQs
            equivalent, ctx = EQs(hypothesisOTA, upper_guard, epsilon, delta, state_num, system)
            learned_system = copy.deepcopy(hypothesisOTA)
        else:
            if debug_flag:
                print("Comparator found a counterexample!!!")
            equivalent = False

        if not equivalent:
            # show ctx
            if debug_flag:
                print("***************** counterexample is as follow. *******************")
                print([dtw.show() for dtw in ctx])
            # deal with ctx
            table = obsTable.deal_ctx(table, ctx, system)
            table_num = table_num + 1
            if debug_flag:
                print("***************** New-Table" + str(table_num) + " is as follow *******************")
                table.show()

    endLearning = time.time()

    if learned_system is None or not equivalent:
        value = {
            "isFinished": True,
            "result": {
                "result": 'fail',
            },
            "model": None
        }
    else:
        # verify model quality
        correct_flag, passing_rate = validate(learned_system, system, upper_guard)
        learned_system = remove_sink_state(learned_system.build_simple_hypothesis())
        print('success')
        value = {
            "isFinished": True,
            "result": {
                "result": 'success',
                "learningTime": endLearning - startLearning,
                "mqNum": system.mq_num,
                "eqNum": system.eq_num,
                "testNum": system.test_num,
                "tables explored": table_num,
                "passingRate": passing_rate,
                "correct": str(correct_flag)
            },
            "model": ota_to_JSON(learned_system)
        }
    update_cache(learning_id, value)
    return True


def ota_to_JSON(ota):
    trans = {}
    for i in range(len(ota.trans)):
        trans[i] = [ota.trans[i].source, ota.trans[i].action, ota.trans[i].show_guards(), ota.trans[i].reset, ota.trans[i].target]
    value = {
        "states": ota.states,
        "inputs": ota.actions,
        "initState": ota.init_state,
        "acceptStates": ota.accept_states,
        "trans": trans
    }
    return value


def addMiddleModels(learning_id, ota):
    value = {
        "lastModified": time.time(),
        "middleModels": ota_to_JSON(ota)
    }
    update_cache(learning_id, value)
    return True
