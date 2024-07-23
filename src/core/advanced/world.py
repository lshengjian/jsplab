
from __future__ import annotations
from typing import  List,Dict
from collections import defaultdict
from ..datadef.constant import Constant
from .advanced.componets import *
from .world_object import  *
#from .constants import CraneAction
from .advanced.crane import Crane
from .advanced.tank import Tank
from .workpiece import Workpiece
# from .cranehelper import CraneHelper
from .advanced.config import build
#from epsim.utils import get_state,get_observation # for image
import logging

from src.utils import get_dataclass_by_name
from omegaconf import OmegaConf
from .advanced.shapes import TILE_SIZE
logger = logging.getLogger(__name__.split('.')[-1])
'''
外部接口
1) 加入一批物料
add_jobs(codes:List[str]) #add_jobs(['A','A','B'])
2) 选择下一个天车为当前控制对象
next_crane()
3) 给当前天车发作业指令
set_command(action:int]) #set_command(0)
4) 给所有天车发作业指令
set_commands(actions:List[int]) #set_command([0,1])
5) 更新系统
update()
6) 获取当前天车的状态
get_observation()
7) 获取全部天车的状态
get_observations()

自动版规则：
1) 当上料槽位有空时,顺序把待加工物料放到槽位上
2) 当物料放入下料槽位后,物料加工结束,从系统内消失。

加分规则：
1) 在加工槽位出槽时加工的时间在正常加工时段,加1分
2) 物料正常加工结束,加10分

扣分规则：
1) 在加工槽位出槽时物料加工的时间少于最少或多余最多3秒内  减1分
2) 在加工槽位出槽时物料加工的时间少于最少或多余最多超3秒 减3分
3) 放错槽位 游戏结束
4) 天车相撞 游戏结束
'''


class World:
    def __init__(self,case_directory='test01',product_codes:List[str]=['A']*3,max_steps=3000,cool_down_time=100,auto_put_starts=True,auto_dispatch_crane=False):
        config = OmegaConf.load("conf/constant.yaml")
        self.args:Constant = get_dataclass_by_name('Constant')(**config)
        self.product_codes=product_codes
        TILE_SIZE=self.args.TILE_SIZE
        #self.config_directory=config_directory
        self.max_steps=max_steps
        self.auto_put_starts=auto_put_starts
        self.auto_dispatch_crane=auto_dispatch_crane
        self.init_cool_down=cool_down_time
        self.cool_down=cool_down_time
        self.is_over=False
        self.num_todo=0
        self._rewards={} #key : DP;H11;H12...
        self.is_timeout=False
        self.score=0
        self.num_step=0
        self.ops_dict:Dict[int,OperateData]=None
        self.name2cranes:Dict[str,Crane]={}
        self.max_y: int = 2
        self.all_cranes:List[Crane] = []
        self.pos_tanks:Dict[int,Tank] = {} 
        self.group_tanks:Dict[int,List[Tank]]=defaultdict(list)
        self.group_limits:Dict[int,List[int,int]]={}
        self.group_cranes:Dict[int,List[Crane]]=defaultdict(list)
        self.starts:List[Tank]=[]
        self.ends:List[Tank]=[]
        self.product_procs:Dict[str,List[OpTimeData]]=defaultdict(list)
        self.products=[]
        self.product_idx=0
        self.cur_crane_index=0
        self.state=None
        self.cur_prd_code:str=None
        
        self._masks={} #key : DP;H11;H12..
        self.load_config(case_directory)
        #self.dispatch:CraneHelper=CraneHelper(self)


    def reset(self):
        self.is_over=False
        self.is_timeout=False
        self.num_todo=0
        self.cur_crane_index=0
        self.product_idx=0
        self.cur_prd_code=None
        self.num_step=0
        self.score=0
        self.products.clear()
        for crane in self.all_cranes:
            crane.reset()
        for tank in  self.pos_tanks.values():
            tank.reset()
        Workpiece.UID={}
        self.cool_down=self.init_cool_down
        self.state=None
        self.add_jobs(self.product_codes)
        self._rewards={} 

    def add_jobs(self,ps:List[str]=[]):
        self.products.extend(ps)
        self.num_todo+=len(ps)
        if len(self.products)>0:
            self.cur_prd_code=self.products[0]
        #print('add_jobs')
        if self.auto_put_starts:
            self.products2starts()
    @property
    def  masks(self):
        rt={}
        for k,v in self._masks.items():
            rt[k]={'action_masks':v}
        return rt
    
    @property
    def  reward(self):
        return sum(self._rewards.values())

    @property
    def  cur_crane(self):
        return self.all_cranes[self.cur_crane_index]



    def next_crane(self):
        for c in self.all_cranes:
            c.color=Color(255,255,255)
        self.cur_crane_index=(self.cur_crane_index+1)%len(self.all_cranes)
        self.cur_crane.color=Color(255,0,0)
        
    def put_product(self):
        if self.cur_prd_code is None:
            self._rewards[self.args.DISPATCH_CODE]=-1
            return
        self.products2starts()


    def shift_product(self):
        self.cur_prd_code=None if len(self.products)<1 else self.products[0]
        
        if self.cur_prd_code is None:
            #self._rewards[SHARE.DISPATCH_CODE]=-1
            return 
        buff1=[]
        buff2=[]
        
        for p in self.products:
            if p==self.cur_prd_code:
                buff1.append(p)
            else:
                buff2.append(p)
        buff2.extend(buff1) 
        self.products=buff2
        self.cur_prd_code=buff2[0]
        
    def do_dispatch(self,action:ProductAction):
        self._rewards[self.args.DISPATCH_CODE]=0
        for i,crane in enumerate(self.all_cranes):
            self._rewards[crane.cfg.name]=0
        if action==ProductAction.Next:
            self.shift_product()
        elif action==ProductAction.SelectCurrent:
            self.put_product()
        

    def set_crane_commands(self,actions:Dict[str,CraneAction]):
        assert len(actions)==len(self.all_cranes)
        for i,crane in enumerate(self.all_cranes):
            self._rewards[crane.cfg.name]=0
            #print(actions)
            crane.set_command(actions[crane.cfg.name])

            
    def update(self):
        if self.is_over or self.is_timeout:
            return
        self.num_step+=1
        self.cool_down-=1
        

        if self.num_step>self.max_steps:
            self.is_timeout=True
            return
        
        for crane in self.all_cranes:
            crane.step()

        tanks=self.pos_tanks.values()
        for t in tanks:
            t.step()
        self._check_cranes()
        self._check_tanks()
        if self.num_todo<1:
            self.is_over=True
            self._rewards[self.args.DISPATCH_CODE]+=20
            logger.info("!!!GOOD JOB!!!")
        elif self.auto_put_starts:
            #print(self.todo_cnt)
            self.products2starts()
        self.score+=self.reward
    
    def num_jobs_in_first_group(self):
        rt=0
        for s in self.group_tanks[1]:
            if s.carrying != None:
                rt+=1
        for c in self.group_cranes[1]:
            if c.carrying != None:
                rt+=1
        return rt

    def get_state_img(self,scrern_img:np.ndarray,nrows,ncols): #仿真系统的全部状态数据
        self.state= None#get_state(scrern_img,nrows,ncols,SHARE.TILE_SIZE)
        return self.state
    
    def get_observation_img(self,agv:Crane):
        return  None#get_observation(self.state,agv.x,SHARE.MAX_CRANE_SEE_DISTANCE,SHARE.TILE_SIZE,SHARE.MAX_X)

    def get_state(self): #仿真系统的全部状态数据
        rt=[]
        for crane in self.all_cranes:
            rt.append(crane.state2data())
        for slot in self.pos_tanks.values():
            rt.append(slot.state2data()) 
        for pcode in self.products:
            wp=Workpiece.make_new(pcode)
            rt.append(wp.state2data())
        for k in range(len(rt),self.args.MAX_STATE_LIST_LEN):
            rt.append([0.]*len(rt[0]))
        return np.array(rt,dtype=np.float32)
    
    def get_observation(self,agv:Crane):
        group:int=agv.cfg.group
        rt=[]
              
        rt.append(agv.state2data())
        for crane in self.group_cranes[group]:
            if agv==crane:continue
            rt.append(crane.state2data())
        cs=[]
        for slot in self.group_tanks[group]:
            dis=abs(slot.x-agv.x)
            if dis<=self.args.MAX_CRANE_SEE_DISTANCE:
                cs.append((dis,slot))
        if len(cs)>0:
            cs.sort(key=lambda x:x[0])
            size=len(rt)
            for _,slot in cs:
                if size<self.args.MAX_OBS_LIST_LEN:
                    rt.append(slot.state2data())
                    size+=1
                else:
                    break 
                              
        for k in range(len(rt),self.args.MAX_OBS_LIST_LEN):
            rt.append([0.]*len(rt[0]))
        rt=np.array(rt,dtype=np.float32)
        #print(rt.shape)
        return rt.ravel()

         
    def get_crane_bound(self,crane:Crane)->Tuple[Tank|Crane,Tank|Crane]:
        g=crane.cfg.group
        x1,x2=map(int, self.group_limits[g])
        left=None
        right=None
        l_side=list(filter(lambda agv:agv.x<crane.x, self.group_cranes[g]))
        r_side=list(filter(lambda agv:agv.x>crane.x, self.group_cranes[g]))
        l_side.sort(key=lambda c:c.x,reverse=True)
        r_side.sort(key=lambda c:c.x)
        if len(l_side)>0:
            left=l_side[0]
            x1=left.x+1+self.args.MIN_CRANE_SAFE_DISTANCE

        if len(r_side)>0:
            right=r_side[0]
            x2=right.x-1-self.args.MIN_CRANE_SAFE_DISTANCE
        return x1,x2,left,right


    
    def products2starts(self):
        ps=self.products[:]
        if len(ps)<1:
            self._rewards[self.args.DISPATCH_CODE]-=0.1
            logger.info('no products!')
            return

        have_empty=False
        for s in self.starts:
            if s.carrying is None:
                have_empty=True
                break
        if not have_empty:
            self._rewards[self.args.DISPATCH_CODE]-=0.1
            logger.info('no empty start!')
            return
        doing_jobs=self.num_jobs_in_first_group()

        if  doing_jobs>int(len(self.group_cranes[1])+1):
            self._rewards[self.args.DISPATCH_CODE]-=0.01
            logger.info('Too much material to handle at the same time!')
            return
        if self.auto_put_starts and np.random.random()<0.995:
            return
        
        for s in self.starts:
            #print(s)
            if  len(ps)>0  and s.carrying is None:
                wp:Workpiece=Workpiece.make_new(ps[0],s.x)
                #print('products2starts')
                self.plan_next(wp)
                s.put_in(wp)
                wp.start_tick=self.num_step
                wp.end_tick=9999 #todo
                t=0
                for limit in self.product_procs[ps[0]]:
                    t+=limit.op_time
                wp.total_op_time=t
                ps.remove(ps[0])
                break
        self.products=ps
        self.cur_prd_code=None if len(ps)<1 else ps[0]

    def load_config(self,config_directory:str):
        self.ops_dict,tanks,cranes,procs=build(config_directory)
        self.group_limits.clear()
         
        self.all_cranes.clear()
        self.group_cranes.clear()

        self.pos_tanks.clear()
        self.group_tanks.clear()
                
        self.starts.clear()
        self.ends.clear()
        self.product_procs.clear()


        for data in procs:
            pd:OpTimeData=data
            self.product_procs[pd.product_code].append(pd)

        for data in tanks:
            tank_data:TankData=data
            g=tank_data.group
            x1,x2=self.group_limits.get(g,[1000,-1000])
            for x in tank_data.offsets:
                if x<x1:
                    x1=x
                if x>x2:
                    x2=x 
                self.group_limits[g]=[int(x1),int(x2)]   
                tank:Tank=Tank(x,tank_data,self.args)
                tank.color=self.ops_dict[tank.cfg.op_key].color
                if tank_data.op_key==self.args.START_KEY:
                    self.starts.append(tank)
                elif tank_data.op_key==self.args.END_KEY:
                    self.ends.append(tank)
                self.pos_tanks[int(x)]=tank
                self.group_tanks[g].append(tank)

        for data in cranes:
            cfg:CraneData=data
            crane:Crane=Crane(cfg.offset,cfg,self.args)
            self.name2cranes[cfg.name]=crane
            self.all_cranes.append(crane)
            self.group_cranes[cfg.group].append(crane)
        self.max_x: int = max(list(self.pos_tanks.keys()))
     


    def _get_next_op_limit(self,wp:Workpiece):
        slot:Tank=wp.attached
        assert slot  is not None
        cur=wp.target_op_data
        ps=self.product_procs[wp.product_code]
        cur_idx=ps.index(wp.target_op_data)
        rt=None
        if cur_idx<len(ps)-1:
            rt=ps[cur_idx+1]
        return rt



                
    def mask2str(self,masks):
        flags=[]
        for i,flag in enumerate(masks):
            if flag: flags.append(Directions[i])
        return ''.join(flags)

    def get_masks(self,crane:Crane):
        self.dispatch.decision()
       
        #return self.masks[crane.cfg.name]

    def get_dispatch_masks(self):
        rt=np.ones(3,dtype=np.uint8)
        
        is_full=True
        for s in self.starts:
            if s.carrying is None:
                is_full=False
                break 
        doing_jobs=self.num_jobs_in_first_group()

        if is_full or doing_jobs>int(len(self.group_cranes[1])) or self.cool_down>0:
            #print('is_full')
            rt[ProductAction.SelectCurrent]=0
        if len(self.products)<1:
            #print('no more products')
            rt[ProductAction.Next]=0
            rt[ProductAction.SelectCurrent]=0
        self._masks[self.args.DISPATCH_CODE]=rt
        if self.cool_down<1:
            self.cool_down=self.init_cool_down

    

    def plan_next(self,wp:Workpiece):
        ps=self.product_procs[wp.product_code]
        #print(ps[0])
        if wp.target_op_data is None:#第一次规划，放到上料位
            wp.set_next_operate(ps[0],self.ops_dict)
            return
        idx=ps.index(wp.target_op_data)
        if idx<len(ps)-1:
            wp.set_next_operate(ps[idx+1],self.ops_dict)



    def _translate(self,source:Crane|Tank,target:Crane|Tank):
        '''
        在天车和工作槽位间转移物料
        '''  

        wp,reward=source.take_out()
        if type(target) is Tank: 
            if target in self.ends:
                self._rewards[source.cfg.name]+=10
                self.num_todo-=1
                del wp
                return 
            if target.cfg.op_key==self.args.SWAP_KEY:
                x=target.x+1
                target=self.pos_tanks[x]
        if target.carrying!=None:
            logger.error(f'{target} already have {target.carrying}')
            self._rewards[source.cfg.name]-=5
            self.is_over=True
            return 

        target.put_in(wp)
        if type(target) is Crane:
            self._rewards[target.cfg.name]=reward
            self.plan_next(wp)
            # if target.locked_slot!=None:
            #     print(f'{target} unlock {source}')
            #     target.reset_lock()
            

         
        



    def _check_collide(self,crane:Crane)->bool:
        '''
        天车移动后进行碰撞检测
        '''  
        collide=False
        pos=self._round(crane.x)
        slot=self.pos_tanks.get(pos,None)
        if slot!=None and abs(crane.y-1)<0.1:
            wp:Workpiece=crane.carrying
            if wp==None and crane.last_action==CraneAction.Top and slot.carrying!=None:
                self._translate(slot,crane)
                
            if wp!=None and crane.last_action==CraneAction.Bottom  :
                if wp.target_op_data.op_key!=slot.cfg.op_key:
                    logger.error(f'{wp.target_op_data.op_key} not same as {slot.cfg.op_key}')
                    self._rewards[crane.cfg.name]-=5
                    self.is_over=True
                    return
                self._translate(crane,slot)
                
                    
        cranes=self.group_cranes[crane.cfg.group]
        for c in cranes:
            if c==crane:
                continue
            if abs(c.x-crane.x)<self.args.MIN_CRANE_SAFE_DISTANCE:
                collide=True
                logger.error(f'{c} too close to {crane}')
                if c.last_action!=CraneAction.Stay:
                    self._rewards[c.cfg.name]-=5
                if crane.last_action!=CraneAction.Stay:
                    self._rewards[crane.cfg.name]-=5
                break

        return collide
        



    def _check_tanks(self):
        tanks=self.pos_tanks.values()
        for t in tanks:
            if t.cfg.op_key<self.args.MIN_OP_KEY or t.carrying is None:
                continue
            op:OpTimeData=t.carrying.target_op_data
            if t.timer>op.max_time+self.args.LONG_ALARM_TIME:
                self.is_over=True
                logger.error(f'{t} op timeout!')
                agvs=[]
                for agv in self.group_cranes[t.cfg.group]:
                    if (agv.carrying is None):
                        agvs.append((abs(agv.x-t.x),agv))
                
                if len(agvs)>0:
                    agvs.sort(key=lambda x:x[0])
                    agv=agvs[0][1]  #最近的空闲天车失职！
                    self._rewards[agv.cfg.name]-=5
                    

                break  

    def _check_cranes(self):
        for c in self.all_cranes:
            if  self._out_bound(c):
                logger.error(f'{c} out  bount!')
                self._rewards[c.cfg.name]-=5
                self.is_over=True
                
                return
            if self._check_collide(c):
                self.is_over=True
                #logger.error(f'{c} collided!')
                return
                
    def _out_bound(self,crane:Crane):
        x=crane.x
        y=crane.y
        x1,x2=self.group_limits[crane.cfg.group]
        return x<x1 or y<0 or x>x2 or y>self.max_y
    
    def _round(self,x:float)->int:
        return int(x+0.5)

    
    def pprint(self):
        for k,cs in self.group_cranes.items():
            print(f'Group {k}')
            for c in cs:
                print(f'{c}')
        print(f'='*18)
        for k,cs in self.group_tanks.items():
            print(f'Group {k}')
            for c in cs:
                print(f'{c}')





   





 
                












 

 