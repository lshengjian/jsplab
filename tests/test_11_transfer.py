from jsplab.core import Transfer
from jsplab.cbd import GameObject,EventManager
def on_arrived(com:Transfer):
    print(com.x)


def test_transfer():
    center=EventManager()
    center.subscribe('on_transfer_arrived',on_arrived)
    demo=GameObject()
    tran=demo.add_component(Transfer)
    tran.center=center
    tran.x1=0
    tran.x2=10
    tran.x=8
    for i in range(10):
        demo.update(1,i+1)
    assert 0==tran.x
    tran.carring=True
    #demo.set_component_enable(Transfer,False)
    for i in range(10,20):
        demo.update(1,i+1)
    assert 10==tran.x