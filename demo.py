from jsplab.instances.linklist import *
from jsplab.instances.instance import *
from jsplab.solvers.ortools_fjsp import fjsp_solver

if __name__ == '__main__':
    ins=Instance('jsp_2x3')
    ins.parse('data/jsp_demo/jsp2x3.xlsx')
    d,t=fjsp_solver(ins)
    print(d,t)
    ins=Instance('fjsp_10x6')
    with open('data/fjsp/MK/Mk02.fjs','r') as f:
        text=f.readlines()



    ins.parse_text(text)
    d,t=fjsp_solver(ins)
    print(d,t)


    # 创建一个字符串链表
    # str_list = LinkedList[str]()
    # str_list.append('a')
    # str_list.append('b')
    # str_list.append('c')
    # str_list.display()
    # # 创建一个链表
    # llist: LinkedList = LinkedList[int]()
    # llist.append(1)
    # llist.append(2)
    # llist.append(3)
    # llist.append(4)
    # llist.append(5)

    # # 显示链表内容
    # llist.display()

    # # 使用 lambda 表达式查找偶数
    # even_numbers: List[Node] = llist.find(lambda x: x % 2 == 0)
    # print("Even numbers:", list(map(str,even_numbers)))

