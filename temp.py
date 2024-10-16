
from jsplab.utils import TextHelper
def demo():
    data = ['# demo', '12;34.8 #45','  # none','4,5']
    data = TextHelper.get_numpy_data(data,convet2int=True)
    print(data)
    assert data.shape == (2,2)
    assert data[0][1] == 35
if __name__ == '__main__':
    demo()