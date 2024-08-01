from src.utils import get_dataclass_by_name
from omegaconf import OmegaConf
from typing import List
from dataclasses import dataclass
import logging,yaml
import logging.config
@dataclass
class Constant:
    FPS:int 
    EPS:float
    MAX_STEP_SCALE:float
    CRANE_UP_TIME:float 
    CRANE_DOWN_TIME:float
    CRANE_HEIGHT:int #天车高度
    CRANE_SAFE_DISTANCE:int #天车安全距离
    CRANE_VELOCITY:List[float] #天车默认移动速度
    def __post_init__(self):
        vx,vy=self.CRANE_VELOCITY
        if vy>self.EPS:
            if self.CRANE_UP_TIME==0:
                self.CRANE_UP_TIME=self.CRANE_HEIGHT/vy
            if self.CRANE_DOWN_TIME==0:
                self.CRANE_DOWN_TIME=self.CRANE_HEIGHT/vy


    '''
    WINDOW_TITLE:str='title'
    TILE_SIZE:int=48
    COLS_TILE:int=16
    ROWS_TEXT:int= 1
    ROWS_TILE:int= 3
    
    DRAW_TEXT:bool=True
    DISPATCH_CODE:str='DP'

    START_KEY:int=101
    SWAP_KEY:int=102
    END_KEY:int=103
    MIN_OP_KEY:int=200
    MAX_OP_TIME:int=100
    MAX_LOCK_STEPS:int=50
    OBJ_TYPE_SIZE:int=3
    OP_TYPE1_SIZE:int=3
    OP_TYPE2_SIZE:int=6
    PRODUCT_TYPE_SIZE:int=3
    MAX_X:int=100
    MAX_Y:int=2
    MAX_CRANE_SEE_DISTANCE:int=7
    MAX_OBS_LIST_LEN:int=2*MAX_CRANE_SEE_DISTANCE+1+2
    MAX_STATE_LIST_LEN:int=50
    MIN_CRANE_SAFE_DISTANCE:int=2


    SHORT_ALARM_TIME:int=3
    LONG_ALARM_TIME:int=20

    OBSERVATION_IMAGE:bool=False
    '''

# 将配置文件中的字典转换为数据类的实例
G: Constant= get_dataclass_by_name('Constant')(**OmegaConf.load("conf/constant.yaml"))

# with open(file="conf/logging.yaml", mode='r', encoding="utf-8") as file:
#     logging_yaml = yaml.load(stream=file, Loader=yaml.FullLoader)
#     logging.config.dictConfig(config=logging_yaml)
#     logger = logging.getLogger(__name__.split('.')[-1])