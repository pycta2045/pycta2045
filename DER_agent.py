from agents.scpi.handler import SCPI
from agents.gen_agent import generic_agent
from agents.cta2045.handler import command_handler
from agents.com.handler import COM



# measure everything
# something to recv



# scpi = SCPI()
# r = scpi.send('lock screen')
# DER_agent = generic_agent('file.json')
# print(DER_agent.get_state())
# cta = command_handler(fname="agents/cta2045/CTA2045_commands.json")
# cmds = cta.dump_commands()
# shed = cta.get("shed")
# print(cmds)
# print(f'shed: {shed}')
# # DER_agent.charge()

print('--')
com = COM()