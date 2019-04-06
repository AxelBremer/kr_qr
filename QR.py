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
        possible.append(params['IQ'])
    if params['ID'] == 1:
        possible.append(1)
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
            possible += [0]
        else:
            possible += [1]
    # Afther that the tap can be kept running or be closed more. But never get opened again.
    if params['ID'] == 0:
        possible = possible + [-1,0]
    if params['ID'] == -1:
        possible = possible + [-1,0]

    return possible

def next_vq(params):
    """
    Returns all possible next values of vq given the current parameters.
    """
    #possible = [0, 1]
    possible = []
    # if the derivative was 0, q stays the same
    if params['VD'] == 0:
        possible.append(params['VQ'])
        
    # If the derivative was plus
    elif params['VD'] == 1:
        # 0 becomes 1
        if params['VQ'] == 0:
            possible.append(1)
        # 1 becomes 1 or 2
        elif params['VQ'] == 1:
            possible = possible + [1,2]
        # 2 stays 2
        elif params['VQ'] == 2:
            possible.append(2)
    
    elif params['VD'] == -1:
        # 0 stays 0
        if params['VQ'] == 0:
            possible.append(0)
        # 1 becomes 0 or 1
        elif params['VQ'] == 1:
            possible = possible + [0,1]
        # 2 becomes 1 or 2
        elif params['VQ'] == 2:
            possible = possible + [1,2]
    
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
            possible.append(-1)
        # No outflow is zero vd
        else:
            possible.append(0)
    
    # If there is inflow
    elif(new_params['IQ'] == 1):
        # without outflow, vd is 1
        if(new_params['OQ'] == 0):
            possible.append(1)
            
    
    return possible
    
#print(next_vq(s.get_all_params()))




def successor_states(graph, stack, state, infd):
    
    params = state.get_all_params()
    state_counter = state.id+1

    new_state = State({'ID':0,'IQ':0,'VD':0,'VQ':0,'OD':0,'OQ':0}, 0)
    new_state.params['ID'] = infd

    successor_iqs = next_iq(params)
    successor_vqs = next_vq(params)

    for iq  in successor_iqs:
        new_state.params['IQ'] = iq
        for vq in successor_vqs:
          
            new_state.params['VQ'] = vq
            new_state.params['OQ'] = vq

            successor_vds = next_vd(new_state.params)

            for vd in successor_vds:
                new_state.params['VD'] = vd
                new_state.params['OD'] = vd


                if new_state == state:
                    continue
                else:
                    if new_state not in graph[state]:
                        if new_state in graph.keys():
                            if state in graph[new_state]:
                                continue
                        new_state.id = state_counter
                        graph[state] += [new_state]
                        state_counter += 1
                        stack.append(new_state)



def add_successor_states(graph, searched, stack, infd):
    while len(stack) > 0:
        state = stack.pop()
        if state not in searched:
            searched.append(state)
            if state not in graph.keys():
                graph[state] = []
            successor_states(graph, stack, state, infd)

def get_states():
    s = {'ID':[-1,0,1],'IQ':[0,1],'VD':[-1,0,1],'VQ':[0,1,2],'OD':[-1,0,1],'OQ':[0,1,2]}
    combs = [dict(zip(s, v)) for v in product(*s.values())]
    toremove = []
    for s in combs:
        # exogenous behaviour: only turn tap at start
        if s['ID'] == 1 and s['IQ'] == 0 and s['VQ'] != 0:
            if s not in toremove:
                toremove.append(s)
        if s['VQ'] != s['OQ']:
            if s not in toremove:
                toremove.append(s)
        if s['VD'] != s['OD']:
            if s not in toremove:
                toremove.append(s)
        if s['IQ'] == 0 and s['ID'] == -1:
            if s not in toremove:
                toremove.append(s)
        if s['VQ'] == 0 and s['VD'] == -1:
            if s not in toremove:
                toremove.append(s)
        if s['OQ'] == 0 and s['OD'] == -1:
            if s not in toremove:
                toremove.append(s)
        if s['IQ'] == 0 and s['VD'] == 1:
            if s not in toremove:
                toremove.append(s)
        if s['IQ'] == 0 and s['OQ'] > 0 and s['VD'] != -1:
            if s not in toremove:
                toremove.append(s)
        if s['IQ'] == 1 and s['OQ'] == 0 and s['VD'] != 1:
            if s not in toremove:
                toremove.append(s)

    for s in toremove:
        combs.remove(s)

    return combs

def get_transitions(states):
    numstates = len(states)
    state_ids = list(range(0, numstates))
    transitions = list(permutations(state_ids, 2))
    return transitions

def plausible_transitions(states, transitions):
    toremove = []

    for i in transitions:
        prev_state = states[i[0]]
        next_state = states[i[1]]
        
        if i == (4,5):
            print(prev_state)
            print(next_state)

        if(next_state['IQ'] not in next_iq(prev_state)):
            if i not in toremove:
                if i == (4,5): print(1)
                toremove.append(i)
        if(next_state['VQ'] not in next_vq(prev_state)):
            if i not in toremove:
                if i == (4,5): print(2)
                toremove.append(i)
        if(next_state['ID'] not in next_id(prev_state)):
            if i not in toremove:
                if i == (4,5): print(3)
                toremove.append(i)

    for s in toremove:
        transitions.remove(s)
    print("Transitions left after plausible_transitions: ",len(transitions))
    return transitions

def is_instant(prev, new):
    if prev != new:
        if new == 1:
            return 'instant'
        else:
            return 'not-instant'
    return 'neither'

def epsilon_ordering(states, transitions):
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
    print("Transitions left after epsilon_ordering: ",len(transitions))
    return transitions

def state_to_string(i,s):
    string = str(i)
    string += "\nInflow: (d:" + d_name[s['ID']] + ", q:" + q_name[s['IQ']] + ")\n"
    string += "Volume: (d:" + d_name[s['VD']] + ", q:" + q_name[s['VQ']] + ")\n"
    string += "Outflow: (d:" + d_name[s['OD']] + ", q:" + q_name[s['OQ']] + ")\n"
    return string

def create_graph(states, transitions):
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
    transitions = plausible_transitions(states, transitions)
    transitions = epsilon_ordering(states, transitions)

    create_graph(states, transitions)

if __name__ == '__main__':
    main()