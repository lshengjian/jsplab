import itertools,random
from util import make_demo_data,cost,get_tour_from_pos,make_random_data,show
import numpy as np
from numpy.typing import NDArray


def demo_cost():
    cities,dis=make_demo_data()
    num_city=cities.shape[0]
    numbers = list(range(1,num_city))
    permutations =list(itertools.permutations(numbers))
    for _ in range(3):
        route=[0]+list(random.choice(permutations))
        fee=cost(route,dis)
        print(f'route:{route},cost:{fee:.2f}')

def cost_fn(pos, distance_matrix):
    return cost(get_tour_from_pos(pos),distance_matrix)


def main():
    num_birds=30
    num_city=20

    cities,distance_matrix=make_random_data(num_city)

    birds_pos=np.random.randn(num_birds,num_city)
    birds_cost=np.apply_along_axis(cost_fn, axis=1, arr=birds_pos, distance_matrix=distance_matrix)
    idxs=np.argsort(birds_cost)
    birds_best_pos=birds_pos.copy()
    birds_best_cost= birds_cost.copy()

    best_pos=birds_pos[idxs[0]].copy()
    best_cost=birds_cost[idxs[0]]
    print(f"init cost:{best_cost}")

    for t in range(10000):
        birds_pos=(birds_pos+birds_best_pos)/2+np.random.randn(num_birds,num_city)*0.2
        birds_cost=np.apply_along_axis(cost_fn, axis=1, arr=birds_pos, distance_matrix=distance_matrix)
        idxs=np.argsort(birds_cost)

        idxs2= birds_cost<birds_best_cost
        birds_best_pos[idxs2,:]=birds_pos[idxs2,:]
        birds_best_cost[idxs2]=birds_cost[idxs2]
        if (birds_cost[idxs[0]]<best_cost):
            best_cost=birds_cost[idxs[0]]
            best_pos=birds_pos[idxs[0]]
            print(f"step:{t+1} cost:{best_cost}")

    route=get_tour_from_pos(best_pos)
    citie_names=list(map(lambda x:str(x+1),route))
    show(cities,route,citie_names) 
    

if __name__ == "__main__":
    #demo_cost()
    main()