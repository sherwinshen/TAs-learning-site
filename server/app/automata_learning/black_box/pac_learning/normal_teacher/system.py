import copy
from app.automata_learning.black_box.pac_learning.normal_teacher.timedWord import TimedWord, ResetTimedWord
from app.automata_learning.black_box.pac_learning.normal_teacher.timeInterval import Guard, BracketNum, Bracket
from app.automata_learning.black_box.pac_learning.normal_teacher.hypothesis import OTA, OTATran


class System(object):
    def __init__(self, actions, states, trans, init_state, accept_states):
        self.actions = actions
        self.states = states
        self.trans = trans
        self.init_state = init_state
        self.accept_states = accept_states

        self.mq_num = 0
        self.eq_num = 0
        self.test_num = 0

    # Perform tests(LTWs) on the system(smart teacher), return value and LRTWs(补全)
    def test_LTWs(self, LTWs):
        self.mq_num += 1
        if not LTWs:
            if self.init_state in self.accept_states:
                value = 1
            else:
                value = 0
            return [], value
        else:
            LRTWs = []
            value = None
            now_time = 0
            cur_state = self.init_state
            for ltw in LTWs:
                if ltw.time < now_time:
                    value = -1
                    LRTWs.append(ResetTimedWord(ltw.action, ltw.time, True))
                    break
                else:
                    DTW = TimedWord(ltw.action, ltw.time - now_time)
                    cur_state, value, reset = self.test_DTW(DTW, now_time, cur_state)
                    if reset:
                        LRTWs.append(ResetTimedWord(ltw.action, ltw.time, True))
                        now_time = 0
                    else:
                        LRTWs.append(ResetTimedWord(ltw.action, ltw.time, False))
                        now_time = ltw.time
                    if value == -1:
                        break
            # 补全
            len_diff = len(LTWs) - len(LRTWs)
            if len_diff != 0:
                temp = LTWs[len(LRTWs):]
                for i in temp:
                    LRTWs.append(ResetTimedWord(i.action, i.time, True))
            return LRTWs, value

    # Perform tests(DTWs) on the system, return value and DRTWs(full)
    def test_DTWs(self, DTWs):
        self.test_num += 1
        DRTWs = []
        value = None
        now_time = 0
        cur_state = self.init_state
        for dtw in DTWs:
            time = dtw.time + now_time
            new_LTW = TimedWord(dtw.action, time)
            flag = False
            for tran in self.trans:
                if tran.source == cur_state and tran.is_passing_tran(new_LTW):
                    flag = True
                    cur_state = tran.target
                    if tran.reset:
                        now_time = 0
                        reset = True
                    else:
                        now_time = time
                        reset = False
                    DRTWs.append(ResetTimedWord(dtw.action, dtw.time, reset))
                    break
            if not flag:
                DRTWs.append(ResetTimedWord(dtw.action, dtw.time, True))
                value = -1
                break
        # 补全
        len_diff = len(DTWs) - len(DRTWs)
        if len_diff != 0:
            temp = DTWs[len(DRTWs):]
            for i in temp:
                DRTWs.append(ResetTimedWord(i.action, i.time, True))
        if value != -1:
            if cur_state in self.accept_states:
                value = 1
            else:
                value = 0
        return DRTWs, value

    # input -> DTW(single)，output -> curState and value - for logical-timed test
    def test_DTW(self, DTW, now_time, cur_state):
        value = None
        reset = False
        tran_flag = False  # tranFlag为true表示有这样的迁移
        if DTW is None:
            if cur_state in self.accept_states:
                value = 1
            else:
                value = 0
        else:
            LTW = TimedWord(DTW.action, DTW.time + now_time)
            for tran in self.trans:
                if tran.source == cur_state and tran.is_passing_tran(LTW):
                    tran_flag = True
                    cur_state = tran.target
                    if tran.reset:
                        reset = True
                    break
            if not tran_flag:
                value = -1
                cur_state = 'sink'
                reset = True
            if cur_state in self.accept_states:
                value = 1
            elif cur_state != 'sink':
                value = 0
        return cur_state, value, reset

    # Perform tests(DTWs) on the system, return value
    def test_DTWs_normal(self, DTWs, is_mq=False):
        if is_mq:
            self.mq_num += 1
        else:
            self.test_num += 1
        value = 0
        now_time = 0
        cur_state = self.init_state
        for dtw in DTWs:
            time = dtw.time + now_time
            new_LTW = TimedWord(dtw.action, time)
            flag = False
            for tran in self.trans:
                if tran.source == cur_state and tran.is_passing_tran(new_LTW):
                    flag = True
                    cur_state = tran.target
                    if tran.reset:
                        now_time = 0
                    else:
                        now_time = time
                    break
            if not flag:
                value = -1
                break
        if value != -1:
            if cur_state in self.accept_states:
                value = 1
            else:
                value = 0
        return value

    # input -> DTW(single)，output -> curState and value - for logical-timed test
    def test_DTW_normal(self, DTW, now_time, cur_state):
        value = None
        reset = False
        tran_flag = False  # tranFlag为true表示有这样的迁移
        if DTW is None:
            if cur_state in self.accept_states:
                value = 1
            else:
                value = 0
        else:
            LTW = TimedWord(DTW.action, DTW.time + now_time)
            for tran in self.trans:
                if tran.source == cur_state and tran.is_passing_tran(LTW):
                    tran_flag = True
                    cur_state = tran.target
                    if tran.reset:
                        reset = True
                    break
            if not tran_flag:
                value = -1
                cur_state = 'sink'
                reset = True
            if cur_state in self.accept_states:
                value = 1
            elif cur_state != 'sink':
                value = 0
        return cur_state, value, reset


class SysTran(object):
    def __init__(self, tran_id, source, action, guards, reset, target):
        self.tran_id = tran_id
        self.source = source
        self.action = action
        self.guards = guards
        self.reset = reset
        self.target = target

    def is_passing_tran(self, tw):
        if tw.action == self.action:
            for guard in self.guards:
                if guard.is_in_interval(tw.time):
                    return True
        return False

    def show_guards(self):
        guard_list = self.guards[0].show()
        for i in range(1, len(self.guards)):
            guard_list = guard_list + 'U' + self.guards[i].show()
        return guard_list


# Build system based on json file
def build_system(model):
    actions = model["inputs"]
    states = model["states"]
    init_state = model["initState"]
    accept_states = model["acceptStates"]
    tran_list = model["trans"]

    trans = []
    for tran in tran_list:
        tran_id = str(tran)
        source = tran_list[tran][0]
        target = tran_list[tran][4]
        action = tran_list[tran][1]
        reset = tran_list[tran][3] == "r"
        # time guard
        intervals = tran_list[tran][2]
        intervals_list = intervals.split('U')
        guards = []
        for guard in intervals_list:
            new_guard = Guard(guard.strip())
            guards.append(new_guard)
        trans.append(SysTran(tran_id, source, action, guards, reset, target))
    return System(actions, states, trans, init_state, accept_states)


# make system complete
def build_canonicalOTA(system):
    actions = system.actions
    states = system.states
    trans = system.trans
    init_state = system.init_state
    accept_states = system.accept_states

    sinkFlag = False
    newTrans = []
    sink_state = None
    tranNumber = len(system.trans)

    for state in system.states:
        guardDict = {}
        for action in actions:
            guardDict[action] = []
        for tran in trans:
            if tran.source == state:
                for action in actions:
                    if tran.action == action:
                        for guard in tran.guards:
                            guardDict[action].append(guard)
        for key, value in guardDict.items():
            if len(value) > 0:
                addGuards = complement_intervals(value)
            else:
                addGuards = [Guard('[0,+)')]
            if len(addGuards) > 0:
                sink_state = 'sink'
                sinkFlag = True
                for guard in addGuards:
                    tempTran = OTATran(tranNumber, state, key, [guard], True, sink_state)
                    tranNumber = tranNumber + 1
                    newTrans.append(tempTran)
    if sinkFlag:
        states.append(sink_state)
        for tran in newTrans:
            trans.append(tran)
        for action in actions:
            guards = [Guard('[0,+)')]
            tempTran = OTATran(tranNumber, sink_state, action, guards, True, sink_state)
            tranNumber = tranNumber + 1
            trans.append(tempTran)
    newOTA = OTA(actions, states, trans, init_state, accept_states, sink_state)
    return newOTA


# 补全区间
def complement_intervals(guards):
    partitions = []
    key = []
    floor_bn = BracketNum('0', Bracket.LC)
    ceil_bn = BracketNum('+', Bracket.RO)
    for guard in guards:
        min_bn = guard.min_bn
        max_bn = guard.max_bn
        if min_bn not in key:
            key.append(min_bn)
        if max_bn not in key:
            key.append(max_bn)
    copyKey = copy.deepcopy(key)
    for bn in copyKey:
        complement = bn.complement()
        if complement not in copyKey:
            copyKey.append(complement)
    if floor_bn not in copyKey:
        copyKey.insert(0, floor_bn)
    if ceil_bn not in copyKey:
        copyKey.append(ceil_bn)
    copyKey.sort()
    for index in range(len(copyKey)):
        if index % 2 == 0:
            tempGuard = Guard(copyKey[index].getBN() + ',' + copyKey[index + 1].getBN())
            partitions.append(tempGuard)
    for g in guards:
        if g in partitions:
            partitions.remove(g)
    return partitions
