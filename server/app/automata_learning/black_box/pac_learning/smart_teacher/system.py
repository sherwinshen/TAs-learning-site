import app.automata_learning.black_box.pac_learning.smart_teacher.timeInterval as timeInterval
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import ResetTimedWord, TimedWord


class System(object):
    def __init__(self, inputs, states, trans, initState, acceptStates):
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates


class SysTran(object):
    def __init__(self, tranId, source, input, guards, isReset, target):
        self.tranId = tranId
        self.source = source
        self.input = input
        self.guards = guards
        self.isReset = isReset
        self.target = target

    def isPass(self, tw):
        if tw.input == self.input:
            for guard in self.guards:
                if guard.isInInterval(tw.time):
                    return True
        return False

    def showGuards(self):
        temp = self.guards[0].show()
        for i in range(1, len(self.guards)):
            temp = temp + 'U' + self.guards[i].show()
        return temp


# build target system
def buildSystem(model):
    inputs = model["inputs"]
    states = model["states"]
    trans = model["trans"]
    initState = model["initState"]
    acceptStates = model["acceptStates"]
    # trans
    transSet = []
    for tran in trans:
        tranId = str(tran)
        source = trans[tran][0]
        target = trans[tran][4]
        input = trans[tran][1]
        # reset signal
        resetTemp = trans[tran][3]
        isReset = False
        if resetTemp == "r":
            isReset = True
        # time guard
        intervalsStr = trans[tran][2]
        intervalsList = intervalsStr.split('U')
        guards = []
        for guard in intervalsList:
            newGuard = timeInterval.Guard(guard.strip())
            guards.append(newGuard)
        systemTran = SysTran(tranId, source, input, guards, isReset, target)
        transSet += [systemTran]
    transSet.sort(key=lambda x: x.tranId)
    system = System(inputs, states, transSet, initState, acceptStates)
    return system


# input -> DTWs，output -> DRTWs and value - for delay-timed test
def systemTest(DTWs, targetSys):
    DRTWs = []
    value = []
    nowTime = 0
    curState = targetSys.initState
    for dtw in DTWs:
        if curState == "sink":
            DRTWs.append(ResetTimedWord(dtw.input, dtw.time, True))
            value = -1
        else:
            time = dtw.time + nowTime
            newLTW = TimedWord(dtw.input, time)
            flag = False
            for tran in targetSys.trans:
                if tran.source == curState and tran.isPass(newLTW):
                    flag = True
                    curState = tran.target
                    if tran.isReset:
                        nowTime = 0
                        isReset = True
                    else:
                        nowTime = time
                        isReset = False
                    DRTWs.append(ResetTimedWord(dtw.input, dtw.time, isReset))
                    break
            if not flag:
                DRTWs.append(ResetTimedWord(dtw.input, dtw.time, True))
                value = -1
                curState = "sink"
    if curState in targetSys.acceptStates:
        value = 1
    elif curState != 'sink':
        value = 0
    return DRTWs, value


# input -> DTW(single)，output -> curState and value - for logical-timed test
def systemOutput(DTW, nowTime, curState, targetSys):
    value = None
    resetFlag = False
    tranFlag = False  # tranFlag为true表示有这样的迁移
    if DTW is None:
        if curState in targetSys.acceptStates:
            value = 1
        else:
            value = 0
    else:
        LTW = TimedWord(DTW.input, DTW.time + nowTime)
        for tran in targetSys.trans:
            if tran.source == curState and tran.isPass(LTW):
                tranFlag = True
                curState = tran.target
                if tran.isReset:
                    resetFlag = True
                break
        if not tranFlag:
            value = -1
            curState = 'sink'
            resetFlag = True
        if curState in targetSys.acceptStates:
            value = 1
        elif curState != 'sink':
            value = 0
    return curState, value, resetFlag
