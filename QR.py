from state import State
from itertools import product

state_counter = 0

s = State({'ID':1,'IQ':0,'VD':1,'VQ':1,'OD':0,'OQ':0}, state_counter)

def next_iq(params):
    """
    Returns all possible next values of iq given the current parameters.
    """
    #possible = [0, 1]
    possible = []
    if params['ID'] == 0:
        possible.append(params['IQ'])
    if params['ID'] == 1:
        possible.append(1)
    if params['ID'] == -1:
        possible.append(0)
    
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
        # 1 becomes 1 or 2
        elif params['VQ'] == 1:
            possible = possible + [0,1]
        # 2 becomes 1
        elif params['VQ'] == 2:
            possible.append(1)
    
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

def get_all_combinations():
    s = {'ID':[-1,0,1],'IQ':[0,1],'VD':[-1,0,1],'VQ':[0,1,2],'OD':[-1,0,1],'OQ':[0,1,2]}
    combs = [dict(zip(s, v)) for v in product(*s.values())]
    print(len(combs))
    toremove = []
    for s in combs:
        if s['VQ'] != s['OQ']:
            if s not in toremove:
                toremove.append(s)
        if s['VD'] != s['OD']:
            if s not in toremove:
                toremove.append(s)
        if s['IQ'] == 0 and s['ID'] != 0:
            if s not in toremove:
                toremove.append(s)
        if s['VQ'] == 0 and s['VD'] != 0:
            if s not in toremove:
                toremove.append(s)
        if s['OQ'] == 0 and s['OD'] != 0:
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
    print(len(combs))
    for s in combs:
        print(s)

def main():
    # state_graph = {}    
    # # Empty container
    # empty = State({'ID':0,'IQ':0,'VD':0,'VQ':0,'OD':0,'OQ':0}, state_counter)
    # stack = [empty]
    # searched = []
    # # Inflow increasing
    # infd = 1
    # add_successor_states(state_graph, searched, stack, infd)

    # for state in state_graph:
    #     print("ID: ", state.id)

    #     print("State: ", state.get_all_params())
    get_all_combinations()

if __name__ == '__main__':
    main()