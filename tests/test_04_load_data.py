from jsplab.utils import load_data

import time
def test_read_tanks():
    data=load_data('epsp/free_move_times.csv')
    assert 13==len(data)
    for i in range(13):
        assert 0==data[i,i]
    for i in range(13):
        for j in range(i+1,13):
            assert data[j,i]==data[i,j]
