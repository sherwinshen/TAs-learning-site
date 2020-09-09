from app.automata_learning.black_box.pac_learning.smart_teacher.system import systemOutput, systemTest
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import TimedWord, ResetTimedWord


# logical-timed test -  input->LTWs，output->LRTWs，invalid or sink 则终止，并补全LRTWs
def testLTWs(LTWs, targetSys):
    if not LTWs:
        if targetSys.initState in targetSys.acceptStates:
            value = 1
        else:
            value = 0
        return [], value
    else:
        LRTWs = []
        value = None
        nowTime = 0
        curState = targetSys.initState
        for ltw in LTWs:
            if ltw.time < nowTime:
                value = -1
                LRTWs.append(ResetTimedWord(ltw.input, ltw.time, True))
                break
            else:
                DTW = TimedWord(ltw.input, ltw.time - nowTime)
                curState, value, resetFlag = systemOutput(DTW, nowTime, curState, targetSys)
                if resetFlag:
                    LRTWs.append(ResetTimedWord(ltw.input, ltw.time, True))
                    nowTime = 0
                else:
                    LRTWs.append(ResetTimedWord(ltw.input, ltw.time, False))
                    nowTime = ltw.time
                if value == -1:
                    break
        # 补全
        lenDiff = len(LTWs) - len(LRTWs)
        if lenDiff != 0:
            temp = LTWs[len(LRTWs):]
            for i in temp:
                LRTWs.append(ResetTimedWord(i.input, i.time, True))
        return LRTWs, value


# delay-timed test - input->DTWs，output->DRTWs
def testDTWs(DTWs, targetSys):
    DRTWs, value = systemTest(DTWs, targetSys)
    return DRTWs, value
