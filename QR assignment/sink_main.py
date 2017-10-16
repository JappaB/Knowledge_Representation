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

def generate_state(state1):
    raise NotImplementedError()


# state1: starting state
# state2: resulting state
# NB: Is directional
def valid_transition(state1, state2):

    raise NotImplementedError()

    # Continuity (derivatives can't change sign without passing STD

    # Derivative has to change before magnitude

    # Point quantities change before ranges

    # All quantity calculus checks out

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
    for q1 in [NEG, STD, POS]:
        for q2 in [NEG, STD, POS]:
            print(q1 + " and ", q2, '=', infl_addition(q1, q2))



if __name__ == '__main__':
	main()
