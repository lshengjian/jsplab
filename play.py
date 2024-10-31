import pyglet
from collections import defaultdict
from jsplab.core import *
from jsplab.conf.mhp import MultiHoistProblem
from jsplab.core.jobshop import JobShop
from jsplab.core.render import Render
FPS = 24
RESOLUTION = 720, 480
###############################################
#  Initialize pyglet window and graphics batch:
###############################################
window = pyglet.window.Window(width=RESOLUTION[0],
                              height=RESOLUTION[1],
                              caption="My Game")


cur_hoist_idx=0

def on_hited(sender):
    print('too close')
    pyglet.app.exit()
cfg=MultiHoistProblem('mhp/t4j2.csv',2)
jsp=JobShop(cfg)
render=Render(jsp)
jsp.center.subscribe('on_hited',on_hited)
#job:Job=jsp.start_job()
cmds=defaultdict(list)
cmds[0].extend([TransportCommand(0,1,0,2),TransportCommand(0,2,0,3)])
cmds[1].extend([TransportCommand(1,3,2,6),TransportCommand(2,3,3,6)])
jsp.cmds=cmds
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
    render.draw()
    

def main(dt):
    jsp.update(1)
    render.update()
    


####################################################
#  Schedule a World update and start the pyglet app:
####################################################
if __name__ == "__main__":

    pyglet.clock.schedule_interval(main, interval=1.0/FPS)
    pyglet.app.run()