from jsplab.utils import get_dataclass_by_name,load_config
from dataclasses import asdict
from jsplab.conf import G

def test_read_data_from_yaml():
    config = load_config("conf/demo.yaml")
    D1=get_dataclass_by_name('Data1','demo')
    # 将配置文件中的字典转换为数据类的实例
    my_data_instance = D1(**config.data1)
    assert {'delay': 0.3, 'msg': 'hello world'}==asdict(my_data_instance)
    D2=get_dataclass_by_name('Data2','demo')
    # 将配置文件中的字典转换为数据类的实例
    my_data_instance = D2(**config.data2)
    assert {'seq': [1, 2, 3]}==asdict(my_data_instance)

def test_read_global_data():
    assert 1e-8==G.EPS
