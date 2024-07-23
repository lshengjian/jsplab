from src.utils import get_dataclass_by_name
from omegaconf import OmegaConf
from dataclasses import asdict
from pathlib import Path
from src.datadef.constant import Constant
def test_read_data_from_yaml():
    path=Path(__file__).parent.parent/"conf/demo.yaml"
    config = OmegaConf.load(path)
    D1=get_dataclass_by_name('Data1','demo')
    # 将配置文件中的字典转换为数据类的实例
    my_data_instance = D1(**config.data1)
    assert {'delay': 0.3, 'msg': 'hello world'}==asdict(my_data_instance)
    D2=get_dataclass_by_name('Data2','demo')
    # 将配置文件中的字典转换为数据类的实例
    my_data_instance = D2(**config.data2)
    assert {'seq': [1, 2, 3]}==asdict(my_data_instance)

def test_read_global_data():
    config = OmegaConf.load("conf/constant.yaml")
    D1=get_dataclass_by_name('Constant')
    # 将配置文件中的字典转换为数据类的实例
    g: Constant= D1(**config)
    assert 1e-8==g.EPS