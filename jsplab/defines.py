from typing import List
from dataclasses import dataclass
import collections
from typing import TypeVar
from numpy.typing import NDArray

TVector = TypeVar('TVector', NDArray, List)
TMatrix = TypeVar('TMatrix', NDArray, List[List])

Operate_type = collections.namedtuple("Operate_type", "machine duration")


@dataclass
class Instance_Data:
    name: str = ''



@dataclass
class JSP_Data(Instance_Data):
    jobs_data: List[List[Operate_type]] = None


@dataclass
class FJSP_Data(Instance_Data):
    '''
     op_times:  the processing time matrix with shape [N, M],
                where op_pt[i,j] is the processing time of the ith operation
                on the jth machine or 0 if $O_i$ can not process on $M_j$

    '''
    num_tasks: TVector = None
    op_times: TMatrix = None
