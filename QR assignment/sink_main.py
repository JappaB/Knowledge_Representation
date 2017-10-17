import itertools

MAX = "MAX"
POS = "+"
NEG = "-"
ZER = "0"
AMB = "?"

value_control_model = {
    "VC" : [(("volume", MAX), ("outflow", MAX)), (("volume", ZER), ("outflow", ZER))],
}

influence_model = {
    "volume" : [("inflow", POS), ("outflow", NEG)]
}

proportionality_model = {
    "outflow" : [("volume", POS)]
}

# Calculates the sign of the affected quantity by adding the signs of the
# two quantities that determine the affected. Can be used for both influence
# and proportionality calculus.
#
# q1: sign of quantity 1
# q2: sign of quantity 2
# returns: sign of affected quantity

def quantity_addition(q1, q2):
    if q1 == q2:
        return q1
    if q1 == ZER or q2 == ZER:
        return (q1 + q2).replace(ZER, "")
    if q1 != q2:
        return AMB

def quantity_multiplication(q1, q2):
    if q1 == ZER or q2 == ZER:
        return ZER
    if q1 == q2:
        return POS
    if q2 != q1:
        return NEG

def generate_all_states():
    derivative_values = [NEG, ZER, POS]
    states = []

    for derivative_in in derivative_values:
        for derivative_out in  derivative_values:
            for derivative_vol in derivative_values:
                for magnitude_in in [ZER, POS]:
                    for magnitude_out in [ZER, POS, MAX]:
                        for magnitude_vol in [ZER, POS, MAX]:
                            volume = Volume(magnitude_vol, derivative_vol)
                            inflow = Inflow(magnitude_in, derivative_in)
                            outflow = Outflow(magnitude_out, derivative_out)
                            states.append(State(inflow, outflow, volume))

    return states

def index_distance(l, item1, item2):
    i1 = l.index(item1)
    i2 = l.index(item2)

    return abs(i1 - i2)

def valid_state(state):
    # Value Control relations must hold
    all_vc_hold = True
    for domain, range in value_control_model["VC"]:
        # mag: MAX -> mag: MAX / mag: 0 -> mag:
        if not (state[domain[0]].magnitude == domain[1]) == (state[range[0]].magnitude == range[1]):
            all_vc_hold = False

    # Can't be max with positive derivative or zero with negative
    der_matches_mag = True
    for key, value in state.iteritems():
        if value.symbol_pair() in [ZER+NEG, MAX+POS]: der_matches_mag = False

    # All quantity calculus checks out
    calculus_check = True
    for quantity, influences in influence_model.iteritems():
        if len(influences) == 0: continue

        # TODO: understand what happens in this case
        if len(influences) == 1: continue

        if len(influences) == 2:
            # Calculate effects of influence by multiplying magnitude with sign of arrow
            source1, sign1 = influences[0]
            effect1 = quantity_multiplication(state[source1].magnitude, sign1)

            source2, sign2 = influences[1]
            effect2 = quantity_multiplication(state[source2].magnitude, sign2)

            addition = quantity_addition(effect1, effect2)

            # The addition of the effects should match the derivative of the affected quantity
            if not (state[quantity].derivative == addition or addition == AMB):
                calculus_check = False

    for quantity, proportionalities in proportionality_model.iteritems():
        if len(proportionalities) == 0: continue

        if len(proportionalities) == 1:
            source, sign = proportionalities[0]
            effect = quantity_multiplication(state[source].derivative, sign)

            if not state[quantity].derivative == effect:
                calculus_check = False

    return all_vc_hold and der_matches_mag and calculus_check


# state1: starting state dictionary
# state2: resulting state dictionary
# NB: Is directional
def valid_transition(state1, state2):


    for label, quantity in state1.iteritems():
        # Continuity (derivatives can't change sign without passing STD)
        # Also holds for quantities (can't go from ZER to MAX)
        # Check if derivative changes with more than a single step
        derivative_change = index_distance(quantity.der_q_space, quantity.derivative, state2[label].derivative)

        if derivative_change != 1 and derivative_change != 0: return False

        # Check if magnitude changes with more than a single step
        magnitude_change = index_distance(quantity.mag_q_space, quantity.magnitude, state2[label].magnitude)
        if magnitude_change != 1 and magnitude_change != 0: return False

        # Derivative has to change before magnitude
        if derivative_change == 1 and magnitude_change != 0: return False


        # Point quantities change before ranges

        # mag: ZER, der: POS must transit to POS,POS
        # if (ZER+POS -> POS+POS) should hold
        if not(not(quantity.symbol_pair() == ZER+POS) or state2[label].symbol_pair() == POS+POS): return False

        # mag: MAX, der: NEG must transit to POS,NEG
        # if (MAX+NEG -> POS+NEG) should hold
        if not(not(quantity.symbol_pair()) == MAX+NEG or state2[label].symbol_pair() == POS+NEG): return False



    # You cannot change the inflow (derivative) during an instable point state,
    # eg. MAX+NEG or ZER+POS

    return True

class Inflow:
    magnitude = None
    derivative = None
    mag_q_space = [ZER, POS]
    der_q_space = [ZER, POS, NEG]

    def symbol_pair(self):
        return self.magnitude + self.derivative

    def __init__(self, magnitude, derivative):

        self.magnitude = magnitude
        self.derivative = derivative

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class Outflow:
    magnitude = None
    derivative = None
    mag_q_space = [ZER, POS, MAX]
    der_q_space = [ZER, POS, NEG]

    def symbol_pair(self):
        return self.magnitude + self.derivative

    def __init__(self, magnitude, derivative):
        self.magnitude = magnitude
        self.derivative = derivative

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class Volume:
    magnitude = None
    derivative = None
    mag_q_space = [ZER, POS, MAX]
    der_q_space = [ZER, POS, NEG, AMB]

    def symbol_pair(self):
        return self.magnitude + self.derivative

    def __init__(self, magnitude, derivative):
        self.magnitude = magnitude
        self.derivative = derivative

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class State:
    volume = None
    outflow = None
    inflow = None

    def __str__(self):
        pretty_print = "Quantity | Magnitude | Derivative \n" \
                       "Inflow:  | " + self.inflow.magnitude + " \t\t | " + self.inflow.derivative + "\n" \
                       "Volume:  | " + self.volume.magnitude + " \t\t | " + self.volume.derivative + "\n" \
                       "Outflow: | " + self.outflow.magnitude + " \t\t | " + self.outflow.derivative + "\n"
        return pretty_print

    def __init__(self, inf, outf, vol):
        self.volume = vol
        self.outflow = outf
        self.inflow = inf

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
           return False

    def __ne__(self, other):
        return not self.__eq__(other)


def main():
    vol = Volume(NEG, NEG)
    outf = Outflow(NEG, NEG)
    inf = Inflow(NEG, NEG)


    # Test influence addition
    # for q1 in [NEG, ZER, POS]:
    #     for q2 in [NEG, ZER, POS]:
    #         print(q1 + " and ", q2, '=', quantity_addition(q1, q2))
    #
    # print "--------"
    #
    # for q1 in [NEG, ZER, POS]:
    #     for q2 in [NEG, ZER, POS]:
    #         print(q1 + " and ", q2, '=', quantity_multiplication(q1, q2))

    states = generate_all_states()
    valid_states = list(filter(lambda x: valid_state(x.__dict__), states))
    print len(valid_states)

    valid_transitions = []
    for state1, state2 in itertools.combinations(valid_states, 2):

        if valid_transition(state1.__dict__, state2.__dict__):
            valid_transitions.append( (state1, state2) )
        if valid_transition(state2.__dict__, state1.__dict__):
            valid_transitions.append( (state2, state1) )

    print len(valid_transitions)

if __name__ == '__main__':
	main()
