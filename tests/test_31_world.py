# import  sys
# from os import path

# dir=path.abspath(path.dirname(__file__) + './..')
# sys.path.append(dir)
# from src.core import World

# def test_build_world():
#     wd=World('test01')
#     assert len(wd.group_cranes)==1
#     x1,x2=wd.group_limits[1]
#     assert x1==1 and x2==9


# def test_add_jobs():
#     wd=World('test01')
#     wd.reset()
#     wd.add_jobs(['A']*2)
#     assert len(wd.products)==2
#     assert wd.starts[0].carrying is None
#     assert wd.starts[1].carrying is None

#     assert len(wd.pos_tanks)==7
#     assert len(wd.product_procs['A'])==3
#     wd.pprint()

# if __name__ == "__main__":
#     test_add_jobs()    
    

