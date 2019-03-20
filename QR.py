from state import State

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
    
print(next_vq(s.get_all_params()))