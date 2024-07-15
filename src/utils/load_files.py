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
            # with open(file, 'r') as f:
            #     text = f.readlines()
            # ins=None
            # if file.suffix=='.fjs':
            #     ins = InstanceFJSP(file.stem)
            # elif file.suffix=='.js':
            #     ins=InstanceJSP(file.stem)
            # ins.parse(text)
            rt.append(file)

    return rt
