class A:
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def run(self,  file):
        print(f'{self.__class__.__name__}:{file}')
        # 这里是算法的实现
        result = self.param1 + self.param2
        return result