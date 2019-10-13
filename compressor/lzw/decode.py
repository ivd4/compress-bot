import sys

from bitarray import bitarray

from compressor.lzw.codedict import DecompDict


def bits_to_int(bits):
    res = 0
    was_one = 0
    for bit in bits:
        was_one |= bit
        if was_one:
            res <<= 1
            res += bit
    return res


def decompress_bytes(encoded):
    if encoded == b"":
        return b""

    dictionary = DecompDict.make_dict()
    encoded_bits = bitarray()
    encoded_bits.frombytes(encoded)

    msg = bytearray()
    first_code_len = dictionary.min_code_len
    prev = bits_to_int(encoded_bits[0: first_code_len])
    msg.extend(dictionary[prev])
    cur, code_len, was_one = 0, 0, 0

    for bit in encoded_bits[first_code_len:]:
        was_one |= bit
        if was_one:
            cur <<= 1
            cur += bit
        code_len += 1
        if code_len == dictionary.code_len:
            try:
                entry = dictionary[cur]
                ch = entry[0]
                new_bytes = dictionary[prev] + bytes([ch])
            except KeyError:
                ch = dictionary[prev][0]
                entry = dictionary[prev] + bytes([ch])
                new_bytes = entry

            msg.extend(entry)
            dictionary.add_bytes(new_bytes)
            prev = cur
            cur, code_len, was_one = 0, 0, 0
    return msg


def read_data(compressed_filename):
    data = b""
    with open(compressed_filename, "rb") as comp_file:
        data = comp_file.read()
    return data


def make_file(result_filename, msg):
    string = msg.decode("utf-8")
    with open(result_filename, "w") as res_file:
        res_file.write(string)


def main():
    assert len(sys.argv) > 2, "Not enough arguments"
    compressed_filename = sys.argv[1]
    result_filename = sys.argv[2]
    compressed_data = read_data(compressed_filename)
    msg = decompress_bytes(compressed_data)
    make_file(result_filename, msg)


if __name__ == '__main__':
    main()
