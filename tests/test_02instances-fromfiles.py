from jsplab.instances.parsers import  IParse,ParserExcel,ParserStandardJspFile,ParserFjspFile

def test_read_from_excel():
    ins:IParse=ParserExcel()
    name,data,_=ins.parse('jsp/demo/3x3.xlsx')
    ins.debug(data) #pytest -s
    assert '3x3'==name
    assert 8==len(data) # proc1(3 tasks) have 1 job, proc2(2 tasks) have 2 jobs
    assert 'J1-1|3'==str(data[0])
    assert 'J1-1|3,[(1,3)]'==data[0].str_info()
    assert 'J1-2|2,[(2,2)]'==data[1].str_info()

def test_read_standard_jsp():
    ins:IParse=ParserStandardJspFile()
    name,data,_=ins.parse('jsp/demo/3x3')
    ins.debug(data) #pytest -s
    assert '3x3'==name
    assert 8==len(data) # 3 jobs ,3 tasks per job

def test_read_fjsp():
    ins:IParse=ParserFjspFile()
    name,data,_=ins.parse('fjsp/MK/Mk01.fjs')
    ins.debug(data) #pytest -s
    assert 'Mk01'==name
    assert 55==len(data) 