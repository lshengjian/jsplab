from jsplab import FJSP_Data,JSP_Data,Operate_type
from jsplab.utils import InstanceFJSP, load_data_list
from pathlib import Path


def test_load_Mks():
    dir = Path(__file__).parent.parent
    ds = load_data_list(dir/'data/fjsp/Mk')
    assert len(ds) == 10
    d: FJSP_Data = ds[0]
    assert d.name == 'Mk01' and len(
        d.num_tasks) == 10 and d.op_times.shape[1] == 6
    assert d.num_tasks.sum() == d.op_times.shape[0]

def test_load_study_jsp():
    dir = Path(__file__).parent.parent
    ds = load_data_list(dir/'data/jsp_demo/study')
    assert len(ds) == 1
    d: JSP_Data = ds[0]
    assert d.name == '3x3' and len(d.jobs_data)==3  
    job11:Operate_type= d.jobs_data[0][0]
    assert job11.machine==0 and  job11.duration==1
