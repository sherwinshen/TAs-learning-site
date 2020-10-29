class TimedWord(object):
    def __init__(self, action, time):
        self.action = action
        self.time = time

    def __eq__(self, tw):
        if self.action == tw.action and self.time == tw.time:
            return True
        else:
            return False

    def __lt__(self, other):
        return (self.time, self.action) < (other.time, other.action)

    def show(self):
        return "(" + self.action + "," + str(self.time) + ")"


class ResetTimedWord(object):
    def __init__(self, action, time, reset):
        self.action = action
        self.time = time
        self.reset = reset

    def __eq__(self, rtw):
        if self.action == rtw.action and self.time == rtw.time and self.reset == rtw.reset:
            return True
        else:
            return False

    def show(self):
        return "(" + self.action + "," + str(self.time) + "," + str(self.reset) + ")"


# DRTWs -> LRTWs
def DRTW_to_LRTW(drtws):
    lrtws = []
    now_time = 0
    for drtw in drtws:
        lrtw = ResetTimedWord(drtw.action, drtw.time + now_time, drtw.reset)
        lrtws.append(ResetTimedWord(drtw.action, drtw.time + now_time, drtw.reset))
        if lrtw.reset:
            now_time = 0
        else:
            now_time = lrtw.time
    return lrtws


# LRTW -> DTW
def LRTW_to_DTW(lrtws):
    dtws = []
    now_time = 0
    for lrtw in lrtws:
        dtw = TimedWord(lrtw.action, lrtw.time - now_time)
        dtws.append(dtw)
        if lrtw.reset:
            now_time = 0
        else:
            now_time = lrtw.time
    return dtws


# LRTW -> LTW
def LRTW_to_LTW(lrtws):
    ltws = []
    for lrtw in lrtws:
        dtw = TimedWord(lrtw.action, lrtw.time)
        ltws.append(dtw)
    return ltws


# LRTW -> DRTW
def LRTW_to_DRTW(lrtws):
    drtws = []
    now_time = 0
    for lrtw in lrtws:
        drtw = ResetTimedWord(lrtw.action, lrtw.time - now_time, lrtw.reset)
        drtws.append(drtw)
        if lrtw.reset:
            now_time = 0
        else:
            now_time = lrtw.time
    return drtws
