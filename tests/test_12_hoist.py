from jsplab.core import *
from jsplab.cbd import GameObject,EventManager
def on_arrived(s:IState):
    print(s.hoist.x,s.hoist.y)   


def test_transfer():
    center=EventManager()
    center.subscribe('on_hoist_at_top',on_arrived)
    center.subscribe('on_hoist_at_bottom',on_arrived)
    demo=GameObject()
    h=demo.add_component(Hoist)
    h.center=center
    h.x=0
    h.y=0
    h.fsm.add_state(FreeState(h))
    h.fsm.add_state(MovingState(h))
    h.fsm.add_state(LoweringState(h))
    h.fsm.add_state(LiftingState(h))
    h.fsm.set_state('FreeState')
   
    for i in range(1,60):
        print('*'*5+str(i)+'*'*5)
        if i==5:
            h.cmd=TransportCommand(3,6)
        if i==30:
            h.cmd=ShiftCommand(2)
        demo.update(1,i+1)
    assert 2==h.x and 0==h.y