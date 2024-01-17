import numpy as np
from colorama import init
from numpy.lib.index_tricks import MGridClass
from termcolor import colored
import copy,random
from pjsp import BIG_NUM
from pjsp.utils import get_critical_path

__all__=['LSO']


class LSO:
    def __init__(self, instance,N=20,mp=0.2):
        super().__init__()
        self.instance=instance
        self.op_times = instance.op_times
        self.job_steps=instance.job_steps
        self.step_jobs=instance.step_jobs
        self.job_ids=list(self.job_steps.keys())
        
        self.N = N
        self.D = sum(self.job_steps.values())
        self.num_leader=int(self.N*mp)
        
        init()  # Init colorama for color display
        self.reset()

    def reset(self):
        self.cache=[]
        self.Cs = np.zeros((self.N,self.D*2),dtype=int)#基因段,前半部分是机器，后半部分是操作工件
        self.Fs=np.ones(self.N,dtype=int)*BIG_NUM
        self.Sols=[None]*self.N
        self.cnts=np.zeros(self.N,dtype=int)
        self.best=BIG_NUM
        self.best_sol=None
        self.best_cnt=0

        for i in range(self.N):
            p=np.random.random()
            ms,js=None,None
            ms,js=self.instance.random_selection()
            '''
            if p<0.333:
                ms,js=self.instance.random_selection()
            elif p<0.666:
                ms,js=self.instance.local_selection()
            else:
                ms,js=self.instance.global_selection()
            '''
                
            self.Cs[i,:]=list(ms)+list(js)
            self.Fs[i],self.Sols[i]=self.fitness(ms,js)
        self.arg_idxs=np.argsort(self.Fs)    
    def get_m_idx(self,idx):
        js=self.Cs[idx,self.D:]
        job_steps={}
        for i,id in enumerate(js):
            step=job_steps.get(id,1)
            op_inx=self.instance.get_op_index(id,step)
            if op_inx==i:
                return op_inx
        
        return -1
   
    def run(self,T=200,verbose=True):
        if verbose:
            print(colored('-'*16, 'yellow'))
            print(colored('LSO start!', 'yellow'))
            print(colored(f'N:{self.N},D:{self.D}', 'yellow'))
        num_leader=self.num_leader
        self.reset()
        #np.random.seed(1972)


        for t in range(1,T+1):
            k=t/T
            self.best_cnt+=1
            for i,p in enumerate(self.arg_idxs):
                partner_idx=self.arg_idxs[np.random.randint(num_leader)]
                while partner_idx==p:
                    partner_idx=self.arg_idxs[np.random.randint(num_leader)]
                ms1,ms2=self.crossover_machine(p,partner_idx,0.5)#-0.4*k
                os1,os2=self.crossover_operation(p,partner_idx)
                checks=[(ms1,os1),(ms2,os2)]#,(ms1,os2),(ms2,os1)
                
                self.cnts[p]+=1
                color='red' if i<num_leader else 'green'
                for ms,os in checks:
                    fit,sol=self.fitness(ms,os)
                    flag=self.update_chs(p,fit,ms,os,sol,False)
                    if t>T//2 and flag<1 and random.random()<k*0.5:
                        flag=self.update_chs(p,fit,ms,os,sol,True)
                    if flag>1 and verbose:
                        print(colored(f"[{t:03d}] {i+1} found new best:{self.best}", color))
                        break

                if self.cnts[p]>=T//20:
                    if np.random.random()<0.5:
                        ms=self.Cs[p,0:self.D]
                        os=self.instance.get_random_jobs()
                    else:
                        ms=self.instance.get_random_machines()
                        os=self.Cs[p,self.D:]
                    fit,sol=self.fitness(ms,os)
                    self.update_chs(p,fit,ms,os,sol,True)

                if 0<i<3 :
                    self.local_search(p)     
            if self.best_cnt>=T//3:
                if verbose:
                    print(colored(f"[{t:03d}] no better solution found", 'yellow'))
                break
            if (t%4==0):
                self.arg_idxs=np.argsort(self.Fs) 
        
        
        if verbose:
            print(colored('LSO end!', 'yellow'))
        
        return self.best,self.best_sol
    #机器部分交叉
    def crossover_machine(self,idx1,idx2,p):
        ms1=self.Cs[idx1,0:self.D].copy()
        ms2=self.Cs[idx2,0:self.D].copy()
        ps=np.random.rand(self.D)
        idxs=ps<p
        ms1[idxs],ms2[idxs]=ms2[idxs],ms1[idxs]
        return ms1,ms2
        
    #工序交叉部分
    def crossover_operation(self,idx1,idx2):
        D=self.D
        job_num=self.instance.number_total_jobs
        data1=self.Cs[idx1,D:]
        data2=self.Cs[idx2,D:]

        os1 =self.Cs[idx1,D:].copy()
        os2 =self.Cs[idx2,D:].copy()

        job_ids = [i+1 for i in range(job_num)]
        random.shuffle(job_ids)
        r = random.randint(1, job_num - 1)
        ds = job_ids[0:r]
        idxs1=np.zeros(D,dtype=bool)
        idxs2=np.zeros(D,dtype=bool)
       
        for d in ds:
            idxs1+=os1==d
            idxs2+=os2==d
        os1[~idxs1]=data2[~idxs2]
        os2[~idxs2]=data1[~idxs1]
        return os1,os2
        

    def replace_machine(self,ms,op):
        op_idx=op['op_idx']
        m_id=self.instance.get_quick_machine(op_idx,op['machine_id'])
        ms2=copy.deepcopy(ms)
        ms2[op_idx]=m_id
        return ms2


    def swap_ops(self,js,op1,op2):
        js2=copy.deepcopy(js)
        idx1,idx2=op1['idx'],op2['idx']
        js2[idx1],js2[idx2]=op2['job_id'],op1['job_id']
        #op1['op_idx'],op2['op_idx']=op2['op_idx'],op1['op_idx']
        return js2

    def update_chs(self,idx,fit,ms,os,sol=None,force=False):
        flag= 0
        if fit<self.Fs[idx]:
            flag=1
            self.cnts[idx]=0
        if force or flag:
            self.Fs[idx]=fit
            self.Sols[idx]=sol
            self.Cs[idx,0:self.D]=ms
            self.Cs[idx,self.D:]=os

        if fit<self.best:
            self.best=fit
            self.best_sol=sol
            self.best_cnt=0
            
            flag=2
        return flag



    def local_search(self,idx,verbose=True):
        ns=[]
        sol=self.Sols[idx]
        ms,js=self.instance.encode(sol)
        cps=get_critical_path(sol)
        
        for cp in cps:
            
            head=cp[0]
            tail=cp[-1]
            for blk in cp:
                
                if len(blk.ops)==1:
                    #print(blk)
                    ms1=self.replace_machine(ms,blk.ops[0])
                    ns.append((ms1,js))
                if len(blk.ops)>=2:
                    if blk==head:
                        js1=self.swap_ops(js,blk.ops[-2],blk.ops[-1])
                        # if js1 not in self.cache:
                        #     self.cache.append(js1)
                        ns.append((ms,js1))
                        
                    elif blk==tail or len(blk.ops)==2:
                        js1=self.swap_ops(js,blk.ops[0],blk.ops[1])
                        ns.append((ms,js1))

                    elif len(blk.ops)>3:
                        js1=self.swap_ops(js,blk.ops[-2],blk.ops[-1])
                        js2=self.swap_ops(js1,blk.ops[0],blk.ops[1])
                        ns.append((ms,js2))
                # while len(self.cache)>7:
                #      self.cache.pop(0)
        for ms1,js1 in ns:
            fit,sol=self.fitness(ms1,js1)
            flag=self.update_chs(idx,fit,ms1,js1,sol,False)
            if flag>1 and verbose:
                print(colored(f'local search found new best:{self.best}', 'yellow'))
                #break
  
                
    def fitness(self,ms,js):
        return self.instance.decode(ms,js)


