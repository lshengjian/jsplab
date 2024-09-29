from src.core import  *
from src.envs import ElectroplateJobShopEnv

def test_shop():
    phaser:IParse=ExcelFileParser()
    #ins=paser.parse('epsp/demo/1x(3+1).xlsx')
    ins=phaser.parse('epsp/demo/2x(3+1).xlsx')
    shop=JobShop(ins)
    env=ElectroplateJobShopEnv(shop,2,2)
    obs,info=env.reset()
    print(obs[0:shop.num_machines]) #offset
    print(obs[1:shop.num_machines]) #working time
    print(obs[2:,shop.num_machines]) #
    print(obs[2:,shop.num_machines+1])
    print(obs[2:,:shop.num_machines])

    assert len(info['mask'])==shop.num_jobs
    assert (obs<=1).all()
    assert obs.shape==(shop.num_jobs+2,shop.num_machines+2)
    #assert len(obs)==num_jobs+num_machines+num_jobs+num_jobs*num_machines
if __name__ == '__main__':
    test_shop()