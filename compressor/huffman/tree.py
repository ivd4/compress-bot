__all__ = ["Node", "Leaf"]


from collections import namedtuple

from compressor.huffman.bitseq import BitArray


def get_bitseq_char_len(bitseq, encoding, pos=0):
    if encoding == "binary" or not bitseq[pos]:
        return 8
    length = 0
    current_pos = pos
    while bitseq[current_pos]:
        length += 8
        current_pos += 1
    return length


class Node(namedtuple("Node", ["left", "right"])):
    def walk(self, code, acc):
        """
        Recursive traverse tree and assign codes for all leaves.
        Return maximal code length of node subtree.
        """
        left_seq = BitArray(acc)
        right_seq = BitArray(acc)
        left_seq.append(0)
        right_seq.append(1)
        return max(self.left.walk(code, left_seq),
                   self.right.walk(code, right_seq))

    def show(self):
        print(0)
        self.left.show()
        print(1)
        self.right.show()

    def encode(self, acc, encoding):
        """ Encodes node to bit-sequence.  """
        acc.append(0)
        self.left.encode(acc, encoding)
        self.right.encode(acc, encoding)


class Leaf(namedtuple("Leaf", ["char"])):
    def walk(self, code, acc):
        code[self.char] = acc or BitArray('0')
        return len(acc) or 1

    def show(self):
        print(self.char)

    def encode(self, acc, encoding):
        """ Encodes leaf to bit-sequence."""
        acc.append(1)
        char_bits = BitArray()

        if encoding == "utf-8":
            char_bits.frombytes(self.char.encode(encoding))
        else:
            char_bits.frombytes(bytes([self.char]))

        acc.extend(char_bits)

    @classmethod
    def from_bitseq(cls, bit_seq, encoding):

        if encoding == "utf-8":
            char = bit_seq.tobytes().decode(encoding)
        else:
            char = bit_seq.tobytes()

        return Leaf(char)


def from_bitseq(bitseq, encoding, pos=0):
    if bitseq[pos]:
        pos += 1
        char_len = get_bitseq_char_len(bitseq, encoding, pos)
        return (Leaf.from_bitseq(
            bitseq[pos: pos + char_len], encoding),
            pos + char_len)
    else:
        pos += 1
        left_child, pos = from_bitseq(bitseq, encoding, pos)
        right_child, pos = from_bitseq(bitseq, encoding, pos)
        return Node(left_child, right_child), pos
