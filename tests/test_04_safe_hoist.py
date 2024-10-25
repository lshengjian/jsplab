from jsplab.core.jobshop import JobShop
# import time
# start_time = time.perf_counter()
def test_safe():
    hs1=JobShop.get_safe_hoists(0,1,3,2)
    assert hs1=={0}
    hs2=JobShop.get_safe_hoists(9,8,3,2)
    assert hs2=={2}
    hs1=JobShop.get_safe_hoists(0,4,3,2)
    assert hs1=={0,1,2}
    hs2=JobShop.get_safe_hoists(9,4,3,2)
    assert hs2=={2,1,0}
    hs1=JobShop.get_safe_hoists(0,6.36,3,2)
    assert hs1=={0,1,2}
    hs2=JobShop.get_safe_hoists(9,6.36,3,2)
    assert hs2=={2,1}