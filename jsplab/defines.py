import collections
from typing import Union,List,TypeVar

from rich.console import Console


__all__=['console','OperateType','T']
T = TypeVar('T')
console = Console()
OperateType = collections.namedtuple("OperateType", "machine duration")
# Point = namedtuple('Point', ['x', 'y'], defaults=(0.0, 0.0))


# class Instance_Data:
#     name: str = ''
#     Union[NDArray, List[List]]


# @dataclass
# class JSP_Data(Instance_Data):
#     jobs_data: List[List[OperateType]] = None


# @dataclass
# class FJSP_Data(Instance_Data):
#     '''
#      op_times:  the processing time matrix with shape [N, M],
#                 where op_pt[i,j] is the processing time of the ith operation
#                 on the jth machine or 0 if $O_i$ can not process on $M_j$

#     '''
#     num_tasks: TVector = None
#     op_times: TMatrix = None
