'''
Axel Bremer: 2656186
Rochelle Choenni: 2656454
Creates a state transition graph by using qualitative reasoning about a container system.
Dependencies: "pip install graphviz" and "sudo apt-get install graphviz"
'''
from itertools import product
from itertools import permutations
from graphviz import Digraph
import os

os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

state_counter = 0

d_name = {0:'0', -1:'-', 1:'+'}
q_name = {0:'0', 1:'+', 2:'Max'}

def next_iq(params):
    """
    Returns all possible next values of iq given the current parameters.
    """
    possible = []
    if params['ID'] == 0:
        possible = [params['IQ']]
    if params['ID'] == 1:
        possible = [1]
    if params['ID'] == -1:
        if params['IQ'] == 1:
            possible = [0,1]
        if params['IQ'] == 0:
            possible = [0]
    
    return possible

def next_id(params):
    """
    Returns all possible next values of id given the current parameters. The exogenous behaviour 
    programmed in is opening the tap and only being able to close it once the container is full.
    """
    possible = []
    # If the container is full you can stop opening the tap.
    if params['ID'] == 1:
        if params['VQ'] == 2:
            possible = [0]
        else:
            possible = [1]
    # Afther that the tap can be kept running or be closed more. But never get opened again.
    if params['ID'] == 0:
        possible = [-1,0]
    if params['ID'] == -1:
        possible = [-1,0]

    return possible

def next_vq(params):
    """
    Returns all possible next values of vq given the current parameters.
    """
    #possible = [0, 1]
    possible = []
    # if the derivative was 0, q stays the same
    if params['VD'] == 0:
        possible = [params['VQ']]
        
    # If the derivative was plus
    elif params['VD'] == 1:
        # 0 becomes 1
        if params['VQ'] == 0:
            possible = [1]
        # 1 becomes 1 or 2
        elif params['VQ'] == 1:
            possible = [1,2]
        # 2 stays 2
        elif params['VQ'] == 2:
            possible = [2]
    
    elif params['VD'] == -1:
        # 0 stays 0
        if params['VQ'] == 0:
            possible = [0]
        # 1 becomes 0 or 1
        elif params['VQ'] == 1:
            possible = [0,1]
        # 2 becomes 1 or 2
        elif params['VQ'] == 2:
            possible = [1]
    
    return possible
    
def next_vd(new_params):
    """
    Returns all possible next values of vd given the current parameters.
    """
    possible = []

    # Don't let the sink overflow
    if(new_params["VQ"] == 2):
        possible = [0]

    
    # No inflow quantity
    elif(new_params['IQ'] == 0):
        # With outflow is negative vd
        if(new_params['OQ'] in [1,2]):
            possible = [-1]
        # No outflow is zero vd
        else:
            possible = [0]
    
    # If there is inflow
    elif(new_params['IQ'] == 1):
        # without outflow, vd is 1
        if(new_params['OQ'] == 0):
            possible = [1]
            
    
    return possible

def get_states():
    '''
    First generates each possible state given the quantity and derivative space. It then truncates
    the state space by deleting impossible states given the dependencies and exogenous behaviour.
    '''
    s = {'ID':[-1,0,1],'IQ':[0,1],'VD':[-1,0,1],'VQ':[0,1,2],'OD':[-1,0,1],'OQ':[0,1,2]}
    combs = [dict(zip(s, v)) for v in product(*s.values())]
    toremove = []
    for s in combs:
        # exogenous behaviour: only turn tap at start
        if s['ID'] == 1 and s['IQ'] == 0 and s['VQ'] != 0:
            if s not in toremove:
                toremove.append(s)
        # correspondence of max and 0 of volume and outflow
        if s['VQ'] != s['OQ']:
            if s not in toremove:
                toremove.append(s)
        # proportionality volume to outflow
        if s['VD'] != s['OD']:
            if s not in toremove:
                toremove.append(s)
        # The derivative cannot be -1 if the quantity is 0
        if s['IQ'] == 0 and s['ID'] == -1:
            if s not in toremove:
                toremove.append(s)
        if s['VQ'] == 0 and s['VD'] == -1:
            if s not in toremove:
                toremove.append(s)
        if s['OQ'] == 0 and s['OD'] == -1:
            if s not in toremove:
                toremove.append(s)
        # Direct influence: Volume derivative cannot be 1 if inflow quantity is 0
        if s['IQ'] == 0 and s['VD'] == 1:
            if s not in toremove:
                toremove.append(s)
        
        # Direct influence: Volume derivative has to be -1 if outflow is positive and there is no inflow
        if s['IQ'] == 0 and s['OQ'] > 0 and s['VD'] != -1:
            if s not in toremove:
                toremove.append(s)

        # Direct influence: Volume derivative has to be 1 if inflow is positive and there is no outflow
        if s['IQ'] == 1 and s['OQ'] == 0 and s['VD'] != 1:
            if s not in toremove:
                toremove.append(s)
        
    for s in toremove:
        combs.remove(s)

    return combs

def get_transitions(states):
    '''
    Generates all possible state transitions and then deletes the ones that are impossible.
    '''
    numstates = len(states)
    state_ids = list(range(0, numstates))
    transitions = list(permutations(state_ids, 2))
    transitions = plausible_transitions(states, transitions)
    transitions = epsilon_ordering(states, transitions)
    return transitions

def plausible_transitions(states, transitions):
    '''
    Removes the impossible transitions by checking the iq, vq and id value transitions.
    '''
    toremove = []

    for i in transitions:
        prev_state = states[i[0]]
        next_state = states[i[1]]

        if(next_state['IQ'] not in next_iq(prev_state)):
            if i not in toremove:
                toremove.append(i)
        if(next_state['VQ'] not in next_vq(prev_state)):
            if i not in toremove:
                toremove.append(i)
        if(next_state['ID'] not in next_id(prev_state)):
            if i not in toremove:
                toremove.append(i)

        # Don't let the sink overflow
        if(prev_state['VQ'] == 2 and next_state['VD'] == 1):
            if i not in toremove:
                toremove.append(i)

    for s in toremove:
        transitions.remove(s)
    return transitions

def is_instant(prev, new):
    '''
    Returns if a certain transition is instant or not.
    '''
    if prev != new:
        if new == 1:
            return 'instant'
        else:
            return 'not-instant'
    return 'neither'

def epsilon_ordering(states, transitions):
    '''
    Removes every state transition that does not follow epsilon ordering.
    If a transition has both an instant and a not instant transition it is impossible.
    '''
    toremove = []

    for t in transitions:
        prev_state = states[t[0]]
        next_state = states[t[1]]

        i = is_instant(prev_state['IQ'], next_state['IQ'])
        v = is_instant(prev_state['VQ'], next_state['VQ'])
        o = is_instant(prev_state['OQ'], next_state['OQ'])

        l = [i,v,o]
        
        if 'instant' in l and 'not-instant' in l:
            toremove.append(t)

    for t in toremove:
        transitions.remove(t)
    return transitions

def state_to_string(i,s):
    '''
    Prints the state in a readable format.
    '''
    string = str(i)
    string += "\nInflow: (d:" + d_name[s['ID']] + ", q:" + q_name[s['IQ']] + ")\n"
    string += "Volume: (d:" + d_name[s['VD']] + ", q:" + q_name[s['VQ']] + ")\n"
    string += "Outflow: (d:" + d_name[s['OD']] + ", q:" + q_name[s['OQ']] + ")\n"
    return string

def create_graph(states, transitions):
    '''
    Creates the actual dot graph and saves it to disk.
    '''
    dot = Digraph(comment='Container')
    dot.node('r2', label='Start by turning on tap')
    
    for i,s in enumerate(states):
        dot.node(str(i), state_to_string(i,s))

    dot.edge('r2', '17')
    
    for t in transitions:
        dot.edge(str(t[0]), str(t[1]))

    
    dot.render('output/container')
    return 

def intrastate(states, state_id):
    state = states[state_id]
    D = ["ID", "VD", "OD"]
    print("In:\n")
    print(state_to_string(state_id, state))
    print("The following intrastate changes happen: ")
    for d in D:
        if(d == "ID"):
            if(state[d] == 1):
                print("-  Inflow derivative is positive in this state (i.e. open the tap more).")
            if(state[d] == 0):
                print("-  Inflow derivative is zero so the quantity remains steady (i.e. the tap is not altered again).")
            if(state[d] == -1): 
                print("-  Inflow derivative is negative in this state (i.e. tap is closed more)")
        if(d == "VD"):
            if(state['IQ'] == 1 and (state["OQ"] == 1 or state["OQ"] == 2)):
                print("-  Inflow and outflow quantities in this state are both positive so the volume derivative could be anything.")
                if (state[d] == 0):
                    print("   In this case it is 0, thus the inflow quantity was equal to the outflow quantity. ")
                elif(state[d] == 1):
                    print("   In this case it is 1, thus the inflow quantity was larger than the outflow quantity. ")
                elif(state[d] == -1):
                    print("   In this case it is -1, thus the outflow quantity was larger than the inflow quantity. ")
            if(state['IQ'] == 0 and (state["OQ"] == 1 or state["OQ"] == 2)):
                print("-  Inflow quantity is 0 while the outflow quantity is positive, thus the volume derivative becomes negative.")
            if(state['IQ'] == 0 and state["OQ"] == 0):
                print("-  Inflow and outflow quantities are both 0, thus the volume derivative becomes 0 as well.")
            if(state['IQ'] == 1 and state["OQ"] == 0):
                print("-  Inflow quantity is is positive while outflow is 0, thus the volume derivative becomes positive.")
        if(d == "OD"): 
            print("-  In this state, the volume derivative is ", state["VD"], ", thus because of the proportionality dependency the outflow derivative is as well.")
    if(state["VQ"] == 2):
            print('-  The volume and outflow quantity have reached their maximum, thus from here on the inflow derivative can not become positive again.')




def interstates(states, transition, transitions):
    if(transition not in transitions):
        print("There is no legal transition between these states.")
        return
    prev_state = states[transition[0]]
    next_state = states[transition[1]] 
    print("From:\n")
    print(state_to_string(transition[0], prev_state))
    print("To:\n")
    print(state_to_string(transition[1], next_state))
    Q = ["IQ", "VQ"]
    if(prev_state["IQ"] != next_state["IQ"] or prev_state["VQ"] != next_state["VQ"]):
        print("The following interstate changes happen: ")
        for q in Q:
                if(q == "IQ"):
                        if( (prev_state[q] == 0) and (next_state[q] == 1) ):
                            if(prev_state['ID'] == 1):
                                print("- ", q, "changes from: ", prev_state[q], ' to: ', next_state[q])
                                print("   Quantity of the inflow increases because in the previous state the inflow derivative was positive (i.e. tap gets opened more).")
                        if( (prev_state[q] == 1) and (next_state[q] == 0) ):
                            if(prev_state['ID'] == -1):
                                print('- ', q, "changes from: ", prev_state[q], ' to: ', next_state[q])
                                print("   Quantity of the inflow decreases because in the previous state the inflow derivative was negative (i.e. tap closed more).")
                if(q == "VQ"):
                        if( (prev_state[q] == 0) and (next_state[q] == 1) ):
                            if(prev_state['VD'] == 1):
                                print("- ", q, "changes from: ", prev_state[q], ' to: ', next_state[q])
                                print("   Quantity of the volume increases because in the previous state the volume derivative was positive (i.e. more water coming into the sink).")
                                print("- ", "OQ", "changes from: ", prev_state["OQ"], ' to: ', next_state["OQ"])
                                print("   Quantity of the outflow increases because in the previous state the outflow derivative was positive (i.e. more water getting into the drain).")

                        if( (prev_state[q] == 1) and (next_state[q] == 0) ):
                            if(prev_state['VD'] == -1):
                                print('- ', q, "changes from: ", prev_state[q], ' to: ', next_state[q])
                                print("   Quantity of the inflow decreases because in the previous state the inflow derivative was negative (i.e. less water coming into the sink).")
                                print("- ", "OQ", "changes from: ", prev_state["OQ"], ' to: ', next_state["OQ"])
                                print("   Quantity of the outflow decreases because in the previous state the outflow derivative was negative (i.e. less water getting into the drain).")
                        if( (prev_state[q] == 1) and (next_state[q] == 2) ):
                            if(prev_state['VD'] == 1):
                                print("- ", q, "changes from: ", prev_state[q], ' to: ', next_state[q])
                                print("   Quantity of the volume reaches its maximum because in the previous state the volume derivative was positive, while the volume quantity was already positive.")
                                print("- ", "OQ", "changes from: ", prev_state["OQ"], ' to: ', next_state["OQ"])
                                print("   Quantity of the outflow reaches its maximum because in the previous state the outflow derivative was positive, while the volume quantity was already positive.")
               
                        if( (prev_state[q] == 2) and (next_state[q] == 1) ):
                            if(prev_state['VD'] == -1):
                                print('- ', q, "changes from: ", prev_state[q], ' to: ', next_state[q])
                                print("   Quantity of the inflow is not at its maximum anymore because in the previous state the inflow derivative was negative.")
                                print("- ", "OQ", "changes from: ", prev_state["OQ"], ' to: ', next_state["OQ"])
                                print("   Quantity of the outflow is not at its maximum anymore because in the previous state the outflow derivative was negative.")

    else:
        print("Quantities do not change between these states.")


def main():
    states = get_states()
    transitions = get_transitions(states)
    create_graph(states, transitions)
    print('Number of states:',len(states))
    print('Number of transitions:',len(transitions))
    interstates(states, (23,21), transitions)
    intrastate(states, 12)



if __name__ == '__main__':
    main()