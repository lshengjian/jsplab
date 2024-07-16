
from src.utils.crane_state import get_crane_states

def test_vrane_move():
    #time   0   1   2   3   4   5   6   7   8   9   0   1   2   3   4
    pos   =[3,  2,  1,  0,  0,  0,  1,  2,  3,  4,  4,  4,  3,  3,  3]
    #step1 '←','←','←','o','o','→','→','→','→','o','o','←','o','o','o'
    #step2 '←','←','←','↑','↑','→','→','→','→','↓','↓','←','o','o','o'

    info=get_crane_states(pos,[(3,11)])#移动发生在3~11秒
    info=list(map(str,info))
    assert info==['←', '←', '←', '↑', '↑', '→', '→', '→', '→', '↓', '↓', '←', 'o', 'o', 'o']
