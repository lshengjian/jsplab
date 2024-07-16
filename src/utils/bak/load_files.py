from pathlib import Path
from typing import List


def files_in_dir(directory: str) -> List[Path]:
    """
        load all files within the specified directory
    :param directory: the directory of files
    :return: a list of file path in the directory
    """
    rt: List[Path] = []
    dir = Path(directory)
    if not dir.exists():
        print(f'{directory} not exists')
        return rt

    for file in dir.glob('*'):
        if file.is_file:
            rt.append(file)

    return rt
