import struct


class FirmwareBin:
    BLOCK_ID_BYTE_LEN = 0x04

    def __init__(self, bin_path):
        self.bin_path = bin_path
        with open(self.bin_path, "rb") as f:
            self.binary_data = list(f.read())
            self.firmware_len = len(list(self.binary_data))
            self.curr_block = 0

    def set_mtu_size(self, mtu_size):
        self.block_size = mtu_size + self.BLOCK_ID_BYTE_LEN
        self.blocks_num = self.firmware_len / mtu_size + (self.firmware_len % mtu_size)

    def get_blocks_number(self):
        return self.blocks_num

    def is_read_complete(self):
        return self.curr_block >= self.blocks_num

    def get_next_block(self):
        block_id_bytes = list(struct.pack('>I', self.curr_block))
        if self.curr_block < self.blocks_num:
            return block_id_bytes + self.binary_data[self.curr_block * self.block_size : (self.curr_block + 1) * self.block_size]
        return None

    # meta data getters
    def get_img_id(self): # 8
        return self.binary_data[0:8]

    def get_bim_ver(self):
        return self.binary_data[0xc]

    def get_meta_var(self):
        return self.binary_data[0xd]

    def get_img_cp_stat(self):
        return self.binary_data[0xf]

    def get_img_crc_stat(self):
        return self.binary_data[0x10]

    def get_img_type(self):
        return self.binary_data[0x12]

    def get_img_no(self):
        return self.binary_data[0x13]

    def get_img_len(self): # 4
        return self.binary_data[0x18 : 0x1c]

    def get_soft_ver(self): # 4
        return self.binary_data[0x20 : 0x24]

    def get_metadata_value(self):
        pattern = '<8sBBBBBBI4s'
        len = int.from_bytes(self.get_img_len(), byteorder='little', signed=False)
        metadata_bytes = struct.pack(pattern,
                                    bytearray(self.get_img_id()),
                                    self.get_bim_ver(),
                                    self.get_meta_var(),
                                    self.get_img_cp_stat(),
                                    self.get_img_crc_stat(),
                                    self.get_img_type(),
                                    self.get_img_no(),
                                    len,
                                    bytearray(self.get_soft_ver()))
        return metadata_bytes
