import os
import io
import sys
from itertools import zip_longest

from grid import create_char_grid, convert_to_pil_image

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def read_sint16le(stream):
    return int.from_bytes(stream.read(2), byteorder='little', signed=True)

def read_uint16le(stream):
    return int.from_bytes(stream.read(2), byteorder='little', signed=False)

def read_char_data(stream, offsets):
    for offset, end in zip_longest(offsets, offsets[1:]):
        assert f.tell() == offset, (f.tell(), offset)
        yield stream.read(end - offset if end else None)

def read_char(cdata):
    with io.BytesIO(cdata) as s:
        height = read_uint16le(s)
        width = read_uint16le(s)
        flags = read_uint16le(s)
        data = s.read()
        return height, width, flags, data

def convert_char(height, width, flags, data):
    rwidth = (width + 7) // 8
    bitmask = grouper(''.join(f'{x:08b}' for x in data), 8 * rwidth)
    bits = '\n'.join(''.join(x) for x in bitmask)
    return [list(x.encode()[:width]) for x in bits.replace('1', '@').replace('0', '_').split('\n')]

palette = [((53 + x) ** 2 * 13 // 5) % 256 for x in range(256 * 3)]

def decode(stream):
    first_char = ord(stream.read(1))
    last_char = ord(stream.read(1))
    height_above_baseline = read_sint16le(stream)
    height_below_baseline = read_sint16le(stream)
    space_between_lines = read_sint16le(stream)
    space_between_chars = read_sint16le(stream)
    assert stream.tell() == 0xA
    chars = range(first_char, last_char + 1)
    index = tuple(read_sint16le(stream) for c in chars)
    char_data = read_char_data(stream, index)
    char_images = [convert_char(*read_char(cdata)) for cdata in char_data]
    return chars, char_images

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('no filename given')
        exit(1)

    filename = sys.argv[1]
    basename = os.path.basename(filename)
    with open(filename, 'rb') as f:
        chars, char_images = decode(f)
        im = create_char_grid(chars.stop, [(c, cim) for c, cim in zip(chars, char_images)])
        im.putpalette(palette)
        im.save(f'{basename}.png')
