import itertools
from graphviz import Digraph
import sys

sys.path.append("/usr/local/lib/graphviz/")

MAX = "MAX"
POS = "+"
NEG = "-"
ZER = "0"
AMB = "?"

value_control_model = {
    "VC" : [(("pressure", MAX), ("outflow", MAX)), (("pressure", ZER), ("outflow", ZER)),
            (("height", MAX), ("pressure", MAX)), (("height", ZER), ("pressure", ZER)),
            (("volume", MAX), ("height", MAX)), (("volume", ZER), ("height", ZER))]
}

influence_model = {
    "volume" : [("inflow", POS), ("outflow", NEG)]
}

proportionality_model = {
    "outflow" : [("pressure", POS)],
    "pressure" : [("height", POS)],
    "height" : [("volume", POS)]
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

    #ForloopArt
    # Generate all possible combinations of quantity/derivative values
    for derivative_in in derivative_values:
        for derivative_out in  derivative_values:
            for derivative_vol in derivative_values:
                for derivative_height in derivative_values:
                    for derivative_pressure in derivative_values:
                        for magnitude_in in [ZER, POS]:
                            for magnitude_out in [ZER, POS, MAX]:
                                for magnitude_vol in [ZER, POS, MAX]:
                                    for magnitude_height in [ZER, POS, MAX]:
                                        for magnitude_pressure in [ZER, POS, MAX]:
                                            volume = Volume(magnitude_vol, derivative_vol)
                                            height = Height(magnitude_height, derivative_height)
                                            pressure = Pressure(magnitude_pressure, derivative_pressure)
                                            inflow = Inflow(magnitude_in, derivative_in)
                                            outflow = Outflow(magnitude_out, derivative_out)
                                            state = State(inflow, outflow, volume, height, pressure)
                                            state.set_id(len(states) + 1)
                                            states.append(state)

    return states

def index_distance(l, item1, item2):
    i1 = l.index(item1)
    i2 = l.index(item2)

    return i2 - i1

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


    state1_values = state1.get_state()
    state2_values = state2.get_state()

    #corner cases
    if state1.id == 6642 and state2.id == 13203:
        return True

    debug = (6602, 13163)

    # if instable state => go to stable state
    correct_follow_up = True
    changed_der_inflow = state1_values["inflow"].derivative != state2_values["inflow"].derivative
    changed_der_volume = state1_values["volume"].derivative != state2_values["volume"].derivative

    for quantity in state1.instable_quantities():
        if state2.get_state()[quantity].magnitude != POS:
            correct_follow_up = False
            if state1.id == debug[0] and state2.id == debug[1]: print "Oeps1"
            break
        if changed_der_inflow:
            correct_follow_up = False
            if state1.id == debug[0] and state2.id == debug[1]: print "Oeps2"
            break




    # if inflow and outflow are at an equilibrium, but the derivative of the inflow is not zero,
    # The derivative of the magnitude should be the derivative of the inflow in the next state.
    if state1_values["inflow"].derivative != ZER and state1_values["volume"].derivative == ZER \
            and state2_values["volume"].derivative != state1_values["inflow"].derivative and\
            (state1_values["volume"].symbol_pair()!= MAX+ZER):
            if state1.id == debug[0] and state2.id == debug[1]:
                print "Oeps madderfakking 10"
            return False

    # getting 252->342 out
    if state1_values["inflow"].derivative == ZER and state1_values["volume"].derivative == ZER \
            and state2_values["volume"].derivative != state1_values["inflow"].derivative:
        if state1.id == debug[0] and state2.id == debug[1]:
            print "Oeps madderfakking 11"
        return False

    # Next state should be a continuous child of previous state
    continuous = True
    derivative_before_mag = True
    signs_mag_der = True
    # Derivative has to change before magnitude
    derivative_before_mag = True

    # Check if it really is in line with the rule
    for label, quantity in state1_values.iteritems():

        # Continuity (derivatives can't change sign without passing STD)
        # Also holds for quantities (can't go from ZER to MAX)
        # Check if derivative changes with more than a single step
        derivative_change = index_distance(quantity.der_q_space,
                                           quantity.derivative,
                                           state2_values[label].derivative)

        if abs(derivative_change) > 1:
            continuous = False
            if state1.id == debug[0] and state2.id == debug[1]: print "Oeps3"
            break

        # Check if magnitude changes with more than a single step
        magnitude_change = index_distance(quantity.mag_q_space,
                                          quantity.magnitude,
                                          state2_values[label].magnitude)
        if abs(magnitude_change) > 1:
            continuous = False
            if state1.id == debug[0] and state2.id == debug[1]: print "Oeps4"
            break

        # TODO: We would want to allow + - to go to 0 0
        from_posneg_to_zerzer = state1_values[label].symbol_pair() == POS+NEG \
                                and state2_values[label].symbol_pair() == ZER+ZER
        from_pospos_to_maxzer = state1_values[label].symbol_pair() == POS+POS \
                                and state2_values[label].symbol_pair() == MAX+ZER

        if state1.id == debug[0] and state2.id == debug[1]:
            print not(from_posneg_to_zerzer), not(from_pospos_to_maxzer)
        # if state1.id == debug[0] and state2.id == debug[1]:
        #     print from_posneg_to_zerzer
        if abs(derivative_change) == 1 and abs(magnitude_change) != 0:

            if not (from_posneg_to_zerzer or from_pospos_to_maxzer) or (changed_der_inflow and changed_der_volume):
                derivative_before_mag = False
                if state1.id == debug[0] and state2.id == debug[1]: print "Oeps5"
                break

        #Positive derivative can't lead to negative mag change, and vice versa
        if quantity.derivative == ZER and state2_values[label].magnitude != state1_values[label].magnitude:
            signs_mag_der = False
            if state1.id == debug[0] and state2.id == debug[1]: print "Oeps6"
            break
        if quantity.derivative == POS and magnitude_change < 0:
            signs_mag_der = False
            if state1.id == debug[0] and state2.id == debug[1]: print "Oeps7"
            break
        if quantity.derivative == NEG and magnitude_change > 0:
            if state1.id == debug[0] and state2.id == debug[1]: print "Oeps8"
            signs_mag_der = False
            break




        # You cannot change the inflow (derivative) during an instable point state,
        # eg. MAX+NEG or ZER+POS
    return (correct_follow_up and continuous and derivative_before_mag and signs_mag_der)

class Inflow:
    magnitude = None
    derivative = None
    mag_q_space = [ZER, POS]
    der_q_space = [NEG, ZER, POS]

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
    der_q_space = [NEG, ZER, POS]

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

class Height:
    magnitude = None
    derivative = None
    mag_q_space = [ZER, POS, MAX]
    der_q_space = [NEG, ZER, POS]

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

class Pressure:
    magnitude = None
    derivative = None
    mag_q_space = [ZER, POS, MAX]
    der_q_space = [NEG, ZER, POS]

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
    der_q_space = [NEG, ZER, POS]

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
    id = None
    volume = None
    height = None
    pressure = None
    outflow = None
    inflow = None

    def set_id(self, id):
        self.id = id

    def instable_quantities(self):
        quants = []

        for label, quantiy in self.get_state().iteritems():
            if quantiy.symbol_pair() in [MAX+NEG, ZER+POS]:
                quants.append(label)

        return quants

    def get_state(self):
        return {
            "volume" : self.volume,
            "outflow" : self.outflow,
            "height" : self.height,
            "pressure" : self.pressure,
            "inflow" : self.inflow
        }

    def __str__(self):
        pretty_print = "id" +str(self.id)+"  | M | D \n" \
                       "Inflow:   | " + self.inflow.magnitude + "  | " + self.inflow.derivative + "\n" \
                       "Volume:   | " + self.volume.magnitude + "  | " + self.volume.derivative + "\n" \
                       "Height:   | " + self.height.magnitude + "  | " + self.height.derivative + "\n" \
                       "Pressure: | " + self.pressure.magnitude + " | " + self.pressure.derivative + "\n"\
                       "Outflow:  | " + self.outflow.magnitude + "  | " + self.outflow.derivative + "\n"
        return pretty_print

    def __init__(self, inf, outf, vol, hght, press):
        self.volume = vol
        self.height = hght
        self.pressure = press
        self.outflow = outf
        self.inflow = inf

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_state() == other.get_state()
        else:
           return False

    def __ne__(self, other):
        return not self.__eq__(other)

def create_state_graph(components, relations):
    u = Digraph()

    point_states = []

    for state in components:
        if state.instable_quantities():
            point_states.append(str(state.id))
        u.node(str(state.id), str(state))

    for transition in relations:
        u.edge(str(transition[0].id), str(transition[1].id))

    styles = {
        'graph': {
            'rankdir':'UD',
            'center':'true',
            'margin':'0.2',
            'nodesep':'0.1',
            'ranksep':'0.3',
        },
        'stablenode': {
            'fontname': 'Courier',
            'fontsize': '12',
            'shape': 'box',
            'width': '.3',
        },
        'unstablenode': {
            'fontname': 'Courier',
            'fontsize': '10',
            'shape': 'box',
            'color': 'lightgrey',
            'width': '.3',
        },
        'activeedge': {
            'fontname': 'Courier',
            'fontsize': '10',
        },
        'passiveedge': {
            'fontname': 'Courier',
            'fontsize': '10',
            'color': 'lightgrey',
        }
    }

    u.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    u.save("graph.gv")

def main():

    states = generate_all_states()
    valid_states = list(filter(lambda x: valid_state(x.get_state()), states))

    # for i, state in enumerate(valid_states):
    #     state.set_id(i + 1)

    valid_transitions = []
    counter =0
    for state1, state2 in itertools.combinations(valid_states, 2):

        if valid_transition(state1, state2):
            valid_transitions.append( (state1, state2) )
        if valid_transition(state2, state1):
            valid_transitions.append( (state2, state1) )

    create_state_graph(valid_states, valid_transitions)

if __name__ == '__main__':
	main()
