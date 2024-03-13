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


def main():
    num_birds=20
    num_city=10
    cities,dis=make_random_data(num_city)

    birds_pos=np.random.randn(num_birds,num_city)
    birds_cost=np.ones(num_birds)*1e10
    birds_best_pos=birds_pos.copy()
    birds_best_cost= birds_cost.copy()

    best_pos=birds_pos[0].copy()
    best_cost=cost(get_tour_from_pos(best_pos),dis)
    print(f"init cost:{best_cost}")

    for t in range(1000):
        birds_pos=(birds_pos+birds_best_pos)/2+np.random.randn(num_birds,num_city)*0.1
        for i in range(num_birds):
            birds_cost[i]=cost(get_tour_from_pos(birds_pos[i]),dis)
            if birds_cost[i]<best_cost:
                best_cost=birds_cost[i]
                best_pos[:]=birds_pos[i,:]
                print(f"step:{t+1} cost:{best_cost}")

        idxs= birds_cost<birds_best_cost
        birds_best_pos[idxs,:]=birds_pos[idxs,:]

    route=get_tour_from_pos(best_pos)
    citie_names=list(map(lambda x:str(x+1),route))
    show(cities,route,citie_names) 
    

if __name__ == "__main__":
    #demo_cost()
    main()