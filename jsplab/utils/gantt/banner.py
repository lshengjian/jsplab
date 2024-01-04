# flake8: noqa

'''

print("\033[0;40;32m color!!! \033[0m Hello \n");

\033 声明了转义序列的开始，然后是 [ 开始定义颜色。后面的 1 定义了高亮显示字符。
然后是背景颜色,40表示黑色背景。
接着是前景颜色,32表示绿色。
用 \033[0m 关闭转义序列， \033[0m 是终端默认颜色。
字色              背景              颜色
---------------------------------------
30                40              黑色
31                41              紅色
32                42              綠色
33                43              黃色
34                44              藍色
35                45              紫紅色
36                46              青藍色
37                47              白色

0 终端默认设置（黑底白字）
1 高亮显示
4 使用下划线
5 闪烁
7 反白显示
8 不可见



'''
# import importlib.metadata
# __version__ = importlib.metadata.version("graph_jsp_env")

VERSION = '0.0.1'


CEND = '\33[0m'
CBOLD = '\33[1m'
CITALIC = '\33[3m'
CURL = '\33[4m'
CBLINK = '\33[5m'
CBLINK2 = '\33[6m'
CSELECTED = '\33[7m'

CBLACK = '\33[30m'
CRED = '\33[31m'
CGREEN = '\33[32m'
CYELLOW = '\33[33m'
CBLUE = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE = '\33[36m'
CWHITE = '\33[37m'

CBLACKBG = '\33[40m'
CREDBG = '\33[41m'
CGREENBG = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG = '\33[44m'
CVIOLETBG = '\33[45m'
CBEIGEBG = '\33[46m'
CWHITEBG = '\33[47m'

# noqa: E501, W291
banner = f"""          
    {CEND}{CGREEN}{CBOLD}
    =================================================={CBLINK}
    █            Job Shop Problem Environment        █  
    ==================================================
    {CEND}     
    {CVIOLETBG}Version:   {CYELLOW}{VERSION} {CEND} {CBLUE}(by Alex){CEND}            
"""


