from ..world_object import WorldObj
from ...datadef.constant import Constant
from .shapes import get_crane_shape
from .rendering import set_color,blend_imgs
from .componets import *
from ..workpiece import Workpiece
import logging
logger = logging.getLogger(__name__.split('.')[-1])
from .tank import Tank
class Crane(WorldObj):
    def __init__(self,  x:int,cfg:CraneData,args:Constant):
        self.cfg:CraneData=cfg
        self.args:Constant=args
        #self.timer:int=0
        self.action:CraneAction=CraneAction.Stay
        self.last_action:CraneAction=CraneAction.Stay
        self._forces:list=[0,0] #light,left
        self.locked_slot:Tank=None
        self._lock_cnt:int=0
        super().__init__(x)

    
    def resert_force(self):  
        self._forces=[0,0]  
    
    
    @property
    def forces(self)->float:
        return self._forces[0],self._forces[1]
    
    def add_force(self,val)->float:
        idx=0 if  val>0 else 1
        self._forces[idx]+=abs(val)

    @property
    def state(self)->State:
        wp:Workpiece=self.carrying
        data=State(NodeType.Crane)
        if wp!=None:
            data=wp.state.clone()
            data.node_type=NodeType.Crane
        return data  
         
    def __str__(self):
        old=super().__str__()
        return f'{self.cfg.name} {Directions[self.last_action]} {old}'

    def reset(self):
        super().reset()
        self._y=2.0
        self.timer=0
        self.locked_slot=None
        self._lock_cnt=0
        self.action=CraneAction.Stay
        self.last_action=CraneAction.Stay

    def set_command(self,act:CraneAction):
        self.action=act
        self.last_action=act

    def lock(self,slot:Tank):
        if self.locked_slot!=None:
            self.locked_slot.locked=False
        self.locked_slot=slot
        slot.locked=True
        self._lock_cnt=0

    def step(self):
        # if self.locked_slot!=None:
        #     self._lock_cnt+=1
        #     if self._lock_cnt>SHARE.MAX_LOCK_STEPS:
        #         print(f'{self} lock reset')
        #         self.reset_lock()
        if self.action==CraneAction.Stay:
            return
        dir=DIR_TO_VEC[self.action]
        self._x=self._x+dir[0]*self.cfg.speed_x
        self._y=self._y+dir[1]*self.cfg.speed_y
        # self._y=np.clip(self._y,0,2)
        self.action=CraneAction.Stay

    def reset_lock(self):
        if self.locked_slot!=None :
            self.locked_slot.locked=False
        self.locked_slot=None
        self._lock_cnt=0

    def put_in(self,wp:Workpiece):
        if wp is None:
            return
        logger.debug(f'put {wp} to {self}')
        #print(f'put {wp} to {self}')
        wp.attached=self
        self.carrying=wp
        

    
    def take_out(self)->tuple:
        rt=self.carrying
        self.carrying=None
        return rt,0     
      
    @property
    def image(self):
        img=get_crane_shape(self.last_action)
        r,g,b=self.color.rgb
        img=set_color(img,r,g,b)
        if self.carrying!=None:
            wp:Workpiece=self.carrying
            img_wp=wp.image
            img=blend_imgs(img_wp,img,(0,0))

        return img   
         
      