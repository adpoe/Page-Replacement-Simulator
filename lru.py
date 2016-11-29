""" 'Least Recently Used' Page Replacement Algorithm Implementation
"""

# Hit or new item:  add to page table and mark in hash table the memory load #
# Miss:   go through hash table, find lowest #, outright, since numbers are growing, evict it. call add again

class LRU:

    def __init__(self, page_table, trace):
        # set the variables for our algorithm
        self.PAGE_TABLE = page_table
        self.trace = trace
        self.frame_list = page_table.frame_table

        #initalize our PPNs
        counter = 0
        for elem in self.frame_list:
            elem.PPN = counter
            counter += 1

        # output variables
        self.hit = False
        self.evict = False
        self.dirty = False

    def add_or_update_successful(self, vpn, read_or_write):
        # first check if we have a hit
        for elem in self.frame_list:
            if elem.VPN == vpn:
                # mark that we had a hit
                self.hit = True

                # add the page
                # set values accordingly
                elem.in_use = True
                elem.VPN = vpn
                # if we're doing a write, need to set dirty bit
                if read_or_write == 'W':
                    elem.dirty = True
                # if we have a READ, mark the last reference variable, so we know that this was the last time our
                # selected VPN was accessed
                else:
                    elem.last_reference = self.PAGE_TABLE.total_memory_accesses
                # and return
                return True

        else:
            self.hit = False
            # try and add to an empty space, even though we have a page fault
            if not self.add_after_page_fault(vpn, read_or_write):
                # and if that returns false, we need to EVICT and try again
                self.evict = True
                self.evict_page()

            return False

    def add_after_page_fault(self, vpn, read_or_write):
        for elem in self.frame_list:
            if not elem.in_use:

                elem.in_use = True
                elem.VPN = vpn
                # if we're doing a write, need to set dirty bit
                if read_or_write == 'W':
                    elem.dirty = True
                else:
                    # if we have a read, mark our reference
                    elem.last_reference = self.PAGE_TABLE.total_memory_accesses
                # and return
                return True

        # if we make it this far, then all items are in use, so return false
        return False

    def evict_page(self):
        lowest_value = None
        lowest_value_vpn = 0
        lowest_value_ppn = 0

        for elem in self.frame_list:
            # index by the key to get a value
            value = elem.last_reference
            # find the lowest value overall, and get its PPN and VPN
            if lowest_value is None or value < lowest_value:
                lowest_value = value
                lowest_value_vpn = elem.VPN
                lowest_value_ppn = elem.PPN


        # remove the lowest value vpn
        self.remove(lowest_value_ppn, lowest_value_vpn)

    def remove(self, ppn, vpn):
        removal_page = self.frame_list[ppn]
        # if the page is dirty, we need to do a disk write
        if removal_page.dirty:
            self.dirty = True
        removal_page.in_use = False
        removal_page.dirty = False
        removal_page.vpn = None

    def run_algorithm(self):
        # keep track of our memory accesses
        self.PAGE_TABLE.total_memory_accesses = 0

        # run the algorithm while we have items left in the trace
        while len(self.trace) > 0:
            # reset output variables
            self.hit = False
            self.evict = False
            self.dirty = False

            # pull out next item of the trace
            next_address = self.trace[0]
            next_vpn = self.PAGE_TABLE.get_VPN(next_address[0])
            next_read_or_write = next_address[1]

            # run it in our algorithm
            """ ALGORITHM HERE """

            if not self.add_or_update_successful(next_vpn, next_read_or_write):
                self.add_after_page_fault(next_vpn, next_read_or_write)

            """ END ALGORITHM """
            # then remove it from the trace, so it isn't processed a second time
            self.trace.pop(0)

            self.PAGE_TABLE.total_memory_accesses += 1
            # print trace to screen
            if self.hit:
                print "Memory address: " + str(next_address[0]) + " VPN="+ str(next_vpn) + ":: number " + \
                      str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->HIT"
            elif not self.evict:
                  print "Memory address: " + str(next_address[0]) + " VPN="+ str(next_vpn) + ":: number " + \
                      str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->PAGE FAULT - NO EVICTION"
                  # else, we have a page fault
                  self.PAGE_TABLE.page_faults += 1
            elif self.evict and not self.dirty:
                 print "Memory address: " + str(next_address[0]) + " VPN="+ str(next_vpn) + ":: number " + \
                      str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->PAGE FAULT - EVICT CLEAN"
                 # else, we have a page fault
                 self.PAGE_TABLE.page_faults += 1
            else:
                 print "Memory address: " + str(next_address[0]) + " VPN="+ str(next_vpn) + ":: number " + \
                      str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->PAGE FAULT - EVICT DIRTY"
                 # else, we have a page fault
                 self.PAGE_TABLE.page_faults += 1
                 self.PAGE_TABLE.writes_to_disk += 1

        self.print_results()

    def print_results(self):
        print "Algorithm: Clock"
        print "Number of frames:   "+str(len(self.PAGE_TABLE.frame_table))
        print "Total Memory Accesses: "+str(self.PAGE_TABLE.total_memory_accesses)
        print "Total Page Faults: "+str(self.PAGE_TABLE.page_faults)
        print "Total Writes to Disk: "+str(self.PAGE_TABLE.writes_to_disk)


