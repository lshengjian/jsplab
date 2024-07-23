import os,numpy as np
from PIL import Image
from gymnasium.error import DependencyNotInstalled
from src.datadef.constant import Constant
from typing import Dict
from src.core import World,Crane
from src.core.advanced.shapes import get_slot_shape ,get_crane_shape,get_workpiece_shape
from src.core.advanced.rendering import set_color,blend_imgs
from copy import deepcopy
RENDER_DIR=os.path.abspath(os.path.dirname(__file__) )

def get_font(pygame,font_size=16,shadow=False):
    if shadow:
        return pygame.font.Font(RENDER_DIR+'/fonts/WHARMBY.TTF', font_size)
    return pygame.font.SysFont('arial', font_size)


def make_surface(img,pygame):
    #img= np.transpose(img, axes=(1, 0, 2))
    img=img.swapaxes(0,1)
    return pygame.surfarray.make_surface(img)


class Renderer:
    #LANG:str='chinese'
    def __init__(self,world:World):
        self.world:World=world
        #config = OmegaConf.load("conf/constant.yaml")
        #self.CONST:Constant=get_dataclass_by_name('Constant')(**config)
        self.args:Constant=world.args
        args=self.args

        self.nrows=args.ROWS_TILE
        self.ncols=args.COLS_TILE
        tile_size=args.TILE_SIZE
        self.window_size =  self.ncols*tile_size, tile_size*(self.nrows*3+args.ROWS_TEXT)
        self.draw_text=args.DRAW_TEXT
        self.tile_size=args.TILE_SIZE
        self._surface = None
        self.clock = None
    
    def show_text(self,pygame,msg,x,y,fsize=16,shadow=False,color=(255, 221, 85)):
        font=get_font(pygame,fsize,shadow)
        textSerface = font.render(msg, True,color )#,(0,0,0)
        width, height = font.size(msg)
        self._surface.blit(textSerface, (x, y))
    
    def _draw_products(self,pygame):
        x=0
        for code in self.world.products:
            img=get_workpiece_shape(code)
            if self.world.cur_prd_code==code:
                img=set_color(img,245,16,40)
            self._surface.blit(make_surface(img,pygame),(x,self.args.TILE_SIZE))
            x+=self.args.TILE_SIZE
        
    def _draw(self,pygame):
        self._surface.fill((0,0,0))
        ps_size=len(self.world.products)
        left=(ps_size+0.2)*self.tile_size
        reward=self.world.reward
        score=self.world.score
        step_count=self.world.num_step
        
        key=self.world.cur_crane.cfg.name
        if self.draw_text:
            self.show_text(pygame,f'R:{reward:.1f} S:{score:.1f} T:{step_count}',
                       left,self.tile_size//3,self.tile_size,True,(155,34,237))
        
        key=self.world.cur_crane.cfg.name
        if self.draw_text and key in self.world._masks:
            flags=self.world.mask2str(self.world._masks[key])
            self.show_text(pygame,f'{flags}',left,self.tile_size+20,self.tile_size//2,False,(55,234,137))
        self._draw_products(pygame)
        merges=[]
        crane_offsets:Dict[int,Crane]={}#:
        for agv in self.world.all_cranes:
            x=int(agv.x+0.5)
            if  x in self.world.pos_tanks and agv.y>=1:
                merges.append(x)
                crane_offsets[x]=agv
        for x,t in self.world.pos_tanks.items():
            r=x//self.ncols
            c=x%self.ncols
            if r%2==1:
                c=self.ncols-1-c
            if x not in merges:
                self._surface.blit(make_surface(t.image,pygame),(c*self.tile_size,self.tile_size*(3*(r+1)+1)))
            else:
                img2=deepcopy(t.image)
                #img2[:,:,:]=t.image
                crane_img=crane_offsets[x].image
                img2=blend_imgs(crane_img,img2,(0,int(crane_offsets[x].y-1)*self.tile_size))
                self._surface.blit(make_surface(img2,pygame),(c*self.tile_size,self.tile_size*(3*(r+1)+1)))
            
                
        for agv in self.world.all_cranes:
            x=int(agv.x+0.5)
            if  x in merges: continue
            r=x//self.ncols
            c=x%self.ncols
            if r%2==1:
                c=self.ncols-1-c
            img=make_surface(agv.image,pygame)
            self._surface.blit(img,(c*self.tile_size,(agv.y+3*(r+1))*self.tile_size))
           


    def render(self,mode='ansi'):
        if mode=='ansi':
            return
        try:
            import pygame
            import pygame.font
            #from pygame import gfxdraw
            
        except ImportError as e:
            raise DependencyNotInstalled(
                "pygame is not installed, run `pip install gymnasium`"
            ) from e

        if self._surface is None:
            pygame.init()
            if mode == "human":
                pygame.display.init()
                pygame.display.set_caption(self.args.WINDOW_TITLE)
                #self.font  =  pygame.font.Font(None,26)
                self._surface = pygame.display.set_mode(self.window_size)# ,pygame.DOUBLEBUF, 32)
            elif mode == "rgb_array":
                self._surface = pygame.Surface(self.window_size)#,pygame.SRCALPHA, 32)
                
                #print(self._surface.get_width(), self._surface.get_height())

        assert (
            self._surface is not None
        ), "Something went wrong with pygame. This should never happen."

        if self.clock is None:
            self.clock = pygame.time.Clock()
        
        self._draw(pygame)
        pygame.event.pump()
        if mode == "human":
            pygame.display.flip()
            if self.args.FPS>0:
                self.clock.tick(self.args.FPS)
            return


        #elif mode == "rgb_array":
            # img=pygame.image.tostring(self._surface, 'RGB')
            # img=Image.frombytes('RGB', (self._surface.get_width(), self._surface.get_height()), img)
            # img=img.resize((self.ncol*SHARE.TILE_SIZE, SHARE.TILE_SIZE*self.nrow*3))
        return np.array(pygame.surfarray.pixels3d(self._surface)).swapaxes(0,1)

    def close(self):
        pass

 