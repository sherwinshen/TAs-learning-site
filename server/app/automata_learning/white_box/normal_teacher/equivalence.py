# OTA equivalence

from app.automata_learning.white_box.normal_teacher.ota import Timedword, ResetTimedword, State
from app.automata_learning.white_box.normal_teacher.interval import Constraint
from app.automata_learning.white_box.normal_teacher.otatable import Element
import copy


def get_regions(max_time_value):
    """
        Partition R into a finite collection of one-dimensional regions depending on the appearing max time value.
    """
    regions = []
    bound = 2 * max_time_value + 1
    for i in range(0, bound + 1):
        if i % 2 == 0:
            temp = i // 2
            r = Constraint('[' + str(temp) + ',' + str(temp) + ']')
            regions.append(r)
        else:
            temp = (i - 1) // 2
            if temp < max_time_value:
                r = Constraint('(' + str(temp) + ',' + str(temp + 1) + ')')
                regions.append(r)
            else:
                r = Constraint('(' + str(temp) + ',' + '+' + ')')
                regions.append(r)
    return regions


def minnum_in_region(constraint):
    """
        return the minimal number in the region. For [5,9], return 5; for (4,10), return 4.1 .
    """
    if constraint.closed_min:
        return int(constraint.min_value)
    else:
        return float(constraint.min_value + '.1')


def state_to_letter(state, max_time_value):
    integer = int(state.v)
    fraction = state.get_fraction()
    if fraction > 0.0:
        if integer < max_time_value:
            region = Constraint('(' + str(integer) + ',' + str(integer + 1) + ')')
        else:
            region = Constraint('(' + str(integer) + ',' + '+' + ')')
    else:
        region = Constraint('[' + str(integer) + ',' + str(integer) + ']')
    return Letter(state.location, region)


class Letter(object):
    """
        The definition of letter. A letter is a pair (location, region).
        "location" for indicating the location
        "constraint" for the region
    """

    def __init__(self, location, constraint):
        self.location = location
        if isinstance(constraint, str):
            constraint = Constraint(constraint)
        self.constraint = constraint

    def __eq__(self, letter):
        if self.location == letter.location and self.constraint == letter.constraint:
            return True
        else:
            return False

    def __hash__(self):
        return hash(("LETTER", self.location, self.constraint))

    def to_state(self, i):
        """
            Transform a letter to a state.
        """
        location = self.location
        v = 0
        if self.constraint.isPoint():
            v = self.constraint.min_value + '.0'
        else:
            v = self.constraint.min_value + '.' + str(i + 1)
        return State(location, v)

    def show(self):
        return self.location.get_flagname() + ',' + self.constraint.show()

    def __str__(self):
        return self.show()

    def __repr__(self):
        return self.show()


class Letterword(object):
    """
        The definition of letterword lw for the letterword list itself prelw for the pre letterword object.
    """

    def __init__(self, lw, prelw=None, action="DELAY"):
        self.lw = lw or []
        self.prelw = prelw
        self.action = action

    def __eq__(self, letterword):
        if self.lw == letterword.lw:
            return True
        else:
            return False

    def __hash__(self):
        return hash(("LETTERWORD", self.lw, self.prelw, self.action))

    def show(self):
        return self.lw  # , self.action

    def __str__(self):
        return self.show()

    def __repr__(self):
        return self.show()


class ABConfiguration(object):
    """
        The definition of A/B-configuration.
    """

    def __init__(self, Ac, Bstate):
        self.Aconfig = copy.deepcopy(Ac)
        self.Bstate = copy.deepcopy(Bstate)

    def configuration_to_letterword(self, max_time_value):
        """
            Transform an A/B-configuration to a letterword.
        """
        allstates = [state for state in self.Aconfig]
        allstates.append(self.Bstate)
        allstates.sort(key=lambda x: x.get_fraction())
        temp_letterword = []
        current_fraction = -1
        for state in allstates:
            if state.get_fraction() == current_fraction:
                temp_letterword[len(temp_letterword) - 1].add(state_to_letter(state, max_time_value))
            else:
                new_letters = set()
                new_letters.add(state_to_letter(state, max_time_value))
                temp_letterword.append(new_letters)
                current_fraction = state.get_fraction()
        return temp_letterword


def letterword_dominated(lw1, lw2):
    """
        To determine whether letterword lw1 is dominated by letterword lw2 (lw1 <= lw2)
    """
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


def immediate_letter_asucc(letter, action, ota):
    location_name = letter.location.name
    region = letter.constraint
    for tran in ota.trans:
        if tran.source == location_name and action == tran.label and region.issubset(tran.constraints[0]):
            succ_location_name = tran.target
            succ_location = ota.findlocationbyname(succ_location_name)
            if tran.reset:
                region = Constraint("[0,0]")
            if succ_location is not None:
                return Letter(succ_location, region)
    return None


def immediate_asucc(letterword, A, B):
    """
        Perform the immediate 'a' action in case of L(B) is a subset of L(A).
    """
    results = []
    if len(letterword.lw) == 1:
        letter1, letter2 = list(letterword.lw[0])
        for action in B.sigma:
            if letter1.location.flag == A.locations[0].flag:
                B_letter = immediate_letter_asucc(letter2, action, B)
                A_letter = immediate_letter_asucc(letter1, action, A)
            else:
                B_letter = immediate_letter_asucc(letter1, action, B)
                A_letter = immediate_letter_asucc(letter2, action, A)
            if B_letter is not None and A_letter is not None:
                B_ispoint = B_letter.constraint.isPoint()
                A_ispoint = A_letter.constraint.isPoint()
                if A_ispoint and B_ispoint:
                    w = [{A_letter, B_letter}]
                elif A_ispoint and B_ispoint == False:
                    w = [{A_letter}, {B_letter}]
                elif A_ispoint == False and B_ispoint:
                    w = [{B_letter}, {A_letter}]
                else:
                    w = [{A_letter, B_letter}]
                current_lw = Letterword(w, letterword, action)
                if current_lw not in results:
                    results.append(current_lw)
    elif len(letterword.lw) == 2:
        letter1, letter2 = list(letterword.lw[0])[0], list(letterword.lw[1])[0]
        for action in B.sigma:
            if letter1.location.flag == A.locations[0].flag:
                B_letter = immediate_letter_asucc(letter2, action, B)
                A_letter = immediate_letter_asucc(letter1, action, A)
                if B_letter is not None and A_letter is not None:
                    B_ispoint = B_letter.constraint.isPoint()
                    A_ispoint = A_letter.constraint.isPoint()
                    if A_ispoint and B_ispoint:
                        w = [{A_letter, B_letter}]
                    elif A_ispoint and B_ispoint == False:
                        w = [{A_letter}, {B_letter}]
                    elif A_ispoint == False and B_ispoint:
                        w = [{B_letter}, {A_letter}]
                    else:
                        w = [{A_letter}, {B_letter}]
                    current_lw = Letterword(w, letterword, action)
                    if current_lw not in results:
                        results.append(current_lw)
            else:
                B_letter = immediate_letter_asucc(letter1, action, B)
                A_letter = immediate_letter_asucc(letter2, action, A)
                if B_letter is not None and A_letter is not None:
                    B_ispoint = B_letter.constraint.isPoint()
                    A_ispoint = A_letter.constraint.isPoint()
                    if A_ispoint and B_ispoint:
                        w = [{A_letter, B_letter}]
                    elif A_ispoint and B_ispoint == False:
                        w = [{A_letter}, {B_letter}]
                    elif A_ispoint == False and B_ispoint:
                        w = [{B_letter}, {A_letter}]
                    else:
                        w = [{B_letter}, {A_letter}]
                    current_lw = Letterword(w, letterword, action)
                    if current_lw not in results:
                        results.append(current_lw)
    else:
        raise NotImplementedError()
    return results


# Transform a letterword to A/B-configuration.
def letterword_to_configuration(letterword, flag):
    lwlen = len(letterword)
    G = []
    Bstate = None
    for letters, i in zip(letterword, range(lwlen)):
        for letter in list(letters):
            state = letter.to_state(i)
            if state.location.flag == flag:
                G.append(state)
            else:
                Bstate = state
    return ABConfiguration(G, Bstate)


# Returns r_0^1 for r_0, r_1 for r_0^1, etc.
def next_region(region, max_time_value):
    if region.isPoint():
        if int(region.max_value) == max_time_value:
            return Constraint('(' + region.max_value + ',' + '+' + ')')
        else:
            return Constraint('(' + region.max_value + ',' + str(int(region.max_value) + 1) + ')')
    else:
        if region.max_value == '+':
            return Constraint('(' + region.min_value + ',' + '+' + ')')
        else:
            return Constraint('[' + region.max_value + ',' + region.max_value + ']')


# Compute the Succ of letterword.
def compute_wsucc(letterword, max_time_value, A, B):
    # First compute all possible time delay
    results = []
    last_region = Constraint('(' + str(max_time_value) + ',' + '+' + ')')
    if len(letterword.lw) == 1:
        result = letterword.lw[0]
        while any(letter.constraint != last_region for letter in result):
            results.append(Letterword([result], letterword))
            new_result = set()
            for letter in result:
                new_letter = Letter(letter.location, next_region(letter.constraint, max_time_value))
                new_result.add(new_letter)
            result = new_result
        current_lw = Letterword([result], letterword)
        if current_lw not in results:
            results.append(current_lw)
    elif len(letterword.lw) == 2:
        if len(letterword.lw[0]) != 1 and len(letterword.lw[1]) != 1:
            raise NotImplementedError()
        result = letterword.lw
        while list(result[0])[0].constraint != last_region or list(result[1])[0].constraint != last_region:
            results.append(Letterword(result, letterword))
            new_result = []
            l1, l2 = list(result[0])[0], list(result[1])[0]
            if l1.constraint.isPoint():
                new_result.append({Letter(l1.location, next_region(l1.constraint, max_time_value))})
                new_result.append({l2})
            else:
                new_result.append({Letter(l2.location, next_region(l2.constraint, max_time_value))})
                new_result.append({l1})
            result = new_result
        current_lw = Letterword(result, letterword)
        if current_lw not in results:
            results.append(current_lw)
            new_result = Letterword([current_lw.lw[1], current_lw.lw[0]], letterword)
            if new_result not in results:
                results.append(new_result)
    else:
        raise NotImplementedError()

    # Next, perform the immediate 'a' transition
    next = []
    for letterword in results:
        next_ws = immediate_asucc(letterword, A, B)
        for next_w in next_ws:
            if next_w not in next:
                next.append(next_w)
    return results, next


def is_bad_letterword(letterword, A, B):
    """
        Determine whether a letterword is bad in case of L(B) is a subset of L(A)
    """
    if len(letterword) == 1:
        letter1, letter2 = list(letterword[0])
    elif len(letterword) == 2:
        letter1, letter2 = list(letterword[0])[0], list(letterword[1])[0]
    else:
        raise NotImplementedError()
    location1 = letter1.location
    location2 = letter2.location
    if location1.flag == B.locations[0].flag:
        if location1.name in B.accept_names:
            value1 = 1
        elif location1.name == B.sink_name:
            value1 = -1
        else:
            value1 = 0
        if location2.name in A.accept_names:
            value2 = 1
        elif location2.name == A.sink_name:
            value2 = -1
        else:
            value2 = 0
        return value1 != value2
        # if location1.name in B.accept_names and location2.name not in A.accept_names:
        #     return True
        # else:
        #     return False
    else:
        if location1.name in A.accept_names:
            value1 = 1
        elif location1.name == A.sink_name:
            value1 = -1
        else:
            value1 = 0
        if location2.name in B.accept_names:
            value2 = 1
        elif location2.name == B.sink_name:
            value2 = -1
        else:
            value2 = 0
        return value1 != value2
        # if location2.name in B.accept_names and location1.name not in A.accept_names:
        #     return True
        # else:
        #     return False


def explored_dominated(explored, w):
    if len(explored) == 0:
        return False
    for v in explored:
        if letterword_dominated(v, w):
            return True
    return False


# Determine whether L(B) is a subset of L(A).
def ota_inclusion(max_time_value, A, B):
    A_init_name = A.initstate_name
    B_init_name = B.initstate_name
    L1 = A.findlocationbyname(A_init_name)
    Q1 = B.findlocationbyname(B_init_name)
    w0 = [{Letter(L1, "[0,0]"), Letter(Q1, "[0,0]")}]
    to_explore = [Letterword(w0, None, '')]
    explored = []
    while True:
        if len(to_explore) == 0:
            return True, None
        w = to_explore[0]
        del to_explore[0]
        if is_bad_letterword(w.lw, A, B):
            return False, w
        while explored_dominated(explored, w):
            if len(to_explore) == 0:
                return True, None
            w = to_explore[0]
            del to_explore[0]
            if is_bad_letterword(w.lw, A, B):
                return False, w
        wsucc, next = compute_wsucc(w, max_time_value, A, B)
        for nw in next:
            if nw not in to_explore:
                to_explore.append(nw)
        if w not in explored:
            explored.append(w)


# When get a letterword, find the path ends in the letterword.
def findpath(letterword):
    current_lw = letterword
    path = [current_lw]
    while current_lw.prelw is not None:
        path.insert(0, current_lw.prelw)
        current_lw = current_lw.prelw
    return path


# Given a path, return the delay timedword.
def findDelayTimedwords(letterword, flag, sigma):
    path = findpath(letterword)
    delay_timedwords = []
    current_clock_valuation = 0
    delay_time = 0
    for letterword in path:
        if len(letterword.lw) == 1:
            letter1, letter2 = list(letterword.lw[0])
        elif len(letterword.lw) == 2:
            letter1, letter2 = list(letterword.lw[0])[0], list(letterword.lw[1])[0]
        else:
            raise NotImplementedError()
        if letter1.location.flag == flag:
            temp_region = letter1.constraint
        else:
            temp_region = letter2.constraint
        if letterword.action == "DELAY":
            delay_time = minnum_in_region(temp_region) - current_clock_valuation
            current_clock_valuation = minnum_in_region(temp_region)
        elif letterword.action in sigma:
            new_timedword = Timedword(letterword.action, delay_time)
            delay_timedwords.append(new_timedword)
            current_clock_valuation = minnum_in_region(temp_region)
        elif letterword.action == '':
            pass
        else:
            raise NotImplementedError()
    return delay_timedwords


def dTWs_to_dRTWs(letterword, flag, ota):
    tws = findDelayTimedwords(letterword, flag, ota.sigma)
    dRTWs = []
    if len(tws) == 0:
        return []
    else:
        current_location = ota.initstate_name
        current_clock_valuation = 0
        reset = True
        for tw in tws:
            if not reset:
                current_clock_valuation = current_clock_valuation + tw.time
            else:
                current_clock_valuation = tw.time
            for tran in ota.trans:
                if tran.source == current_location and tran.is_pass(Timedword(tw.action, current_clock_valuation)):
                    dRTWs.append(ResetTimedword(tw.action, tw.time, tran.reset))
                    current_location = tran.target
                    reset = tran.reset
                    break
    return dRTWs


def equivalence_query(max_time_value, teacher, hypothesis):
    """
        Smart teacher
    """
    flag_pos, w_pos = ota_inclusion(max_time_value, hypothesis, teacher)
    if not flag_pos:
        drtw_pos = dTWs_to_dRTWs(w_pos, 's', teacher)
        ctx_pos = Element(drtw_pos, [])
        return False, ctx_pos
    else:
        flag_neg, w_neg = ota_inclusion(max_time_value, teacher, hypothesis)
        if not flag_neg:
            drtw_neg = dTWs_to_dRTWs(w_neg, 's', teacher)
            ctx_neg = Element(drtw_neg, [])
            return False, ctx_neg
        else:
            return True, None


def equivalence_query_normal(max_time_value, teacher, hypothesis, prev_ctx=None):
    """
        Normal teacher
    """
    if prev_ctx is not None:
        for ctx in prev_ctx:
            teacher_res = teacher.is_accepted_delay(ctx.tws)
            hypothesis_res = hypothesis.is_accepted_delay(ctx.tws)
            if teacher_res != hypothesis_res and hypothesis_res != -2:
                return False, ctx

    flag_pos, w_pos = ota_inclusion(max_time_value, hypothesis, teacher)
    if not flag_pos:
        dtw_pos = findDelayTimedwords(w_pos, 's', teacher.sigma)
        ctx_pos = Element(dtw_pos, [])
        return False, ctx_pos
    else:
        flag_neg, w_neg = ota_inclusion(max_time_value, teacher, hypothesis)
        if not flag_neg:
            dtw_neg = findDelayTimedwords(w_neg, 's', teacher.sigma)
            ctx_neg = Element(dtw_neg, [])
            return False, ctx_neg
        else:
            return True, None
