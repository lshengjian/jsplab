from ortools.sat.python import cp_model
from collections import defaultdict,namedtuple
import matplotlib.pyplot as plt
from jsplab.conf.mhp import MultiHoistProblem

class OrToolSolver:
    def __init__(self,p:MultiHoistProblem,up_time=1,down_time=1):
        self.problem=p
        self.hoists_pos = defaultdict(list)
        self.hoists_steps = defaultdict(list)
        self.up_time=up_time
        self.down_time=down_time
        self.model = cp_model.CpModel()

    def set_hoist_pos(self,hoist_index,t0,tick,offset,flag):
        x1,x2=self.problem.min_offset,self.problem.max_offset
        model=self.model 
        horizon=self.horizon
        x=model.new_int_var(x1, x2, '')
        t=model.NewIntVar(0, 2*horizon, '')
        model.add(t==t0+tick)
        r = model.NewIntVar(0, horizon, '')
        model.add_modulo_equality(r,t,self.T)
        model.add_element(r,self.hoists_pos[hoist_index],x)
        model.add(x==offset).only_enforce_if(flag)

    def solve(self):
        model=self.model 
        ticks, horizon = self.get_max_time()
        T=model.new_int_var(horizon//2, horizon, f'T')
        self.T=T
        num_hoists = self.problem.num_hoists  
        
        
        
        num_moves = sum([len(proc_times) for proc_times in ticks])
        all_moves = range(num_moves)
        all_hoists = range(num_hoists)
        shifts = {}
        
        for m in all_moves:
            for h in all_hoists:
                shifts[(m,h)] = model.new_bool_var(f"m{m}_h{h}")
        for  m in all_moves:
            model.add_exactly_one(shifts[(m,h)] for h in all_hoists)
        cumulative_var=self.set_hoists_safe_pos()

        mi=0
        for p_id,proc_times in enumerate(ticks):
            t0=model.new_constant(0) if p_id==0 else model.new_int_var(0, horizon, f'proc{p_id}')
            #proc_start.append(t0)
            model.add(t0<T)
            times=list(proc_times.keys())
            for start in times:
                
                xs=set()
                for hoist_pos in proc_times[start]:
                    tick,offset=hoist_pos.tick,hoist_pos.x
                    xs.add(offset)
                xs=list(xs)
                hs=set(self.problem.select_hoists_by_offset(xs[0]))&set(self.problem.select_hoists_by_offset(xs[1]))
                hs=list(hs)
                print(mi,xs,hs)  
                if len(hs)==1:
                    model.add(shifts[(mi,hs[0])]==1)

                for h in all_hoists:
                    for hoist_pos in proc_times[start]:
                        tick,offset=hoist_pos.tick,hoist_pos.x
                        self.set_hoist_pos(h,t0,start+tick,offset,shifts[(mi,h)])
                mi+=1


        model.minimize(cumulative_var+T)

        # 创建求解器并求解模型
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # 输出结果
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            TV=solver.Value(T)
            print(f'T: {TV}')
            
            for h in all_hoists:
                Y=[solver.Value(pos) for pos in self.hoists_pos[h]]
                x = range(len(Y))
                plt.plot(x, Y, label=f'H{h}')

            plt.xlabel('Index')
            plt.ylabel('Value')
            #plt.xticks(range(0,50,2))
            plt.title(f'T={TV}')
            plt.legend()
            plt.show()
        else:
            print('No solution found.')

    def set_hoists_safe_pos(self,  ):
        x1,x2=self.problem.min_offset,self.problem.max_offset
        model=self.model
        num_hoists=self.problem.num_hoists
        horizon=self.horizon

        for t in range(horizon):
            for i in range(num_hoists):
                self.hoists_pos[i].append(model.new_int_var(x1, x2, f'x_{i}_{t}'))
        for i in range(0,num_hoists):
            pos_T=model.NewIntVar(x1, x2, '')
            model.add_element(self.T,self.hoists_pos[i],pos_T)
            model.add(self.hoists_pos[i][0]==pos_T)
        # 添加安全距离约束
        for t in range(horizon):
            for i in range(0,num_hoists):
                if i>0:
                    model.add(self.hoists_pos[i][t]>=self.hoists_pos[i-1][t]+2)
                if t>0:
                    dx=model.NewIntVar(0,x2-x1,'')
                    model.add_abs_equality(dx,self.hoists_pos[i][t-1]-self.hoists_pos[i][t])
                    model.add(dx<=1)
                    self.hoists_steps[i].append(dx)
                steps=[]
        for hoist in self.hoists_steps.keys():
            steps.extend(self.hoists_steps[hoist])

        return  cp_model.LinearExpr.Sum(steps)

    def get_max_time(self):
        ticks=self.problem.get_times_ticks()
        max_times=[]
        for proc_times in ticks:
            max_t=0
            times=list(proc_times.keys())
            start=times[-1]
            move_time=proc_times[start][-1].tick
            max_t=start+move_time
            max_times.append(max_t)
        
        horizon=max(max_times)#//num_hoists+1
        self.horizon=horizon
        return ticks,horizon

'''
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        def __init__(self, shifts, num_moves, num_hoists):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._num_moves = num_moves
            self._num_hoists = num_hoists
            self._solution_count = 0
            self._solution_limit = 5

        def on_solution_callback(self):
            self._solution_count += 1
            print(f"Solution {self._solution_count}")
            for h in range(self._num_hoists):
                print(f"H-{h}")
                for i in range(self._num_moves):
                    is_working = False
                    if self.value(self._shifts[(i, h)]):
                            is_working = True
                            print(f"  shift m{i+1}")

            if self._solution_count >= self._solution_limit:
                print(f"Stop search after {self._solution_limit} solutions")
                self.stop_search()

        def solutionCount(self):
            return self._solution_count
'''