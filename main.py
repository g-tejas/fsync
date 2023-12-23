import collections
import hashlib
import zlib

BLOCK_SIZE = 4096

def md5_chunk(chunk):
    m = hashlib.md5()
    m.update(chunk)
    return m.hexdigest()

def adler32_chunk(chunk):
    return zlib.adler32(chunk)

class RsyncLUT:
    def __init__(self):
        pass
    def __getitem__(self, block_data):
        pass


class Chunks:
    """
    Data structure that holds rolling checksum for source file
    """
    def __init__(self):
        self.chunks = []
