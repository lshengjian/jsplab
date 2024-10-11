from typing import TypeVar, Dict, Type,Optional

T = TypeVar('T', bound='Component')

class GameObject:
    """游戏对象管理多个组件"""
    def __init__(self):
        self.components: Dict[Type[Component], Component] = {}

    def add_component(self, component_class: Type[T]) -> T:
        """创建并添加一个组件到游戏对象"""
        if component_class not in self.components:
            component = component_class()  # 创建组件实例
            component.game_object = self  # 设定组件所属的游戏对象
            self.components[component_class] = component            
        return self.components[component_class]  
    def get_component(self, component_class: Type[T]) -> Optional[T]:
        """获取游戏对象上的一个组件"""
        return self.components.get(component_class, None)

    def update(self,delta_time:float=0.016,total_time=0):
        """更新游戏对象的所有组件"""
        for component in self.components.values():
            component.update()

class Component:
    """游戏组件基类"""
    def __init__(self):
        self.game_object: Optional[GameObject] = None    
        def update(self,delta_time:float=0.016,total_time=0):
            pass