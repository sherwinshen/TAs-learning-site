import queue
import time
import copy

from app.automata_learning.black_box.pac_learning.normal_teacher.system import build_system
from app.automata_learning.black_box.pac_learning.normal_teacher.obsTable import init_table_normal, make_closed, make_consistent, deal_ctx
from app.automata_learning.black_box.pac_learning.normal_teacher.hypothesis import struct_discreteOTA, struct_hypothesisOTA, remove_sink_state
from app.automata_learning.black_box.pac_learning.normal_teacher.teacher import EQs
from app.automata_learning.black_box.pac_learning.normal_teacher.pac import minimize_counterexample_normal
from app.data_storage.init import update_cache


def black_normal_pac_learning(learning_id, request_data, startTime, timeout, debug_flag=False):
    # build target system
    system = build_system(request_data['model'])
    # makeOTA(buildSystem(modelFile), filePath, '/results/targetSys')

    actions = request_data["model"]["inputs"]
    upper_guard = request_data["upperGuard"]
    epsilon = request_data["epsilon"]  # accuracy
    delta = request_data["delta"]  # confidence
    state_num = len(request_data["model"]["states"])

    # pac learning OTA
    startLearning = time.time()
    if debug_flag:
        print("********** start learning *************")

    need_to_explore = queue.PriorityQueue()

    # init table
    for table in init_table_normal(actions, system):
        # table.show()
        need_to_explore.put((table.table_id, table))  # 优先级为表格的有效长度

    # List of existing counterexamples
    prev_ctx = []

    # Current number of tables
    t_number = 0
    target = None
    while True and time.time() - startTime <= timeout:
        if need_to_explore.qsize() == 0:
            break
        depth, current_table = need_to_explore.get()
        t_number = t_number + 1

        print("Table %s: current %s has parent-%s by %s" % (t_number, current_table.table_id, current_table.parent, current_table.reason))
        if debug_flag:
            current_table.show()
            print("--------------------------------------------------")

        # First check if the table is closed
        flag_closed, closed_move = current_table.is_closed()
        if not flag_closed:
            if debug_flag:
                print("------------------make closed--------------------------")
            temp_tables = make_closed(closed_move, actions, current_table, system)
            if len(temp_tables) > 0:
                for table in temp_tables:
                    # table.show()
                    need_to_explore.put((table.table_id, table))
            continue

        # If is closed, check if the table is consistent
        flag_consistent, prefix_LTWs, e_index, reset_i, reset_j, index_i, index_j = current_table.is_consistent()
        if not flag_consistent:
            if debug_flag:
                print("------------------make consistent--------------------------")
            temp_tables = make_consistent(prefix_LTWs, e_index, reset_i, reset_j, index_i, index_j, current_table, system)
            if len(temp_tables) > 0:
                for table in temp_tables:
                    # table.show()
                    need_to_explore.put((table.table_id, table))
            continue

        # If prepared, check conversion to FA
        discreteOTA = struct_discreteOTA(current_table, actions)
        if discreteOTA is None:
            continue
        if debug_flag:
            print("***************** discreteOTA_" + str(system.eq_num + 1) + " is as follow. *******************")
            discreteOTA.show_discreteOTA()

        # Convert FA to OTA
        hypothesisOTA = struct_hypothesisOTA(discreteOTA)
        if debug_flag:
            print("***************** Hypothesis_" + str(system.eq_num + 1) + " is as follow. *******************")
            hypothesisOTA.show_OTA()

        equivalent, ctx = True, None
        if prev_ctx is not None:
            for ctx in prev_ctx:
                real_value = system.test_DTWs_normal(ctx)
                value = hypothesisOTA.test_DTWs_normal(ctx)
                if real_value != value:
                    equivalent = False
                    ctx = minimize_counterexample_normal(hypothesisOTA, system, ctx)
                    break

        if equivalent:
            system.eq_num += 1
            equivalent, ctx = EQs(hypothesisOTA, upper_guard, epsilon, delta, system.eq_num, state_num, system)

        if not equivalent:
            # show ctx
            if debug_flag:
                print("***************** counterexample is as follow. *******************")
                print([dtw.show() for dtw in ctx])
            # deal with ctx
            if ctx not in prev_ctx:
                prev_ctx.append(ctx)
            temp_tables = deal_ctx(current_table, ctx, system)
            if len(temp_tables) > 0:
                for table in temp_tables:
                    # table.show()
                    need_to_explore.put((table.table_id, table))
        else:
            target = copy.deepcopy(hypothesisOTA)
            break
    endLearning = time.time()

    if target is None:
        value = {
            "isFinished": True,
            "result": {
                "result": 'fail',
            },
            "model": None
        }
    else:
        print('success')
        target_without_sink = remove_sink_state(target)
        value = {
            "isFinished": True,
            "result": {
                "result": 'success',
                "learningTime": endLearning - startLearning,
                "mqNum": system.mq_num,
                "eqNum": system.eq_num,
                "testNum": system.test_num,
                "tables explored": t_number,
            },
            "model": ota_to_JSON(target_without_sink)
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
        "sinkState": ota.sink_state,
        "trans": trans
    }
    return value
