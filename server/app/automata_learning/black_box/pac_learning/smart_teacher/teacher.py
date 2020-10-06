from app.automata_learning.black_box.pac_learning.smart_teacher.pac import pac_equivalence_query


# LRTWs + value
def TQs(LTWs, system):
    LRTWs, value = system.test_LTWs(LTWs)
    return LRTWs, value


# equivalence query
def EQs(hypothesis, upper_guard, epsilon, delta, state_num, system):
    # use pac testing as equivalence query
    equivalent, ctx = pac_equivalence_query(hypothesis, upper_guard, epsilon, delta, state_num, system.eq_num, system)
    system.eq_num += 1
    return equivalent, ctx
