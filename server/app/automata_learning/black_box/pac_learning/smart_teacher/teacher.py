import math
import copy
from app.automata_learning.black_box.pac_learning.smart_teacher.tester import testLTWs, testDTWs
from app.automata_learning.black_box.pac_learning.smart_teacher.sampling import sampleGenerationMain, sampleGenerationMain_old
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import TimedWord, ResetTimedWord, DRTW_to_LRTW, LRTW_to_LTW


# membership query
def TQs(LTWs, targetSys, mqNum):
    mqNum += 1
    LRTWs, value = testLTWs(LTWs, targetSys)
    return LRTWs, value, mqNum


# new method - equivalence query - ctx is DRTWs
def EQs_new(hypothesis, upperGuard, epsilon, delta, stateNum, targetSys, eqNum, testNum):
    testSum = int((math.log(1 / delta) + math.log(2) * (eqNum + 1)) / epsilon)
    for length in range(1, math.ceil(stateNum * 1.5)):
        ctx = None
        i = 0
        while i < testSum // stateNum:
            i += 1
            testNum += 1
            # Generate sample (delay-timed word) according to fixed distribution
            sample = sampleGenerationMain(targetSys, upperGuard, length)

            # Compare the results
            if isCounterexample(targetSys, hypothesis, sample):
                if ctx is None or sample < ctx:
                    ctx = sample

        if ctx is not None:
            ctx = minimizeCounterexample(targetSys, hypothesis, ctx)
            realDRTWs, realValue = testDTWs(ctx, targetSys)
            return False, realDRTWs, testNum
    return True, None, testNum


# old method - equivalence query - ctx is DRTWs
def EQs_old(hypothesis, upperGuard, epsilon, delta, stateNum, targetSys, eqNum, testNum):
    flag = True  # True -> equivalence，False -> not equivalence
    ctx = []
    testSum = (math.log(1 / delta) + math.log(2) * (eqNum + 1)) / epsilon
    i = 1
    toSinkCount = 0
    while i <= testSum:
        sample = sampleGenerationMain_old(hypothesis.inputs, upperGuard, stateNum)  # sample is DTWs
        DRTWs, value = getHpyDTWsValue(sample, hypothesis)
        realDRTWs, realValue = testDTWs(sample, targetSys)
        i += 1
        testNum += 1
        # compare result
        if realValue == -1:
            toSinkCount += 1
            if realValue == -1 and value == 1:
                flag = False
                ctx = realDRTWs
                break
            else:
                i -= 1
                continue
        elif (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
            flag = False
            ctx = realDRTWs
            break
    # print('# test to sink State: ', toSinkCount, ' testNum of current EQ: ', i)
    return flag, ctx, testNum


# --------------------------------- auxiliary function ---------------------------------

#  Compare evaluation of teacher and hypothesis on the given sample
def isCounterexample(teacher, hypothesis, sample):
    # Evaluation of sample on the teacher, should be -1, 0, 1
    realDRTWs, realValue = testDTWs(sample, teacher)
    # Evaluation of sample on the hypothesis, should be -1, 0, 1
    DRTWs, value = getHpyDTWsValue(sample, hypothesis)
    if realValue == -1:
        if realValue == -1 and value == 1:
            return True
        else:
            return False
    elif (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
        return True
    else:
        return False


# Hypothesis - input->DTWs，output->DRTWs+value
def getHpyDTWsValue(sample, hypothesis):
    DRTWs = []
    nowTime = 0
    curState = hypothesis.initState
    for dtw in sample:
        if curState == hypothesis.sinkState:
            DRTWs.append(ResetTimedWord(dtw.input, dtw.time, True))
        else:
            time = dtw.time + nowTime
            newLTW = TimedWord(dtw.input, time)
            for tran in hypothesis.trans:
                if tran.source == curState and tran.isPass(newLTW):
                    curState = tran.target
                    if tran.isReset:
                        nowTime = 0
                        isReset = True
                    else:
                        nowTime = time
                        isReset = False
                    DRTWs.append(ResetTimedWord(dtw.input, dtw.time, isReset))
                    break
    if curState in hypothesis.acceptStates:
        value = 1
    elif curState == hypothesis.sinkState:
        value = -1
    else:
        value = 0
    return DRTWs, value


# Minimize a given delay-timed word
def minimizeCounterexample(teacher, hypothesis, sample):
    reset = []

    # Fix computation with 0.1
    def round1(x):
        return int(x * 10 + 0.5) / 10

    def one_lower(x):
        if round1(x - int(x)) == 0.1:
            return int(x)
        else:
            return round1(x - 0.9)

    # Find sequence of reset information
    realDRTWs, realValue = testDTWs(sample, teacher)
    ltw = LRTW_to_LTW(DRTW_to_LRTW(realDRTWs))
    for DRTW in realDRTWs:
        reset.append(DRTW.isReset)

    def normalize(trace):
        newTrace = []
        for k in trace:
            if math.modf(float(k.time))[0] == 0.0:
                time = math.modf(float(k.time))[1]
            else:
                time = math.modf(float(k.time))[1] + 0.1
            newTrace.append(TimedWord(k.input, time))
        return newTrace

    ltw = normalize(ltw)

    # print('ltw:', [i.show() for i in ltw])

    def ltw_to_dtw(ltw):
        dtw = []
        for j in range(len(ltw)):
            if j == 0 or reset[j - 1]:
                dtw.append(TimedWord(ltw[j].input, ltw[j].time))
            else:
                dtw.append(TimedWord(ltw[j].input, round1(ltw[j].time - ltw[j - 1].time)))
        return dtw

    # print('initial dtw:', [i.show() for i in ltw_to_dtw(ltw)])
    for i in range(len(ltw)):
        while True:
            if i == 0 or reset[i - 1]:
                can_reduce = (ltw[i].time > 0)
            else:
                can_reduce = (ltw[i].time > ltw[i - 1].time)
            if not can_reduce:
                break
            ltw2 = copy.deepcopy(ltw)
            ltw2[i] = TimedWord(ltw[i].input, one_lower(ltw[i].time))
            if not isCounterexample(teacher, hypothesis, ltw_to_dtw(ltw2)):
                break
            ltw = copy.deepcopy(ltw2)

    # print('final dtw:', [i.show() for i in ltw_to_dtw(ltw)])
    return ltw_to_dtw(ltw)
