# from typing import List, Protocol, Any


# class Observer(Protocol):
#     def on_notify(self, data: Any) -> None:
#         pass
# class Subject:
#     def __init__(self):
#         self.data=None
#         self._observers: List[Observer] = []

#     def add_observer(self, observer: Observer) -> None:
#         self._observers.append(observer)

#     def remove_observer(self, observer: Observer) -> None:
#         self._observers.remove(observer)

#     def notify_observers(self) -> None:
#         for observer in self._observers:
#             observer.on_notify(self.data)
