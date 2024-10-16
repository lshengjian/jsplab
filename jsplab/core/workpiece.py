from jsplab.cbd import Component,EventManager
from jsplab.conf import G
class Workpiece(Component):
    def __init__(self):
        super().__init__()
        self.product_code='A'
        self.steps=3
        self.cur_step=0
  