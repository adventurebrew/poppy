import sys
import os

if __name__ == "__main__":
    import glob
    if len(sys.argv) < 3:
        print('no filenames given')
        exit(1)

    source = sys.argv[1]
    target = sys.argv[2]
    with open(source, 'r', encoding='cp1255') as f, \
            open(target, 'wb') as o:
        for line in f:
            lines = line.split('$')
            o.write('\r'.join(text[::-1] for text in lines).replace('`', '"').encode('cp862') + b'\0')
