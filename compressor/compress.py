import sys

from compressor.huffman.encode import compress_string as hcompress_string, \
                                      compress_bytes as hcompress_bytes, \
                                      make_compressed_file as hmake_file

from lzw.encode import compress_bytes as lzw_compress
from lzw.encode import make_file as lzw_make_file


def archive_files(origin_filenames, result_filename,
                  algorithm="huffman"):

    content_list = []
    for filename in origin_filenames:
        with open(filename) as file:
            file_string = file.read()
            length = len(file_string)
            content_list.append("{} {}\n".format(filename, str(length)))
            content_list.append(file_string)

    content = ''.join(content_list)
    if algorithm == "huffman":
        huffman_to_file(content, result_filename)
    elif algorithm == "lzw":
        lzw_to_file(content, result_filename)


def archive_binary_files(origin_filenames, result_filename):
    content_list = []
    for filename in origin_filenames:
        with open(filename, "rb") as file:
            file_bytes = file.read()
            length = len(file_bytes)
            byte_header = bytearray(filename.encode("utf-8"))
            byte_header.append(12)  # "\x0c"
            byte_header.extend(bytes(str(length), "utf-8"))
            byte_header.append(14)  # '\x0e'
            content_list.append(byte_header)
            content_list.append(file_bytes)

    content = b''.join(content_list)

    lzw_to_file(content, result_filename)


def unite_files(names_list, data_list, result_filename):
    content_list = []
    for name, data in zip(names_list, data_list):
        length = len(data)
        byte_header = bytearray(name.encode("utf-8"))
        byte_header.append(12)  # "\x0c"
        byte_header.extend(bytes(str(length), "utf-8"))
        byte_header.append(14)  # '\x0e'
        content_list.append(byte_header)
        content_list.append(data)

    content = b''.join(content_list)
    lzw_to_file(content, result_filename)


def huffman_to_file(content, result_filename):
    compressed = hcompress_string(content)
    hmake_file(compressed, result_filename)


def huffman_bin_to_file(content, result_filename):
    compressed = hcompress_bytes(content.encode("utf-8"))
    hmake_file(compressed, result_filename)


def lzw_to_file(content, result_filename, mode="bin"):
    if mode == "bin":
        compressed = lzw_compress(content)
    else:
        compressed = lzw_compress(content.encode("utf-8"))
    lzw_make_file(compressed, result_filename)


def main():
    assert len(sys.argv) > 2, "Not enough arguments!"
    result_filename = sys.argv[-1]
    origin_filenames = sys.argv[1:-1]

    archive_binary_files(origin_filenames, result_filename)
    print("Compressed to {} file.".format(result_filename))


if __name__ == '__main__':
    main()
