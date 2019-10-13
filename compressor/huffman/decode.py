import sys

from compressor.huffman.bitseq import BitArray
from compressor.huffman import tree


def parse_bytes(file_bytes):
    file_bits = BitArray()
    file_bits.frombytes(file_bytes)

    enc_bit = file_bits[0]

    extra = int(file_bits[1:4].to01(), 2)
    file_bits.rstrip(extra)

    encoding = "utf-8" if enc_bit else "binary"
    file_bits = file_bits[4:]

    tree_root, code_startpos = tree.from_bitseq(file_bits, encoding)
    encoded = file_bits[code_startpos:]
    return tree_root, encoded, encoding


def get_origin_message(tree_root, encoded, encoding):
    cur_node = tree_root
    origin_list = []
    for bit in encoded:
        if type(cur_node) != tree.Leaf:
            if bit:
                cur_node = cur_node.right
            else:
                cur_node = cur_node.left
        if type(cur_node) == tree.Leaf:
            origin_list.append(cur_node.char)
            cur_node = tree_root

    if encoding == "utf-8":
        return "".join(origin_list)
    else:
        return b"".join(origin_list)


def make_file(message, filename, encoding="utf-8"):
    if encoding == "utf-8":
        with open(filename, "w", encoding=encoding) as out_file:
            out_file.write(message)
    else:
        with open(filename, "wb") as out_file:
            out_file.write(message)


def decompress(file_bytes):
    if not file_bytes:
        return "", "ascii"

    tree_root, encoded, encoding = parse_bytes(file_bytes)

    message = get_origin_message(tree_root, encoded, encoding)
    return message, encoding


def main():
    compressed_filename = sys.argv[1]
    data_filename = sys.argv[2]

    with open(compressed_filename, "rb") as compressed_file:
        file_bytes = compressed_file.read()

    message, encoding = decompress(file_bytes)
    make_file(message, data_filename, encoding)


if __name__ == "__main__":
    main()
