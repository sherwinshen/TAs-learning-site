# Equivalence query under PAC.

import random
import math
import copy
from app.automata_learning.black_box.pac_learning.normal_teacher.ota import Timedword
from app.automata_learning.black_box.pac_learning.normal_teacher.otatable import Element


def isCounterexample(teacher, hypothesis, sample):
    """
        Compare evaluation of teacher and hypothesis on the given sample (a delay-timed word).
    """
    # Evaluation of sample on the teacher, should be -1, 0, 1
    realValue = teacher.is_accepted_delay(sample.tws)

    # Evaluation of sample on the hypothesis, should be -1, 0, 1
    value = hypothesis.is_accepted_delay(sample.tws)

    return (realValue == 1 and value != 1) or (realValue != 1 and value == 1)


def minimizeCounterexample(teacher, hypothesis, sample):
    """
        Minimize a given delay-timed word.
    """
    reset = []
    current_state = hypothesis.initstate_name
    current_clock = 0
    ltw = []

    # Fix computation with 0.1
    def round1(x):
        return int(x * 10 + 0.5) / 10

    def one_lower(x):
        if round1(x - int(x)) == 0.1:
            return int(x)
        else:
            return round1(x - 0.9)

    # Find sequence of reset information
    for tw in sample.tws:
        current_clock = round1(current_clock + tw.time)
        ltw.append(Timedword(tw.action, current_clock))
        for tran in hypothesis.trans:
            found = False
            if current_state == tran.source and tran.is_pass(Timedword(tw.action, current_clock)):
                reset.append(tran.reset)
                current_state = tran.target
                if tran.reset:
                    current_clock = 0
                found = True
                break
        assert found

    # print('ltw:', ltw)

    def ltw_to_dtw(ltw):
        dtw = []
        for i in range(len(ltw)):
            if i == 0 or reset[i - 1]:
                dtw.append(Timedword(ltw[i].action, ltw[i].time))
            else:
                dtw.append(Timedword(ltw[i].action, round1(ltw[i].time - ltw[i - 1].time)))
        return Element(dtw, [])

    # print('initial:', ltw_to_dtw(ltw).tws)

    for i in range(len(ltw)):
        while True:
            if i == 0 or reset[i - 1]:
                can_reduce = (ltw[i].time > 0)
            else:
                can_reduce = (ltw[i].time > ltw[i - 1].time)
            if not can_reduce:
                break
            ltw2 = copy.deepcopy(ltw)
            ltw2[i] = Timedword(ltw[i].action, one_lower(ltw[i].time))
            # print('try', ltw_to_dtw(ltw2).tws)
            if not isCounterexample(teacher, hypothesis, ltw_to_dtw(ltw2)):
                break
            # print('change')
            ltw = ltw2

    # print('final:', ltw_to_dtw(ltw).tws)
    return ltw_to_dtw(ltw)


def pac_equivalence_query(A, upperGuard, teacher, hypothesis, eqNum, epsilon, delta):
    """
        Equivalence query using random test cases.
    """

    # Number of tests in the current round.
    testNum = int((math.log(1 / delta) + math.log(2) * (eqNum + 1)) / epsilon)

    stateNum = len(teacher.locations)
    for length in range(1, stateNum + 2):
        ctx = None
        correct = 0
        i = 0
        while i < testNum // stateNum:
            i += 1
            # Generate sample (delay-timed word) according to fixed distribution
            sample = sampleGenerationMain(A, upperGuard, length)

            # Compare the results
            if isCounterexample(teacher, hypothesis, sample):
                if ctx is None or sample.tws < ctx.tws:
                    ctx = sample

        if ctx is not None:
            ctx = minimizeCounterexample(teacher, hypothesis, ctx)
            return False, ctx, length + correct / (testNum // stateNum)

    return True, None, stateNum + 1


def sampleGeneration(inputs, upperGuard, stateNum, length=None):
    """
        Generate a sample.
    """
    sample = []
    if length is None:
        length = random.randint(1, stateNum)
    for i in range(length):
        input = inputs[random.randint(0, len(inputs) - 1)]
        time = random.randint(0, upperGuard * 2 + 1)
        if time % 2 == 0:
            time = time // 2
        else:
            time = time // 2 + 0.1
        temp = Timedword(input, time)
        sample.append(temp)
    return Element(sample, [])


def min_constraint_double(c):
    """
        Get the double of the minimal number in an interval.
        1. if the interval is empty, return None
        2. if [a, b$, return "2 * a".
        3. if (a, b$, return "2 * a + 1".
    """
    if c.isEmpty():
        return None
    if c.closed_min:
        return 2 * int(c.min_value)
    else:
        return 2 * int(c.min_value) + 1


def max_constraint_double(c, upperGuard):
    """
        Get the double of the maximal number in an interval.
        1. if the interval is empty, return None
        2. if $a, b], return "2 * b".
        3. if $a, b), return "2 * b - 1".
        4. if $a, +), return "2 * upperGuard + 1".
    """
    if c.isEmpty():
        return None
    if c.closed_max:
        return 2 * int(c.max_value)
    elif c.max_value == '+':
        return 2 * upperGuard + 1
    else:
        return 2 * int(c.max_value) - 1


def sampleDistribution(distr):
    s = sum(distr)
    if s == 0:
        return None
    a = random.randint(0, s - 1)

    for i, n in enumerate(distr):
        if n > a:
            return i
        else:
            a -= n


def sampleGeneration_valid(teacher, upperGuard, length):
    """
        Generate a sample adapted to the given teacher.
    """

    # First produce a path (as a list of transitions) in the OTA
    path = []
    current_state = teacher.initstate_name
    for i in range(length):
        edges = []
        for tran in teacher.trans:
            if current_state == tran.source:
                edges.append(tran)
        edge = random.choice(edges)
        path.append(edge)
        current_state = edge.target

    # Next, figure out (double of) the minimum and maximum logical time.
    min_time, max_time = [], []
    for tran in path:
        assert len(tran.constraints) == 1
        min_time.append(min_constraint_double(tran.constraints[0]))
        max_time.append(max_constraint_double(tran.constraints[0], upperGuard))

    # For each transition, maintain a mapping from logical time to the number of choices.
    weight = dict()
    for i in reversed(range(length)):
        tran = path[i]
        mn, mx = min_time[i], max_time[i]
        weight[i] = dict()
        if i == length - 1 or tran.reset:
            for j in range(mn, mx + 1):
                weight[i][j] = 1
        else:
            for j in range(mn, mx + 1):
                weight[i][j] = 0
                for k, w in weight[i + 1].items():
                    if k >= j:
                        weight[i][j] += w

    # Now sample according to the weights
    double_times = []
    cur_time = 0
    for i in range(length):
        start_time = max(min_time[i], cur_time)
        distr = []
        for j in range(start_time, max_time[i] + 1):
            distr.append(weight[i][j])
        if sum(distr) == 0:
            return None  # sampling failed
        cur_time = sampleDistribution(distr) + start_time
        double_times.append(cur_time)
        if path[i].reset:
            cur_time = 0

    # Finally, change doubled time to fractions.
    ltw = []
    for i in range(length):
        if double_times[i] % 2 == 0:
            time = double_times[i] // 2
        else:
            time = double_times[i] // 2 + 0.1
        ltw.append(Timedword(path[i].label, time))

    # Convert logical-timed word to delayed-timed word.
    dtw = []
    for i in range(length):
        if i == 0 or path[i - 1].reset:
            dtw.append(Timedword(path[i].label, ltw[i].time))
        else:
            dtw.append(Timedword(path[i].label, ltw[i].time - ltw[i - 1].time))

    return Element(dtw, [])


def sampleGenerationMain(teacher, upperGuard, length):
    if random.randint(0, 1) == 0:
        return sampleGeneration(teacher.sigma, upperGuard, len(teacher.locations), length)
    else:
        sample = None
        while sample is None:
            sample = sampleGeneration_valid(teacher, upperGuard, length)
        return sample


if __name__ == "__main__":
    random.seed(1)

    import sys
    from normalLearning.ota import buildOTA, buildAssistantOTA

    A = buildOTA(sys.argv[1], 's')
    AA = buildAssistantOTA(A, 's')
    A.show()
    for i in range(100):
        sample = sampleGenerationMain(A, A.max_time_value(), 4)
        if sample:
            print(sample.tws)
