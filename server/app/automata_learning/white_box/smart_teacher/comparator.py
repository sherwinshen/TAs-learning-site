from app.automata_learning.white_box.smart_teacher.equivalence import equivalence


def model_compare(hypothesis_pre, hypothesis_now, system):
    # Do not compare for the first time
    if hypothesis_pre is None:
        return True, []

    eq_flag, ctx = equivalence(hypothesis_now, hypothesis_pre)  # ctx is DTWs
    if eq_flag:
        raise Exception('eq_flag must be false!')
    flag = True
    DRTWs_real, value_real = system.test_DTWs(ctx)
    # 这个测试可以认为是mq上，不记录在test数量上
    system.test_num -= 1
    system.mq_num += 1
    DRTWs_now, value_now = hypothesis_now.test_DTWs(ctx)
    # if (value_real == 1 and value_now != 1) or (value_real != 1 and value_now == 1):
    if value_real != value_now:
        flag = False
    return flag, ctx
