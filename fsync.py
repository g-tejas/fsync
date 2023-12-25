from collections import *
import hashlib
import zlib
from typing import Optional

BLOCK_SIZE = 4096
Signature = namedtuple("Signature", "weak strong")

def weak_sig(chunk) -> int:
    return zlib.adler32(chunk)
 
def strong_sig(chunk) -> str:
    m = hashlib.md5()
    m.update(chunk)
    return m.hexdigest()

def sign(chunk) -> Signature:
    return Signature(weak = weak_sig(chunk), strong = strong_sig(chunk))

class RsyncLUT:
    def __init__(self):
        self.lut = defaultdict(dict)
        self.chunk_sigs = []

    def append(self, sig: Signature):
        self.chunk_sigs.append(sig)
        self.lut[sig.weak][sig.strong] = len(self.chunk_sigs) - 1

    def __getitem__(self, block_data) -> Optional[int]:
        """
        If this returns non-None, means the data has not changed
        """
        weak = weak_sig(block_data)
        subdict = self.lut.get(weak)
        if subdict:
            strong = strong_sig(block_data)
            return subdict.get(strong)
        return None

def chunkify(file_name: str) -> RsyncLUT:
    """
    Returns a rsync lookup table generated from the file
    """
    print("Chunkifying {}".format(file_name))
    table = RsyncLUT()
    with open(file_name, "rb") as file:
        while True:
            chunk_data = file.read(BLOCK_SIZE)
            if not chunk_data: # EOF
                break
            sig: Signature = Signature(weak=weak_sig(chunk_data), strong=strong_sig(chunk_data))
            table.append(sig)
        return table

def deltas(table: RsyncLUT, file_name: str): 
    """
    The main algorithm. 
    1. Create a lookup table from the destination file
    2. For each file in the source file, look up the chunk in RsyncLUT, determine if it's in destination file
       a. If it is, yield the offset and length of the block in the source file, and advance read head.
    ----------
    table: RsyncLUT
        The lookup table generated from the source file
    file_name: str
        The name of the file (destination) to be compared against the source file

    Yields
    ------
    int
        The offset of the block in the source file
    """
    with open(file_name, "rb") as file:
        block_data: bytes = file.read(BLOCK_SIZE)
        while block_data:
            block_number = table[block_data]
            if block_number:
                # (offset: int, length: int) of the block in the source file
                yield (block_number * BLOCK_SIZE, len(block_data))
                block_data = file.read(BLOCK_SIZE)
            else:
                yield chr(block_data[0])
                block_data = block_data[1:] + file.read(1)

def patch(src_file_name: str, dest_file_name: str):
    """
    Apply the deltas to the destination file. 
    """
    print("Patching {} to {}".format(src_file_name, dest_file_name))
    table = chunkify(dest_file_name) # will be empty if dest_file_name does not exist
    with open(dest_file_name, "w") as outputf, open(src_file_name, "rb") as sourcef:
        for x in deltas(table, src_file_name):
            if not isinstance(x, (int, int)):
                outputf.write(x) # x is a string, 1 byte
            else:
                offset, length = x
                sourcef.seek(offset)
                outputf.write(sourcef.read(length))
