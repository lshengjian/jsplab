from .problem import IProblem
from functools import reduce 
import numpy as np
from numpy.typing import NDArray
from typing import List
import operator  
import logging
logger = logging.getLogger(__name__.split('.')[-1])
class BaseSIA:
    def __init__(self, num_individuals=20):
        self.num_individuals = num_individuals
        self.problem=None

    @property
    def name(self)->str:
        return self.__class__.__name__
    
    def run(self, iterations=1000):
        self.num_iterations:int=iterations
        num_quit=iterations//3
        self.cnt=0
        records:List[float]=[]
        for t in range(iterations):
            self.iterate(t)
            self.cnt+=1
            records.append(self.best_cost)
            if self.cnt>num_quit:
                break 
        self.records:NDArray=np.array(records)
        return self.best_cost,self.best_x
        
    def reset(self,problem:IProblem):
        #problem.reset()
        self.problem:IProblem=problem
        num_weights=reduce(operator.mul, problem.shape, 1) 
        self.xs:NDArray=np.random.randn(self.num_individuals,num_weights)
        costs=np.apply_along_axis(problem.cost, axis=1, arr=self.xs)
        self.sort_indexs=np.argsort(costs)
        min_idx=self.sort_indexs[0]
        self.best_xs:NDArray=self.xs.copy()
        self.best_costs:NDArray= costs.copy()
        self.best_x:NDArray=self.xs[min_idx].copy()
        self.best_cost:float=costs[min_idx]
        

    def check_best(self,t:int,xs:NDArray,costs:NDArray)->bool:
        idxs= costs<self.best_costs
        #self.xs[:,:]=xs[:,:]
        self.best_xs[idxs,:]=xs[idxs,:]
        self.best_costs[idxs]=costs[idxs]
        min_idx=np.argmin(costs)
        if (costs[min_idx]<self.best_cost):
            self.best_cost=costs[min_idx]
            self.best_x=xs[min_idx]
            self.record_best(t,min_idx)
            self.sort_indexs=np.argsort(costs)
            self.cnt=0
            return True
        return False

    def iterate(self,t:int):
        xs=self.new_positions(t)
        costs=np.apply_along_axis(self.problem.cost, axis=1, arr=xs)
        if not self.check_best(t,xs,costs) and t%7==6:
            self.sort_indexs=np.argsort(costs)

    def record_best(self,t=0,index=0):
        logger.debug(f"step:{t+1} agent{index+1} find best:{self.best_cost}")

    def new_positions(self,t:int)->NDArray:
        pass