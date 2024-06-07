import yaml
import importlib
import time
import pandas as pd

from functools import lru_cache

# 假设你有一个函数用于加载模块
@lru_cache(maxsize=None)  # maxsize=None表示无限制缓存大小
def load_class(algorithm_name):
    try:
        # 使用importlib动态加载模块
        module = importlib.import_module(f'algorithms.{algorithm_name}')
        return getattr(module, algorithm_name)
    except ImportError:
        print(f"Module {algorithm_name} not found.")
        return None

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        
        return result,run_time
    return wrapper
# 定义算法工厂函数
def get_algorithm_instance(algorithm_name, parameters):
    # 获取算法类
    algorithm_class = load_class(algorithm_name)
    # 实例化算法类，并传入参数
    algorithm_instance = algorithm_class(**parameters)
    return algorithm_instance
@measure_time
def run_algorithm(algorithm, test_case):
    print(f"{algorithm['name']}, {test_case['name']}")
    algorithm_instance = get_algorithm_instance(algorithm['name'], algorithm['parameters'])
    # 执行算法
    return algorithm_instance.run(test_case['file'])

def main():
    # 读取YAML配置文件
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # 获取算法和测试案例的列表
    algorithms = config['algorithms']
    test_cases = config['test_cases']

    results = []
    for a in algorithms:
        for t in test_cases:
            num,run_time=run_algorithm(a,t)
            print(num,run_time)
            #print(f"Running time of {func.__name__}: {run_time:.4f} seconds")
            results.append({'Algorithm': a['name'], 'Test Case':t['name'],'Num':num, 'Run Time': run_time})
    results_df = pd.DataFrame(results)
    results_df = results_df.round(6)
    results_df.to_excel('results.xlsx', index=False)
if __name__ == '__main__':
    main()

        