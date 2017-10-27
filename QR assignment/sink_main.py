import itertools
from graphviz import Digraph
import tempfile
import sys

sys.path.append("/usr/local/lib/graphviz/")
#TODO: verwijder onderstaande counter #patch
counter =0
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


def interstate_tap_change(state1,state2):

    state1_values = state1.get_state()
    state2_values = state2.get_state()

    if state1_values["inflow"].derivative == POS and state2_values["inflow"].derivative == ZER:
        return "The tap stopped being opened any further"

    if state1_values["inflow"].derivative == ZER and state2_values["inflow"].derivative == POS:
        return "The tap started to be opened"

    if state1_values["inflow"].derivative == ZER and state2_values["inflow"].derivative == NEG:
        return "The tap started to be closed"

    if state1_values["inflow"].derivative == NEG and state2_values["inflow"].derivative == ZER:
        return "The tap stopped being closed any further"
    else:
        return "There is no change in how much water comes out of the tap"

def interstate_magnitude_change_volume_and_outflow(state1,state2):
# TODO: Nog inflow in de text verwerken?
    state1_values = state1.get_state()
    state2_values = state2.get_state()

    if state1_values["volume"].magnitude == POS and state2_values["volume"].magnitude == ZER:
        return "the sink ran empty"

    if state1_values["volume"].magnitude == ZER and state2_values["volume"].magnitude == POS:
        return "the sink starts to fill up"

    if state1_values["volume"].magnitude == MAX and state2_values["volume"].magnitude == POS:
        return "the sink started to lose some water from it's maximum"

    if state1_values["volume"].magnitude == POS and state2_values["volume"].magnitude == MAX:
        return "the sink filled up to it's maximum"
    else:
        return "the volume and the outflow did not change"


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

    # corner cases
    # if state1.id == 3 and state2.id == 7:
    #     return True
    # if state1.id == 23 and state2.id == 20:
    #     return False
    # if state1.id == 12 and state2.id == 21:
    #     return False
    # if state1.id == 3 and state2.id == 12:
    #     return False
    # if state1.id == 14 and state2.id == 2:
    #     return False
    # if state1.id == 14 and state2.id == 20:
    #     return False
    # if state1.id == 20 and state2.id == 14:
    #     return False
    # if state1.id == 8 and state2.id == 2:
    #     return False
    # if state1.id == 2 and state2.id == 8:
    #     return False


    debug = (2,0)

    # if instable state => go to stable state
    correct_follow_up = True
    changed_der_inflow = state1_values["inflow"].derivative != state2_values["inflow"].derivative
    changed_der_volume = state1_values["volume"].derivative != state2_values["volume"].derivative

    # Also instable Patch  23->20, 14->20 (probably not needed anymore)
    #state_information = self.get_state()
    # if state1_values['volume'].derivative == ZER and state1_values['inflow'].magnitude == POS\
    #         and state2_values['volume'].derivative:
    #     return False


    # # patch 14->11 2->8 (instable states)
    volume_derivative_change = index_distance(state1_values['volume'].der_q_space,
                                              state1_values['volume'].derivative,
                                              state2_values['volume'].derivative)

    # patch ctd. : If not in an equilibrium (2->0) or at maximum volume (..->..),
    #  a positive magnitude of the inflow should result in a positive derivative of the volume
    if volume_derivative_change < 0 and state1_values['inflow'].magnitude == POS \
            and state2_values['volume'].magnitude != MAX and state1_values['volume'].derivative != ZER:
        if state1.id == debug[0] and state2.id == debug[1]: print "oeps12"
        return False
    #
    # patch Daan rule extension (14->20, 8->2):
    if volume_derivative_change > 0 and state1_values['inflow'].magnitude == POS \
            and state1_values['inflow'].derivative != state2_values['inflow'].derivative:
        return False



    # If instable point state, the next state should be the stable correct follw up state
    for quantity in state1.instable_quantities():
        if state2.get_state()[quantity].magnitude != POS:
            correct_follow_up = False
            if state1.id == debug[0] and state2.id == debug[1]: print "Oeps1"
            break
        if changed_der_inflow:
            correct_follow_up = False
            if state1.id == debug[0] and state2.id == debug[1]: print "Oeps2"
            break



    # Might be not necessary anymore

    # # if inflow and outflow are at an equilibrium, but the derivative of the inflow is not zero,
    # # The derivative of the magnitude should be the derivative of the inflow in the next state.
    # if state1_values["inflow"].derivative != ZER and state1_values["volume"].derivative == ZER \
    #         and state2_values["volume"].derivative != state1_values["inflow"].derivative and\
    #         (state1_values["volume"].symbol_pair()!= MAX+ZER):
    #         if state1.id == debug[0] and state2.id == debug[1]:
    #             print "Oeps madderfakking 10"
    #         return False
    #
    # # getting 252->342 out
    # if state1_values["inflow"].derivative == ZER and state1_values["volume"].derivative == ZER \
    #         and state2_values["volume"].derivative != state1_values["inflow"].derivative:
    #     if state1.id == debug[0] and state2.id == debug[1]:
    #         print "Oeps madderfakking 11"
    #     return False




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
        #Patch
        # from_maxzer_to_maxneg= state1_values[label].symbol_pair() == MAX+ZER \
        #                         and state2_values[label].symbol_pair() == MAX+NEG
        # from_poszer_to_pospos= state1_values[label].symbol_pair() == POS+ZER \
        #                         and state2_values[label].symbol_pair() == POS+POS


        # if state1.id == debug[0] and state2.id == debug[1]:
        #     print from_posneg_to_zerzer
        #TODO: global counter weghalen
        # global counter


        # magnitude cannot change if derivative = ZER
        if abs(magnitude_change) == 1 and  state1_values[label].derivative == ZER:

            #TODO: Onderstaande if kan hierdoor weg, je kunt dit checken met de counter
            # if not (from_posneg_to_zerzer or from_pospos_to_maxzer) or (changed_der_inflow and changed_der_volume):
                # counter += 1
                # print counter
                derivative_before_mag = False
                if state1.id == debug[0] and state2.id == debug[1]:
                    print "Oeps5"
                    print from_posneg_to_zerzer
                    print from_pospos_to_maxzer
                    print from_posneg_to_zerzer or from_pospos_to_maxzer
                    print not (from_posneg_to_zerzer or from_pospos_to_maxzer)
                    print changed_der_inflow and changed_der_volume
                    print not (from_posneg_to_zerzer or from_pospos_to_maxzer) or (changed_der_inflow and changed_der_volume)

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

        pretty_print = "id: " +str(self.id)+"  | M | D \n" \
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

def state_difference(state1, state2):
    diff = {}
    for label, value in state1.get_state().iteritems():
        der_change = index_distance(value.der_q_space, value.derivative, state2.get_state()[label].derivative)
        mag_change = index_distance(value.mag_q_space, value.magnitude, state2.get_state()[label].magnitude)
        diff[label] = (mag_change, der_change)

    return diff

def describe_intrastate(state):

    translation_derivative = {
        "sink" : {
            POS : "increasing",
            ZER : "steady",
            NEG : "decreasing"
        },
        "tap" : {
            POS : "opening",
            ZER : "idle",
            NEG : "closing"
        }
    }

    translation_magnitude = {
        "sink" : {
            MAX : "full",
            POS : "filled but not full",
            ZER : "empty"
        },
        "tap" : {
            POS: "opened",
            ZER: "closed"
        }
    }

    translation_explanation = {
        POS : "there is more water coming out of the tap than is going through the drain",
        ZER : "exactly the same amount of water is going down the drain as is coming in from the tap",
        NEG : "there is more water going out of the drain than is coming trough the tap"
    }

    intra_tap = "the tap is " + translation_magnitude["tap"][state.inflow.magnitude] + \
                ", and " + translation_derivative["tap"][state.inflow.derivative]
    level_sink = "The sink is " + translation_magnitude["sink"][state.volume.magnitude]
    intra_sink = "This level is " + translation_derivative["sink"][state.volume.derivative] + \
           " because " + translation_explanation[state.volume.derivative]

    return intra_tap + ". " + level_sink + ". " + intra_sink

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


    u.save('graph.gv')

def remove_weird_states(states):
    weird_ids = [18, 16, 4, 13]
    for state in states:
        if state.id in weird_ids:
            states.remove(state)


def main():

    states = generate_all_states()
    valid_states = list(filter(lambda x: valid_state(x.get_state()), states))

    for i in range(len(valid_states)):
        valid_states[i].set_id(i)

    remove_weird_states(valid_states)

    valid_state_ids = list(map(lambda x: str(x.id), valid_states))

    valid_transitions = []
    counter = 0
    for state1, state2 in itertools.combinations(valid_states, 2):

        if valid_transition(state1, state2):
            valid_transitions.append( (state1, state2) )
        if valid_transition(state2, state1):
            valid_transitions.append( (state2, state1) )

    valid_transition_ids = list(map(lambda x: (str(x[0].id), str(x[1].id)), valid_transitions))

    create_state_graph(valid_states, valid_transitions)

    while True:
        print "Do you want an interstate explanation or an intrastate explanation?"
        choice = 0
        while choice not in ["inter", "intra"]:
            choice = raw_input("Type 'inter' or 'intra': ")

            if choice == 'inter':
                print "Look at the state graph and enter the id's of the states you want to compare"
                from_state = None
                to_state = None

                while True:

                    while from_state not in valid_state_ids:
                        from_state = raw_input("From state: ")

                    while to_state not in valid_state_ids or to_state == from_state:
                        to_state = raw_input("To state: ")

                    if (from_state, to_state) in valid_transition_ids:
                        break
                    else:
                        from_state = 0
                        to_state = 0

                from_state_obj = valid_states[int(from_state)]
                to_state_obj = valid_states[int(to_state)]
                print "In the first state", describe_intrastate(from_state_obj)
                print interstate_tap_change(from_state_obj, to_state_obj)
                print "Furthermore, ", interstate_magnitude_change_volume_and_outflow(from_state_obj, to_state_obj)
                print "In the following state", describe_intrastate(to_state_obj)

            if choice == 'intra':
                state = 0
                while state not in valid_state_ids:
                    print "Look at the state graph and enter the id of the state you want to inspect"
                    state = raw_input("id: ")

                state_obj = valid_states[int(state)]
                print "In this state", describe_intrastate(state_obj)

            print
            print "----------------------------"
            print

if __name__ == '__main__':
	main()
