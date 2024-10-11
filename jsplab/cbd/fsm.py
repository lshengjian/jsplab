from typing import Protocol,List
from .base import Component
class IState(Protocol):

    def enter(self):
        """状态进入时调用"""
        ...

    def exit(self):
        ...

    def update(self,delta_time:float,total_time):
        """状态更新，每帧调用"""
        ...

class FSM:
    """状态机组件，管理和切换不同的状态"""
    def __init__(self):
        self.states :List[IState]= {}
        self.current_state :IState= None

    def add_state(self, state:IState):
        name=state.__class__.__name__
        self.states[name] = state    
    def set_state(self, state_name):
        if state_name in self.states:
            if self.current_state:
                self.current_state.exit()
            self.current_state = self.states.get(state_name,None)
            if self.current_state is not None:
                self.current_state.enter()

    def update(self,delta_time:float=1,total_time=1):
        if self.current_state:
            self.current_state.update(delta_time,total_time)