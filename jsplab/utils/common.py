import numpy as np
from logging import config
import yaml
from omegaconf import OmegaConf
from  pathlib import Path
from  importlib import import_module
import re
from typing import List
from functools import lru_cache
# 假设 datadef 目录在当前工作目录下
__all__=["text2nums","clean_comment","one_hot","load_config","get_dataclass_by_name"]

package_prefix = 'jsplab.conf'

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



def text2nums(text: str, toInt=True):
    ds = map(float, re.findall(r'\d+\.?\d*', text))
    ds = map(lambda x: round(x) if toInt else round(x, 2), ds)
    return list(ds)


def clean_comment(lines: List[str]) -> List[List[int]]:
    rt = []
    for line in lines:
        line = line.split("#")[0]
        ds = text2nums(line)
        if len(ds) > 0:
            rt.append(ds)
    return rt

def one_hot(index:int,size:int):
    rt=np.zeros((size,))
    rt[index]=1
    return rt#.tolist()

def load_config(fname:str):
    fpath=Path(__file__).parent.parent.parent/f"{fname}"
    return OmegaConf.load(fpath)

with open(file=Path(__file__).parent.parent.parent/"conf/logging.yaml", mode='r', encoding="utf-8") as file:
    logging_yaml = yaml.load(stream=file, Loader=yaml.FullLoader)
    config.dictConfig(logging_yaml)
    #logger = logging.getLogger(__name__.split('.')[-1])
    



