from copy import deepcopy
from itertools import product
from app.automata_learning.black_box.pac_learning.normal_teacher.timedWord import TimedWord, ResetTimedWord, LRTW_to_DTW, DRTW_to_LRTW, LRTW_to_LTW

table_id = 0


class ObsTable(object):
    def __init__(self, S, R, E, parent, reason):
        global table_id
        self.S = S
        self.R = R
        self.E = E
        self.table_id = table_id
        table_id += 1
        self.parent = parent
        self.reason = reason  # init, make_closed, make_consistent, add_ctx

    def __lt__(self, other):
        return self.table_id < other.table_id

    def show(self):
        print("table ID: ", str(self.table_id))
        print("new_E: " + str(len(self.E)))
        for e in self.E:
            print([ltw.show() for ltw in e])
        print("new_S: " + str(len(self.S)))
        for s in self.S:
            print([lrtw.show() for lrtw in s.LRTWs], s.values, s.suffixes_resets)
        print("new_R: " + str(len(self.R)))
        for r in self.R:
            print([lrtw.show() for lrtw in r.LRTWs], r.values, r.suffixes_resets)

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

    # Determine whether the table is consistent.
    def is_consistent(self):
        flag = True
        e_index = 0
        prefix_LTWs = []
        reset_i = []
        reset_j = []
        index_i = 0
        index_j = 0
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
                                        prefix_LTWs = [TimedWord(newLRTWs1[0].action, newLRTWs1[0].time)]
                                        for k in range(0, len(e1.values)):
                                            if e1.values[k] != e2.values[k]:
                                                e_index = k
                                                reset_i = [newLRTWs1[0].reset] + table_element[i].suffixes_resets[k]
                                                reset_j = [newLRTWs2[0].reset] + table_element[j].suffixes_resets[k]
                                                index_i = i
                                                index_j = j
                                                return flag, prefix_LTWs, e_index, reset_i, reset_j, index_i, index_j
        return flag, prefix_LTWs, e_index, reset_i, reset_j, index_i, index_j


class Element(object):
    def __init__(self, LRTWs, values, suffixes_resets):
        self.LRTWs = LRTWs
        self.values = values
        self.suffixes_resets = suffixes_resets

    def __eq__(self, element):
        if self.LRTWs == element.LRTWs and self.values == element.values:
            return True
        else:
            return False


# initial tables
def init_table_normal(actions, system):
    if system.init_state in system.accept_states:
        init_value = 1
    else:
        init_value = 0
    S = [Element([], [init_value], [[]])]
    R = []
    E = [[]]
    tables = [ObsTable(S, R, E, parent=-1, reason="init")]
    for i in range(0, len(actions)):
        temp_tables = []
        for table in tables:
            new_DTWs = [TimedWord(actions[i], 0)]  # 同样也是LTWs
            value = system.test_DTWs_normal(new_DTWs, True)
            if value == -1:  # now at sink
                guesses = [True]
            else:
                guesses = [True, False]
            for guess in guesses:
                new_LRTWs = [ResetTimedWord(new_DTWs[0].action, new_DTWs[0].time, guess)]
                new_element = Element(new_LRTWs, [value], [[]])
                temp_R = table.R + [new_element]
                new_table = ObsTable(deepcopy(S), deepcopy(temp_R), deepcopy(E), parent=-1, reason="init")
                temp_tables.append(new_table)
        tables = temp_tables
    return tables


# Make table closed.
def make_closed(closed_move, actions, table, system):
    element = closed_move[0]
    table.S.append(element)
    table.R.remove(element)

    element_list = []
    for i in range(0, len(actions)):
        action_element_list = []
        if element.values[0] == -1:  # 原先已经是无效状态了，再加一个LTW还是无效状态
            new_LRTWs = element.LRTWs + [ResetTimedWord(actions[i], 0, True)]
            new_Element = fill_sink_row(new_LRTWs, table.E)
            action_element_list.append(new_Element)
        else:
            new_LRTWs = element.LRTWs + [ResetTimedWord(actions[i], 0, True)]
            if is_LRTWs_valid(new_LRTWs):
                DTWs = LRTW_to_DTW(new_LRTWs)
                value = system.test_DTWs_normal(DTWs, True)
                system.mq_num -= 1
                if value == -1:
                    system.mq_num += 1
                    new_Element = fill_sink_row(new_LRTWs, table.E)
                    action_element_list.append(new_Element)
                else:
                    guesses = [True, False]
                    for guess in guesses:
                        new_LRTWs = element.LRTWs + [ResetTimedWord(actions[i], 0, guess)]
                        new_Element_list = fill_guess_row(new_LRTWs, table.E, system)
                        action_element_list += new_Element_list
            else:  # make closed 的时候是允许无效的情况存在的
                new_Element = fill_sink_row(new_LRTWs, table.E)
                action_element_list.append(new_Element)
        element_list.append(action_element_list)

    table_list = []
    situations = [situation for situation in product(*element_list)]
    for situation in situations:
        temp_table = ObsTable(deepcopy(table.S), deepcopy(table.R) + deepcopy(list(situation)), deepcopy(table.E), parent=table.table_id, reason="make_closed")
        if check_table_consistent(temp_table):
            table_list.append(temp_table)
    return table_list


# Make table consistent.
def make_consistent(prefix_LTWs, e_index, reset_i, reset_j, index_i, index_j, table, system):
    table_elements = [s for s in table.S] + [r for r in table.R]
    new_e_LTWs = prefix_LTWs + table.E[e_index]
    table.E.append(new_e_LTWs)

    resets = []
    for i in range(len(table_elements)):
        select = []
        if i == index_i:
            select.append(reset_i)
        elif i == index_j:
            select.append(reset_j)
        else:
            if table_elements[i].values[0] == -1:
                select.append([True] * len(new_e_LTWs))
            else:
                temp_list = [[True, False]] * (len(new_e_LTWs) - 1) + [[True]]
                select = [list(situation) for situation in product(*temp_list)]
                # 再一次进行过滤，去除无效的猜测
                temp_select = []
                for temp in select:
                    new_LRTWs = table_elements[i].LRTWs + combine_LRTWs_with_LTWs(new_e_LTWs, temp)
                    if is_combined_LRTWs_valid(new_LRTWs):
                        temp_select.append(temp)
                select = temp_select
        resets.append(select)
    resets_list = [list(temp) for temp in product(*resets)]

    tables = []
    for reset_temp in resets_list:
        flag = True
        temp_table = ObsTable(deepcopy(table.S), deepcopy(table.R), deepcopy(table.E), parent=table.table_id, reason="make_consistent")
        for i in range(len(temp_table.S)):
            new_LRTWs = temp_table.S[i].LRTWs + combine_LRTWs_with_LTWs(new_e_LTWs, reset_temp[i])
            if temp_table.S[i].values[0] != -1:
                if is_LRTWs_valid(new_LRTWs):
                    DTWs = LRTW_to_DTW(new_LRTWs)
                    value = system.test_DTWs_normal(DTWs, True)
                    temp_table.S[i].values.append(value)
                    temp_table.S[i].suffixes_resets.append(reset_temp[i])
                else:
                    valid_LRTWs = get_valid_LRTWs(new_LRTWs)
                    DTWs = LRTW_to_DTW(valid_LRTWs)
                    value = system.test_DTWs_normal(DTWs, True)
                    if value == -1:
                        flag = False
                        break
                    temp_table.S[i].values.append(-1)
                    temp_table.S[i].suffixes_resets.append(reset_temp[i])
            else:
                temp_table.S[i].values.append(-1)
                temp_table.S[i].suffixes_resets.append(reset_temp[i])
        if flag:
            s_length = len(temp_table.S)
            for j in range(len(temp_table.R)):
                new_LRTWs = temp_table.R[j].LRTWs + combine_LRTWs_with_LTWs(new_e_LTWs, reset_temp[s_length + j])
                if temp_table.R[j].values[0] != -1:
                    if is_LRTWs_valid(new_LRTWs):
                        DTWs = LRTW_to_DTW(new_LRTWs)
                        value = system.test_DTWs_normal(DTWs, True)
                        temp_table.R[j].values.append(value)
                        temp_table.R[j].suffixes_resets.append(reset_temp[s_length + j])
                    else:
                        valid_LRTWs = get_valid_LRTWs(new_LRTWs)
                        DTWs = LRTW_to_DTW(valid_LRTWs)
                        value = system.test_DTWs_normal(DTWs, True)
                        if value == -1:
                            flag = False
                            break
                        temp_table.R[j].values.append(-1)
                        temp_table.R[j].suffixes_resets.append(reset_temp[s_length + j])
                else:
                    temp_table.R[j].values.append(-1)
                    temp_table.R[j].suffixes_resets.append(reset_temp[s_length + j])
        if flag and check_table_consistent(temp_table):
            tables.append(temp_table)
    return tables


#  Given a counterexample ctx, guess the reset, check the reset, for each suitable one, add it and its prefixes to R (except those already present in S and R).
def deal_ctx(table, ctx, system):
    table_elements = [s for s in table.S] + [r for r in table.R]
    S_R_LRTWs = [s.LRTWs for s in table.S] + [r.LRTWs for r in table.R]

    temp_list = []
    for i in range(len(ctx)):
        value = system.test_DTWs_normal(ctx[:i + 1])
        if value == -1:
            temp_list.append([True])
        else:
            temp_list.append([True, False])
    resets_guess = [list(situation) for situation in product(*temp_list)]

    table_list = []
    for resets in resets_guess:
        LRTWs = combine_LRTWS_with_DTWs(ctx, resets)
        if check_guessed_reset(LRTWs, table_elements):
            element_list = []
            for j in range(len(LRTWs)):
                cur_LRTWs_elements = []
                temp_LRTWs = LRTWs[:j + 1]
                if temp_LRTWs in S_R_LRTWs:
                    continue
                if system.test_DTWs_normal(LRTW_to_DTW(temp_LRTWs), True) == -1:
                    system.mq_num -= 1
                    new_Element = fill_sink_row(temp_LRTWs, table.E)
                    cur_LRTWs_elements.append(new_Element)
                else:
                    new_Element_list = fill_guess_row(temp_LRTWs, table.E, system)
                    cur_LRTWs_elements += new_Element_list
                element_list.append(cur_LRTWs_elements)
            situations = [situation for situation in product(*element_list)]
            for situation in situations:
                temp_table = ObsTable(deepcopy(table.S), deepcopy(table.R) + deepcopy(list(situation)), deepcopy(table.E), parent=table.table_id, reason="add_ctx")
                if check_table_consistent(temp_table):
                    table_list.append(temp_table)
    return table_list


# --------------------------------- auxiliary function ---------------------------------


# 检查表格的猜测均一致
def check_table_consistent(table):
    LRTWs_list = []
    LTWs_list = []
    for s in table.S:
        for i in range(1, len(s.LRTWs) + 1):
            temp_LRTWs = s.LRTWs[:i]
            temp_LTWs = LRTW_to_LTW(temp_LRTWs)
            if temp_LTWs in LTWs_list:
                guess_LRTWs = LRTWs_list[LTWs_list.index(temp_LTWs)]
                if guess_LRTWs != temp_LRTWs:
                    return False
            else:
                LRTWs_list.append(temp_LRTWs)
                LTWs_list.append(temp_LTWs)
        for index in range(len(table.E)):
            if len(table.E[index]) >= 2:
                merge_LRTWs = s.LRTWs + combine_LRTWs_with_LTWs(table.E[index][:-1], s.suffixes_resets[index][:-1])
                for i in range(len(s.LRTWs), len(merge_LRTWs) + 1):
                    temp_LRTWs = merge_LRTWs[:i]
                    temp_LTWs = LRTW_to_LTW(temp_LRTWs)
                    if temp_LTWs in LTWs_list:
                        guess_LRTWs = LRTWs_list[LTWs_list.index(temp_LTWs)]
                        if guess_LRTWs != temp_LRTWs:
                            return False
                    else:
                        LRTWs_list.append(temp_LRTWs)
                        LTWs_list.append(temp_LTWs)
    for r in table.R:
        for j in range(1, len(r.LRTWs) + 1):
            temp_LRTWs = r.LRTWs[:j]
            temp_LTWs = LRTW_to_LTW(temp_LRTWs)
            if temp_LTWs in LTWs_list:
                guess_LRTWs = LRTWs_list[LTWs_list.index(temp_LTWs)]
                if guess_LRTWs != temp_LRTWs:
                    return False
            else:
                LRTWs_list.append(temp_LRTWs)
                LTWs_list.append(temp_LTWs)
        for index in range(len(table.E)):
            if len(table.E[index]) >= 2:
                merge_LRTWs = r.LRTWs + combine_LRTWs_with_LTWs(table.E[index][:-1], r.suffixes_resets[index][:-1])
                for i in range(len(r.LRTWs), len(merge_LRTWs) + 1):
                    temp_LRTWs = merge_LRTWs[:i]
                    temp_LTWs = LRTW_to_LTW(temp_LRTWs)
                    if temp_LTWs in LTWs_list:
                        guess_LRTWs = LRTWs_list[LTWs_list.index(temp_LTWs)]
                        if guess_LRTWs != temp_LRTWs:
                            return False
                    else:
                        LRTWs_list.append(temp_LRTWs)
                        LTWs_list.append(temp_LTWs)
    return True


# 无效填充
def fill_sink_row(LRTWs, E):
    values = [-1] * len(E)
    suffixes_resets = []
    for e in E:
        if not e:
            suffixes_resets.append([])
        else:
            temp = [True] * len(e)
            suffixes_resets.append(temp)
    return Element(LRTWs, values, suffixes_resets)


# 猜测填充
def fill_guess_row(LRTWs, E, system):
    # 调用该函数的时候，要保证LRTWs是有效的
    element_list = []
    resets = guess_resets_in_suffixes(E)
    for reset in resets:
        flag, element = fill(LRTWs, E, reset, system)
        if flag:
            element_list.append(element)
    return element_list


# 根据E的猜测，完成element的填充
def fill(LRTWs, E, reset, system):
    # 调用该函数的时候，要保证LRTWs是有效的
    values = []
    for i in range(len(E)):
        new_LRTWs = LRTWs + combine_LRTWs_with_LTWs(E[i], reset[i])
        if not is_combined_LRTWs_valid(new_LRTWs):
            return False, None
        else:
            if is_LRTWs_valid(new_LRTWs):
                DTWs = LRTW_to_DTW(new_LRTWs)
                value = system.test_DTWs_normal(DTWs, True)
                values.append(value)
            else:
                valid_LRTWs = get_valid_LRTWs(new_LRTWs)
                DTWs = LRTW_to_DTW(valid_LRTWs)
                value = system.test_DTWs_normal(DTWs, True)
                if value == -1:
                    return False, None
                values.append(-1)
    return True, Element(LRTWs, values, reset)


# 保证ctx所猜测的重置，在SUR区域中没有重复
def check_guessed_reset(LRTWs, elements):
    for element in elements:
        for lrtw, i in zip(LRTWs, range(0, len(LRTWs))):
            if i < len(element.LRTWs):
                if lrtw.action == element.LRTWs[i].action and lrtw.time == element.LRTWs[i].time:
                    if lrtw.reset != element.LRTWs[i].reset:
                        return False
                else:
                    break
            else:
                break
    return True


# LTWs结合猜测的reset值得到LRTWs
def combine_LRTWs_with_LTWs(LTWs, reset):
    LRTWs = []
    for i in range(len(LTWs)):
        LRTWs.append(ResetTimedWord(LTWs[i].action, LTWs[i].time, reset[i]))
    return LRTWs


# DTWs结合猜测的reset值得到LRTWs
def combine_LRTWS_with_DTWs(DTWs, reset):
    DRTWs = []
    for i in range(len(DTWs)):
        DRTWs.append(ResetTimedWord(DTWs[i].action, DTWs[i].time, reset[i]))
    return DRTW_to_LRTW(DRTWs)


# 非sink的时候返回对应的E区域的所有可能的reset值
def guess_resets_in_suffixes(E):
    # 返回所有可能的情况，举例:
    # E = [[], [1], [1, 2]]
    # res = [
    #     [[], [True], [True, True]],
    #     [[], [True], [True, False]]
    # ]
    resets_list = []
    for e in E:
        if not e:
            resets_list.append([[]])
        else:
            if len(e) == 1:
                temp_list = [[True]]
            else:
                temp_list = [[True, False]] * (len(e) - 1) + [[True]]
            resets_list.append([list(situation) for situation in product(*temp_list)])
    return [list(resets) for resets in product(*resets_list)]


# determine whether LRTWs are valid
def is_LRTWs_valid(LRTWs):
    if not LRTWs:
        return True
    else:
        now_time = 0
        for lrtw in LRTWs:
            if lrtw.time >= now_time:
                if lrtw.reset:
                    now_time = 0
                else:
                    now_time = lrtw.time
            else:
                return False
        return True


# LRTWs是无效的，取其有效的前部分
def get_valid_LRTWs(LRTWs):
    new_LRTWs = []
    if not LRTWs:
        return new_LRTWs
    else:
        now_time = 0
        for lrtw in LRTWs:
            if lrtw.time >= now_time:
                new_LRTWs.append(lrtw)
                if lrtw.reset:
                    now_time = 0
                else:
                    now_time = lrtw.time
            else:
                return new_LRTWs
        return new_LRTWs


# 针对无效的情况：当中间一个LRTWs无效的时候后续reset都为true才是有效的
def is_combined_LRTWs_valid(LRTWs):
    if not LRTWs:
        return True
    else:
        flag = True
        now_time = 0
        for lrtw in LRTWs:
            if not flag:
                if not lrtw.reset:
                    return False
            else:
                if lrtw.time >= now_time:
                    if lrtw.reset:
                        now_time = 0
                    else:
                        now_time = lrtw.time
                else:
                    flag = False
        return True


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
