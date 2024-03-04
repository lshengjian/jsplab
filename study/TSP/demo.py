import numpy as np
import itertools
import random
from numpy.typing import NDArray
from typing import List
'''
广州 福州 武汉 北京
广州 0 100 200 300
福州 100 0 250 280
武汉 200 250 0 280
北京 300 280 280 0

'''
DIS=np.array([[9999.,100.,200.,300.],
              [100.,9999.,250.,280.],
              [200.,250.,9999.,280.],
              [300.,280.,280.,9999.],
              ])
N=len(DIS[0])
def fitness(tour:List):
    total=0
    cur_id=0
    assert len(tour)==N-1
    print(tour)
    for id in tour:
        total+=DIS[cur_id,id]
        cur_id=id
    total+=DIS[cur_id,0]
    return total
    


def main():
    dis=fitness([1,2,3])
    assert abs(dis-930.)<1e-5
    numbers = list(range(1, N))
    permutations =list(itertools.permutations(numbers))
    

    print(fitness(random.choice(permutations)))
    

if __name__ == "__main__":
    main()