__all__ = ["CompDict", "DecompDict"]


def is_power_of_two(x):
    return (x & (x - 1)) == 0


class BaseDict(dict):
    def __init__(self, min_code_bits_len=8):
        super().__init__()
        self.current_code = 0
        self.min_code_len = min_code_bits_len
        self.code_len = min_code_bits_len

    @classmethod
    def make_dict(cls):
        dictionary = cls()
        for i in range(0, 256):
            dictionary.add(bytes([i]))
        return dictionary


class CompDict(BaseDict):
    def add(self, bytes_):
        if ((self.current_code).bit_length() > self.code_len and
                is_power_of_two(self.current_code)):
            self.code_len += 1
        self[bytes_] = self.current_code
        self.current_code += 1

    def append_code(self, bitseq, cbytes):
        code = self[cbytes]
        bin_string = bin(code)[2:]
        bin_string = bin_string.zfill(max(self.code_len, self.min_code_len))
        bitseq.extend(bin_string)

    def add_byte(self, bitseq, cbytes, byte):
        nbytes = cbytes + byte
        if nbytes in self:
            cbytes = nbytes
        else:
            self.append_code(bitseq, cbytes)
            self.add(nbytes)
            cbytes = byte

        return cbytes


class DecompDict(BaseDict):

    def add(self, bytes_):
        self[self.current_code] = bytes_
        self.current_code += 1
        if ((self.current_code).bit_length() > self.code_len and
                is_power_of_two(self.current_code)):
            self.code_len += 1

    def add_bytes(self, bytes_):
        self.add(bytes_)
