import sys
import os
import time
from time import sleep
import ch347


# Get the parent directory's path
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# Add the parent directory to the system path if not already present
if parent_directory not in sys.path:
    sys.path.insert(0, parent_directory)

dll_path = parent_directory + "\\ch347\\lib"

if dll_path not in sys.path:
    sys.path.insert(0, dll_path)

AT24C256_PAGE_SIZE = 64


class EPPROM:
    def __init__(self, address=0x50, driver=ch347.CH347()):

        # print(driver.list_devices())
        self.address = address << 1
        self.driver = driver

        self.driver.open_device()
        self.driver.i2c_set(2)


    # I2C communication methods
    def read_byte_data(self, register):
        raw_data = self.driver.stream_i2c([self.address, register], 1)
        return raw_data[0]

    def write_byte_data(self, register, value):
        return self.driver.stream_i2c([self.address, register, value], 0)

    def read_i2c_word(self, register):
        """
        Read two i2c registers and combine them.

        register -- the first register to read from.
        Returns the combined read results.
        """

        # Read the data from the registers
        # high = self.read_byte_data(self.address, register)
        # low = self.read_byte_data(self.address, register + 1)
        raw_data = self.driver.stream_i2c([self.address, register], 2)

        # value = (high << 8) + low
        value = raw_data[0] << 8 | raw_data[1]

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    # spec for at24c256, reg is 16b
    def at24c256_read_byte_data(self, register):
        reg = []
        reg.append(register//256)
        reg.append(register % 256)
        write_data = [self.address] + reg
        raw_data = self.driver.stream_i2c(write_data, 1)
        return raw_data[0]
    
    def at24c256_write_byte_data(self, register, value):
        reg = []
        reg.append(register // 256)
        reg.append(register % 256)
        write_data = [self.address] + reg + [value]
        ret = self.driver.stream_i2c(write_data, 0)
        time.sleep(0.05)
        return ret

    def at24c256_write_page(self, register, value):

        if len(value) > AT24C256_PAGE_SIZE:
            print("page write size is %d" % AT24C256_PAGE_SIZE)
            return

        reg = []
        reg.append(register // 256)
        reg.append(register % 256)
        write_data = [self.address] + reg + value
        ret = self.driver.stream_i2c(write_data, 0)
        time.sleep(0.05)
        return ret

    def at24c256_dump_mem(self, register, len):
        reg = []
        reg.append(register // 256)
        reg.append(register % 256)
        write_data = [self.address] + reg
        raw_data = self.driver.stream_i2c(write_data, len)
        i = 0
        print("%03xh:\t" % i, end="")
        for val in raw_data:
            print("%02x" % val, end="\t")
            i = i + 1
            if i % 16 == 0:
                print("")
                if i != len:
                    print("%03xh:\t" % i, end="")

    def close(self):
        self.driver.close_device()

if __name__ == "__main__":
    epprom = EPPROM(address=0x50)

    val_list = []
    for val in range(64):
        val_list.append(val+0x0)

    epprom.at24c256_write_page(0x100, val_list)
    time.sleep(0.05)

    epprom.at24c256_dump_mem(0, 0x150)

    # epprom.at24c256_dump_mem(0, 0x11f)


    epprom.close()
