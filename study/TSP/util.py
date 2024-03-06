import numpy as np
from numpy.typing import NDArray
from typing import Tuple,List
import matplotlib.pyplot as plt

__all__=['show','make_random_data','make_demo_data']

def get_distance_matrix(coords:NDArray):
    '''
    # N=len(pos)
    # rt=np.ones((N,N),dtype=float)*1e10
    # for i in range(N):
    #     temp=pos-pos[i]
    #     temp=temp**2
    #     temp=np.sqrt(temp.sum(axis=1))
    #     idxs=temp>0.1
    #     rt[i][idxs]=temp[idxs]

    # rt=np.sqrt(
    #     ((pos[:, :, None] - pos[:, :, None].T) ** 2).sum(axis=1)
    # )

    '''
    expanded_coords = np.expand_dims(coords, axis=1)  # 
    relative_positions = expanded_coords - expanded_coords.transpose((1, 0, 2))  # 计算相对位置矩阵  
    distances = np.linalg.norm(relative_positions, axis=2)  # 计算欧几里德距离    
    return distances

def make_random_data(N=5,low=-10,high=10)->Tuple[NDArray,NDArray]:
    '''
    元组第一个数据是坐标，第二个是距离矩阵
    '''
    while True:
        city_coords=np.random.randint(low,high,(N,2))
        dis_matrix=get_distance_matrix(city_coords)
        dis_matrix[dis_matrix<1e-10]=1e10
        if len(dis_matrix>1e10-1e-10)==N:
            break
    return city_coords,dis_matrix

def make_demo_data():
    city_coords = np.array([[0, 0], [5, 3], [-3, 4], [7, 10]],dtype=float)
    dis_matrix=get_distance_matrix(city_coords)
    return city_coords,dis_matrix

def show(city_coordinates:NDArray,route:List[int],cities:List[str]):
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
    
def test01_expand_dims():
    data=np.array([[1,2],[3,4],[5,6]],dtype=float)
    assert(data.shape==(3,2))
    data=np.expand_dims(data,1)
    assert(data.shape==(3,1,2))
    data2=data.transpose((1, 0, 2)) 
    assert(data2.shape==(1,3,2))
    data3=data-data2
    assert(data3.shape==(3,3,2))

def demo_cities(is_random:bool=True):
    N=12
    pos,dis=make_random_data(N) if is_random else make_demo_data()
    N=len(pos)
    route=list(range(N))
    citie_names=list(map(lambda x:str(x+1),route))
    show(pos,route,citie_names)

'''
运行前先安装依赖库：
pip install numpy
pip install matplotlib

'''

if __name__ == "__main__":
    
    test01_expand_dims()

    demo_cities(is_random=False)
    demo_cities(is_random=True)

    