import json

# agent's possible states
STATES = {
        0 : 'unplugged',
        1 : 'charging',
        2 : 'fully charged'
}

class generic_agent:
    def __init__(obj, in_file):
        '''
            params: 
                * file that contains information about the behavior of the agent
            return:
                None
        '''
        obj.in_file = in_file
        obj.state = 0 # starts unplugged
        return
    def read_file(self):
        '''
            params:
                None
            return:
                * contents of the json file
            function:
                * reads content of json file and returns content
        '''
        with open(self.in_file,'r') as f:
            content = json.load(f)
        self.info = content
        return content
    def get_state(self):
        '''
            params:
                None
            return:
                * current state of agent
        '''
        return STATES[self.state]
