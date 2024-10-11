from jsplab.cbd import *

class IdleState:
    def enter(self):
        print("Player is now idle.")
    def exit(self):
        pass
    def update(self,delta_time:float,total_time):
        pass

class RunState:
    def enter(self):
        print("Player is now run.")
    def exit(self):
        pass
    def update(self,delta_time:float,total_time):
        pass


# Simulate player taking damageplayer.take_damage(10)
def test_FSM():
    fsm = FSM()
    fsm.add_state(IdleState())
    fsm.add_state(RunState())

    # 设置初始
    fsm.set_state("IdleState")
    fsm.update()
    assert IdleState==type(fsm.current_state)  

    # 假设某个条件满足时切换
    fsm.set_state("RunState")
    assert RunState==type(fsm.current_state)  