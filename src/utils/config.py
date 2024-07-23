from  importlib import import_module
from  pathlib import Path
from functools import lru_cache
# 假设 datadef 目录在当前工作目录下

datadef_dir = 'src.datadef'

@lru_cache(maxsize=None)  # maxsize=None表示无限制缓存大小
def get_dataclass_by_name(class_name: str,dir=''):

    # 构建模块文件的路径
    file_path =Path(__file__).parent.parent/f'datadef/{dir}/{class_name.lower()}.py'# os.path.join(datadef_dir, f"{class_name.lower()}.py")
    
    # 检查文件是否存在
    if not file_path.is_file:
        raise FileNotFoundError(f"No such file: {file_path}")
    
    # 构建模块名（去掉.py扩展名）
    module_name = file_path.stem.lower()
    
    # 动态导入模块
    pk_name=datadef_dir if len(dir)<1 else datadef_dir+f'.{dir}'

    module = import_module(pk_name+f'.{module_name}')
    return getattr(module, class_name)

