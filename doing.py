from jsplab.core.jobshop import JobShop

if __name__ == "__main__":
    hs1=JobShop.get_safe_hoists(0,1,3,2)
    assert hs1=={0}
    hs2=JobShop.get_safe_hoists(9,8,3,2)
    assert hs2=={2}