import re
from typing import List


def text2nums(text: str, toInt=True):
    ds = map(float, re.findall(r'\d+\.?\d*', text))
    ds = map(lambda x: round(x) if toInt else round(x, 2), ds)
    return list(ds)


def clean_comment(lines: List[str]) -> List[List[int]]:
    rt = []
    for line in lines:
        line = line.split("#")[0]
        ds = text2nums(line)
        if len(ds) > 0:
            rt.append(ds)
    return rt
