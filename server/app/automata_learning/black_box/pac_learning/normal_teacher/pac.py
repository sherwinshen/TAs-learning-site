import math
import copy
from app.automata_learning.black_box.pac_learning.normal_teacher.sampling import sample_generation_main
from app.automata_learning.black_box.pac_learning.normal_teacher.timedWord import TimedWord


# Equivalence query using random test cases based on pac
def pac_equivalence_query(hypothesis, upper_guard, epsilon, delta, state_num, eq_num, system):
    # Number of tests in the current round.
    test_num = int((math.log(1 / delta) + math.log(2) * (eq_num + 1)) / epsilon)
    ctx = None
    for length in range(1, math.ceil(state_num * 1.5)):  # 如果没有state_num，则自定义长度范围
        i = 0
        while i < test_num // state_num:
            i += 1
            # Generate sample (delay-timed word) according to fixed distribution
            sample = sample_generation_main(upper_guard, length, system)

            # Compare the results
            flag = is_counterexample_normal(hypothesis, system, sample)
            if flag:
                # if ctx is None or sample < ctx:
                ctx = sample
                break
        if ctx is not None:
            ctx = minimize_counterexample_normal(hypothesis, system, ctx)
            return False, ctx
    return True, ctx


# PAC中使用的等价查询数进行了分层
def pac_equivalence_query_level(hypothesis, upper_guard, epsilon, delta, level, m_i, state_num, system):
    # Number of tests in the current round.
    test_num = int((math.log(1 / delta) + math.log(2) * (level + 1) + math.log(m_i)) / epsilon)
    ctx = None
    for length in range(1, math.ceil(state_num * 1.5)):  # 如果没有state_num，则自定义长度范围
        i = 0
        while i < test_num // state_num:
            i += 1
            # Generate sample (delay-timed word) according to fixed distribution
            sample = sample_generation_main(upper_guard, length, system)

            # Compare the results
            flag = is_counterexample_normal(hypothesis, system, sample)
            if flag:
                # if ctx is None or sample < ctx:
                ctx = sample
                break
        if ctx is not None:
            ctx = minimize_counterexample_normal(hypothesis, system, ctx)
            return False, ctx
    return True, ctx


def is_counterexample_normal(hypothesis, system, sample):
    real_value = system.test_DTWs_normal(sample, False)
    value = hypothesis.test_DTWs_normal(sample)
    return real_value != value


def minimize_counterexample_normal(hypothesis, system, ctx):
    reset = []
    current_state = hypothesis.init_state
    current_clock = 0
    LTWs = []
    for tw in ctx:
        current_clock = current_clock + tw.time
        LTWs.append(TimedWord(tw.action, current_clock))
        for tran in hypothesis.trans:
            if current_state == tran.source and tran.is_passing_tran(TimedWord(tw.action, current_clock)):
                reset.append(tran.reset)
                current_state = tran.target
                if tran.reset:
                    current_clock = 0
                break
    for i in range(len(LTWs)):
        while True:
            if i == 0 or reset[i - 1]:
                can_reduce = (LTWs[i].time > 0)
            else:
                can_reduce = (LTWs[i].time > LTWs[i - 1].time)
            if not can_reduce:
                break
            LTWs_temp = copy.deepcopy(LTWs)
            LTWs_temp[i] = TimedWord(LTWs[i].action, one_lower(LTWs[i].time))
            if not is_counterexample_normal(hypothesis, system, LTW_to_DTW(LTWs_temp, reset)):
                break
            LTWs = LTWs_temp
    return LTW_to_DTW(LTWs, reset)


def one_lower(x):
    if x - int(x) == 0.5:
        return int(x)
    else:
        return x - 0.5


def LTW_to_DTW(LTWs, reset):
    DTWs = []
    for j in range(len(LTWs)):
        if j == 0 or reset[j - 1]:
            DTWs.append(TimedWord(LTWs[j].action, LTWs[j].time))
        else:
            DTWs.append(TimedWord(LTWs[j].action, LTWs[j].time - LTWs[j - 1].time))
    return DTWs
