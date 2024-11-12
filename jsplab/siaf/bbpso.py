from numpy.typing import NDArray
from .base import BaseSIA
import numpy as np
class BBPSO(BaseSIA):
    def __init__(self, particles=20,step=1,best_weight=0.5):
        super().__init__(particles)
        self.step=step
        self.best_weight=best_weight

    def new_positions(self,t:int)->NDArray:
        w=self.best_weight
        noises=np.random.randn(self.num_individuals,len(self.best_x))
        return w*self.best_x*+(1-w)*self.best_xs+self.step*noises
    