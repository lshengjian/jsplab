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
    tran.x1=10
    tran.x2=12
    tran.x=8
    for i in range(10):
        demo.update(1,i+1)
    assert 10==tran.x
    tran.carring=True
    demo.set_component_enable(Transfer,False)
    for i in range(10,20):
        demo.update(1,i+1)
    assert 10==tran.x
    demo.set_component_enable(Transfer,True)
    for i in range(20,30):
        demo.update(1,i+1)
    assert 12==tran.x
    tran.carring=False
    for i in range(30,40):
        demo.update(1,i+1)
    assert 10==tran.x