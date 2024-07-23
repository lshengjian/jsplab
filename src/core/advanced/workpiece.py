from .world_object import WorldObj
from typing import Dict
from .advanced.componets import *
from .advanced.shapes import get_workpiece_shape
from .advanced.rendering import set_color
class Workpiece(WorldObj):
    UID={}
    def __init__(self, product_code='A',x=0):
        self.timer=0
        self.product_code=product_code
        self.target_op_data:OpTimeData=None
        self.start_tick=0
        self.end_tick=0
        self.total_op_time=0
        super().__init__(x)

    @property
    def left_time(self):
        return self.end_tick-(self.total_op_time+self.start_tick)
    
    

    @property
    def state(self)->State:
        op_limit=self.target_op_data
        op_key=0 if  op_limit is None else op_limit.op_key
        duration=0 if  op_limit is None else op_limit.duration
        return State(NodeType.Operate,op_key,self.product_code,self.x ,self.y,duration)
        
    @staticmethod
    def make_new(code='A',x=0):
        rt=Workpiece(code,x)
        rt.inc_uid()
        return rt
    def __str__(self):
        return f'{self.product_code}-{self.id} ({self.x},{self.y})'
        


    def inc_uid(self):
        uid=Workpiece.UID.get(self.product_code,0)
        self.id=uid+1
        Workpiece.UID[self.product_code]=self.id

    def set_next_operate(self,pd:OpTimeData,ops_dict:Dict[int,OperateData]):
        self.target_op_data=pd
        self.color=ops_dict[pd.op_key].color


    @property
    def image(self):
        img=get_workpiece_shape(self.product_code)
        r,g,b=self.color.rgb
        img=set_color(img,r,g,b)
        return img        
        
