from typing import List
from dataclasses import dataclass

from typing import TypeVar
from numpy.typing import NDArray

TVector = TypeVar('TVector', NDArray, List)
TMatrix = TypeVar('TMatrix', NDArray, List[List])


@dataclass
class INSTANCE_DATA:
    '''
     op_times:  the processing time matrix with shape [N, M],
                where op_pt[i,j] is the processing time of the ith operation
                on the jth machine or 0 if $O_i$ can not process on $M_j$
    
    '''

    name: str = ''
    num_tasks: TVector = None
    op_times: TMatrix = None
