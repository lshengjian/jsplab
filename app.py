'''
from hydra import initialize_config_dir
from omegaconf import OmegaConf
def main():
    # 手动初始化配置目录
    #initialize_config_dir(config_dir="conf/server", job_name="my_app")

    # 手动加载
    cfg = OmegaConf.load("conf/server/apache.yaml")

    print(OmegaConf.to_yaml(cfg))

if __name__ == '__main__':
    main()

'''
from omegaconf import DictConfig, OmegaConf
import hydra

@hydra.main(version_base=None, config_path="./conf", config_name="config")
def my_app(cfg:DictConfig):
    print(OmegaConf.to_yaml(cfg))

if __name__ == "__main__":
    my_app()
