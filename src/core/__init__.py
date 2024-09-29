#from .machine import Machine
from .task import *
from .instance import Instance
from .parsers import *
from .hoist import *
from .shop import *
import logging,yaml
from pathlib import Path
logging.basicConfig(level=logging.DEBUG,  # 设置日志级别  
                    format='%(name)s - %(levelname)s - %(message)s')  # 设置输出格式  

# with open(Path(__file__).parent.parent.parent/'conf/logging.yaml', 'r',encoding='utf-8') as file:  
#     config = yaml.safe_load(file)  
#     logging.config.dictConfig(config) 