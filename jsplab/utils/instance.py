
from typing import List

from .. import INSTANCE_DATA

class Instance:
    def __init__(self, name):
        self.data:INSTANCE_DATA=INSTANCE_DATA(name)
        
        
        

    def parse(self,lines:List[str]):
        pass


    # def parse_from_file(self,fname:str):
    #     pass

