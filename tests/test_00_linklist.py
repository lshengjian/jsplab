
from jsplab.instances.linklist import *
from jsplab.instances import Instance



def test_01():
    str_list = LinkedList[str]()
    str_list.append('a')
    ds=str_list.to_list()
    assert len(ds) == 1 and ds[0]=='a'
    str_list.append('c')
    str_list.append('b')
    ds=str_list.to_list()
    a,c,b=ds
    assert len(ds) == 3 and a=='a' and b=='b' and c=='c'
    str_list.display()



def test_02():
    ins=Instance('jsp_2x3')
    ins.parse('data/jsp_demo/jsp2x3.xlsx')
    assert 2==len(ins.data)
    assert 3==len(ins.data[0])
    assert 2==len(ins.data[1])