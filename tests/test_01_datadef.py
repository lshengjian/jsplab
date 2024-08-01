from src.utils import get_dataclass_by_name
from omegaconf import OmegaConf
from dataclasses import asdict
from pathlib import Path
from src.datadef import G

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
    assert 12==G.FPS
    assert 1e-8==G.EPS
    assert 2==G.CRANE_UP_TIME==G.CRANE_DOWN_TIME
    assert 1.0==G.CRANE_VELOCITY[0] and 1.0==G.CRANE_VELOCITY[1]