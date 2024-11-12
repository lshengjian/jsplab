from numpy.typing import NDArray
from .base import BaseSIA
import numpy as np
from .problem import IProblem
class PSO(BaseSIA):
    def __init__(self, particles=20,inertia=0.5,cognitive_coeff=1.5, social_coeff=1.5):
        super().__init__(particles)
        self.cognitive_coeff=cognitive_coeff
        self.social_coeff=social_coeff
        self.inertia=inertia

    def reset(self,problem:IProblem):
        super().reset(problem)
        self.vs= np.random.uniform(-1, 1, size=self.best_x.shape)

    def new_positions(self,t:int)->NDArray:
        r1, r2 = np.random.rand(2)  
        cognitive = self.cognitive_coeff * r1 * (self.best_xs - self.xs)  
        social = self.social_coeff * r2 * (self.best_x - self.xs)    
        noise = np.random.normal(0, 0.1, size=self.vs.shape)   
        self.vs = self.inertia * self.vs + cognitive + social + noise  
        self.xs += self.vs  
        return self.xs
 
        #self.xs = np.clip(self.xs, bounds[:, 0], bounds[:, 1])  
       


