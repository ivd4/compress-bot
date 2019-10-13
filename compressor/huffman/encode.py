import sys
import heapq
from collections import Counter

from compressor.huffman.bitseq import BitArray
from huffman.tree import Node, Leaf


def make_encoded_bytes(tree_bits, message_bits, encoding):
    encoded_len = 4 + len(tree_bits) + len(message_bits)

    extra = (8 - encoded_len % 8) % 8

    encoded_bits = BitArray()
    if encoding == "utf-8":
        encoded_bits.append(1)
    else:
        encoded_bits.append(0)

    encoded_bits.extend("{0:03b}".format(extra))
    encoded_bits.extend(tree_bits)
    encoded_bits.extend(message_bits)

    return encoded_bits.tobytes()


def huffman_encode(message, encoding="utf-8"):
    if not message:
        if encoding == "utf-8":
            return ""
        else:
            return b""
    h = []
    for ch, freq in Counter(message).items():
        h.append((freq, len(h), Leaf(ch)))

    heapq.heapify(h)

    count = len(h)
    while len(h) > 1:
        freq1, _count1, left = heapq.heappop(h)
        freq2, _count2, right = heapq.heappop(h)
        heapq.heappush(h, (freq1 + freq2, count, Node(left, right)))
        count += 1

    code = {}
    root = None
    if h:
        [(_freq, _count, root)] = h
        root.walk(code, BitArray())

    tree_bits = serialize_tree(root, encoding)

    message_bits = BitArray()
    for ch in message:
        message_bits.extend(code[ch])

    encoded = make_encoded_bytes(tree_bits, message_bits, encoding)
    return encoded


def serialize_tree(root, encoding):
    tree_bits = BitArray()
    root.encode(tree_bits, encoding)
    return tree_bits


def make_compressed_file(encoded_bytes, filename):
    with open(filename, "wb") as out_file:
        out_file.write(encoded_bytes)


def get_encoding(message):
    try:
        message.encode('ascii')
    except UnicodeEncodeError:
        return "utf-8"
    else:
        return "ascii"


def read_data():
    data_filename = sys.argv[1]
    compressed_filename = sys.argv[2]

    with open(data_filename) as data_file:
        message = data_file.read()

    return message, compressed_filename


def compress_string(message):
    return huffman_encode(message, "utf-8")


def compress_bytes(message):
    return huffman_encode(message, "binary")


def main():
    message, compressed_filename = read_data()
    encoded = compress_string(message)
    make_compressed_file(encoded, compressed_filename)


if __name__ == "__main__":
    main()
