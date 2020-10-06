import math
import copy
from app.automata_learning.black_box.pac_learning.smart_teacher.sampling import sample_generation_main
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import TimedWord, DRTW_to_LRTW, LRTW_to_LTW


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
            flag = is_counterexample(hypothesis, system, sample)
            if flag:
                # if ctx is None or sample < ctx:
                ctx = sample
                break
        if ctx is not None:
            ctx = minimize_counterexample(hypothesis, system, ctx)
            return False, ctx
    return True, ctx


# --------------------------------- auxiliary function ---------------------------------

#  Compare evaluation of teacher and hypothesis on the given sample (a delay-timed word).
def is_counterexample(hypothesis, system, sample):
    system_res, real_value = system.test_DTWs(sample)
    hypothesis_res, value = hypothesis.test_DTWs(sample)
    return real_value != value


def minimize_counterexample(hypothesis, system, ctx):
    # Find sequence of reset information
    reset = []
    DRTWs, value = system.test_DTWs(ctx)
    for drtw in DRTWs:
        reset.append(drtw.reset)
    # ctx to LTWs
    LTWs = LRTW_to_LTW(DRTW_to_LRTW(DRTWs))
    # start minimize
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
            if not is_counterexample(hypothesis, system, LTW_to_DTW(LTWs_temp, reset)):
                break
            LTWs = copy.deepcopy(LTWs_temp)
    return LTW_to_DTW(LTWs, reset)


# --------------------------------- auxiliary function ---------------------------------

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
