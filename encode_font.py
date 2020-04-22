import os
import io
import sys

import itertools

import numpy as np
from grid import read_image_grid, resize_frame

def read_sint16le(stream):
    return int.from_bytes(stream.read(2), byteorder='little', signed=True)

def write_sint16le(number):
    return number.to_bytes(2, byteorder='little', signed=True)

def write_uint16le(number):
    return number.to_bytes(2, byteorder='little', signed=False)

def encode_char(data, flags=0):
    height, width = data.shape
    print(height, width)
    data = 1 * (data - ord('_') != 0)
    return write_uint16le(height) + write_uint16le(width) + write_uint16le(flags) \
        + bytes(np.packbits(data, axis=1).ravel().tolist())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('no filename given')
        exit(1)

    filename = sys.argv[1]
    ref = sys.argv[2]
    target = 'new-font.bin'
    frames = read_image_grid(filename)
    frames = enumerate(resize_frame(frame) for frame in frames)
    available = [(idx, char) for idx, char in frames if char is not None]
    first_char, _ = available[0]
    last_char, _ = available[-1]
    print(first_char, last_char)
    with open(ref, 'rb') as stream:
        stream.seek(2)
        height_above_baseline = read_sint16le(stream)
        height_below_baseline = read_sint16le(stream)
        space_between_lines = read_sint16le(stream)
        space_between_chars = read_sint16le(stream)
    print(height_above_baseline, height_below_baseline, space_between_lines, space_between_chars)
    char_range = range(first_char, last_char + 1)
    assert len(char_range) == (last_char - first_char + 1)
    encoded_chars = {idx: encode_char(char) for idx, (loc, char) in available}

    spacer = b'\0\0\0\0\0\0'

    with open(target, 'wb') as output:
        output.write(bytes([first_char, last_char]))
        output.write(write_sint16le(height_above_baseline))
        output.write(write_sint16le(height_below_baseline))
        output.write(write_sint16le(space_between_lines))
        output.write(write_sint16le(space_between_chars))
        offset = output.tell()
        assert offset == 0xA
        offset += 2 * len(char_range)
        for c in char_range:
            output.write(write_sint16le(offset))
            offset += len(encoded_chars.get(c, spacer))
            print('OFFSET', c, write_sint16le(offset))
        for c in char_range:
            output.write(encoded_chars.get(c, spacer))
            print('DATA', c, encoded_chars.get(c, spacer))
