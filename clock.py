""" 'Clock' Page Replacement Algorithm Implementation
"""

##########################
######## ALGORITHM #######
##########################
class Clock():

    def __init__(self, page_table, trace):
        self.PAGE_TABLE = page_table
        self.trace = trace
        self.frame_queue = page_table.frame_queue

        # output variables
        self.hit = False
        self.evict = False
        self.dirty = False

    def add_page_or_update(self, mem_address):

        # first, try to add a page outright, and if it works, we're done
        vpn = self.PAGE_TABLE.get_VPN(mem_address[0])
        read_or_write = mem_address[1]

        # if we don't successfully add or update...
        if self.frame_queue.add_or_update_successful(vpn, read_or_write) == False:
            # if we don't find something, then we page fault, and we need to evict a page
            self.PAGE_TABLE.page_faults += 1
            self.evict = True

            # And we need to find a victim frame
            victim_frame = self.frame_queue.find_victim()

            # run swap demon for dirty and unreferenced pages, if necessary
            # happens WHEN no victim frame is found on first run,
            # this also means we are going to write a dirty page to disk when we run the swap daemon
            while victim_frame is None:
                # run the swap daemon, and account for the number of writes to disk
                num_disk_writes = self.frame_queue.flush_dirty_and_unreferenced_pages()
                self.PAGE_TABLE.writes_to_disk += num_disk_writes
                # if we write to disk, we did a dirty eviction
                if num_disk_writes > 0:
                    self.dirty = True

                # then get a victim page, since there must be one now that we've flushed
                victim_frame = self.frame_queue.find_victim()

            # and remove the victim page
            self.frame_queue.remove(victim_frame)

            # then add the frame in the newly freed space
            self.frame_queue.add_or_update_successful(vpn, read_or_write)

        # otherwise, we've got a hit
        else:
            self.hit = True


    def run_algorithm(self):
        # keep track of our memory accesses
        self.PAGE_TABLE.total_memory_accesses = 0


        # run the algorithm while we have items left in the trace
        while len(self.trace) > 0:
            self.hit = False
            self.evict = False
            self.dirty = False


            # pull out next item of the trace
            next_address = self.trace[0]
            next_vpn = self.PAGE_TABLE.get_VPN(next_address[0])
            # run it in our algorithm
            self.add_page_or_update(next_address)
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
            elif self.evict and not self.dirty:
                print "Memory address: " + str(next_address[0]) + " VPN="+ str(next_vpn) + ":: number " + \
                      str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->PAGE FAULT - EVICT CLEAN"
            else:
                print "Memory address: " + str(next_address[0]) + " VPN="+ str(next_vpn) + ":: number " + \
                      str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->PAGE FAULT - EVICT DIRTY"

        self.print_results()

    def print_results(self):
        print "Algorithm: Clock"
        print "Number of frames:   "+str(len(self.PAGE_TABLE.frame_table))
        print "Total Memory Accesses: "+str(self.PAGE_TABLE.total_memory_accesses)
        print "Total Page Faults: "+str(self.PAGE_TABLE.page_faults)
        print "Total Writes to Disk: "+str(self.PAGE_TABLE.writes_to_disk)
