from typing import List
from enum import Enum
from rich.console import Console


__all__=['MoveType','MOVE_FLAGS','JobShopType','console']

console = Console()


class MoveType(Enum):
    stop='o'
    right='→'
    up='↑'
    left='←'
    down='↓'
    def __str__(self):
        return self.value

MOVE_FLAGS = [flag for _, flag in MoveType.__members__.items()]

class JobShopType(Enum):
    jsp = "_generate_instance_jsp"
    fjsp = "_generate_instance_fjsp"

    @classmethod
    def is_jsp_type_implemented(cls, jsp_type: str = "") -> bool:
        return True if jsp_type in cls.str_list_of_jsp_types_implemented() else False

    @classmethod
    def str_list_of_jsp_types_implemented(cls) -> List[str]:
        return [name for name, _ in cls.__members__.items()]



