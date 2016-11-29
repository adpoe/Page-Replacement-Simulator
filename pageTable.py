# Thoughts:  We have 4kb pages, and a 32 bit address space.
#            This means we have 2^12 bits, or bottom 12 bits of our addresses reserved for
#            intra-page addressing. The rest determine if we are using a page that's already in use
#            So we're looking at the first 20 bits to see fi we've got a match...
import parseInput as parse
import circularQueue as cq

class PageTable():
    def __init__(self, how_many_frames):
        # data storage
        self.num_frames = how_many_frames
        self.page_faults = 0
        self.writes_to_disk = 0
        self.total_memory_accesses = 0
        self.next_free_frame = 0 # Use this to make added a frame and checking for page fault O(1)
        self.fast_index = {}

        # the table itself will be a list, which we can index into
        self.frame_table = []

        # circular queue of frames, used ONLY when we use the CLOCK algorithm
        self.frame_queue = cq.CircularQueue(how_many_frames)

        # initialize the list so that it has however many frames the user chose
        for frame in range (0, self.num_frames):
            next_frame = Frame()
            next_frame.dirty = False
            next_frame.in_use = False
            # anything else we need to add, can add here
            self.frame_table.append(next_frame)
        return

    def getPTE(self, memory_tuple):
        # get mem address and rwbit from the tuples in our trace file
        mem_addr = memory_tuple[0]
        rwbit = memory_tuple[1]

        # translate the memory address into a VPN and an OFFSET
        vpn = self.get_VPN(mem_addr)
        offset = self.get_page_offset(mem_addr)

    def get_VPN(self, memory_address):
        VPN_MASK = 0xFFFFF000  # 0b11111111111111111111000000000000 mask first 20 bits 0xFFFFF0000
        hex_int = int(memory_address, 16)
        #binary_int = int(parse.hex_string_to_binary_int(memory_address), 16)
        vpn_value = hex_int & VPN_MASK
        return vpn_value

    def get_page_offset(self, memory_address):
        PAGE_OFFSET_MASK = 0x00000FFF  # 0b00000000000000000000111111111111 mask bottom 12 bits  0x00000FFFF
        # binary_int = int(parse.hex_string_to_binary_int(memory_address), 16)
        hex_int = int(memory_address, 16)
        offset_value = hex_int & PAGE_OFFSET_MASK
        return offset_value

class Frame():
    def __init__(self):
        self.VPN = 0           # Virtual Page Number, or the number we use to determine if the page
                               # is already in memory
        self.dirty = False     # D Bit
        self.in_use = False    # R Bit
        self.PPN = 0           # Physical page number, or index in the page table
        self.instructions_until_next_reference = None    # How many instructions until
                                                         # this page is next used

        # reference bit, used for CLOCK algorithm
        self.reference = False

        # aging value, used by AGING algorithm
        self.aging_value = 0

        # last referenced, for LRU
        self.last_reference = 0

class VirtualAddress():
    def __init__(self, address):
        self.virtual_page_number = None   # top 20 bits
        self.page_offset = None           # bottom 12 bits
