import pyglet
from jsplab.core import *
from jsplab.conf.mhp import MultiHoistProblem
from jsplab.core.jobshop import JobShop
FPS = 24
RESOLUTION = 720, 480
###############################################
#  Initialize pyglet window and graphics batch:
###############################################
window = pyglet.window.Window(width=RESOLUTION[0],
                              height=RESOLUTION[1],
                              caption="My Game")
batch = pyglet.graphics.Batch()
timer=0
cur_hoist_idx=0

def on_hited(sender):
    print('too close')
    pyglet.app.exit()
cfg=MultiHoistProblem('mhp/t4j2.csv')
jsp=JobShop(cfg,2)
jsp.center.subscribe('on_hited',on_hited)
job:Job=jsp.start_job()
################################################
#  Set up pyglet events for input and rendering:
################################################
# @window.event
# def on_key_press(key, mod):
#     if key == pyglet.window.key.RIGHT:
#         pass



@window.event
def on_key_release(key, mod):
    global cur_hoist_idx
    if key ==pyglet.window.key.RIGHT:
        cfg1:ProcStep=job.cur_task.cfg
        cfg2:ProcStep=job.next_task.cfg
        jsp.exe(cur_hoist_idx,TransportCommand(cfg1.tank_index,cfg2.tank_index,cfg1.offset,cfg2.offset))

    if key ==pyglet.window.key.LEFT:
        cfg:ProcStep=job.cur_task.cfg
        jsp.exe(cur_hoist_idx,ShiftCommand(cfg.tank_index,cfg.offset))
        
    if key==pyglet.window.key.TAB:
        jsp.hoist_sprites[cur_hoist_idx].color=(0,255,0,100)
        cur_hoist_idx=(cur_hoist_idx+1)%2
        jsp.hoist_sprites[cur_hoist_idx].color=(255,0,0,255)

        

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