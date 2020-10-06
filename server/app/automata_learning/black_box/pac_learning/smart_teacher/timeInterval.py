from enum import IntEnum


class Bracket(IntEnum):
    RO = 1
    LC = 2
    RC = 3
    LO = 4


class BracketNum:
    def __init__(self, value, bracket):
        self.value = value
        self.bracket = bracket

    def __eq__(self, bn):
        if self.value == '+' and bn.value == '+':
            return True
        elif self.value == '+' and bn.value != '+':
            return False
        elif self.value != '+' and bn.value == '+':
            return False
        elif float(self.value) == float(bn.value) and self.bracket == bn.bracket:
            return True
        else:
            return False

    def complement(self):
        if self.value == '+':
            return BracketNum('+', Bracket.RO)  # ceil
        if float(self.value) == 0 and self.bracket == Bracket.LC:
            return BracketNum('0', Bracket.LC)  # floor
        tempValue = self.value
        tempBracket = None
        if self.bracket == Bracket.LC:
            tempBracket = Bracket.RO
        if self.bracket == Bracket.RC:
            tempBracket = Bracket.LO
        if self.bracket == Bracket.LO:
            tempBracket = Bracket.RC
        if self.bracket == Bracket.RO:
            tempBracket = Bracket.LC
        return BracketNum(tempValue, tempBracket)

    def __lt__(self, bn):
        if self.value == '+':
            return False
        elif bn.value == '+':
            return True
        elif float(self.value) > float(bn.value):
            return False
        elif float(self.value) < float(bn.value):
            return True
        else:
            if self.bracket < bn.bracket:
                return True
            else:
                return False

    def __gt__(self, bn):
        if self.value == '+':
            if bn.value == '+':
                return False
            else:
                return True
        if bn.value == '+':
            return False
        if float(self.value) > float(bn.value):
            return True
        elif float(self.value) < float(bn.value):
            return False
        else:
            if self.bracket > bn.bracket:
                return True
            else:
                return False

    def __ge__(self, bn):
        return not self.__lt__(bn)

    def __le__(self, bn):
        return not self.__gt__(bn)

    def getBN(self):
        if self.bracket == Bracket.LC:
            return '[' + self.value
        if self.bracket == Bracket.LO:
            return '(' + self.value
        if self.bracket == Bracket.RC:
            return self.value + ']'
        if self.bracket == Bracket.RO:
            return self.value + ')'


class Guard:
    def __init__(self, guard):
        self.guard = guard
        self.__build()

    def __build(self):
        min_type, max_type = self.guard.split(',')

        # 处理左边
        if min_type[0] == '[':
            self.closed_min = True
            min_bn_bracket = Bracket.LC
        else:
            self.closed_min = False
            min_bn_bracket = Bracket.LO
        self.min_value = min_type[1:].strip()
        self.min_bn = BracketNum(self.min_value, min_bn_bracket)

        # 处理右边
        if max_type[-1] == ']':
            self.closed_max = True
            max_bn_bracket = Bracket.RC
        else:
            self.closed_max = False
            max_bn_bracket = Bracket.RO
        self.max_value = max_type[:-1].strip()
        self.max_bn = BracketNum(self.max_value, max_bn_bracket)

    def __eq__(self, guard):
        if self.min_bn == guard.min_bn and self.max_bn == guard.max_bn:
            return True
        else:
            return False

    def get_min(self):
        return float(self.min_value)

    def get_closed_min(self):
        return self.closed_min

    def get_max(self):
        if self.max_value == '+':
            return float("inf")
        else:
            return float(self.max_value)

    def get_closed_max(self):
        return self.closed_max

    def __hash__(self):
        return hash(("CONSTRAINT", self.get_min(), self.closed_min, self.get_max(), self.closed_max))

    def is_point(self):
        if self.min_value == '+' or self.max_value == '+':
            return False
        if self.get_min() == self.get_max() and self.closed_min and self.closed_max:
            return True
        else:
            return False

    def is_subset(self, c2):
        min_bn1 = self.min_bn
        max_bn1 = self.max_bn
        min_bn2 = c2.min_bn
        max_bn2 = c2.max_bn
        if min_bn1 >= min_bn2 and max_bn1 <= max_bn2:
            return True
        else:
            return False

    def is_in_interval(self, num):
        if num < self.get_min():
            return False
        elif num == self.get_min():
            if self.closed_min:
                return True
            else:
                return False
        elif self.get_min() < num < self.get_max():
            return True
        elif num == self.get_max():
            if self.closed_max:
                return True
            else:
                return False
        else:
            return False

    def is_empty(self):
        if self.max_bn < self.min_bn:
            return True
        else:
            return False

    def show(self):
        return self.guard


# Merge guards
def simple_guards(guards):
    if len(guards) == 1 or len(guards) == 0:
        return guards
    else:
        sorted_guards = sort_guards(guards)
        result = []
        temp_guard = sorted_guards[0]
        for i in range(1, len(sorted_guards)):
            first_right = temp_guard.max_bn
            second_left = sorted_guards[i].min_bn
            if float(first_right.value) == float(second_left.value):
                if (first_right.bracket == 1 and second_left.bracket == 2) or (first_right.bracket == 3 and second_left.bracket == 4):
                    left = temp_guard.guard.split(',')[0]
                    right = sorted_guards[i].guard.split(',')[1]
                    guard = Guard(left + ',' + right)
                    temp_guard = guard
                elif first_right.bracket == 1 and second_left.bracket == 4:
                    result.append(temp_guard)
                    temp_guard = sorted_guards[i]
            else:
                result.append(temp_guard)
                temp_guard = sorted_guards[i]
        result.append(temp_guard)
        return result


# Sort guards
def sort_guards(guards):
    for i in range(len(guards) - 1):
        for j in range(len(guards) - i - 1):
            if guards[j].max_bn > guards[j + 1].max_bn:
                guards[j], guards[j + 1] = guards[j + 1], guards[j]
    return guards
