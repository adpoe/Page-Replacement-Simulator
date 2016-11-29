""" 'Aging' Page Replacement Algorithm Implementation
"""
import time

##########################
######## ALGORITHM #######
##########################
# To do -- re run for everything and fix recommendation to 0.00001
class Aging:

    def __init__(self, page_table, trace, refresh_rate):
        # set the variables for our algorithm
        self.PAGE_TABLE = page_table
        self.trace = trace
        self.frame_queue = page_table.frame_table
        index = 0
        # set our PPNs ins the page table
        for elem in self.frame_queue:
            elem.PPN = index
            index += 1

        # output variables
        self.hit = False
        self.evict = False
        self.dirty = False

        # refresh variables for aging
        self.refresh_time_in_ms = refresh_rate
        self.refresh = False
        self.time_of_last_refresh = time.clock()

    def age_and_mark_if_referenced_during_last_tick(self):
        # iterate through the frame queue
        for elem in self.frame_queue:

            # shift right all bits by 1
            elem.aging_value >>= 1

            # if the element was referenced,
            # and write a 1 in MSB
            if elem.reference:
                elem.aging_value |= (1 << 7)


    def collect_data_on_references_during_this_tick(self):
        # check if it's time to refresh and age
        if time.clock() - self.time_of_last_refresh >= self.refresh_time_in_ms:
            # add or update, then reset the reference bits
            self.age_and_mark_if_referenced_during_last_tick()
            self.time_of_last_refresh = time.clock()

            # then reset all the reference bits
            for elem in self.frame_queue:
                elem.reference = False


    def add_or_update_page(self, vpn, read_or_write):
        # try and add/update, if success, we're done... otherwise need to evict
        # first see if the element is already present,
        # and gather info about the values as we do it
        lowest_value_page_number = 0
        lowest_value_overall = 257  # higher than the highest value in 8 bits, which is 255
        for elem in self.frame_queue:
            # gather info on the page values, as we do it
            if elem.aging_value < lowest_value_overall:
                lowest_value_page_number = elem.PPN
                lowest_value_overall = elem.aging_value

            # check for it a hit
            if elem.VPN == vpn:
                # mark hit as true
                self.hit = True
                # if we're doing a write, the element is dirty
                if read_or_write == 'W':
                    elem.dirty = True
                # otherwise we're doing a read
                else:
                    elem.reference = True
                # and exit, because we have a hit
                return

        # so look for an empty page, first, and if we find one, use it
        for elem in self.frame_queue:
            # check for a free element
            if elem.in_use == False:
                # set values accordingly
                elem.in_use = True
                elem.VPN = vpn
                # if we're doing a write, need to set dirty bit
                if read_or_write == 'W':
                    elem.dirty = True
                # if we're not writing, then we're reading, and so we need to set the reference bit
                else:
                    elem.reference = True
                # and return
                return

        # if page table is full and the VPN is not in the page table currently,
        # then we also need to evict, a page.
        # so, we evict the page with lowest value
        self.evict_lowest_value_page(lowest_value_page_number)
        self.add_or_update_page(vpn, read_or_write)
        return

    def evict_lowest_value_page(self, ppn):
        # get a handle to the page we want to remove
        page = self.frame_queue[ppn]
        self.evict = True

        # if dirty, write to disk
        if page.dirty:
            self.dirty = True
            self.PAGE_TABLE.writes_to_disk += 1
            self.remove(ppn)

        # if clean, no disk write
        else:
            self.remove(ppn)

    def remove(self, ppn):
        removal_page = self.frame_queue[ppn]
        removal_page.in_use = False
        removal_page.referenced = False
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

            self.collect_data_on_references_during_this_tick()
            self.add_or_update_page(next_vpn, next_read_or_write)


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

        self.print_results()

    def print_results(self):
        print "Algorithm: Aging"
        print "Number of frames:   "+str(len(self.PAGE_TABLE.frame_table))
        print "Refresh Rate:       "+str(self.refresh_time_in_ms)
        print "Total Memory Accesses: "+str(self.PAGE_TABLE.total_memory_accesses)
        print "Total Page Faults: "+str(self.PAGE_TABLE.page_faults)
        print "Total Writes to Disk: "+str(self.PAGE_TABLE.writes_to_disk)
