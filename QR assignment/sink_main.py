MAX = "MAX"
POS = "+"
NEG = "-"
STD = "/"
ZER = "0"
AMB = "?"

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
    if q1 == STD or q2 == STD:
        return (q1 + q2).replace(STD, "")
    if q1 != q2:
        return AMB

def generate_all_states():
    derivative_values = [NEG, STD, POS]
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


# state1: starting state
# state2: resulting state
# NB: Is directional
def valid_transition(state1, state2):

    raise NotImplementedError()

    # Continuity (derivatives can't change sign without passing STD)
    # Also holds for quantities (can't go from ZER to MAX)

    # Can't be max with positive derivative or zero with negative

    # Derivative has to change before magnitude

    # Point quantities change before ranges

    # All quantity calculus checks out

    # Value Control relations must hold

conceptual_model = {
    "outflow" : [("volume", "I", NEG)],
    "volume" : [("outflow", "P", POS), ("outflow", "VC", MAX), ("outflow", "VC", ZER)],
    "inflow" : [("volume", "I", POS)]
}

class Inflow:
    magnitude = None
    derivative = None
    mag_q_space = [ZER, POS]
    der_q_space = [STD, POS, NEG]

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
    q_space = [ZER, POS, MAX]
    der_q_space = [STD, POS, NEG]


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
    q_space = [ZER, POS, MAX]
    der_q_space = [STD, POS, NEG]

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

    conceptual_model = {
        outflow : [(volume, "I", NEG)],
        volume : [(outflow, "P", POS), ("outflow", "VC", MAX), ("outflow", "VC", ZER)],
        inflow : [(volume, "I", POS)]
    }

    # def __str__(self):
    #     pretty_print = "Quantity | Magnitude | Derivative" \
    #                    "Volume:  | " + self.volume.magnitude + " | " + self.volume.derivative + "\n" \
    #                    "" \
    #                    ""
    #     return

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
    # for q1 in [NEG, STD, POS]:
    #     for q2 in [NEG, STD, POS]:
    #         print(q1 + " and ", q2, '=', quantity_addition(q1, q2))

    states = generate_all_states()

if __name__ == '__main__':
	main()
