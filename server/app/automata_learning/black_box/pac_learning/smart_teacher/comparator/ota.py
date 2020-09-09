# definitions of timed automata with one clock (OTA)
# read a json file to build an OTA

class Location(object):
    """
        The definition of location.
        "Name" for location name;
        "init" for indicating the initial state;
        "accept" for indicating accepting states;
        "flag" for indicating the OTA
        "sink" for indicating the location whether it is the sink state.
    """

    def __init__(self, name="", init=False, accept=False, flag='s', sink=False):
        self.name = name
        self.init = init
        self.accept = accept
        self.flag = flag
        self.sink = sink

    def __eq__(self, location):
        if self.name == location.name and self.init == location.init and self.accept == location.accept and self.flag == location.flag:
            return True
        else:
            return False

    def __hash__(self):
        return hash(("LOCATION", self.name, self.init, self.accept, self.flag))

    def get_name(self):
        return self.name

    def get_flagname(self):
        return self.flag + '_' + self.name

    def show(self):
        return self.get_flagname() + ',' + str(self.init) + ',' + str(self.accept) + ',' + str(self.sink)


class State(object):
    """
        The definition of state. 
        A state is a pair (l, v) where l is a location and v is a clock valuation.
    """

    def __init__(self, location, v):
        self.location = location
        self.v = v

    def get_fraction(self):
        _, fraction_str = str(self.v).split('.')
        fraction = float('0.' + fraction_str)
        return fraction

    def show(self):
        return "(" + self.location.get_flagname() + "," + str(self.v) + ")"


class OTATran(object):
    """
        The definition of OTA transition.
        "source" for the source location name;
        "target" for the target location name;
        "label" for the action name;
        "reset" for indicating whether the clock resets or not;
        "constraints" for the timing constraints.
        "flag" for indicating the OTA
    """

    def __init__(self, id, source="", label="", constraints=None, reset=False, target="", flag=""):
        self.id = id
        self.source = source
        self.label = label
        self.constraints = constraints or []
        self.reset = reset
        self.target = target
        self.flag = flag

    def is_pass(self, tw):
        """Determine whether local(logical) timeword tw can pass the transition.
        """
        if tw.action == self.label:
            for constraint in self.constraints:
                if constraint.isininterval(tw.time):
                    return True
        else:
            return False
        return False

    def is_pass_reset(self, tw):
        if tw.action == self.label and tw.reset == self.reset:
            for constraint in self.constraints:
                if constraint.isininterval(tw.time):
                    return True
        else:
            return False
        return False

    def __eq__(self, otatran):
        if self.source == otatran.source and self.label == otatran.label and self.constraints == otatran.constraints and self.reset == otatran.reset and self.target == otatran.target and self.flag == otatran.flag:
            return True
        else:
            return False

    def __hash__(self):
        return hash(("OTATRAN", self.source, self.label, self.constraints[0], self.reset, self.target, self.flag))

    def show_constraints(self):
        length = len(self.constraints)
        if length == 0:
            return "[0,+)"
        else:
            temp = self.constraints[0].guard
            for i in range(1, length):
                temp = temp + 'U' + self.constraints[i].guard
            return temp


class OTA(object):
    """
        The definition of Timed Automata with one clock (OTA).
        "name" for the OTA name string;
        "sigma" for the labels list;
        "locations" for the locations list;
        "trans" for the transitions list;
        "initstate_name" for the initial location name;
        "accept_names" fot the list of accepting locations.
    """

    def __init__(self, name, sigma, locations, trans, init, accepts):
        self.name = name
        self.sigma = sigma or []
        self.locations = locations or []
        self.trans = trans or []
        self.initstate_name = init
        self.accept_names = accepts or []
        self.sink_name = ""

        self.membership_query = dict()
        self.mem_query_num = 0
        self.equiv_query_num = 0

    def max_time_value(self):
        """
            Get the max time value constant appearing in OTA.
            Return "max_time_value" for the max time value constant;
            #Return "closed" for indicating whether we can reach the max time value constant.
        """
        max_time_value = 0
        for tran in self.trans:
            for c in tran.constraints:
                if c.max_value == '+':
                    temp_max_value = float(c.min_value)
                else:
                    temp_max_value = float(c.max_value)
                if max_time_value < temp_max_value:
                    max_time_value = temp_max_value
        return max_time_value

    def findlocationbyname(self, lname):
        for l in self.locations:
            if l.name == lname:
                return l
        return None

    def is_accepted(self, tws):
        """
            Determine whether the OTA accepts a local(logical) timed words or not.
        """
        if len(tws) == 0:
            if self.initstate_name in self.accept_names:
                return 1
            else:
                return 0
        else:
            current_statename = self.initstate_name
            for tw in tws:
                flag = False
                for tran in self.trans:
                    if tran.source == current_statename and tran.is_pass(tw):
                        current_statename = tran.target
                        flag = True
                        break
                if not flag:
                    return -1
            if current_statename in self.accept_names:
                return 1
            else:
                return 0

    def run_delaytimedwords(self, tws):
        """
            Run a delay timed words, return the final location name.
        """
        length = len(tws)
        if length == 0:
            return True, self.initstate_name
        else:
            current_statename = self.initstate_name
            current_clock_valuation = 0
            reset = True
            for tw in tws:
                if not reset:
                    current_clock_valuation = current_clock_valuation + tw.time
                else:
                    current_clock_valuation = tw.time
                flag = False
                for tran in self.trans:
                    if current_statename == tran.source and tran.is_pass(Timedword(tw.action, current_clock_valuation)):
                        current_statename = tran.target
                        reset = tran.reset
                        flag = True
                        if current_statename == self.sink_name:
                            return True, self.sink_name
                        break
                if not flag:
                    return False, ""
                else:
                    pass
            return True, current_statename

    def is_accepted_delay(self, tws):
        self.mem_query_num += 1
        tws = tuple(tws)
        if tws in self.membership_query:
            return self.membership_query[tws]

        flag, current_statename = self.run_delaytimedwords(tws)
        if not flag:
            res = -2
        elif current_statename == self.sink_name:
            res = -1
        elif current_statename in self.accept_names:
            res = 1
        else:
            res = 0

        self.membership_query[tws] = res
        return res

    def run_resettimedwords(self, tws):
        """
            Run a resettimedwords, return the final location.
        """
        length = len(tws)
        if length == 0:
            return self.initstate_name
        else:
            current_statename = self.initstate_name
            current_clock_valuation = 0
            reset = True
            for tw in tws:
                if reset == False and tw.time < current_clock_valuation:
                    return self.sink_name
                else:
                    flag = False
                    for tran in self.trans:
                        if tran.source == current_statename and tran.is_pass(tw):
                            current_statename = tran.target
                            current_clock_valuation = tw.time
                            reset = tw.reset
                            if reset:
                                current_clock_valuation = 0
                            flag = True
                            break
                    if not flag:
                        raise NotImplementedError("run_resettimedwords: an unhandle resettimedword!")
                    else:
                        pass
            return current_statename

    def show(self):
        print("OTA name: ")
        print(self.name)
        print("sigma and length of sigma: ")
        print(self.sigma, len(self.sigma))
        print("Location (name, init, accept, sink) :")
        for l in self.locations:
            print(l.show())
        print("transitions (id, source_state, label, target_state, constraints, reset): ")
        for t in self.trans:
            print(t.id, t.flag + '_' + t.source, t.label, t.flag + '_' + t.target, t.show_constraints(), t.reset)
        print("init state: ")
        print(self.initstate_name)
        print("accept states: ")
        print(self.accept_names)
        print("sink states: ")
        print(self.sink_name)


class Timedword(object):
    """
        The definition of timedword without resetting information.
    """

    def __init__(self, action, time):
        self.action = action
        self.time = time

    def __eq__(self, tw):
        if self.action == tw.action and self.time == tw.time:
            return True
        else:
            return False

    def __hash__(self):
        return hash((self.action, self.time))

    def show(self):
        return '(' + self.action + ',' + str(self.time) + ')'

    def __str__(self):
        return self.show()

    def __repr__(self):
        return self.show()
