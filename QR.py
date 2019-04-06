'''
Axel Bremer: 2656186
Rochelle Choenni:
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
            possible = possible + [0,1]
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
            possible = [1,2]
    
    return possible
    
def next_vd(new_params):
    """
    Returns all possible next values of vd given the current parameters.
    """
    possible = []
    
    # No inflow quantity
    if(new_params['IQ'] == 0):
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
    print("Transitions: ",len(transitions))
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

    
    dot.render('test-output/container')
    return 

def main():
    states = get_states()
    print('Number of states:',len(states))
    transitions = get_transitions(states)
    create_graph(states, transitions)

if __name__ == '__main__':
    main()