from typing import List
from dataclasses import dataclass
from ..utils import load_config,get_dataclass_by_name
#electroplating Tank --- 电镀槽
#Hoist  -- 搬运天车
#transfer cart --转运车
@dataclass
class Constant:
    FPS:int 
    EPS:float

    MIN_DISTANCE:float
    HOIST_UP_TIME:float 
    HOIST_DOWN_TIME:float
    HOIST_HEIGHT:float #天车高度
    HOIST_SAFE_DISTANCE:float #天车安全距离
    HOIST_VELOCITY:List[float] #天车默认移动速度

    def __post_init__(self):
        vx,vy=self.HOIST_VELOCITY
        if vy>self.EPS:
            if self.HOIST_UP_TIME==0:
                self.HOIST_UP_TIME=self.HOIST_HEIGHT/vy
            if self.HOIST_DOWN_TIME==0:
                self.HOIST_DOWN_TIME=self.HOIST_HEIGHT/vy



# 将配置文件中的字典转换为数据类的实例
G: Constant= get_dataclass_by_name('Constant')(**load_config("conf/constant.yaml"))

