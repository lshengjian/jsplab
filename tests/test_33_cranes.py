# import  sys
# from os import path

# dir=path.abspath(path.dirname(__file__) + './..')
# sys.path.append(dir)
# from src.core import build,World,Workpiece,CraneAction

# def test_cranes():
#     world=World()
#     world.reset()
#     world.add_jobs(['A'])

#     start=world.starts[0]
#     wp:Workpiece=start.carrying
#     assert wp.y==1 and  wp.x==1
#     assert  wp.attached==start and start.carrying==wp

#     crane=world.group_cranes[1][0]
#     assert   crane.x==3 and crane.y==2
#     crane.set_command(CraneAction.Left)
#     world.update()
#     assert crane.x==2 and crane.y==2
#     crane.set_command(CraneAction.Left)
#     world.update()
#     crane.set_command(CraneAction.Top)
#     world.update()
#     assert crane.x==1 and crane.y==1
#     assert  wp.attached==crane and crane.carrying==wp
#     assert wp.x==1 and wp.y==1
#     assert wp.target_op_limit.op_name=='镀银'
#     crane.set_command(CraneAction.Top)
#     world.update()
#     for i in range(8):
#         crane.set_command(CraneAction.Right)
#         world.update()
#     assert wp.y==0 and  wp.x==9
#     crane.set_command(CraneAction.Bottom)
#     world.update()
#     assert wp.y==1
#     crane.set_command(CraneAction.Bottom)
#     world.update()
#     assert world.is_over
#     #assert crane.carrying==None
    

 


# if __name__ == "__main__":
#     test_cranes()

