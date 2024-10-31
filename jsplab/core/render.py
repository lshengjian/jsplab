from .jobshop import JobShop
import pyglet
from pyglet.shapes import Circle,BorderedRectangle
from .hoist import Hoist
from .tank import Tank
from .job import Job
OFFSET=(1,1)
class Render:
    def __init__(self,shop: JobShop):
        self.shop: JobShop=shop
        self.hoist_sprites=[]
        self.tank_sprites=[]
        self.job_sprites=[]
        batch = pyglet.graphics.Batch()
        for _ in shop.hoists:
            self.hoist_sprites.append(BorderedRectangle(0,0,48,24,color=(0,255,0,100),batch=batch))
        for _ in shop.tanks:
            self.tank_sprites.append(Circle(0,0,20,batch=batch))
        for i,_ in enumerate(shop.jobs):
            self.job_sprites.append(Circle(i*100+200,200,10,color=(20,34,236,200),batch=batch))
        self.batch=batch
        shop.center.subscribe('on_hoist_drop',self.on_hoist_drop)

    def on_hoist_drop(self,hoist:Hoist,job:Job):
        if job!=None :
            idx=job.cur_task.cfg.tank_index
            if idx==len(self.shop.tanks)-1:
                sp=self.job_sprites.pop()  
                sp.batch=None
                sp.delete()  
                #print('delete job sp')

    def draw(self):
        self.batch.draw()

    def update(self):
        for i,sp in enumerate(self.hoist_sprites):
            j:Hoist=self.shop.hoists[i]
            dx,dy=OFFSET
            sp.x=(j.x+dx)*64-sp.width//2
            sp.y=(j.y+dy)*64-sp.height//2
                
        for i,sp in enumerate(self.tank_sprites):
            t:Tank=self.shop.tanks[i]
            sp.x=(t.x+OFFSET[0])*64
            sp.y=64
        js=set(self.shop.jobs)-set(self.shop.todo)
        for i,job in enumerate(js):
            j:Job=job
            sp=self.job_sprites[i]
            sp.x=(j.x+OFFSET[0])*64
            sp.y=(j.y+OFFSET[1])*64