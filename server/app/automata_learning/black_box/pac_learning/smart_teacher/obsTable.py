import math
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import TimedWord, ResetTimedWord, LRTW_to_LTW, DRTW_to_LRTW
from app.automata_learning.black_box.pac_learning.smart_teacher.teacher import TQs


class ObsTable(object):
    def __init__(self, S, R, E):
        self.S = S
        self.R = R
        self.E = E

    def show(self):
        print("new_E:" + str(len(self.E)))
        for e in self.E:
            print([ltw.show() for ltw in e])
        print("new_S:" + str(len(self.S)))
        for s in self.S:
            print([lrtw.show() for lrtw in s.LRTWs], s.values)
        print("new_R:" + str(len(self.R)))
        for r in self.R:
            print([lrtw.show() for lrtw in r.LRTWs], r.values)

    # Determine whether table is prepared
    def is_prepared(self):
        closed_flag, closed_move = self.is_closed()
        consistent_flag, consistent_add = self.is_consistent()
        if closed_flag and consistent_flag:
            return True
        else:
            return False

    # Determine whether it is closed
    def is_closed(self):
        closed_move = []
        for r in self.R:
            flag = False
            for s in self.S:
                if r.values == s.values:
                    flag = True
                    break
            if not flag:
                closed_move.append(r)  # 找到一个不满足closed情况就返回，这里不选择返回所有情况的方法
                break
        if len(closed_move) > 0:
            return False, closed_move
        else:
            return True, closed_move

    # Determine whether it is consistent
    def is_consistent(self):
        flag = True
        consistent_add = []
        table_element = [s for s in self.S] + [r for r in self.R]
        for i in range(0, len(table_element) - 1):
            for j in range(i + 1, len(table_element)):
                if table_element[i].values == table_element[j].values:
                    temp_elements1 = []
                    temp_elements2 = []
                    for element in table_element:
                        if is_prefix(element.LRTWs, table_element[i].LRTWs):
                            temp_elements1.append(element)
                        if is_prefix(element.LRTWs, table_element[j].LRTWs):
                            temp_elements2.append(element)
                    for e1 in temp_elements1:
                        for e2 in temp_elements2:
                            newLRTWs1 = delete_prefix(e1.LRTWs, table_element[i].LRTWs)
                            newLRTWs2 = delete_prefix(e2.LRTWs, table_element[j].LRTWs)
                            if len(newLRTWs1) == len(newLRTWs2) == 1:
                                if newLRTWs1[0].action == newLRTWs2[0].action and newLRTWs1[0].time == newLRTWs2[0].time:
                                    if e1.values != e2.values:
                                        flag = False
                                        for k in range(0, len(e1.values)):
                                            if e1.values[k] != e2.values[k]:
                                                new_index = k
                                                consistent_add = [TimedWord(newLRTWs1[0].action, newLRTWs1[0].time)] + self.E[new_index]
                                                return flag, consistent_add
        return flag, consistent_add


class Element(object):
    def __init__(self, LRTWs, values):
        self.LRTWs = LRTWs
        self.values = values  # [value]


# init observation table
def initTable(actions, system):
    table = ObsTable([], [], [])
    # deal with E
    table.E.append([])
    # deal with S
    element = fill_table_row([], table, False, system)
    table.S.append(element)
    # deal with R
    table = extend_R(table.S[0], actions, table, system)
    return table


# make closed
def make_closed(table, actions, close_move, system):
    # close_move将其从R移至S
    for r in close_move:
        table.S.append(r)
        table.R.remove(r)
    # 处理R
    for s in close_move:
        table = extend_R(s, actions, table, system)
    return table


# make consistent
def make_consistent(table, consistent_add, system):
    table.E.append(consistent_add)
    for i in range(0, len(table.S)):
        if is_valid(table.S[i].LRTWs):
            LTWs = LRTW_to_LTW(table.S[i].LRTWs) + consistent_add
            LRTWs, value = TQs(LTWs, system)
            temp_value = value
            table.S[i].values.append(temp_value)
        else:
            table.S[i].values.append(-1)
    for j in range(0, len(table.R)):
        if is_valid(table.R[j].LRTWs):
            LTWs = LRTW_to_LTW(table.R[j].LRTWs) + consistent_add
            LRTWs, value = TQs(LTWs, system)
            temp_value = value
            table.R[j].values.append(temp_value)
        else:
            table.R[j].values.append(-1)
    return table


def deal_ctx(table, ctx, system):
    DRTWs, value = system.test_DTWs(ctx)
    system.test_num -= 1
    new_ctx = normalize(DRTW_to_LRTW(DRTWs))
    pref = prefixes(new_ctx)
    LRTWs_list = [s.LRTWs for s in table.S] + [r.LRTWs for r in table.R]
    for LRTWs in pref:
        need_add_flag = True
        for temp_LRTWs in LRTWs_list:
            if LRTWs == temp_LRTWs:
                need_add_flag = False
                break
        if need_add_flag:
            temp_element = fill_table_row(LRTWs, table, False, system)
            table.R.append(temp_element)
    return table


# --------------------------------- auxiliary function ---------------------------------


# determine whether pre is the prefix of tws （判断pre是否是tws的前缀）
def is_prefix(tws, pre):
    if len(pre) == 0:
        return True
    else:
        if len(tws) < len(pre):
            return False
        else:
            for i in range(0, len(pre)):
                if tws[i] == pre[i]:
                    pass
                else:
                    return False
            return True


# remove prefix pre （删除tws的前缀pre）
def delete_prefix(tws, pre):
    if len(pre) == 0:
        return tws
    else:
        new_tws = tws[len(pre):]
        return new_tws


# Expand into a row according to s (根据s扩充成一行)
def fill_table_row(LRTWs, table, flag, system):
    # flag判断是否进入Error状态或查询是否有效 - flag为True表示已进入Error状态或无效
    if flag:
        values = [-1] * len(table.E)
        system.mq_num += len(table.E)
        element = Element(LRTWs, values)
    else:
        values = []
        if is_valid(LRTWs):
            for e in table.E:
                LTWs = LRTW_to_LTW(LRTWs) + e
                tempLRTWs, tempValue = TQs(LTWs, system)
                if len(e) != 0:
                    value = tempValue
                else:
                    value = tempValue
                values.append(value)
        else:
            values = [-1] * len(table.E)
            system.mq_num += len(table.E)
        element = Element(LRTWs, values)
    return element


# S adds s and table expands R area (S添加s,扩展R区域)
def extend_R(s, actions, table, system):
    table_LRTWS = [s.LRTWs for s in table.S] + [r.LRTWs for r in table.R]
    for action in actions:
        LTWs = LRTW_to_LTW(s.LRTWs) + [TimedWord(action, 0)]
        LRTWs, value = TQs(LTWs, system)
        system.mq_num -= 1
        if value == -1:
            element = fill_table_row(LRTWs, table, True, system)
        else:
            element = fill_table_row(LRTWs, table, False, system)
        if element.LRTWs not in table_LRTWS:
            table.R.append(element)
    return table


# determine whether LRTWs are valid （LRTWs是否有效）
def is_valid(LRTWs):
    if not LRTWs:
        return True
    else:
        nowTime = 0
        for lrtw in LRTWs:
            if lrtw.time >= nowTime:
                if lrtw.reset:
                    nowTime = 0
                else:
                    nowTime = lrtw.time
            else:
                return False
        return True


# prefix set of tws （tws前缀集）
def prefixes(tws):
    new_prefixes = []
    for i in range(1, len(tws) + 1):
        temp_tws = tws[:i]
        new_prefixes.append(temp_tws)
    return new_prefixes


# time normalization
def normalize(trace):
    new_trace = []
    for i in trace:
        if math.modf(float(i.time))[0] == 0.0:
            time = math.modf(float(i.time))[1]
        else:
            time = math.modf(float(i.time))[1] + 0.5
        new_trace.append(ResetTimedWord(i.action, time, i.reset))
    return new_trace


# get corresponding resetList in e (获得E中对应的resetList)
def get_resets(LRTWs, e):
    resets = []
    temp_LRTWs = LRTWs[-len(e):]
    for i in temp_LRTWs:
        resets.append(i.reset)
    return resets
