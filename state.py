class State:
    """
    Has an integer id.
    Has a list of states it can go to containing their id's.
    Contains 6 parameters, in a parameter list. 
    Inflow:
        params[ID] Derivative: -, 0, +
        params[IQ] Quantity: 0, +
    Volume:
        params[VD] Derivative: -, 0, +
        params[VQ] Quantity: 0, +, max
    Outflow:
        params[OD] Derivative: -, 0, +
        params[OQ] Quantity: 0, +, max
        
    -   = -1
    0   =  0
    +   =  1
    max =  2
    """
    
    def __init__(self, given_params, given_id):
        self.id = given_id
        self.params = given_params
        
    def get_param(self, name):
        return self.params[name]
        
    def get_all_params(self):
        return self.params
        
    def get_id():
        return self.id
        
    def set_id(id):
        self.id = id
        
    def set_param(self, name, value):
        self.params[name] = value
        
    def get_id(self, name):
        return self.id
