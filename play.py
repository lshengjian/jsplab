import pyglet
from jsplab.core import *
from jsplab.core.jobshop import JobShop
FPS = 60
RESOLUTION = 720, 480
###############################################
#  Initialize pyglet window and graphics batch:
###############################################
window = pyglet.window.Window(width=RESOLUTION[0],
                              height=RESOLUTION[1],
                              caption="My Game")
batch = pyglet.graphics.Batch()
timer=0


def on_hited(sender):
    print('too close')
    pyglet.app.exit()
jsp=JobShop()
jsp.center.subscribe('on_hited',on_hited)
################################################
#  Set up pyglet events for input and rendering:
################################################
@window.event
def on_key_press(key, mod):
    if key == pyglet.window.key.RIGHT:
        pass
    if key == pyglet.window.key.LEFT:
        pass
    if key == pyglet.window.key.UP:
        pass
    if key == pyglet.window.key.DOWN:
        pass


@window.event
def on_key_release(key, mod):
    if key ==pyglet.window.key.LEFT:
        jsp.exe(1,ShiftCommand(7))
        
    if key==pyglet.window.key.RIGHT:
        jsp.exe(0,WorkCommand(2,6))

@window.event
def on_draw():
    # Clear the window:
    window.clear()
    # Draw the batch of Renderables:
    batch.draw()

def main(dt):
    global timer
    timer+=1
    jsp.update(1,timer)
    jsp.render(batch)


####################################################
#  Schedule a World update and start the pyglet app:
####################################################
if __name__ == "__main__":

    pyglet.clock.schedule_interval(main, interval=1.0/FPS)
    pyglet.app.run()