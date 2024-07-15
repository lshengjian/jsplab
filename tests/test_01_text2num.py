
from src.utils.text_helper import text2nums, clean_comment

def test_split_nums():
    data = text2nums('12 34.5')
    assert data[0] == 12 and data[1] == 34
    data = text2nums('12\t37.5')
    assert data[0] == 12 and data[1] == 38
    data = text2nums('12\t37.525', False)
    assert data[0] == 12.00 and data[1] == 37.52


def test_clean_text():
    data = ['# demo', '12 34.8']
    data = clean_comment(data)

    assert len(data) == 1

    assert data[0][0] == 12 and data[0][1] == 35



# def test_str_linklist():
#     str_list = LinkedList[str]()
#     str_list.append('a')
#     ds=str_list.to_list()
#     assert len(ds) == 1 and ds[0]=='a'
#     str_list.append('c')
#     str_list.append('b')
#     ds=str_list.to_list()
#     a,c,b=ds
#     assert len(ds) == 3 and a=='a' and b=='b' and c=='c'
#     str_list.display()

# def test_int_linklist():
#     llist: LinkedList[int] = LinkedList[int]()
#     llist.append(1)
#     llist.append(2)
#     llist.append(3)

#     data=llist.to_list()
#     assert len(data) == 3 and data[0]==1

#     # 使用 lambda 表达式查找偶数
#     even_numbers: List[Node[int]] = llist.find(lambda x: x % 2 == 0)
#     data= list(map(str,even_numbers))
#     assert len(data) == 1 and data[0]=='2'

# def test_task_linklist():
#     llist: LinkedList = LinkedList[Task]()

#     task1=Task(job_index=0,task_index=0,machine_times=[0,1],runtime=6)
#     task2=Task(job_index=1,task_index=2,machine_times=[1,2],runtime=5)
#     task3=Task(job_index=2,task_index=1,machine_times=[2,0],runtime=4)
#     llist.append(task1)
#     llist.append(task2)
#     llist.append(task3)
#     nodes: List[Node[Task]] = llist.find(lambda item: item.runtime<=5)
#     data= list(map(str,nodes))
#     assert len(data) == 2 and 'J2-3|5'==data[0] and 'J3-2|4'==data[1]
    



