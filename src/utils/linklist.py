from typing import  Generic,Callable,  Optional, List,TypeVar
from rich.text import Text
from ..core.defines import *
T = TypeVar('T')
class Node(Generic[T]):
    def __init__(self, data: T):
        self.data:T = data
        self.next:Optional[Node] = None

    def __str__(self) -> str:
        return f"{self.data}"


class LinkedList(Generic[T]):
    def __init__(self):
        self.head:Optional[Node] = None

    def to_list(self)->List[T]:
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def append(self, data: T) -> None:
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def insert_at_begin(self, data: T) -> None:
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def insert_at_node(self, node: Node) -> None:
        if not self.head:
            self.head = node
        else:
            current = self.head
            while current.next and current.next!=node:
                current = current.next
            next=current.next
            current.next = node
            node.next=next

    def find(self, condition: Callable[[T], bool]) -> List[Node]:
        result: List[Node] = []
        current: Optional[Node] = self.head
        while current:
            if condition(current.data):
                result.append(current)
            current = current.next
        return result
    
    def __str__(self):
        current: Optional[Node] = self.head
        result=[]
        while current:
            result.append(str(current.data))
            current = current.next
        return ','.join(result)    
    
    def display(self) -> None:
        current: Optional[Node] = self.head
        while current:
            if current == self.head:
                console.print(Text(str(current.data), style="bold red"), end=' ')
            elif current.next is None:
                console.print(Text(str(current.data), style="bold blue"), end=' ')
            else:
                console.print(str(current.data),style="green", end=' ')
            current = current.next
        print()

if __name__ == '__main__':

    # 创建一个字符串链表
    str_list = LinkedList[str]()
    str_list.append('a')
    str_list.append('b')
    str_list.append('c')
    str_list.display()
    # 创建一个链表
    llist: LinkedList = LinkedList[int]()
    llist.append(1)
    llist.append(2)
    llist.append(3)
    llist.append(4)
    llist.append(5)

    # 显示链表内容
    llist.display()

    # 使用 lambda 表达式查找偶数
    even_numbers: List[Node] = llist.find(lambda x: x % 2 == 0)
    print("Even numbers:", list(map(str,even_numbers)))

