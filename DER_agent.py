from scpi.handler import SCPI
from agents.gen_agent import generic_agent





# measure everything
# something to recv



scpi = SCPI()
DER_agent = generic_agent('file.json')
print(DER_agent.get_state())
