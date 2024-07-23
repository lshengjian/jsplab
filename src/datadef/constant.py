from dataclasses import dataclass

@dataclass
class Constant:
    WINDOW_TITLE:str='title'
    TILE_SIZE:int=48
    COLS_TILE:int=16
    ROWS_TEXT:int= 1
    ROWS_TILE:int= 3
    FPS:int= 12
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

    EPS:float=1e-8
    #AUTO_DISPATCH:bool=False
    OBSERVATION_IMAGE:bool=False
