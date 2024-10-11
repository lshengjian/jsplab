from jsplab.core import Transfer
from jsplab.cbd import GameObject,EventManager
def on_arrived(com:Transfer):
    print(com.x)

if __name__ == "__main__":
    center=EventManager()
    center.subscribe('on_arrived',on_arrived)
    demo=GameObject()
    com=demo.add_component(Transfer)
    com.center=center
    com.x1=0
    com.x2=10
    com.x=8
    for i in range(10):
        demo.update(1,i+1)
    com.carring=True
    #demo.set_component_enable(Transfer,False)
    for i in range(10,20):
        demo.update(1,i+1)
    

