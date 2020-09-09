import copy
import random
import math
from app.automata_learning.black_box.pac_learning.smart_teacher.comparator.equivWrapper import buildCanonicalOTA, transform_system
from app.automata_learning.black_box.pac_learning.smart_teacher.comparator.equivalence import equivalence_query_normal
from app.automata_learning.black_box.pac_learning.smart_teacher.sampling import sampleGenerationMain
from app.automata_learning.black_box.pac_learning.smart_teacher.teacher import getHpyDTWsValue
from app.automata_learning.black_box.pac_learning.smart_teacher.tester import testDTWs


def validate(learnedSys, targetSys, upperGuard, stateNum, eqNum, delta, epsilon):
    flag = False
    testNum = int((math.log(1 / delta) + math.log(2) * (eqNum + 1)) / epsilon)
    if testNum < 20000:
        testNum = 20000

    A = copy.deepcopy(targetSys)
    AA = buildCanonicalOTA(A)
    sys = transform_system(AA, "A", "s")
    HH = copy.deepcopy(learnedSys)
    sys2 = transform_system(HH, "B", "q")

    equivalent, _ = equivalence_query_normal(AA.max_time_value(), sys, sys2)
    if equivalent:
        flag = True
        # print("Completely correct!")
        return flag, 1.0

    failNum = 0
    # print('Start validation')
    for i in range(testNum):
        # if i % 1000 == 0:
        #     print(i, 'of', testNum)
        length = random.randint(1, math.ceil(stateNum * 1.5))
        sample = sampleGenerationMain(targetSys, upperGuard, length)
        DRTWs, value = getHpyDTWsValue(sample, learnedSys)
        realDRTWs, realValue = testDTWs(sample, targetSys)
        if (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
            failNum += 1
    return flag, (testNum - failNum) / testNum
