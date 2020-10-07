import random
from app.automata_learning.black_box.pac_learning.normal_teacher.timedWord import TimedWord


# 采样方式：一半取有效测试用例，一半取通用测试用例(也就是可能无效) - 也不一定一半可以通过概率控制
def sample_generation_main(upper_guard, length, system):
    p_choice = 0.5
    if random.random() >= p_choice:
        sample = sample_generation_custom(upper_guard, length, system)
    else:
        sample = None
        while sample is None:
            sample = sample_generation_valid(upper_guard, length, system)
    return sample


# 采样方式-old：长度均匀分布（或高斯分布），action和time均匀分布 —— 实验效果较差
def sample_generation_main_old_1(actions, upperGuard, stateNum):
    sample = []
    length = random.randint(1, stateNum * 2)
    for i in range(length):
        action = actions[random.randint(0, len(actions) - 1)]
        time = random.randint(0, upperGuard * 2 + 1)
        if time % 2 == 0:
            time = time // 2
        else:
            time = time // 2 + 0.5
        temp = TimedWord(action, time)
        sample.append(temp)
    return sample


# 采样 - 随机的测试序列（该序列不一定有效）
def sample_generation_custom(upper_guard, length, system):
    # 注意，通用采样情况下测试集可能是无效的，也就是可能会到达sink状态
    sample = None
    while sample is None:
        sample = sample_generation_valid(upper_guard, length, system)
    action = random.choice(system.actions)
    time = random.randint(0, upper_guard * 3 + 1)
    if time % 2 == 0:
        time = time // 2
    else:
        time = time // 2 + 0.5
    index = random.randint(0, len(sample) - 1)
    sample[index] = TimedWord(action, time)  # 随机替换其中一个
    return sample


# 采样 - 有效的测试序列
def sample_generation_valid(upper_guard, length, system):
    # First produce a path (as a list of transitions) in the OTA
    path = []
    cur_state = system.init_state
    for i in range(length):
        edges = []
        for tran in system.trans:
            if cur_state == tran.source:
                edges.append(tran)
        edge = random.choice(edges)
        path.append(edge)
        cur_state = edge.target

    # Next, figure out (double of) the minimum and maximum logical time of each edge in path.
    min_time, max_time = [], []
    for tran in path:
        min_time.append(min_constraint_double(tran.guards[0]))
        max_time.append(max_constraint_double(tran.guards[0], upper_guard))

    # For each transition, maintain a mapping from logical time to the number of choices.
    weight = dict()
    for i in reversed(range(length)):
        tran = path[i]
        min_value, max_value = min_time[i], max_time[i]
        weight[i] = dict()
        if i == length - 1 or tran.reset:
            for j in range(min_value, max_value + 1):
                weight[i][j] = 1
        else:
            for j in range(min_value, max_value + 1):
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
        cur_time = sample_distribution(distr) + start_time
        double_times.append(cur_time)
        if path[i].reset:
            cur_time = 0

    # Finally, change doubled time to fractions.
    ltw = []
    for i in range(length):
        if double_times[i] % 2 == 0:
            time = double_times[i] // 2
        else:
            time = double_times[i] // 2 + 0.5
        ltw.append(TimedWord(path[i].action, time))

    # Convert logical-timed word to delayed-timed word.
    dtw = []
    for i in range(length):
        if i == 0 or path[i - 1].reset:
            dtw.append(TimedWord(path[i].action, ltw[i].time))
        else:
            dtw.append(TimedWord(path[i].action, ltw[i].time - ltw[i - 1].time))
    return dtw


# --------------------------------- auxiliary function ---------------------------------

#  Get the double of the minimal number in an interval.
def min_constraint_double(c):
    """
        1. if the interval is empty, return None
        2. if [a, b$, return "2 * a".
        3. if (a, b$, return "2 * a + 1".
    """
    if c.is_empty():
        return None
    if c.closed_min:
        return int(2 * float(c.min_value))
    else:
        return int(2 * float(c.min_value) + 1)


#  Get the double of the maximal number in an interval.
def max_constraint_double(c, upperGuard):
    """
        1. if the interval is empty, return None
        2. if $a, b], return "2 * b".
        3. if $a, b), return "2 * b - 1".
        4. if $a, +), return "2 * upperGuard + 1".
    """
    if c.is_empty():
        return None
    if c.closed_max:
        return int(2 * float(c.max_value))
    elif c.max_value == '+':
        return int(2 * upperGuard + 1)
    else:
        return int(2 * float(c.max_value) - 1)


def sample_distribution(distr):
    s = sum(distr)
    if s == 0:
        return None
    a = random.randint(0, s - 1)
    for i, n in enumerate(distr):
        if n > a:
            return i
        else:
            a -= n
