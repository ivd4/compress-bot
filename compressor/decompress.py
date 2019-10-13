import sys
import os
from io import BytesIO, StringIO

from compressor.huffman.decode import decompress as h_decompress
from compressor.lzw.decode import decompress_bytes as lzw_decompress


def decompress_file(filename):
    with open(filename, "rb") as compressed_file:
        compressed_bytes = compressed_file.read()
        decompress_bytes(compressed_bytes)


def decompress_bytes(file_bytes, algorithm="lzw"):
    if algorithm == "lzw":
        content = lzw_decompress(file_bytes)
    else:
        content, _encoding = h_decompress(file_bytes)

    if algorithm == "huffman":
        content = content.decode("utf-8")

    if algorithm == "lzw":
        gen = byte_content_split(content)
        mode = "wb"
    else:
        gen = content_split(content)
        mode = "w"

    for name, data in gen:
        with open(name, mode) as current_file:
            current_file.write(data)


def make_new_name(name):
    splitted = name.rsplit(os.sep, 1)
    if os.environ.get('ENV') == 'dev' and len(splitted) > 1:
        poor_name = splitted[1]
        path = splitted[0]
        return path + os.sep + "b." + poor_name
    return name


def content_split(content):
    sio = StringIO(content)
    while True:
        header = sio.readline().strip()

        if not header:
            raise StopIteration()
        name, str_size = header.split()
        name = make_new_name(name)
        data = sio.read(int(str_size))
        yield name, data


def byte_content_split(content):
    bio = BytesIO(content)
    s12 = int.to_bytes(12, 1, "big")
    s14 = int.to_bytes(14, 1, "big")

    while True:
        byte_header = bytearray()
        while True:
            byte = bio.read(1)
            if not byte or byte == s14:
                break
            byte_header.extend(byte)
        if not byte_header:
            raise StopIteration()

        splitted = byte_header.split(s12)
        name, size = splitted
        name = make_new_name(name.decode("utf-8"))
        size = int(size.decode("utf-8"))
        data = bio.read(size)
        yield name, data


def main():
    assert len(sys.argv) != 1, "Expected one argument!"
    compressed_filename = sys.argv[1]
    decompress_file(compressed_filename)
    print("File {} decompressed!".format(compressed_filename))


if __name__ == '__main__':
    main()
