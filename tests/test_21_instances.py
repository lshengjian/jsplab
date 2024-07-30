from src.core import  *

def test_read_from_excel():
    paser:IParse=ExcelFileParser()
    info=paser.parse('jsp/demo/3x3.xlsx')
    paser.debug(info) #pytest -s
    assert '3x3'==info.name
    data=info.tasks
    assert 8==len(data) 
    assert 'J1-1|3'==str(data[0])
    assert 'J1-1|3,[(1,3)]'==data[0].info
    assert 'J1-2|6,[(2,2)]'==data[1].info
    assert 1==info.max_machines_per_task

def test_read_jsp():
    paser:IParse=StandardJspFileParser()
    info=paser.parse('jsp/demo/3x3')
    paser.debug(info)
    assert '3x3'==info.name
    assert 8==len(info.tasks) # 3 jobs ,3 tasks per job
    


def test_read_fjsp():
    paser:IParse=StandardFjspFileParser()
    info=paser.parse('fjsp/MK/Mk01.fjs')
    paser.debug(info)
    assert 'Mk01'==info.name
    assert 55==len(info.tasks) 
    assert 3==info.max_machines_per_task
    