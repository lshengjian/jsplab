import numpy as np

from omegaconf import OmegaConf



def one_hot(index:int,size:int):
    rt=np.zeros((size,))
    rt[index]=1
    return rt#.tolist()

def load_config(fname:str):
    cfg = OmegaConf.load(fname)
    #print(**cfg)
    return cfg





if __name__ == '__main__':

    load_config('conf/demo/or-tools-solver.yaml')

