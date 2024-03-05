import numpy as np
import itertools
import random
from numpy.typing import NDArray
from typing import List,Tuple
import matplotlib.pyplot as plt
'''
广州 福州 武汉 北京
广州 0 100 200 300
福州 100 0 250 280
武汉 200 250 0 280
北京 300 280 280 0


DemoData=np.array([[9999.,100.,200.,300.],
              [100.,9999.,250.,280.],
              [200.,250.,9999.,280.],
              [300.,280.,280.,9999.],
              ])
'''

def fitness(tour:List,costs:NDArray):
    '''
    ind1 = permutation
    ind2 = permutation[1:] + permutation[:1]
    return distance_matrix[ind1, ind2].sum()
    '''
    total=0
    cur_id=0#起始城市总是0号
    for id in tour:
        total+=costs[cur_id,id]
        cur_id=id
    total+=costs[cur_id,0]#回到起始城市
    return total


def get_distance_matrix(pos:NDArray)->NDArray:  
    # N=len(pos)
    # rt=np.ones((N,N),dtype=float)*1e10
    # for i in range(N):
    #     temp=pos-pos[i]
    #     temp=temp**2
    #     temp=np.sqrt(temp.sum(axis=1))
    #     idxs=temp>0.1
    #     rt[i][idxs]=temp[idxs]
    rt=np.sqrt(
        ((pos[:, :, None] - pos[:, :, None].T) ** 2).sum(axis=1)
    )
    rt[rt<1e-10]=1e10
    return rt
            
def make_random_data(N=5,low=-10,high=10)->Tuple[NDArray,NDArray]:
    '''
    元组第一个数据是距离，第二个是坐标
    '''
    while True:
        city_pos=np.random.randint(low,high,(N,2))
        dis=get_distance_matrix(city_pos)
        if len(dis>=1e10-1e-10)==N:
            break
    
    return city_pos,dis

def test_make_data(N=6):
    pos,dis=make_random_data(N)
    print(pos)
    print(dis)

def show(city_coordinates,route,cities):
    plt.figure(figsize=(6, 6))
    plt.scatter(city_coordinates[:, 0], city_coordinates[:, 1], color='blue', s=100, marker='o')
    # 绘制访问路径
    for i in range(len(route) - 1):
        plt.plot([city_coordinates[route[i], 0], city_coordinates[route[i + 1], 0]],
                [city_coordinates[route[i], 1], city_coordinates[route[i + 1], 1]], color='red', linestyle='-', linewidth=2)

    # 连接最后一个城市和起始城市
    plt.plot([city_coordinates[route[-1], 0], city_coordinates[route[0], 0]],
            [city_coordinates[route[-1], 1], city_coordinates[route[0], 1]], color='red', linestyle='-', linewidth=2)
    # 添加城市名称
    for i, city in enumerate(cities):
        plt.text(city_coordinates[i, 0], city_coordinates[i, 1]+0.3, city, fontsize=12, ha='center', va='bottom')
    plt.show()



def main():
    N=30
    pos,dis=make_random_data(N)
    route=list(range(N))
    cities=list(map(str,route))
    show(pos,route,cities)
    # dis=fitness([1,2,3],DemoData)
    # assert abs(dis-930.)<1e-5
    # numbers = list(range(1, 4))
    # permutations =list(itertools.permutations(numbers))
    

    # print(fitness(random.choice(permutations)))
    

if __name__ == "__main__":
    #test_make_data()
    main()