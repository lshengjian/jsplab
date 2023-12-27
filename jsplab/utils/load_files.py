from pathlib import Path
import numpy as np

from typing import List
from jsplab import Instance_Data
from .instance_fjsp import InstanceFJSP
from .instance_jsp import InstanceJSP

def load_data_list(directory: str) -> List[Instance_Data]:
    """
        load all files within the specified directory
    :param directory: the directory of files
    :return: a list of data (matrix form) in the directory
    """
    rt: List[Instance_Data] = []
    dir = Path(directory)
    if not dir.exists():
        print(f'{directory} not exists')
        return rt

    for file in dir.glob('*'):
        if file.is_file:
            with open(file, 'r') as f:
                text = f.readlines()
            ins=None
            if file.suffix=='.fjs':
                ins = InstanceFJSP(file.stem)
            elif file.suffix=='.js':
                ins=InstanceJSP(file.stem)
            ins.parse(text)
            rt.append(ins.data)

    return rt
