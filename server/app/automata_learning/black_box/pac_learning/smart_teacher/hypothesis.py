import math
from app.automata_learning.black_box.pac_learning.smart_teacher.timeInterval import Guard, simple_guards
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import TimedWord, ResetTimedWord


class OTA(object):
    def __init__(self, actions, states, trans, init_state, accept_states, sink_state):
        self.actions = actions
        self.states = states
        self.trans = trans
        self.init_state = init_state
        self.accept_states = accept_states
        self.sink_state = sink_state

    def show_discreteOTA(self):
        print("Actions: " + str(self.actions))
        print("States: " + str(self.states))
        print("InitState: {}".format(self.init_state))
        print("AcceptStates: {}".format(self.accept_states))
        print("SinkState: {}".format(self.sink_state))
        print("Transitions: ")
        for t in self.trans:
            print(' ' + str(t.tran_id), 'S_' + str(t.source), str(t.action), str(t.time_point), str(t.reset), 'S_' + str(t.target), end="\n")

    def show_OTA(self):
        print("Actions: " + str(self.actions))
        print("States: " + str(self.states))
        print("InitState: {}".format(self.init_state))
        print("AcceptStates: {}".format(self.accept_states))
        print("SinkState: {}".format(self.sink_state))
        print("Transitions: ")
        for t in self.trans:
            print("  " + str(t.tran_id), 'S_' + str(t.source), str(t.action), t.show_guards(), str(t.reset), 'S_' + str(t.target), end="\n")

    def __lt__(self, other):
        return len(self.states) < len(other.states)

    # Perform tests(DTWs) on the hypothesis(smart teacher), return value and DRTWs(full)
    def test_DTWs(self, DTWs):
        DRTWs = []
        now_time = 0
        cur_state = self.init_state
        for dtw in DTWs:
            if cur_state == self.sink_state:
                DRTWs.append(ResetTimedWord(dtw.action, dtw.time, True))
            else:
                time = dtw.time + now_time
                new_LTW = TimedWord(dtw.action, time)
                for tran in self.trans:
                    if tran.source == cur_state and tran.is_passing_tran(new_LTW):
                        cur_state = tran.target
                        if tran.reset:
                            now_time = 0
                            reset = True
                        else:
                            now_time = time
                            reset = False
                        DRTWs.append(ResetTimedWord(dtw.action, dtw.time, reset))
                        break
        if cur_state in self.accept_states:
            value = 1
        elif cur_state == self.sink_state:
            value = -1
        else:
            value = 0
        return DRTWs, value

    # Perform tests(DTWs) on the hypothesis(normal teacher), return value
    def test_DTWs_normal(self, DTWs):
        now_time = 0
        cur_state = self.init_state
        for dtw in DTWs:
            time = dtw.time + now_time
            new_LTW = TimedWord(dtw.action, time)
            for tran in self.trans:
                if tran.source == cur_state and tran.is_passing_tran(new_LTW):
                    cur_state = tran.target
                    if tran.reset:
                        now_time = 0
                    else:
                        now_time = time
                    if cur_state == self.sink_state:
                        return -1
                    break
        if cur_state in self.accept_states:
            value = 1
        else:
            value = 0
        return value

    # build simple hypothesis - merge guards
    def build_simple_hypothesis(self):
        actions = self.actions
        states = self.states
        init_state = self.init_state
        accept_states = self.accept_states
        sink_state = self.sink_state
        trans = []
        tran_num = 0
        for s in self.states:
            for t in self.states:
                for action in actions:
                    for reset in [True, False]:
                        temp = []
                        for tran in self.trans:
                            if tran.source == s and tran.action == action and tran.target == t and tran.reset == reset:
                                temp.append(tran)
                        if temp:
                            guards = []
                            for i in temp:
                                guards += i.guards
                            guards = simple_guards(guards)
                            trans.append(OTATran(tran_num, s, action, guards, reset, t))
                            tran_num += 1
        return OTA(actions, states, trans, init_state, accept_states, sink_state)

    # Get the max time value constant appearing in OTA.
    def max_time_value(self):
        max_time_value = 0
        for tran in self.trans:
            for c in tran.guards:
                if c.max_value == '+':
                    temp_max_value = float(c.min_value) + 1
                else:
                    temp_max_value = float(c.max_value)
                if max_time_value < temp_max_value:
                    max_time_value = temp_max_value
        return max_time_value


class DiscreteOTATran(object):
    def __init__(self, tran_id, source, action, time_point, reset, target):
        self.tran_id = tran_id
        self.source = source
        self.action = action
        self.time_point = time_point
        self.reset = reset
        self.target = target


class OTATran(object):
    def __init__(self, tran_id, source, action, guards, reset, target):
        self.tran_id = tran_id
        self.source = source
        self.action = action
        self.guards = guards
        self.reset = reset
        self.target = target

    def is_passing_tran(self, ltw):
        if ltw.action == self.action:
            for guard in self.guards:
                if guard.is_in_interval(ltw.time):
                    return True
        else:
            return False
        return False

    def show_guards(self):
        temp = self.guards[0].show()
        for i in range(1, len(self.guards)):
            temp = temp + 'U' + self.guards[i].show()
        return temp


def struct_discreteOTA(table, actions):
    states = []
    trans = []
    init_state = ''
    accept_states = []
    sink_state = ''
    # deal with states
    values_name_dict = {}
    for s, i in zip(table.S, range(0, len(table.S))):
        state_name = i
        values_name_dict[str(s.values)] = state_name
        states.append(state_name)
        if not s.LRTWs:
            init_state = state_name
        if s.values[0] == 1:
            accept_states.append(state_name)
        if s.values[0] == -1:
            sink_state = state_name
    # deal with trans
    trans_num = 0
    table_elements = [s for s in table.S] + [r for r in table.R]
    for r in table_elements:
        source = None
        target = None
        if not r.LRTWs:
            continue
        timedWords = [lrtw for lrtw in r.LRTWs]
        w = timedWords[:-1]
        a = timedWords[len(timedWords) - 1]
        for element in table_elements:
            if is_equal(w, element.LRTWs):
                source = values_name_dict[str(element.values)]
            if is_equal(timedWords, element.LRTWs):
                target = values_name_dict[str(element.values)]
        # 确认迁移 action
        action = a.action
        time_point = a.time
        reset = a.reset
        # 添加新迁移还是添加时间点
        need_new_tran_flag = True
        for tran in trans:
            if source == tran.source and action == tran.action and target == tran.target:
                if time_point == tran.time_point:
                    need_new_tran_flag = False
                    break
        if need_new_tran_flag:
            temp_tran = DiscreteOTATran(trans_num, source, action, time_point, reset, target)
            trans.append(temp_tran)
            trans_num = trans_num + 1
    return OTA(actions, states, trans, init_state, accept_states, sink_state)


def struct_hypothesisOTA(discreteOTA):
    trans = []
    for s in discreteOTA.states:
        s_dict = {}
        for key in discreteOTA.actions:
            s_dict[key] = [0]
        for tran in discreteOTA.trans:
            if tran.source == s:
                for action in discreteOTA.actions:
                    if tran.action == action:
                        temp_list = s_dict[action]
                        if tran.time_point not in temp_list:
                            temp_list.append(tran.time_point)
                        s_dict[action] = temp_list
        for value in s_dict.values():
            value.sort()
        for tran in discreteOTA.trans:
            if tran.source == s:
                time_points = s_dict[tran.action]
                guards = []
                tw = tran.time_point
                index = time_points.index(tw)
                if index + 1 < len(time_points):
                    if is_int(tw) and is_int(time_points[index + 1]):
                        tempGuard = Guard("[" + str(tw) + "," + str(time_points[index + 1]) + ")")
                    elif is_int(tw) and not is_int(time_points[index + 1]):
                        tempGuard = Guard("[" + str(tw) + "," + str(math.modf(time_points[index + 1])[1]) + "]")
                    elif not is_int(tw) and is_int(time_points[index + 1]):
                        tempGuard = Guard("(" + str(math.modf(tw)[1]) + "," + str(time_points[index + 1]) + ")")
                    else:
                        tempGuard = Guard("(" + str(math.modf(tw)[1]) + "," + str(math.modf(time_points[index + 1])[1]) + "]")
                    guards.append(tempGuard)
                else:
                    if is_int(tw):
                        tempGuard = Guard("[" + str(tw) + ",+)")
                    else:
                        tempGuard = Guard("(" + str(math.modf(tw)[1]) + ",+)")
                    guards.append(tempGuard)
                for guard in guards:
                    trans.append(OTATran(tran.tran_id, tran.source, tran.action, [guard], tran.reset, tran.target))
    return OTA(discreteOTA.actions, discreteOTA.states, trans, discreteOTA.init_state, discreteOTA.accept_states, discreteOTA.sink_state)


# 去除sink状态的迁移
def remove_sink_state(hypothesis):
    if hypothesis.sink_state == '':
        return hypothesis
    actions = hypothesis.actions
    states = hypothesis.states
    init_state = hypothesis.init_state
    accept_states = hypothesis.accept_states
    states.remove(hypothesis.sink_state)
    trans = []
    for tran in hypothesis.trans:
        if tran.source != hypothesis.sink_state and tran.target != hypothesis.sink_state:
            trans.append(tran)
    return OTA(actions, states, trans, init_state, accept_states, hypothesis.sink_state)


# --------------------------------- auxiliary function ---------------------------------

# Determine whether two LRTWs are the same
def is_equal(LRTWs1, LRTWs2):
    if len(LRTWs1) != len(LRTWs2):
        return False
    else:
        flag = True
        for i in range(len(LRTWs1)):
            if LRTWs1[i] != LRTWs2[i]:
                flag = False
                break
        if flag:
            return True
        else:
            return False


# instance of Int?
def is_int(num):
    x, y = math.modf(num)
    if x == 0:
        return True
    else:
        return False
