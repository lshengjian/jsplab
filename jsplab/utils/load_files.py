from pathlib import Path
import numpy as np

from typing import List
from .. import INSTANCE_DATA
from .instance_fjsp import FjspInstance

def load_data_list(directory: str) -> List[INSTANCE_DATA]:
    """
        load all files within the specified directory
    :param directory: the directory of files
    :return: a list of data (matrix form) in the directory
    """
    rt: List[INSTANCE_DATA] = []
    dir = Path(directory)
    if not dir.exists():
        return rt

    for file in dir.glob('*'):
        if file.is_file:
            # print(file.stem)
            with open(file, 'r') as f:
                text = f.readlines()
            fjsp=FjspInstance(file.stem)
            fjsp.parse(text)
            rt.append(fjsp.data)

    return rt