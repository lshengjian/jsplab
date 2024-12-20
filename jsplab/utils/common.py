import numpy as np
from numpy.typing import NDArray
from omegaconf import OmegaConf
from  pathlib import Path
from  importlib import import_module

from functools import lru_cache
# 假设 datadef 目录在当前工作目录下
__all__=["one_hot","load_config","get_dataclass_by_name"]

package_prefix = 'jsplab.conf'
# def load_data(fpath:str)->NDArray:
#     #if fpath.endswith('.')
#     fpath=Path(__file__).parent.parent.parent/f'data/{fpath}'
#     data = np.genfromtxt(fpath, delimiter=',', encoding='utf-8')  
#     return data
@lru_cache(maxsize=32)  
def get_dataclass_by_name(class_name: str,dir=''):

    # 构建模块文件的路径
    file_path =Path(__file__).parent.parent/f'conf/{dir}/{class_name.lower()}.py'# os.path.join(datadef_dir, f"{class_name.lower()}.py")
    
    # 检查文件是否存在
    if not file_path.is_file:
        raise FileNotFoundError(f"No such file: {file_path}")
    
    # 构建模块名（去掉.py扩展名）
    module_name = file_path.stem.lower()
    
    # 动态导入模块
    pk_name=package_prefix if len(dir)<1 else package_prefix+f'.{dir}'

    module = import_module(pk_name+f'.{module_name}')
    return getattr(module, class_name)


def one_hot(index:int,size:int):
    rt=np.zeros((size,))
    rt[index]=1
    return rt#.tolist()

def load_config(fname:str):
    fpath=Path(__file__).parent.parent.parent/f"{fname}"
    return OmegaConf.load(fpath)



    



