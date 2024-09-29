class EventBus:  
    def __init__(self):  
        # 存储事件和对应的监听函数  
        self.listeners = {}  

    def subscribe(self, event_name, listener):  
        """订阅事件"""  
        if event_name not in self.listeners:  
            self.listeners[event_name] = []  
        self.listeners[event_name].append(listener)  

    def unsubscribe(self, event_name, listener):  
        """取消订阅事件"""  
        if event_name in self.listeners:  
            self.listeners[event_name].remove(listener)  

    def publish(self, event_name, *args, **kwargs):  
        """发布事件，调用所有订阅了该事件的监听函数"""  
        if event_name in self.listeners:  
            for listener in self.listeners[event_name]:  
                listener(*args, **kwargs)  

# 示例用法  
def demo():
    # 创建事件中心实例  
    event_center = EventBus()  

    # 定义事件处理函数  
    def on_user_registered(username):  
        print(f"User {username} has registered.")  

    def on_order_created(order_id):  
        print(f"Order {order_id} has been created.")  

    # 订阅事件  
    event_center.subscribe("user_registered", on_user_registered)  
    event_center.subscribe("order_created", on_order_created)  

    # 发布事件  
    event_center.publish("user_registered", "Alice")  
    event_center.publish("order_created", 12345)  

    # 取消订阅事件  
    event_center.unsubscribe("user_registered", on_user_registered)  

    # 再次发布事件，发现处理函数已被取消订阅  
    event_center.publish("user_registered", "Bob")  # 这个不会触发任何输出

if __name__ == '__main__':
    demo()