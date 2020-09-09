import random
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import TimedWord


def sampleGenerationMain(teacher, upperGuard, length):
    if random.randint(0, 1) == 0:
        return sampleGeneration_invalid(teacher, upperGuard, length)
    else:
        sample = None
        while sample is None:
            sample = sampleGeneration_valid(teacher, upperGuard, length)
        return sample


# Generate a valid sample adapted to the given teacher.
def sampleGeneration_valid(teacher, upperGuard, length):
    # First produce a path (as a list of transitions) in the OTA
    path = []
    current_state = teacher.initState
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
        assert len(tran.guards) == 1
        min_time.append(min_constraint_double(tran.guards[0]))
        max_time.append(max_constraint_double(tran.guards[0], upperGuard))

    # For each transition, maintain a mapping from logical time to the number of choices.
    weight = dict()
    for i in reversed(range(length)):
        tran = path[i]
        mn, mx = min_time[i], max_time[i]
        weight[i] = dict()
        if i == length - 1 or tran.isReset:
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
        if path[i].isReset:
            cur_time = 0

    # Finally, change doubled time to fractions.
    ltw = []
    for i in range(length):
        if double_times[i] % 2 == 0:
            time = double_times[i] // 2
        else:
            time = double_times[i] // 2 + 0.1
        ltw.append(TimedWord(path[i].input, time))

    # Convert logical-timed word to delayed-timed word.
    dtw = []
    for i in range(length):
        if i == 0 or path[i - 1].isReset:
            dtw.append(TimedWord(path[i].input, ltw[i].time))
        else:
            dtw.append(TimedWord(path[i].input, ltw[i].time - ltw[i - 1].time))

    return dtw


# Generate an invalid (maybe) sample adapted to the given teacher.
def sampleGeneration_invalid(teacher, upperGuard, length):
    assert length > 0
    sample_prefix = None
    while sample_prefix is None:
        sample_prefix = sampleGeneration_valid(teacher, upperGuard, length)
    action = random.choice(teacher.inputs)
    time = random.randint(0, upperGuard * 3 + 1)
    if time % 2 == 0:
        time = time // 2
    else:
        time = time // 2 + 0.1
    index = random.randint(0, len(sample_prefix) - 1)
    sample_prefix[index] = TimedWord(action, time)
    return sample_prefix


def sampleGenerationMain_old(inputs, upperGuard, stateNum):
    sample = []
    length = random.randint(1, stateNum * 2)
    for i in range(length):
        input = inputs[random.randint(0, len(inputs) - 1)]
        time = random.randint(0, upperGuard * 2 + 1)
        if time % 2 == 0:
            time = time // 2
        else:
            time = time // 2 + 0.1
        temp = TimedWord(input, time)
        sample.append(temp)
    return sample


# --------------------------------- auxiliary function ---------------------------------

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
        return 2 * int(float(c.min_value))
    else:
        return 2 * int(float(c.min_value)) + 1


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
        return 2 * int(float(c.max_value))
    elif c.max_value == '+':
        return 2 * upperGuard + 1
    else:
        return 2 * int(float(c.max_value)) - 1
