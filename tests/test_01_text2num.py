
from jsplab.utils import TextHelper

def test_split_nums():
    data = TextHelper.text2nums('12 34.5')
    assert data[0] == 12 and data[1] == 34
    data = TextHelper.text2nums('12\t37.5')
    assert data[0] == 12 and data[1] == 38
    data = TextHelper.text2nums('12\t37.525', False)
    assert data[0] == 12.00 and data[1] == 37.52
def test_clean_text():
    data = ['# demo', '12 34.8 #45','  # none']
    data = TextHelper.clean_comment(data)
    assert len(data) == 1
    assert len(data[0])==2 and data[0][0] == 12 and data[0][1] == 35

def test_numpy_data():
    data = ['# demo', '12;34.8 #45','  # none','4,5']
    data = TextHelper.get_numpy_data(data,convet2int=True)
    assert data.shape == (2,2)
    assert data[0][1] == 35

