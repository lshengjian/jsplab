
from jsplab.utils import text2nums, clean_comment

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

