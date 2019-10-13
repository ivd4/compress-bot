import sys

from bitarray import bitarray

from compressor.lzw.codedict import CompDict


def compress_bytes(bytes_seq):
    if bytes_seq == b"":
        return b""

    dictionary = CompDict.make_dict()
    bitseq = bitarray()
    cbytes = bytes([bytes_seq[0]])
    for byte in bytes_seq[1:]:
        cbytes = dictionary.add_byte(bitseq, cbytes, bytes([byte]))
    if cbytes != b"":
        dictionary.append_code(bitseq, cbytes)

    return bitseq.tobytes()


def read_data(input_filename):
    data = b""
    with open(input_filename, "rb") as input_file:
        data = input_file.read()

    return data


def make_file(encoded, output_filename):
    with open(output_filename, "wb") as output_file:
        output_file.write(encoded)


def main():
    assert len(sys.argv) > 2, "Not enough arguments"
    result_filename = sys.argv[2]
    origin_filename = sys.argv[1]
    message = read_data(origin_filename)
    print("Readed")
    encoded = compress_bytes(message)
    print("Compressed")
    make_file(encoded, result_filename)
    print("Writed")


if __name__ == '__main__':
    main()
