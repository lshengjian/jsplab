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
# def get_good_indexs(costs:NDArray):
#     return np.argsort(costs)

def main():
    num_lions=30
    num_city=20
    cub_start=6

    cities,distance_matrix=make_random_data(num_city)

    ps_pos=np.random.randn(num_lions,num_city)
    ps_cost=np.apply_along_axis(cost_fn, axis=1, arr=ps_pos, distance_matrix=distance_matrix)
    idxs=np.argsort(ps_cost)
    ps_best_pos=ps_pos.copy()
    ps_best_cost= ps_cost.copy()

    best_pos=ps_pos[idxs[0]].copy()
    best_cost=ps_cost[idxs[0]]
    print(f"init cost:{best_cost}")
    stat={'Lion':0,'Lioness':0,'lion_cub':0}
    T=5000

    for t in range(T):
        scale=(T-t)/T
        #ps_pos=(best_pos+ps_best_pos)/2+np.random.randn(num_lions,num_city)*0.1
        for i,idx in enumerate(idxs):
            if i==0:
                K=0.8
                ps_pos[idx]=best_pos*K+ps_best_pos[idx]*(1-K)+np.random.randn(num_city)*0.1*scale
            elif i<cub_start:
                co_idx=idxs[np.random.randint(1,cub_start)]
                ps_pos[idx]=(best_pos+ps_best_pos[co_idx]+ps_best_pos[idx])/3+np.random.randn(num_city)*scale
            else:
                follow_idx=idxs[i%cub_start]
                K=0.618
                ps_pos[idx]=ps_best_pos[follow_idx]*K+best_pos*(1-K)+np.random.randn(num_city)*scale
                


        ps_cost=np.apply_along_axis(cost_fn, axis=1, arr=ps_pos, distance_matrix=distance_matrix)
        idxs2= ps_cost<ps_best_cost
        ps_best_pos[idxs2,:]=ps_pos[idxs2,:]
        ps_best_cost[idxs2]=ps_cost[idxs2]
        min_idx=np.argmin(ps_cost)
        if (ps_cost[min_idx]<best_cost):
            best_cost=ps_cost[min_idx]
            best_pos=ps_pos[min_idx]
            
            flag=''
            for i,idx in enumerate(idxs):
                if idx==min_idx:
                    if i==0:
                        flag='Lion'
                    elif i>=cub_start:
                        flag='lion_cub'
                    else:
                        flag='Lioness'
                    stat[flag]+=1
                    break
            print(f"step:{t+1} {flag} find new best:{best_cost}")
            idxs=np.argsort(ps_cost)


    route=get_tour_from_pos(best_pos)
    citie_names=list(map(lambda x:str(x+1),route))
    for k,v in stat.items():
        print(f"{k}:{v}")
    show(cities,route,citie_names) 

    

if __name__ == "__main__":
    #demo_cost()
    main()