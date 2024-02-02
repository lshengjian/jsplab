from abc import ABC, abstractmethod

# 定义一个接口类
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass

# 实现一个具体的类，并继承自接口类
class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14 * self.radius

# 使用接口类定义的方法
circle = Circle(5)
print(circle.area())  # 输出: 78.5
print(circle.perimeter())  # 输出: 31.400000000000002
