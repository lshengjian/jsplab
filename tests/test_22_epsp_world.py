from src.core import  *

def test_epsp_world():
    paser:IParse=ExcelFileParser()
    instance=paser.parse('epsp/2x(4+2).xlsx')

    ms,js=instance.world
    assert 6==len(ms)
    assert 2==len(js)

    for job in js:
        greedy_select(job,ms)
    
    for job in js:
        print(job)

