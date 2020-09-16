import time
import copy
import app.automata_learning.black_box.pac_learning.smart_teacher.obsTable as obsTable
from app.automata_learning.black_box.pac_learning.smart_teacher.teacher import EQs_new as EQs
import app.automata_learning.black_box.pac_learning.smart_teacher.comparator.equivWrapper as equivWrapper
from app.automata_learning.black_box.pac_learning.smart_teacher.hypothesis import structDiscreteOTA, structHypothesisOTA, structSimpleHypothesis, removeSinkState
from app.automata_learning.black_box.pac_learning.smart_teacher.system import buildSystem
from app.automata_learning.black_box.pac_learning.smart_teacher.validate import validate

from app.data_storage.init import update_cache


def black_smart_pac_learning(learning_id, request_data, startTime, timeout, debug=False):
    # build target system
    targetSys = buildSystem(request_data['model'])

    inputs = request_data["model"]["inputs"]
    upperGuard = request_data["upperGuard"]
    epsilon = request_data["epsilon"]  # accuracy
    delta = request_data["delta"]  # confidence
    stateNum = len(request_data["model"]["states"])

    # pac learning OTA
    startLearning = time.time()
    if debug:
        print("********** start learning *************")

    mqNum = 0  # number of MQs
    eqNum = 0  # number of EQs
    testNum = 0  # number of tests

    ### init Table
    table, mqNum = obsTable.initTable(inputs, targetSys, mqNum)
    if debug:
        print("***************** init-Table_1 is as follow *******************")
        table.show()

    ### learning start
    equivalent = False
    stableHpy = None  # learned model
    tNum = 1  # number of table

    while not equivalent and time.time() - startTime <= timeout:
        prepared = obsTable.isPrepared(table)
        while not prepared:
            # make closed
            flagClosed, closedMove = obsTable.isClosed(table)
            if not flagClosed:
                table, mqNum = obsTable.makeClosed(table, inputs, closedMove, targetSys, mqNum)
                tNum = tNum + 1
                if debug:
                    print("***************** closed-Table_" + str(tNum) + " is as follow *******************")
                    table.show()
            # make consistent
            flagConsistent, consistentAdd = obsTable.isConsistent(table)
            if not flagConsistent:
                table, mqNum = obsTable.makeConsistent(table, consistentAdd, targetSys, mqNum)
                tNum = tNum + 1
                if debug:
                    print("***************** consistent-Table_" + str(tNum) + " is as follow *******************")
                    table.show()
            prepared = obsTable.isPrepared(table)

        ### build hypothesis
        # Discrete OTA
        discreteOTA = structDiscreteOTA(table, inputs)
        if debug:
            print("***************** discreteOTA_" + str(eqNum + 1) + " is as follow. *******************")
            discreteOTA.showDiscreteOTA()
        # Hypothesis OTA
        hypothesisOTA = structHypothesisOTA(discreteOTA)
        if debug:
            print("***************** Hypothesis_" + str(eqNum + 1) + " is as follow. *******************")
            hypothesisOTA.showOTA()

        # 添加到 middleModels
        addMiddleModels(learning_id, removeSinkState(structSimpleHypothesis(copy.deepcopy(hypothesisOTA))))

        ### comparator
        flag, ctx, mqNum = equivWrapper.hpyCompare(stableHpy, hypothesisOTA, upperGuard, targetSys, mqNum)
        if flag:
            ### EQs
            equivalent, ctx, testNum = EQs(hypothesisOTA, upperGuard, epsilon, delta, stateNum, targetSys, eqNum, testNum)
            eqNum = eqNum + 1
            stableHpy = copy.deepcopy(hypothesisOTA)
        else:
            if debug:
                print("Comparator found a counterexample!!!")
            equivalent = False

        if not equivalent:
            # show ctx
            if debug:
                print("***************** counterexample is as follow. *******************")
                print([drtw.show() for drtw in ctx])
            # deal with ctx
            table, mqNum = obsTable.dealCtx(table, ctx, targetSys, mqNum)
            tNum = tNum + 1
            if debug:
                print("***************** New-Table" + str(tNum) + " is as follow *******************")
                table.show()

    endLearning = time.time()

    if stableHpy is None or not equivalent:
        value = {
            "isFinished": True,
            "result": {
                "result": 'fail',
            },
            "model": None
        }
    else:
        # verify model quality
        correctFlag, passingRate = validate(stableHpy, targetSys, upperGuard, stateNum, eqNum, delta, epsilon)
        learnedSys = structSimpleHypothesis(stableHpy)
        learnedSys = removeSinkState(learnedSys)
        print('success')
        value = {
            "isFinished": True,
            "result": {
                "result": 'success',
                "learningTime": endLearning - startLearning,
                "mqNum": mqNum,
                "eqNum": eqNum,
                "testNum": testNum,
                "accuracy": 1 - epsilon,
                "passingRate": passingRate,
                "correct": str(correctFlag)
            },
            "model": ota_to_JSON(learnedSys)
        }
    update_cache(learning_id, value)
    return True


def ota_to_JSON(ota):
    trans = {}
    for i in range(len(ota.trans)):
        trans[i] = [ota.trans[i].source, ota.trans[i].input, ota.trans[i].showGuards(), ota.trans[i].isReset, ota.trans[i].target]
    value = {
        "states": ota.states,
        "inputs": ota.inputs,
        "initState": ota.initState,
        "acceptStates": ota.acceptStates,
        "trans": trans
    }
    return value


def addMiddleModels(learning_id, ota):
    value = {
        "middleModels": ota_to_JSON(ota)
    }
    update_cache(learning_id, value)
    return True
