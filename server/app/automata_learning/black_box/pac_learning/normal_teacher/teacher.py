from app.automata_learning.black_box.pac_learning.normal_teacher.pac import pac_equivalence_query, pac_equivalence_query_level


def EQs(hypothesis, upper_guard, epsilon, delta, eq_num, state_num, system):
    # use pac testing as equivalence query
    equivalent, ctx = pac_equivalence_query(hypothesis, upper_guard, epsilon, delta, state_num, eq_num, system)
    system.eq_num += 1
    return equivalent, ctx


def EQs_level(hypothesis, upper_guard, epsilon, delta, level, m_i, state_num, system):
    equivalent, ctx = pac_equivalence_query_level(hypothesis, upper_guard, epsilon, delta, level, m_i, state_num, system)
    system.eq_num += 1
    return equivalent, ctx
