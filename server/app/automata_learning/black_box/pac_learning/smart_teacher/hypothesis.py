import math
import app.automata_learning.black_box.pac_learning.smart_teacher.timeInterval as timeInterval


class OTA(object):
    def __init__(self, inputs, states, trans, initState, acceptStates, sinkState):
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates
        self.sinkState = sinkState

    def max_time_value(self):
        max_time_value = 0
        for tran in self.trans:
            for c in tran.guards:
                if c.max_value == '+':
                    temp_max_value = int(c.min_value)
                else:
                    temp_max_value = int(c.max_value)
                if max_time_value < temp_max_value:
                    max_time_value = temp_max_value
        return max_time_value

    def showDiscreteOTA(self):
        print("Input: " + str(self.inputs))
        print("States: " + str(self.states))
        print("InitState: {}".format(self.initState))
        print("AcceptStates: {}".format(self.acceptStates))
        print("SinkState: {}".format(self.sinkState))
        print("Transitions: ")
        for t in self.trans:
            print(' ' + str(t.tranId), 'S_' + str(t.source), str(t.input), str(t.timePoint), str(t.isReset), 'S_' + str(t.target), end="\n")

    def showOTA(self):
        print("Input: " + str(self.inputs))
        print("States: " + str(self.states))
        print("InitState: {}".format(self.initState))
        print("AcceptStates: {}".format(self.acceptStates))
        print("SinkState: {}".format(self.sinkState))
        print("Transitions: ")
        for t in self.trans:
            print("  " + str(t.tranId), 'S_' + str(t.source), str(t.input), t.showGuards(), str(t.isReset), 'S_' + str(t.target), end="\n")


class DiscreteOTATran(object):
    def __init__(self, tranId, source, input, timePoint, isReset, target):
        self.tranId = tranId
        self.source = source
        self.input = input
        self.timePoint = timePoint
        self.isReset = isReset
        self.target = target


class OTATran(object):
    def __init__(self, tranId, source, input, guards, isReset, target):
        self.tranId = tranId
        self.source = source
        self.input = input
        self.guards = guards
        self.isReset = isReset
        self.target = target

    def isPass(self, ltw):
        if ltw.input == self.input:
            for guard in self.guards:
                if guard.isInInterval(ltw.time):
                    return True
        else:
            return False
        return False

    def showGuards(self):
        temp = self.guards[0].show()
        for i in range(1, len(self.guards)):
            temp = temp + 'U' + self.guards[i].show()
        return temp


# build DiscreteOTA (DFA)
def structDiscreteOTA(table, inputs):
    inputs = inputs
    states = []
    initState = None
    sinkState = None
    acceptStates = []
    valueList_name_dict = {}
    for s, i in zip(table.S, range(0, len(table.S))):
        stateName = i
        valueList_name_dict[makeStr(s.valueList)] = stateName
        states.append(stateName)
        if not s.LRTWs:
            initState = stateName
        if s.valueList[0][0] == 1:
            acceptStates.append(stateName)
        if s.valueList[0][0] == -1:
            sinkState = stateName
    # deal with trans
    trans = []
    transNum = 0
    tableElements = [s for s in table.S] + [r for r in table.R]
    source = None
    target = None
    for r in tableElements:
        if not r.LRTWs:
            continue
        timedWords = [lrtw for lrtw in r.LRTWs]
        w = timedWords[:-1]
        a = timedWords[len(timedWords) - 1]
        for element in tableElements:
            if isEqual(w, element.LRTWs):
                source = valueList_name_dict[makeStr(element.valueList)]
            if isEqual(timedWords, element.LRTWs):
                target = valueList_name_dict[makeStr(element.valueList)]
        # 确认迁移input
        input = a.input
        timePoint = a.time
        isReset = a.isReset
        # 添加新迁移还是添加时间点
        needNewTran = True
        for tran in trans:
            if source == tran.source and input == tran.input and target == tran.target and isReset == tran.isReset:
                if timePoint == tran.timePoint:
                    needNewTran = False
                    break
        if needNewTran:
            tempTran = DiscreteOTATran(transNum, source, input, timePoint, isReset, target)
            trans.append(tempTran)
            transNum = transNum + 1
    discreteOTA = OTA(inputs, states, trans, initState, acceptStates, sinkState)
    return discreteOTA


# build hypothesis
def structHypothesisOTA(discreteOTA):
    inputs = discreteOTA.inputs
    states = discreteOTA.states
    initState = discreteOTA.initState
    acceptStates = discreteOTA.acceptStates
    sinkState = discreteOTA.sinkState
    # deal with trans
    trans = []
    for s in discreteOTA.states:
        s_dict = {}
        for key in discreteOTA.inputs:
            s_dict[key] = [0]
        for tran in discreteOTA.trans:
            if tran.source == s:
                for input in discreteOTA.inputs:
                    if tran.input == input:
                        tempList = s_dict[input]
                        if tran.timePoint not in tempList:
                            tempList.append(tran.timePoint)
                        s_dict[input] = tempList
        for value in s_dict.values():
            value.sort()
        for tran in discreteOTA.trans:
            if tran.source == s:
                timePoints = s_dict[tran.input]
                guards = []
                tw = tran.timePoint
                index = timePoints.index(tw)
                if index + 1 < len(timePoints):
                    if isInt(tw) and isInt(timePoints[index + 1]):
                        tempGuard = timeInterval.Guard("[" + str(tw) + "," + str(timePoints[index + 1]) + ")")
                    elif isInt(tw) and not isInt(timePoints[index + 1]):
                        tempGuard = timeInterval.Guard("[" + str(tw) + "," + str(math.modf(timePoints[index + 1])[1]) + "]")
                    elif not isInt(tw) and isInt(timePoints[index + 1]):
                        tempGuard = timeInterval.Guard("(" + str(math.modf(tw)[1]) + "," + str(timePoints[index + 1]) + ")")
                    else:
                        tempGuard = timeInterval.Guard("(" + str(math.modf(tw)[1]) + "," + str(math.modf(timePoints[index + 1])[1]) + "]")
                    guards.append(tempGuard)
                else:
                    if isInt(tw):
                        tempGuard = timeInterval.Guard("[" + str(tw) + ",+)")
                    else:
                        tempGuard = timeInterval.Guard("(" + str(math.modf(tw)[1]) + ",+)")
                    guards.append(tempGuard)
                for guard in guards:
                    tempTran = OTATran(tran.tranId, tran.source, tran.input, [guard], tran.isReset, tran.target)
                    trans.append(tempTran)
    hypothesisOTA = OTA(inputs, states, trans, initState, acceptStates, sinkState)
    return hypothesisOTA


# build simple hypothesis - merge guards
def structSimpleHypothesis(hypothesis):
    inputs = hypothesis.inputs
    states = hypothesis.states
    initState = hypothesis.initState
    acceptStates = hypothesis.acceptStates
    sinkState = hypothesis.sinkState
    trans = []
    tranNum = 0
    for s in hypothesis.states:
        for t in hypothesis.states:
            for input in inputs:
                for reset in [True, False]:
                    temp = []
                    for tran in hypothesis.trans:
                        if tran.source == s and tran.input == input and tran.target == t and tran.isReset == reset:
                            temp.append(tran)
                    if temp:
                        guards = []
                        for i in temp:
                            guards += i.guards
                        guards = simpleGuards(guards)
                        trans.append(OTATran(tranNum, s, input, guards, reset, t))
                        tranNum += 1
    return OTA(inputs, states, trans, initState, acceptStates, sinkState)


def removeSinkState(hypothesis):
    inputs = hypothesis.inputs
    states = hypothesis.states
    initState = hypothesis.initState
    acceptStates = hypothesis.acceptStates
    states.remove(hypothesis.sinkState)
    trans = []
    for tran in hypothesis.trans:
        if tran.source != hypothesis.sinkState and tran.target != hypothesis.sinkState:
            trans.append(tran)
    return OTA(inputs, states, trans, initState, acceptStates, hypothesis.sinkState)


# --------------------------------- auxiliary function ---------------------------------

# valueList改为str
def makeStr(valueList):
    temp = []
    for v in valueList:
        temp.append(v[0])
        temp += v[1]
    result = ','.join(str(i) for i in temp)
    return result


# Determine whether two LRTWs are the same
def isEqual(LRTWs1, LRTWs2):
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


# 判断是否整数
def isInt(num):
    x, y = math.modf(num)
    if x == 0:
        return True
    else:
        return False


# Sort guards
def sortGuards(guards):
    for i in range(len(guards) - 1):
        for j in range(len(guards) - i - 1):
            if guards[j].max_bn > guards[j + 1].max_bn:
                guards[j], guards[j + 1] = guards[j + 1], guards[j]
    return guards


# Merge guards
def simpleGuards(guards):
    if len(guards) == 1 or len(guards) == 0:
        return guards
    else:
        sortedGuards = sortGuards(guards)
        result = []
        tempGuard = sortedGuards[0]
        for i in range(1, len(sortedGuards)):
            firstRight = tempGuard.max_bn
            secondLeft = sortedGuards[i].min_bn
            if float(firstRight.value) == float(secondLeft.value):
                if (firstRight.bracket == 1 and secondLeft.bracket == 2) or (firstRight.bracket == 3 and secondLeft.bracket == 4):
                    left = tempGuard.guard.split(',')[0]
                    right = sortedGuards[i].guard.split(',')[1]
                    guard = timeInterval.Guard(left + ',' + right)
                    tempGuard = guard
                elif firstRight.bracket == 1 and secondLeft.bracket == 4:
                    result.append(tempGuard)
                    tempGuard = sortedGuards[i]
            else:
                result.append(tempGuard)
                tempGuard = sortedGuards[i]
        result.append(tempGuard)
        return result
