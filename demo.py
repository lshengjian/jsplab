
from typing import List
from src.core import  *
import numpy as np

def demo():
    paser:IParse=ExcelFileParser()
    instance=paser.parse('epsp/2x(4+2).xlsx')

    ms,js=instance.world
    for job in js:
        greedy_select(job,ms)
    
    for job in js:
        print(job)
if __name__ == '__main__':
    demo()

 