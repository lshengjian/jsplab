from src.core import  *
from src.envs import ElectroplateJobShopEnv
def test_shop():
    phaser:IParse=ExcelFileParser()
    #ins=paser.parse('epsp/demo/1x(3+1).xlsx')
    ins=phaser.parse('epsp/demo/2x(3+1).xlsx')
    shop=JobShop(ins)
    env=ElectroplateJobShopEnv(shop,2,2)
    num_jobs=4
    num_machines=4
    obs,info=env.reset()

    assert len(info['mask'])==4
    assert (obs<=1).all()
    assert len(obs)==num_jobs+num_machines+num_jobs+num_jobs*num_machines
