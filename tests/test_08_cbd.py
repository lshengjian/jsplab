from jsplab.cbd import *

class MyGame:
    def __init__(self):
        self.is_over=False
    def on_died(self):
        self.is_over=True
        print(f"Game Over!")

class Health(Component):
    def __init__(self):
        super().__init__()
        self.hp = 10 
    def damage(self,amount:int=1,center:EventManager=None):
        self.hp-=amount
        if self.hp<=0:
            self.hp=0
            if center!=None:
                center.publish('on_died')


# Simulate player taking damageplayer.take_damage(10)
def test_game():
    game=MyGame()
    player = GameObject()
    hc=player.add_component(Health)
    msg_mgr=EventManager()
    msg_mgr.subscribe('on_died',game.on_died)
    msg_mgr.subscribe('on_damaged',hc.damage)

    msg_mgr.publish('on_damaged',amount=5)
    assert hc.hp==5 and game.is_over==False
    msg_mgr.publish('on_damaged',amount=10,center=msg_mgr)
    assert hc.hp==0 and game.is_over==True    

