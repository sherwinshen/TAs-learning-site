import time
import copy
import queue

from app.automata_learning.white_box.normal_teacher.ota import buildOTA, buildAssistantOTA
from app.automata_learning.white_box.normal_teacher.otatable import init_table_normal, add_ctx_normal, make_closed, make_consistent
from app.automata_learning.white_box.normal_teacher.hypothesis import to_fa, fa_to_ota, remove_sinklocation
from app.automata_learning.white_box.normal_teacher.equivalence import equivalence_query_normal

from app.data_storage.init import update_cache


def white_normal_learning(learning_id, request_data, startTime, timeout, debug=False):
    A = buildOTA(request_data['model'], 's')
    AA = buildAssistantOTA(A, 's')
    max_time_value = request_data['upperGuard']
    if debug:
        print("**************Start to learn ...*******************")
        print("---------------initial table-------------------")
    sigma = AA.sigma

    need_to_explore = queue.PriorityQueue()
    for table in init_table_normal(sigma, AA):
        need_to_explore.put((table.effective_len(), table))

    # List of existing counterexamples
    prev_ctx = []

    # Current number of tables
    t_number = 0
    start = time.time()
    eq_total_time = 0
    eq_number = 0
    target = None
    equivalent = False
    while True and time.time() - startTime <= timeout:
        depth, current_table = need_to_explore.get()
        t_number = t_number + 1

        if debug and t_number % 1 == 0:
            print(t_number, need_to_explore.qsize(), current_table.effective_len())
        if debug:
            print("Table " + str(t_number) + " is as follow, %s has parent %s by %s" % (current_table.id, current_table.parent, current_table.reason))
            current_table.show()
            print("--------------------------------------------------")

        # First check if the table is closed
        flag_closed, new_S, new_R, move = current_table.is_closed()
        if not flag_closed:
            if debug:
                print("------------------make closed--------------------------")
            temp_tables = make_closed(new_S, new_R, move, current_table, sigma, AA)
            if len(temp_tables) > 0:
                for table in temp_tables:
                    need_to_explore.put((table.effective_len(), table))
            continue

        # If is closed, check if the table is consistent
        flag_consistent, new_a, new_e_index, reset_index_i, reset_index_j, reset_i, reset_j = current_table.is_consistent()
        if not flag_consistent:
            if debug:
                print("------------------make consistent--------------------------")
            temp_tables = make_consistent(new_a, new_e_index, reset_index_i, reset_index_j, reset_i, reset_j, current_table, sigma, AA)
            if len(temp_tables) > 0:
                for table in temp_tables:
                    need_to_explore.put((table.effective_len(), table))
            continue

        # If prepared, check conversion to FA
        fa_flag, fa, sink_name = to_fa(current_table, t_number)
        if not fa_flag:
            continue

        # Can convert to FA: convert to OTA and test equivalence
        h = fa_to_ota(fa, sink_name, sigma, t_number)
        eq_start = time.time()
        AA.equiv_query_num += 1
        equivalent, ctx = equivalence_query_normal(max_time_value, AA, h, prev_ctx)
        # Add counterexample to prev list
        if not equivalent and ctx not in prev_ctx:
            prev_ctx.append(ctx)
        eq_end = time.time()
        eq_total_time = eq_total_time + eq_end - eq_start
        eq_number = eq_number + 1
        if not equivalent:
            temp_tables = add_ctx_normal(ctx.tws, current_table, AA)
            if len(temp_tables) > 0:
                for table in temp_tables:
                    need_to_explore.put((table.effective_len(), table))
        else:
            target = copy.deepcopy(h)
            break

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
        value = {
            "isFinished": True,
            "result": {
                "result": 'success',
                "learningTime": end_learning - start,
                # "mqNum(cache)": len(AA.membership_query),
                "mqNum": AA.mem_query_num,
                # "eqNum(cache): len(prev_ctx) + 1,
                "eqNum": AA.equiv_query_num,
                "tables explored": t_number,
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
