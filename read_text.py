import operator
import sys
import os
from functools import partial
from itertools import takewhile

def read_char(stream):
    c = stream.read(1)
    if not c:
        raise EOFError('Got Nothing')
    return c

def safe_readcstr(stream):
    bound_read = iter(partial(read_char, stream), b'')
    return b''.join(takewhile(partial(operator.ne, b'\00'), bound_read))

def loop_strings(stream):
    while True:
        try:
            yield safe_readcstr(stream).decode('cp862')
        except EOFError as e:
            break

if __name__ == "__main__":
    import glob
    if len(sys.argv) < 2:
        print('no filename given')
        exit(1)

    for filename in glob.iglob(sys.argv[1]):
        basename = os.path.basename(filename)
        with open(filename, 'rb') as f:
            for line in loop_strings(f):
                print(basename + '\t"' + line.replace('"', '`').replace('\r', '\n') + '"')
