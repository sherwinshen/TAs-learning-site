import copy
from app.automata_learning.black_box.pac_learning.smart_teacher.tester import testDTWs
from app.automata_learning.black_box.pac_learning.smart_teacher.timedWord import TimedWord
from app.automata_learning.black_box.pac_learning.smart_teacher.comparator import equivalence
from app.automata_learning.black_box.pac_learning.smart_teacher.comparator import ota as old_ota
from app.automata_learning.black_box.pac_learning.smart_teacher.comparator import interval as old_interval
from app.automata_learning.black_box.pac_learning.smart_teacher.system import buildSystem
from app.automata_learning.black_box.pac_learning.smart_teacher.hypothesis import OTA, OTATran
import app.automata_learning.black_box.pac_learning.smart_teacher.timeInterval as timeInterval
from app.automata_learning.black_box.pac_learning.smart_teacher.teacher import getHpyDTWsValue


def hpyCompare(stableHpy, hypothesisOTA, upperGuard, targetSys, mqNum):
    """
        stableHpy: old candidate automata
        hypothesisOTA: new candidate automata
        upperGuard: maximum time value
        targetSys: teacher automata
        targetFullSys: complete teacher automata
        mqNum: number of membership queries
        metric: distance between hypothesisOTA and targetSys
    """
    # 第一次不进行比较
    if stableHpy is None:
        return True, [], mqNum

    sys = transform_system(stableHpy, "A", "s")
    sys2 = transform_system(hypothesisOTA, "B", "q")

    max_time_value = max(sys.max_time_value(), sys2.max_time_value(), upperGuard)

    res, w_pos = equivalence.ota_inclusion(int(max_time_value), sys, sys2)
    # dtw_pos is accepted by sys2 but not sys.
    if not res:
        dtw_pos = equivalence.findDelayTimedwords(w_pos, 'q', sys2.sigma)
        # print('res', dtw_pos)

    res2, w_neg = equivalence.ota_inclusion(int(max_time_value), sys2, sys)
    # dtw_neg is accepted by sys but not sys2.
    if not res2:
        dtw_neg = equivalence.findDelayTimedwords(w_neg, 'q', sys.sigma)
        # print('res2', dtw_neg)

    if res and res2:
        raise NotImplementedError('hpyCompare should always find a difference')

    if res and not res2:
        hpy_flag, ctx = 0, dtw_neg
    elif res2 and not res:
        hpy_flag, ctx = 1, dtw_pos
    elif len(w_pos.lw) <= len(w_neg.lw):
        hpy_flag, ctx = 1, dtw_pos
    else:
        hpy_flag, ctx = 0, dtw_neg

    flag = True
    newCtx = []
    tempCtx = []
    for i in ctx:
        tempCtx.append(TimedWord(i.action, i.time))
    realDRTWs, realValue = testDTWs(tempCtx, targetSys)

    if (realValue == 1 and hpy_flag != 1) or (realValue != 1 and hpy_flag == 1):
        flag = False
        newCtx = realDRTWs
    return flag, newCtx, mqNum + 1


def transform_system(system, name, flag):
    """
        Transform system in learning_OTA_by_testing to system in equiv.
    """
    locations = []
    for loc in system.states:
        is_init = (loc == system.initState)
        is_accept = (loc in system.acceptStates)
        is_sink = (loc == system.sinkState)
        locations.append(old_ota.Location(loc, is_init, is_accept, flag, is_sink))

    trans = []
    for tran in system.trans:
        constraints = []
        for guard in tran.guards:
            constraints.append(old_interval.Constraint(guard.guard))
        trans.append(old_ota.OTATran(tran.tranId, tran.source, tran.input, constraints, tran.isReset, tran.target, flag))

    ota = old_ota.OTA(name, system.inputs, locations, trans, system.initState, system.acceptStates)
    ota.sink_name = system.sinkState
    return ota


# 补全targetSys
def buildCanonicalOTA(targetSys):
    inputs = targetSys.inputs
    states = targetSys.states
    trans = targetSys.trans
    initState = targetSys.initState
    acceptStates = targetSys.acceptStates

    sinkFlag = False
    newTrans = []
    sinkState = None
    tranNumber = len(targetSys.trans)

    for state in targetSys.states:
        guardDict = {}
        for input in inputs:
            guardDict[input] = []
        for tran in trans:
            if tran.source == state:
                for input in inputs:
                    if tran.input == input:
                        for guard in tran.guards:
                            guardDict[input].append(guard)
        for key, value in guardDict.items():
            if len(value) > 0:
                addGuards = complementIntervals(value)
            else:
                addGuards = [timeInterval.Guard('[0,+)')]
            if len(addGuards) > 0:
                sinkState = 'sink'
                sinkFlag = True
                for guard in addGuards:
                    tempTran = OTATran(tranNumber, state, key, [guard], True, sinkState)
                    tranNumber = tranNumber + 1
                    newTrans.append(tempTran)
    if sinkFlag:
        states.append(sinkState)
        for tran in newTrans:
            trans.append(tran)
        for input in inputs:
            guards = [timeInterval.Guard('[0,+)')]
            tempTran = OTATran(tranNumber, sinkState, input, guards, True, sinkState)
            tranNumber = tranNumber + 1
            trans.append(tempTran)
    newOTA = OTA(inputs, states, trans, initState, acceptStates, sinkState)
    return newOTA


# 补全区间
def complementIntervals(guards):
    partitions = []
    key = []
    floor_bn = timeInterval.BracketNum('0', timeInterval.Bracket.LC)
    ceil_bn = timeInterval.BracketNum('+', timeInterval.Bracket.RO)
    for guard in guards:
        min_bn = guard.min_bn
        max_bn = guard.max_bn
        if min_bn not in key:
            key.append(min_bn)
        if max_bn not in key:
            key.append(max_bn)
    copyKey = copy.deepcopy(key)
    for bn in copyKey:
        complement = bn.complement()
        if complement not in copyKey:
            copyKey.append(complement)
    if floor_bn not in copyKey:
        copyKey.insert(0, floor_bn)
    if ceil_bn not in copyKey:
        copyKey.append(ceil_bn)
    copyKey.sort()
    for index in range(len(copyKey)):
        if index % 2 == 0:
            tempGuard = timeInterval.Guard(copyKey[index].getBN() + ',' + copyKey[index + 1].getBN())
            partitions.append(tempGuard)
    for g in guards:
        if g in partitions:
            partitions.remove(g)
    return partitions


if __name__ == "__main__":
    experiments_path = '../Automata/'

    A = buildSystem(experiments_path + 'example_sta.json')
    AA = buildCanonicalOTA(A)
    sys = transform_system(AA, "A", "s")
    # sys.show()

    H = buildSystem(experiments_path + 'example_hpy.json')
    HH = buildCanonicalOTA(H)
    sys2 = transform_system(HH, "B", "q")
    # sys2.show()

    max_time_value = 12

    res, w_pos = equivalence.ota_inclusion(max_time_value, sys, sys2)
    # drtw_pos is accepted by sys2 but not sys.
    if not res:
        dtw_pos = equivalence.findDelayTimedwords(w_pos, 'q', sys2.sigma)
        print('res', dtw_pos)

    res2, w_pos2 = equivalence.ota_inclusion(max_time_value, sys2, sys)
    # drtw_pos2 is accepted by sys but not sys2.
    if not res2:
        dtw_neg = equivalence.findDelayTimedwords(w_pos2, 'q', sys.sigma)
        print('res2', dtw_neg)

    print(res)
    print(res2)

    if res and not res2:
        hpy_flag = 0
    elif res2 and not res:
        hpy_flag = 1
    elif len(w_pos.lw) <= len(w_pos2.lw):
        hpy_flag = 1
    else:
        hpy_flag = 0

    print(hpy_flag)
    ctx = []
    for i in dtw_neg:
        ctx.append(TimedWord(i.action,i.time))


    DRTWs, value = getHpyDTWsValue(ctx, AA)
    DRTWs2, value2 = getHpyDTWsValue(ctx, HH)
    print(value, value2)
