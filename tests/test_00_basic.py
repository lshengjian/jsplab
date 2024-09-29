import itertools
import numpy as np
from sortedcontainers import SortedDict  

#pip install sortedcontainers
def test_combination():
    data=list(itertools.product([0, 1], repeat=3)) # [0,1] [0,1] [0,1]各取一个的组合是 2*2*2=8
    assert 8==len(data) and (0,0,0)==data[0] and   (1,1,1)==data[7]

def test_orderdict():
    data = SortedDict({1:3,3:1,2:2}) 
    assert list(data.keys()) ==[1,2,3]
    assert list(data.values()) ==[3,2,1]

    sorted_dict = SortedDict()  


    sorted_dict['b'] = 2  
    sorted_dict['a'] = 1  
    sorted_dict['c'] = 3  

    assert list(sorted_dict.keys())==['a', 'b',  'c']

def test_nonzero():
    idxs=np.nonzero([0,1.5,2])[0] # olny one dimetion
    assert [1,2]==idxs.tolist()
