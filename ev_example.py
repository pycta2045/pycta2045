from agents.models.ev_model import EV

ev = EV()
ev.charge(fname='pl')
print('start time: ',ev.time[0],"power :",ev.power[0])
print('in between',ev.power[30])
print('end time: ',ev.time[-1],"power: ",ev.power[-1])
print(ev.power)
