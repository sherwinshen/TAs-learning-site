import time
import copy

from app.automata_learning.white_box.smart_teacher.ota import buildOTA, buildAssistantOTA
from app.automata_learning.white_box.smart_teacher.otatable import init_table, add_ctx, make_closed, make_consistent, make_evidence_closed
from app.automata_learning.white_box.smart_teacher.hypothesis import to_fa, fa_to_ota, remove_sinklocation
from app.automata_learning.white_box.smart_teacher.equivalence import equivalence_query

from app.data_storage.init import update_cache


def white_smart_learning(learning_id, request_data, startTime, timeout, debug=False):
    A, _ = buildOTA(request_data['model'], 's')
    AA = buildAssistantOTA(A, 's')
    max_time_value = request_data['upperGuard']
    if debug:
        print("**************Start to learn ...*******************")
        print("---------------initial table-------------------")
    sigma = AA.sigma
    T1 = init_table(sigma, AA)
    t_number = 1
    if debug:
        print("Table " + str(t_number) + " is as follow.")
        T1.show()
        print("-----------------------------------------------")
    start = time.time()
    equivalent = False
    eq_total_time = 0
    table = copy.deepcopy(T1)
    eq_number = 0
    target = None
    while not equivalent and time.time() - startTime <= timeout:
        prepared = table.is_prepared(AA)
        while not prepared:
            flag_closed, new_S, new_R, move = table.is_closed()
            if not flag_closed:
                temp = make_closed(new_S, new_R, move, table, sigma, AA)
                table = temp
                t_number = t_number + 1
                if debug:
                    print("Table " + str(t_number) + " is as follow.")
                    table.show()
                    print("--------------------------------------------------")
            flag_consistent, new_a, new_e_index = table.is_consistent()
            if not flag_consistent:
                temp = make_consistent(new_a, new_e_index, table, sigma, AA)
                table = temp
                t_number = t_number + 1
                if debug:
                    print("Table " + str(t_number) + " is as follow.")
                    table.show()
                    print("--------------------------------------------------")
            flag_evi_closed, new_added = table.is_evidence_closed(AA)
            if not flag_evi_closed:
                temp = make_evidence_closed(new_added, table, sigma, AA)
                table = temp
                t_number = t_number + 1
                if debug:
                    print("Table " + str(t_number) + " is as follow.")
                    table.show()
                    print("--------------------------------------------------")
            prepared = table.is_prepared(AA)
        fa, sink_name = to_fa(table, t_number)
        h = fa_to_ota(fa, sink_name, sigma, t_number)
        # 添加到 middleModels
        addMiddleModels(learning_id, remove_sinklocation(copy.deepcopy(h)))
        target = copy.deepcopy(h)
        eq_start = time.time()
        equivalent, ctx = equivalence_query(max_time_value, AA, h)
        eq_end = time.time()
        eq_total_time = eq_total_time + eq_end - eq_start
        eq_number = eq_number + 1
        if not equivalent:
            temp = add_ctx(ctx.tws, table, AA)
            table = temp
            t_number = t_number + 1
            if debug:
                print("Table " + str(t_number) + " is as follow.")
                table.show()
                print("--------------------------------------------------")
    end_learning = time.time()
    if target is None or not equivalent:
        value = {
            "isFinished": True,
            "result": {
                "result": 'fail',
            },
            "model": None
        }
    else:
        print('success')
        target_without_sink = remove_sinklocation(target)
        # target_without_sink = target
        value = {
            "isFinished": True,
            "result": {
                "result": 'success',
                "learningTime": end_learning - start,
                "mqNum": (len(table.S) + len(table.R)) * (len(table.E) + 1),
                "eqNum": eq_number,
                "learnedState": len(target_without_sink.locations),
            },
            "model": ota_to_JSON(target_without_sink)
        }
    update_cache(learning_id, value)
    return True


def ota_to_JSON(ota):
    trans = {}
    for i in range(len(ota.trans)):
        trans[i] = [ota.trans[i].source, ota.trans[i].label, ota.trans[i].show_constraints(), ota.trans[i].reset, ota.trans[i].target]
    states = []
    for j in range(len(ota.locations)):
        states.append(ota.locations[j].name)
    value = {
        "states": states,
        "inputs": ota.sigma,
        "initState": ota.initstate_name,
        "acceptStates": ota.accept_names,
        "sinkState": ota.sink_name,
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
