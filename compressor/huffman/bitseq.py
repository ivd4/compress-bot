__all__ = ["BitArray"]


from bitarray import bitarray


class BitArray(bitarray):
    def poor_str(self):
        return "".join((str(int(bit)) for bit in self[:]))

    def rstrip(self, number):
        """
            Remove bits from the end of bit sequence
        """
        for _ in range(number):
            self.pop()
