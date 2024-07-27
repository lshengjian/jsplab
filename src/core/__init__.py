#from .machine import Machine
from .task import *
from .instance import Instance,get_max_steps
from .parsers import *
from .crane import *
from .shop import *
import logging

logging.basicConfig(level=logging.DEBUG,  # 设置日志级别  
                    format='%(name)s - %(levelname)s - %(message)s')  # 设置输出格式  
