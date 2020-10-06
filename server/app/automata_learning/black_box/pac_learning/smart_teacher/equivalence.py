#  model equivalence checking —— the model is COTA(complete OTA), in other words, hypothesis
from app.automata_learning.black_box.pac_learning.smart_teacher.timeInterval import Guard
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import TimedWord


class Letter(object):
    def __init__(self, state, guard, flag):
        self.state = state
        if isinstance(guard, str):
            guard = Guard(guard)
        self.guard = guard
        self.flag = flag  # "A" or "B"

    def __eq__(self, letter):
        if self.state == letter.state and self.guard == letter.guard and self.flag == letter.flag:
            return True
        else:
            return False

    def __hash__(self):
        return hash(("LETTER", self.state, self.guard))


class LetterWord(object):
    def __init__(self, lw, prelw, action):
        self.lw = lw
        self.prelw = prelw
        self.action = action

    def __eq__(self, letterword):
        return self.lw == letterword.lw


# 注意，传入的model1和model2都要是complete模型
def equivalence(model1, model2, upper_guard):
    upper_guard = max(upper_guard, model1.max_time_value(), model2.max_time_value())
    res, w_pos = ota_inclusion(upper_guard, model1, model2)
    dtw_pos = None
    if not res:
        # dtw_pos is accepted by model2 but not model1
        dtw_pos = find_DTWs(w_pos)

    res2, w_neg = ota_inclusion(upper_guard, model2, model1)
    dtw_neg = None
    if not res2:
        # dtw_neg is accepted by model1 but not model2
        dtw_neg = find_DTWs(w_neg)

    if res and res2:
        return True, None

    ctx = None
    if res and not res2:
        ctx = dtw_neg
    elif res2 and not res:
        ctx = dtw_pos
    elif not res2 and not res:
        if len(find_path(w_pos)) <= len(find_path(w_neg)):
            ctx = dtw_pos
        else:
            ctx = dtw_neg
    return False, ctx


# Determine whether L(B) is a subset of L(A)
def ota_inclusion(upper_guard, A, B):
    w0 = [{Letter(A.init_state, "[0,0]", "A"), Letter(B.init_state, "[0,0]", "B")}]
    explore_list = [LetterWord(w0, None, 'INIT')]
    explored = []
    while True:
        if len(explore_list) == 0:
            return True, None
        w = explore_list[0]
        del explore_list[0]
        if is_bad_letterword(w.lw, A, B):
            return False, w
        while explored_dominated(explored, w):
            if len(explore_list) == 0:
                return True, None
            w = explore_list[0]
            del explore_list[0]
            if is_bad_letterword(w.lw, A, B):
                return False, w
        wsucc, next_list = compute_wsucc(w, upper_guard, A, B)
        for nw in next_list:
            if nw not in explore_list:
                explore_list.append(nw)
        if w not in explored:
            explored.append(w)


# Determine whether a letterword is bad in case of "L(B) is a subset of L(A)"
def is_bad_letterword(letterword, A, B):
    if len(letterword) == 1:
        letter1, letter2 = list(letterword[0])
    elif len(letterword) == 2:
        letter1, letter2 = list(letterword[0])[0], list(letterword[1])[0]
    else:
        raise NotImplementedError()
    location1, flag1 = letter1.state, letter1.flag
    location2, flag2 = letter2.state, letter2.flag
    if flag1 == "B":
        if location1 in B.accept_states and location2 not in A.accept_states:
            return True
        else:
            return False
    else:
        if location2 in B.accept_states and location1 not in A.accept_states:
            return True
        else:
            return False


def explored_dominated(explored, w):
    if len(explored) == 0:
        return False
    for v in explored:
        if letterword_dominated(v, w):
            return True
    return False


# To determine whether letterword lw1 is dominated by letterword lw2 (lw1 <= lw2)
def letterword_dominated(lw1, lw2):
    index = 0
    flag = 0
    for letters1 in lw1.lw:
        for i in range(index, len(lw2.lw)):
            if letters1.issubset(lw2.lw[i]):
                index = i + 1
                flag = flag + 1
                break
            else:
                pass
    if flag == len(lw1.lw):
        return True
    else:
        return False


# Compute the Succ of letterword.
def compute_wsucc(letterword, upper_guard, A, B):
    # First compute all possible time delay
    results = []
    last_region = Guard('(' + str(upper_guard) + ',' + '+' + ')')
    if len(letterword.lw) == 1:
        result = letterword.lw[0]
        while any(letter.guard != last_region for letter in result):
            results.append(LetterWord([result], letterword, 'DELAY'))
            new_result = set()
            for letter in result:
                new_letter = Letter(letter.state, next_region(letter.guard, upper_guard), letter.flag)
                new_result.add(new_letter)
            result = new_result
        current_lw = LetterWord([result], letterword, 'DELAY')
        if current_lw not in results:
            results.append(current_lw)
    elif len(letterword.lw) == 2:
        if len(letterword.lw[0]) != 1 and len(letterword.lw[1]) != 1:
            raise NotImplementedError()
        result = letterword.lw
        while list(result[0])[0].guard != last_region or list(result[1])[0].guard != last_region:
            results.append(LetterWord(result, letterword, 'DELAY'))
            new_result = []
            l1, l2 = list(result[0])[0], list(result[1])[0]
            if l1.guard.is_point():
                new_result.append({Letter(l1.state, next_region(l1.guard, upper_guard), l1.flag)})
                new_result.append({l2})
            else:
                new_result.append({Letter(l2.state, next_region(l2.guard, upper_guard), l2.flag)})
                new_result.append({l1})
            result = new_result
        current_lw = LetterWord(result, letterword, 'DELAY')
        if current_lw not in results:
            results.append(current_lw)
            new_result = LetterWord([current_lw.lw[1], current_lw.lw[0]], letterword, 'DELAY')
            if new_result not in results:
                results.append(new_result)
    else:
        raise NotImplementedError()

    # Next, perform the immediate 'a' transition
    next_list = []
    for letterword in results:
        next_ws = immediate_asucc(letterword, A, B)
        for next_w in next_ws:
            if next_w not in next_list:
                next_list.append(next_w)
    return results, next_list


# Perform the immediate 'a' action in case of L(B) is a subset of L(A).
def immediate_asucc(letterword, A, B):
    results = []
    if len(letterword.lw) == 1:
        letter1, letter2 = list(letterword.lw[0])
        for action in B.actions:
            if letter1.flag == "A":
                B_letter = immediate_letter_asucc(letter2, action, B, "B")
                A_letter = immediate_letter_asucc(letter1, action, A, "A")
            else:
                B_letter = immediate_letter_asucc(letter1, action, B, "B")
                A_letter = immediate_letter_asucc(letter2, action, A, "A")
            if B_letter is not None and A_letter is not None:
                B_is_point = B_letter.guard.is_point()
                A_is_point = A_letter.guard.is_point()
                if A_is_point and B_is_point:
                    w = [{A_letter, B_letter}]
                elif A_is_point and not B_is_point:
                    w = [{A_letter}, {B_letter}]
                elif not A_is_point and B_is_point:
                    w = [{B_letter}, {A_letter}]
                else:
                    w = [{A_letter, B_letter}]
                current_lw = LetterWord(w, letterword, action)
                if current_lw not in results:
                    results.append(current_lw)
    elif len(letterword.lw) == 2:
        letter1, letter2 = list(letterword.lw[0])[0], list(letterword.lw[1])[0]
        for action in B.actions:
            if letter1.flag == "A":
                B_letter = immediate_letter_asucc(letter2, action, B, "B")
                A_letter = immediate_letter_asucc(letter1, action, A, "A")
                if B_letter is not None and A_letter is not None:
                    B_is_point = B_letter.guard.is_point()
                    A_is_point = A_letter.guard.is_point()
                    if A_is_point and B_is_point:
                        w = [{A_letter, B_letter}]
                    elif A_is_point and not B_is_point:
                        w = [{A_letter}, {B_letter}]
                    elif not A_is_point and B_is_point:
                        w = [{B_letter}, {A_letter}]
                    else:
                        w = [{A_letter}, {B_letter}]
                    current_lw = LetterWord(w, letterword, action)
                    if current_lw not in results:
                        results.append(current_lw)
            else:
                B_letter = immediate_letter_asucc(letter1, action, B, "B")
                A_letter = immediate_letter_asucc(letter2, action, A, "A")
                if B_letter is not None and A_letter is not None:
                    B_is_point = B_letter.guard.is_point()
                    A_is_point = A_letter.guard.is_point()
                    if A_is_point and B_is_point:
                        w = [{A_letter, B_letter}]
                    elif A_is_point and not B_is_point:
                        w = [{A_letter}, {B_letter}]
                    elif not A_is_point and B_is_point:
                        w = [{B_letter}, {A_letter}]
                    else:
                        w = [{B_letter}, {A_letter}]
                    current_lw = LetterWord(w, letterword, action)
                    if current_lw not in results:
                        results.append(current_lw)
    else:
        raise NotImplementedError()
    return results


def immediate_letter_asucc(letter, action, ota, flag):
    location_name = letter.state
    region = letter.guard
    for tran in ota.trans:
        if tran.source == location_name and action == tran.action and region.is_subset(tran.guards[0]):
            succ_location = tran.target
            if tran.reset:
                region = Guard("[0,0]")
            if succ_location is not None:
                return Letter(succ_location, region, flag)
    return None


# Given a path, return the delay timedword.
def find_DTWs(letterword):
    path = find_path(letterword)
    DTWs = []
    current_clock_valuation = 0
    delay_time = 0
    for letterword in path:
        if len(letterword.lw) == 1:
            letter1, letter2 = list(letterword.lw[0])
        elif len(letterword.lw) == 2:
            letter1, letter2 = list(letterword.lw[0])[0], list(letterword.lw[1])[0]
        else:
            raise NotImplementedError()
        if letter1.flag == 'A':  # "A" or "B"?
            temp_region = letter1.guard
        else:
            temp_region = letter2.guard
        if letterword.action == "DELAY":
            delay_time = minimum_in_region(temp_region) - current_clock_valuation
            current_clock_valuation = minimum_in_region(temp_region)
        elif letterword.action == 'INIT':
            pass
        else:
            new_timedword = TimedWord(letterword.action, delay_time)
            DTWs.append(new_timedword)
            current_clock_valuation = minimum_in_region(temp_region)
    return DTWs


# When get a letterword, find the path ends in the letterword.
def find_path(letterword):
    current_lw = letterword
    path = [current_lw]
    while current_lw.prelw is not None:
        path.insert(0, current_lw.prelw)
        current_lw = current_lw.prelw
    return path


# --------------------------------- auxiliary function ---------------------------------

def next_region(region, upper_guard):
    if region.is_point():
        if float(region.max_value) == float(upper_guard):
            return Guard('(' + region.max_value + ',' + '+' + ')')
        else:
            return Guard('(' + region.max_value + ',' + str(int(region.max_value) + 1) + ')')
    else:
        if region.max_value == '+':
            return Guard('(' + region.min_value + ',' + '+' + ')')
        else:
            return Guard('[' + region.max_value + ',' + region.max_value + ']')


# Return the minimal number in the region. For [5,9], return 5; for (4,10), return 4.5 .
def minimum_in_region(constraint):
    if constraint.closed_min:
        return int(constraint.min_value)
    else:
        return float(constraint.min_value + '.5')

# if __name__ == '__main__':
#     import json
#     import copy
#     from common.system import build_system
#     from structure.TimeInterval import Bracket, BracketNum
#     from structure.Hypothesis import OTA, OTATran
#
#
#     # 补全targetSys
#     def buildCanonicalOTA(targetSys):
#         actions = targetSys.actions
#         states = targetSys.states
#         trans = targetSys.trans
#         initState = targetSys.init_state
#         acceptStates = targetSys.accept_states
#
#         sinkFlag = False
#         newTrans = []
#         sinkState = None
#         tranNumber = len(targetSys.trans)
#
#         for state in targetSys.states:
#             guardDict = {}
#             for action in actions:
#                 guardDict[action] = []
#             for tran in trans:
#                 if tran.source == state:
#                     for action in actions:
#                         if tran.action == action:
#                             for guard in tran.guards:
#                                 guardDict[action].append(guard)
#             for key, value in guardDict.items():
#                 if len(value) > 0:
#                     addGuards = complementIntervals(value)
#                 else:
#                     addGuards = [Guard('[0,+)')]
#                 if len(addGuards) > 0:
#                     sinkState = 'sink'
#                     sinkFlag = True
#                     for guard in addGuards:
#                         tempTran = OTATran(tranNumber, state, key, [guard], True, sinkState)
#                         tranNumber = tranNumber + 1
#                         newTrans.append(tempTran)
#         if sinkFlag:
#             states.append(sinkState)
#             for tran in newTrans:
#                 trans.append(tran)
#             for action in actions:
#                 guards = [Guard('[0,+)')]
#                 tempTran = OTATran(tranNumber, sinkState, action, guards, True, sinkState)
#                 tranNumber = tranNumber + 1
#                 trans.append(tempTran)
#         newOTA = OTA(actions, states, trans, initState, acceptStates, sinkState)
#         return newOTA
#
#
#     # 补全区间
#     def complementIntervals(guards):
#         partitions = []
#         key = []
#         floor_bn = BracketNum('0', Bracket.LC)
#         ceil_bn = BracketNum('+', Bracket.RO)
#         for guard in guards:
#             min_bn = guard.min_bn
#             max_bn = guard.max_bn
#             if min_bn not in key:
#                 key.append(min_bn)
#             if max_bn not in key:
#                 key.append(max_bn)
#         copyKey = copy.deepcopy(key)
#         for bn in copyKey:
#             complement = bn.complement()
#             if complement not in copyKey:
#                 copyKey.append(complement)
#         if floor_bn not in copyKey:
#             copyKey.insert(0, floor_bn)
#         if ceil_bn not in copyKey:
#             copyKey.append(ceil_bn)
#         copyKey.sort()
#         for index in range(len(copyKey)):
#             if index % 2 == 0:
#                 tempGuard = Guard(copyKey[index].getBN() + ',' + copyKey[index + 1].getBN())
#                 partitions.append(tempGuard)
#         for g in guards:
#             if g in partitions:
#                 partitions.remove(g)
#         return partitions
#
#
#     with open("./model_1.json", 'r') as f1:
#         system1 = json.load(f1)
#     with open("./model_2.json", 'r') as f2:
#         system2 = json.load(f2)
#     system1 = build_system(system1)
#     system2 = build_system(system2)
#
#     system1 = buildCanonicalOTA(system1)
#     system2 = buildCanonicalOTA(system2)
#
#     flag, ctx = equivalence(system1, system2, 10)
#     print(flag)
#     print([i.show() for i in ctx])
