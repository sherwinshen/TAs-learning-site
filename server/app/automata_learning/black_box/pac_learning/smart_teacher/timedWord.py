class TimedWord(object):
    def __init__(self, action, time):
        self.input = action
        self.time = time

    def __eq__(self, tw):
        if self.input == tw.input and self.time == tw.time:
            return True
        else:
            return False

    def __lt__(self, other):
        return (self.time, self.input) < (other.time, other.input)

    def show(self):
        return "(" + self.input + "," + str(self.time) + ")"


class ResetTimedWord(object):
    def __init__(self, action, time, isReset):
        self.input = action
        self.time = time
        self.isReset = isReset

    def __eq__(self, rtw):
        if self.input == rtw.input and self.time == rtw.time and self.isReset == rtw.isReset:
            return True
        else:
            return False

    def show(self):
        return "(" + self.input + "," + str(self.time) + "," + str(self.isReset) + ")"


# —————————————————————————— 方法 ——————————————————————————

# DRTW转为LRTW
def DRTW_to_LRTW(drtws):
    lrtws = []
    nowTime = 0
    for drtw in drtws:
        lrtw = ResetTimedWord(drtw.input, drtw.time + nowTime, drtw.isReset)
        lrtws.append(lrtw)
        if lrtw.isReset:
            nowTime = 0
        else:
            nowTime = lrtw.time
    return lrtws


# LRTW转为DTW
def LRTW_to_DTW(lrtws):
    dtws = []
    nowTime = 0
    for lrtw in lrtws:
        dtw = TimedWord(lrtw.input, lrtw.time - nowTime)
        dtws.append(dtw)
        if lrtw.isReset:
            nowTime = 0
        else:
            nowTime = lrtw.time
    return dtws


# LRTW转为LTW
def LRTW_to_LTW(lrtws):
    ltws = []
    for lrtw in lrtws:
        dtw = TimedWord(lrtw.input, lrtw.time)
        ltws.append(dtw)
    return ltws


# LRTW转为DRTW
def LRTW_to_DRTW(lrtws):
    drtws = []
    nowTime = 0
    for lrtw in lrtws:
        drtw = ResetTimedWord(lrtw.input, lrtw.time - nowTime, lrtw.isReset)
        drtws.append(drtw)
        if lrtw.isReset:
            nowTime = 0
        else:
            nowTime = lrtw.time
    return drtws
