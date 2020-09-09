import math
from app.automata_learning.black_box.pac_learning.smart_teacher.teacher import TQs
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import TimedWord, DRTW_to_LRTW, LRTW_to_LTW, ResetTimedWord


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
            print([lrtw.show() for lrtw in s.LRTWs], s.valueList)
        print("new_R:" + str(len(self.R)))
        for r in self.R:
            print([lrtw.show() for lrtw in r.LRTWs], r.valueList)


class Element(object):
    def __init__(self, LRTWs, valueList):
        self.LRTWs = LRTWs
        self.valueList = valueList  # [value,[resetList]]


# init observation table
def initTable(inputs, targetSys, mqNum):
    table = ObsTable([], [], [])
    # deal with E
    table.E.append([])
    # deal with S
    element, mqNum = fillTableRow([], table, False, targetSys, mqNum)
    table.S.append(element)
    # deal with R
    table, mqNum = extendR(table.S[0], inputs, table, targetSys, mqNum)
    return table, mqNum


# Expand into a row according to s (根据s扩充成一行)
def fillTableRow(LRTWs, table, flag, targetSys, mqNum):
    # flag判断是否进入Error状态或查询是否有效 - flag为True表示已进入Error状态或无效
    if flag:
        valueList = []
        for e in table.E:
            value = [-1, [True for i in range(len(e))]]
            valueList.append(value)
        element = Element(LRTWs, valueList)
    else:
        valueList = []
        if isValid(LRTWs):
            for e in table.E:
                LTWs = LRTW_to_LTW(LRTWs) + e
                tempLRTWs, tempValue, mqNum = TQs(LTWs, targetSys, mqNum)
                if len(e) != 0:
                    resetList = getResetList(tempLRTWs, e)
                    value = [tempValue, resetList]
                else:
                    value = [tempValue, []]
                valueList.append(value)
        else:
            for e in table.E:
                value = [-1, [True for i in range(len(e))]]
                valueList.append(value)
        element = Element(LRTWs, valueList)
    return element, mqNum


# S adds s and table expands R area (S添加s,扩展R区域)
def extendR(s, inputs, table, targetSys, mqNum):
    tableTrace = [s.LRTWs for s in table.S] + [r.LRTWs for r in table.R]
    for input in inputs:
        LTWs = LRTW_to_LTW(s.LRTWs) + [TimedWord(input, 0)]
        LRTWs, tempValue, mqNum = TQs(LTWs, targetSys, mqNum)
        if tempValue == -1:
            element, mqNum = fillTableRow(LRTWs, table, True, targetSys, mqNum)
        else:
            element, mqNum = fillTableRow(LRTWs, table, False, targetSys, mqNum)
        if element.LRTWs not in tableTrace:
            table.R.append(element)
    return table, mqNum


# Determine whether table is prepared
def isPrepared(table):
    flagClosed, closedMove = isClosed(table)
    flagConsistent, consistentAdd = isConsistent(table)
    if flagClosed and flagConsistent:
        return True
    else:
        return False


# Determine whether it is closed
def isClosed(table):
    closedMove = []
    for r in table.R:
        flag = False
        for s in table.S:
            if r.valueList == s.valueList:
                flag = True
                break
        if not flag:
            if elementNotInList(r.valueList, closedMove):
                closedMove.append(r)
    if len(closedMove) > 0:
        return False, closedMove
    else:
        return True, closedMove


# make closed
def makeClosed(table, inputs, closedMove, targetSys, mqNum):
    # close_move将其从R移至S
    for r in closedMove:
        table.S.append(r)
        table.R.remove(r)
    # 处理R
    for i in closedMove:
        table, mqNum = extendR(i, inputs, table, targetSys, mqNum)
    return table, mqNum


# Determine whether it is consistent
def isConsistent(table):
    flag = True
    consistentAdd = []
    tableElement = [s for s in table.S] + [r for r in table.R]
    for i in range(0, len(tableElement) - 1):
        for j in range(i + 1, len(tableElement)):
            if tableElement[i].valueList == tableElement[j].valueList:
                tempElements1 = []
                tempElements2 = []
                for element in tableElement:
                    if isPrefix(element.LRTWs, tableElement[i].LRTWs):
                        tempElements1.append(element)
                    if isPrefix(element.LRTWs, tableElement[j].LRTWs):
                        tempElements2.append(element)
                for e1 in tempElements1:
                    for e2 in tempElements2:
                        newLRTWs1 = deletePrefix(e1.LRTWs, tableElement[i].LRTWs)
                        newLRTWs2 = deletePrefix(e2.LRTWs, tableElement[j].LRTWs)
                        if len(newLRTWs1) == len(newLRTWs2) == 1:
                            if newLRTWs1[0].input == newLRTWs2[0].input and newLRTWs1[0].time == newLRTWs2[0].time:
                                if newLRTWs1[0].isReset != newLRTWs2[0].isReset:
                                    flag = False
                                    temp = TimedWord(newLRTWs1[0].input, newLRTWs1[0].time)
                                    consistentAdd = [temp]
                                    return flag, consistentAdd
                                elif e1.valueList != e2.valueList:
                                    flag = False
                                    for k in range(0, len(e1.valueList)):
                                        if e1.valueList[k] != e2.valueList[k]:
                                            newIndex = k
                                            consistentAdd = [TimedWord(newLRTWs1[0].input, newLRTWs1[0].time)] + table.E[newIndex]
                                            return flag, consistentAdd
    return flag, consistentAdd


# make consistent
def makeConsistent(table, consistentAdd, targetSys, mqNum):
    table.E.append(consistentAdd)
    for i in range(0, len(table.S)):
        if isValid(table.S[i].LRTWs):
            LTWs = LRTW_to_LTW(table.S[i].LRTWs) + consistentAdd
            LRTWs, tempValue, mqNum = TQs(LTWs, targetSys, mqNum)
            value = [tempValue, getResetList(LRTWs, consistentAdd)]
            table.S[i].valueList.append(value)
        else:
            value = [-1, [True for m in range(len(consistentAdd))]]
            table.S[i].valueList.append(value)
    for j in range(0, len(table.R)):
        if isValid(table.R[j].LRTWs):
            LTWs = LRTW_to_LTW(table.R[j].LRTWs) + consistentAdd
            LRTWs, tempValue, mqNum = TQs(LTWs, targetSys, mqNum)
            value = [tempValue, getResetList(LRTWs, consistentAdd)]
            table.R[j].valueList.append(value)
        else:
            value = [-1, [True for n in range(len(consistentAdd))]]
            table.R[j].valueList.append(value)
    return table, mqNum


# deal with ctx (添加反例的所有前缀集)
def dealCtx(table, ctx, targetSys, mqNum):
    newCtx = DRTW_to_LRTW(ctx)
    newCtx = normalize(newCtx)
    pref = prefixes(newCtx)
    LRTWsList = [s.LRTWs for s in table.S] + [r.LRTWs for r in table.R]
    for LRTWs in pref:
        needAdd = True
        for tempLRTWs in LRTWsList:
            if LRTWs == tempLRTWs:
                needAdd = False
                break
        if needAdd:
            tempElement, mqNum = fillTableRow(LRTWs, table, False, targetSys, mqNum)
            table.R.append(tempElement)
    return table, mqNum


# --------------------------------- 辅助函数 ---------------------------------

# time normalization
def normalize(trace):
    newTrace = []
    for i in trace:
        if math.modf(float(i.time))[0] == 0.0:
            time = math.modf(float(i.time))[1]
        else:
            time = math.modf(float(i.time))[1] + 0.5
        newTrace.append(ResetTimedWord(i.input, time, i.isReset))
    return newTrace


# determine whether LRTWs are valid （LRTWs是否有效）
def isValid(LRTWs):
    if not LRTWs:
        return True
    else:
        nowTime = 0
        for lrtw in LRTWs:
            if lrtw.time >= nowTime:
                if lrtw.isReset:
                    nowTime = 0
                else:
                    nowTime = lrtw.time
            else:
                return False
        return True


# get corresponding resetList in e (获得E中对应的resetList)
def getResetList(LRTWs, e):
    restList = []
    tempLRTWs = LRTWs[-len(e):]
    for i in tempLRTWs:
        restList.append(i.isReset)
    return restList


# 判断Element的List中是否已有相同valueList的元素，若存在返回False，不存在则返回True
def elementNotInList(valueList, elementList):
    if len(elementList) == 0:
        return True
    else:
        flag = True
        for i in range(len(elementList)):
            if valueList == elementList[i].valueList:
                flag = False
                break
        if flag:
            return True
        else:
            return False


# determine whether pre is the prefix of tws （判断pre是否是tws的前缀）
def isPrefix(tws, pre):
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
def deletePrefix(tws, pre):
    if len(pre) == 0:
        return tws
    else:
        new_tws = tws[len(pre):]
        return new_tws


# prefix set of tws （tws前缀集）
def prefixes(tws):
    newPrefixes = []
    for i in range(1, len(tws) + 1):
        temp_tws = tws[:i]
        newPrefixes.append(temp_tws)
    return newPrefixes
