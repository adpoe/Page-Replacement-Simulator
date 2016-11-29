""" 'Opt' (optimal)  Page Replacement Algorithm Implementation
"""
import pageTable as pt



## NEXT:  Change print statements to class variables and just write one statement at end, each time.
##        Should speed up significantly.  Replace with variables and make a 1 line print statement for everything.
class Opt():
    """ An implementation of the optimal page replacement algorithm
    """
    def __init__(self, page_table, trace):
        self.PAGE_TABLE = page_table
        self.trace = trace
        self.time_until_use_dict = {}    # HashTable, where the KEY=VPN, VALUE=[NUM_LOADS_UNTIL_USED]
                                    # every iteration of the algorithm we need to subtract value by 1

        # string concatenation variables
        self.hit = False
        self.evict = False
        self.dirty = False

    def get_next_address(self):
        # consume current value at trace[0]. remove it from the list
        self.PAGE_TABLE.total_memory_accesses += 1
        return self.trace.pop(0)

    def update_counters(self, vpn):
        """ need to account for how long until the next memory access of all our current pages
            and this function helps us keep track
        """
        """ OLD VERSION
        for frame in self.PAGE_TABLE.frame_table:
            if frame.instructions_until_next_reference is not None:
                frame.instructions_until_next_reference -= 1
        """
        # remove the 'next' memory access because it is the CURRENT access, it won't happen in the future
        list_of_memory_accesses = self.time_until_use_dict[vpn]
        list_of_memory_accesses.pop(0)
        for frame in self.PAGE_TABLE.frame_table:
            if frame.in_use == True:
                frame.instructions_until_next_reference -= 1
                if frame.instructions_until_next_reference < -1:  # -1 means we just processed this address
                    frame.instructions_until_next_reference = self.find_time_until_next_access(vpn)


    def find_time_until_next_access(self, vpn, counter=0):
        """OLD VERSION
        # for item in the trace, loop until we find next instance of of the vpn,
        # increase a counter each time
        # need also to translate the mem address into a vpn, and can do this with functions
        # in the pagetable class
        while not vpn == self.PAGE_TABLE.get_VPN(self.trace[counter][0]):
            counter += 1

            # check if we'd get an out of bounds exception,
            # and if so, return a number 1 greater than the length of our current trace
            if counter >= len(self.trace):
                break

        # once we find the next occurrence of the vpn, return it
        return counter
        """
        next_index_used = self.time_until_use_dict[vpn][0] # get the number at index 0

        # if we get a None, then time until next access is NEVER, or the current trace length+1,
        # which is effectively 'never'
        if next_index_used == None:
           time_until_next_access = len(self.trace) + 1

        # otherwise, we can calculate time until next use by subtracting the total # of memory acccesses,
        # which is the current 'index' of the trace we're on, from the next index at which VPN appears
        else:
            time_until_next_access = next_index_used - self.PAGE_TABLE.total_memory_accesses

        return time_until_next_access


    def find_vpn_in_page_table(self, vpn):
        page_index = None

        # search through and return index if it's there, None if it's not
        index = 0
        for frame in self.PAGE_TABLE.frame_table:
            if frame.VPN == vpn:
                page_index = index
            index += 1

        return page_index

    def check_for_page_fault(self, vpn):
        if vpn in self.PAGE_TABLE.fast_index:
            return False
        else:
            self.PAGE_TABLE.page_faults += 1
            #print "\t-> PAGE FAULT"
            self.hit = False
            return True


    def add_vpn_to_page_table_or_update(self, vpn, R_or_W):
        # iterate through all the frames in the page table,
        # and if there's an empty space, use it
        if vpn in self.PAGE_TABLE.fast_index:
            #print "\t-> NO EVICTION"
            self.evict = False
            frame_index = self.PAGE_TABLE.fast_index[vpn]
            frame = self.PAGE_TABLE.frame_table[frame_index]
            frame.in_use = True
            frame.dirty = False
            frame.VPN = vpn
            frame.PPN = frame_index
            frame.instructions_until_next_reference = self.find_time_until_next_access(vpn)
            self.PAGE_TABLE.fast_index[vpn] = frame.PPN
            # if we have a write, then the page is dirty
            if R_or_W == 'W':
                frame.dirty = True
            return

        # otherwise, search for a free space
        page_added = False
        index = 0
        for frame in self.PAGE_TABLE.frame_table:
            # then set this frame to in use
            if not frame.in_use:
                #print "\t-> NO EVICTION"
                # self.evict = False
                page_added = True
                frame.in_use = True
                frame.dirty = False
                frame.VPN = vpn
                frame.PPN = index
                frame.instructions_until_next_reference = self.find_time_until_next_access(vpn)
                self.PAGE_TABLE.fast_index[vpn] = frame.PPN
                # if we have a write, then the page is dirty
                if R_or_W == 'W':
                    frame.dirty = True
                break
            index += 1


        # if we don't have any free pages, then we need to pick a page to evict, and try again
        if page_added == False:
            self.evict_vpn_from_page_table()
            self.add_vpn_to_page_table_or_update(vpn, R_or_W)


    def evict_vpn_from_page_table(self):
        least_needed = 0
        most_instructions = 0
        # get time until next reference for ALL pages in our page table currently
        for frame in self.PAGE_TABLE.frame_table:
            # but ONLY launch a search if we don't know how long until next reference yet
            # otherwise, don't search a second or third, etc., time

            # then, use this info to find the least needed VPN overall
            if frame.instructions_until_next_reference > most_instructions:
                least_needed = frame.PPN
                most_instructions = frame.instructions_until_next_reference

        # evict the least needed ppn, and if it's dirty write to disk, increase our disk writes by 1
        removal_frame = self.PAGE_TABLE.frame_table[least_needed]
        self.PAGE_TABLE.fast_index.pop(removal_frame.VPN)
        removal_frame.in_use = False
        removal_frame.VPN = None
        removal_frame.instructions_until_next_reference = None
        if removal_frame.dirty:
            self.PAGE_TABLE.writes_to_disk += 1
            # print "\t-> EVICT DIRTY\n"
            self.evict = True
            self.dirty = True
        else:
            # print "\t-> EVICT CLEAN"
            self.evict = True
            self.dirty = False


    def run_algorithm(self):
        """ run the opt algorithm on all memory accesses in our trace
        """
        # perform preprocessing
        self.preprocess_trace()

        # pop from the list while we still have elements in it
        while len(self.trace) > 0:
            # set string concatenation variables
            self.hit = False
            self.evict = False
            self.dirty = False

            # get next address and vpn from our trace
            next_address = self.get_next_address()
            next_vpn = self.PAGE_TABLE.get_VPN(next_address[0])

            # update our counters for how many instructions until next usage of all pages in our page table
            self.update_counters(next_vpn)
            # then, run the algorithm
            self.opt(next_address)

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


    def opt(self, memory_access):
        # what are the steps for opt?
        # I think we need to run the whole trace... but this strategy may work elsewhere
        vpn = self.PAGE_TABLE.get_VPN(memory_access[0])
        read_or_write = memory_access[1]

        # if page IS in table, just check if we have a write, and if we do have a write,
        # then set the dirty bit to true
        if self.check_for_page_fault(vpn) == False:  # if we do NOT have a page fault
                                                     # the page is already present in table
            # and if page is in the table, we don't have to do anything else,
            # just set dirty bit if we're writing
            if read_or_write == 'W':
                page_index = self.find_vpn_in_page_table(vpn)
                self.PAGE_TABLE.frame_table[page_index].dirty = True
            # print to trace that we have a hit
            # print "\t-> HIT\n"
            self.hit = True

        # else, page fault (make it +1; done in check_for_page_fault() fn),
        # and run the algorithm
        else:
             # if page table isn't full, then we just add next memory address
             # if page table IS full, then go through the WHOLE list of accesses, and find the VPN
             # that's IN memory, which won't be used for the longest time in the future.
             # pick THAT memory address and remove it
             self.add_vpn_to_page_table_or_update(vpn, read_or_write)
             #>>>>>>>>> When we go through the access list for each each page, assign it a value, how long until NEXT
             #          use... then, ONLY search when we don't know how long until next use, for NEW
             #          otherwise subtract 1 from the values we currently have in the table each mem load
             #     if dirty, write to disk, count a disk write


    def print_results(self):
        print "Algorithm: Opt"
        print "Number of frames:   "+str(len(self.PAGE_TABLE.frame_table))
        print "Total Memory Accesses: "+str(self.PAGE_TABLE.total_memory_accesses)
        print "Total Page Faults: "+str(self.PAGE_TABLE.page_faults)
        print "Total Writes to Disk: "+str(self.PAGE_TABLE.writes_to_disk)


    def preprocess_trace(self):
        """
          Build a dictionary with the following format: {VPN: [index_used_1, index_used_2, ... index_used_n], VPN2: ..}
        """
        # want to ONLY iterate through the trace ONCE and pre-process the values we need,
        # so we can get to them faster and easier
        trace_index_number = 0
        for elem in self.trace:

            # get a handle to the VPN at the current index
            VPN = self.PAGE_TABLE.get_VPN(elem[0])

            # if our dictionary already has an instance of the VPN...
            if self.time_until_use_dict.has_key(VPN):
                # then add the current index to the list of indices at which our VPN is needed
                VPN_index_list = self.time_until_use_dict[VPN]
                VPN_index_list.append(trace_index_number)

            # otherwise, we need to make a new entry in the dictionary, and a new list
            else:
                # just give the new key a list with our current trace index number to start with
                self.time_until_use_dict[VPN] = [trace_index_number]

            # update the index number that we are looking at
            trace_index_number += 1

        # Once we're done, put a None to the end of the list to signal that this VPN is never used again
        for key in self.time_until_use_dict:
            value_list = self.time_until_use_dict[key]
            value_list.append(None)