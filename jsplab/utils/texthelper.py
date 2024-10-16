import re
import numpy as np
from numpy.typing import NDArray
from typing import List,Union
from io import StringIO  

class TextHelper:
    @staticmethod
    def get_numpy_data(data_or_file_name:Union[List[str],str] = 'data.csv',convet2int=False)->NDArray:
        lines=data_or_file_name 
        if not isinstance(data_or_file_name,list) :   # 读取原始文件并替换分隔符  
            with open(data_or_file_name, 'r', encoding='utf-8') as f:  
                lines=f.readlines()
        ds=[]
        for line in lines:  
            idx=line.find('#') #忽略备注内容
            if idx>=0:
                line=line[:idx]
            line = re.sub(r'[;,\s]+', ',', line.strip())  # 使用正则表达式将分隔符统一替换为逗号
            if len(line)<1:
                continue
            ds.append(line)
        data = np.loadtxt(StringIO('\n'.join(ds)), delimiter=',') 
        return (data+0.5).astype(int) if convet2int else data

    @staticmethod
    def text2nums(text: str, toInt=True):
        ds = map(float, re.findall(r'\d+\.?\d*', text))
        ds = map(lambda x: round(x) if toInt else round(x, 2), ds)
        return list(ds)

    @staticmethod
    def clean_comment(lines: List[str]) -> List[List[int]]:
        rt = []
        for line in lines:
            idx=line.find('#')
            if idx>=0:
                line=line[:idx]
            ds = TextHelper.text2nums(line)
            if len(ds) > 0:
                rt.append(ds)
        return rt
    
