
from dataclasses import dataclass,asdict
from omegaconf import OmegaConf
from typing import List,Dict
@dataclass
class Data1:
    delay: float
    msg: str
@dataclass
class Data2:
    seq: List[int]
def from_dict(cls:dataclass,dict:Dict)->dataclass:
    return cls(**dict)
def demo1():
    d1=Data1(0.2,'he')
    print(d1)
    d2=from_dict(Data1,{'delay':0.5,'msg':'demo'})
    print(d2)
    d3=from_dict(Data2,{'seq':[2,3,4]})
    print(d3)

def demo2():
    config = OmegaConf.load("conf/demo.yaml")
    # 将配置文件中的字典转换为数据类的实例
    my_data_instance = Data1(**config.data1)
    print(my_data_instance)
    print(asdict(my_data_instance))
if __name__ == '__main__':
    demo2()

 