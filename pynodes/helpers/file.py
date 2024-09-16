import traceback
from pathlib import Path

def write(path, content:str, overwrite=False):
    '''
    Simple functional-oriented string-based-file writer.
    Raises exception if an exception is encountered.
    Output is the given path otherwise.
    '''

    try:

        if overwrite==False:
            assert not Path(path).exists(), f'Overwrite prevented! {str(path)}'
        assert not Path(path).is_dir(), f'Path is a folder. {str(path)}'

        with open(str(path), 'w') as f:
            f.write(content)

    except Exception as e:
        traceback.print_exc()
        raise e

    return path

def read(path):
    with open(path, 'r') as f:
        return f.read()