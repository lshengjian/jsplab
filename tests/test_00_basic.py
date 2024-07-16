import itertools
import numpy as np

def test_combination():
    data=list(itertools.product([0, 1], repeat=3))
    assert 8==len(data) and (0,0,0)==data[0] and   (1,1,1)==data[7]


def test_nonzero():
    idxs=np.nonzero([0,1.5,2])[0] #只有1维
    assert [1,2]==idxs.tolist()
