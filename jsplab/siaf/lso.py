from numpy.typing import NDArray
from .bbpso import BBPSO
import numpy as np
from typing import Dict
from .problem import IProblem
import logging
logger = logging.getLogger(__name__.split('.')[-1])
class LSO(BBPSO):
    def __init__(self, particles=20,step=0.5,best_weight=0.5,num_adult=5 ):
        super().__init__(particles,step,best_weight)
        #print(num_adult,particles)
        #assert 1<=num_adult<=particles//2
        self.num_adult=num_adult
       
    def reset(self,problem:IProblem):
        super().reset(problem)
        self.stat:Dict[str,int]={'King':0,'Lioness':0,'lion_cub':0}
 
    def get_scale_step(self,t:int,index:int):
        T=self.num_iterations
        scale=(T-t)/T
        rt=scale*self.step
        if index==0:
            rt=0.01*rt
        elif index<self.num_adult:
            rt=0.2*self.step
        return rt

    def new_positions(self,t:int)->NDArray:
        w=self.best_weight
        T=self.num_iterations
        step=self.get_scale_step(t,len(self.xs)-1)
        n,d=self.num_individuals,len(self.best_x)
        noises=np.random.randn(n,d)
        xs=w*self.best_x+(1-w)*self.best_xs+step*noises
        for i,idx in enumerate(self.sort_indexs):
            noise=np.random.randn(d)
            step=self.get_scale_step(t,i)
            if i==0:
                K=0.8
                xs[idx]=K*self.best_x+(1-K)*self.best_xs[idx]*+step*noise
            elif i<self.num_adult:
                co_id=np.random.randint(1,self.num_adult)
                co_idx=self.sort_indexs[co_id]
                K=0.618
                xs[idx]=K*self.best_xs[idx]+(1-K)*self.best_xs[co_idx]+step*noise
        return xs
    
    def record_best(self,t=0,index=0):
        i=np.argwhere(self.sort_indexs==index)[0]
        flag='lion_cub'
        if i==0:
            flag='King'
        elif i>self.num_adult:
            flag='lion_cub'
        else:
            flag='Lioness'
        self.stat[flag]+=1
        logger.debug(f"step:{t+1} {flag} find new best:{self.best_cost}")

