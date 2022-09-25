import ctypes
import os

class Memhole():
    mh = None
    memhole_device = None
    buf = None

    def __init__(self):
        if(not __file__.endswith("memhole.py")):
            raise Exception("memhole.py must remain inside the library folder and not be renamed")
        self.mh = ctypes.cdll.LoadLibrary(__file__[0:-len("memhole.py")] + "memhole_lib.so")
        self.mh.create_memhole.restype = ctypes.c_void_p
        self.mh.delete_memhole.argtypes = [ctypes.c_void_p]
        self.mh.attach_to_pid.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.mh.attach_to_pid.restype = ctypes.c_long
        self.mh.get_memory_position.argtypes = [ctypes.c_void_p]
        self.mh.get_memory_position.restype = ctypes.c_void_p
        self.mh.set_memory_position.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        self.mh.set_memory_position.restype = ctypes.c_void_p
        self.mh.read_memory.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_int]
        self.mh.read_memory.restype = ctypes.c_long
        self.mh.connect_memhole.argtypes = [ctypes.c_void_p]
        self.mh.disconnect_memhole.argtypes = [ctypes.c_void_p]
        self.mh.disconnect_memhole.restype = ctypes.c_int
        self.mh.write_memory.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_int]
        self.mh.write_memory.restype = ctypes.c_long
        self.buf = ctypes.create_string_buffer(0)
        self.memhole_device = self.mh.create_memhole()
        if(self.memhole_device == None or self.memhole_device == 0):
            raise Exception("Failed to create memhole device")
    
    def __del__(self):
        self.mh.delete_memhole(self.memhole_device)

    # attach memhole to a pid's memory
    # returns 0 on success, error code on failure
    def attach_to_pid(self, pid) -> int:
        return self.mh.attach_to_pid(self.memhole_device, pid)

    # returns the current memory position of memhole
    def get_memory_position(self) -> int:
        return self.mh.get_memory_position(self.memhole_device)
    
    # set the position of memhole in the process's memory
    # returns the position seeked to or an error code
    def set_memory_position(self, pos) -> int:
        return self.mh.set_memory_position(self.memhole_device, pos, 1)

    # read memory from the process starting at the seeked position
    # NOTE: the position is NOT automatically incremented after a read or write
    # returns the bytes read or an empty byte array on error
    def read_memory(self, size) -> bytes:
        if(size > len(self.buf)):
            self.buf = ctypes.create_string_buffer(size)
        ret = self.mh.read_memory(self.memhole_device, self.buf, size, 1)
        if(ret < 0): print("ret:" + str(ret))
        return self.buf.value[0:ret] if ret >= 0 else []
    
    # write memory on the process starting at the seeked position
    # NOTE: the position is NOT automatically incremented after a read or write
    # returns an error code or number of bytes written
    def write_memory(self, buf) -> int:
        self.buf = ctypes.create_string_buffer(buf)
        return self.mh.write_memory(self.memhole_device, self.buf, len(buf), 1)
    
    # connect the wrapper to memhole
    # under the hood, this aquires a file descriptor to the memhole device
    # returns 0 on success, error code on failure
    def connect_memhole(self) -> int:
        return self.mh.connect_memhole(self.memhole_device)
    
    # disconnect the wrapper from memhole
    # under the hood, this closes the file descriptor to the memhole device
    # returns 0 on success, error code on failure
    def disconnect_memhole(self) -> int:
        return self.mh.disconnect_memhole(self.memhole_device)