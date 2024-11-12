from abc import ABC, abstractmethod
from typing import Tuple
from numpy.typing import NDArray

# 定义一个问题接口
class IProblem(ABC):
    
    @property
    def case_name(self)->str:
        pass

    @property
    def shape(self)->Tuple:
        pass
    
    @abstractmethod
    def cost(self,x:NDArray)->float:
        pass
    
    def show(self,x:NDArray,title='demo',suff:str=''):
        print(x)