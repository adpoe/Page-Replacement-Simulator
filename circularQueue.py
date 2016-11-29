""" a circular queue implementation for use in the clock algorithm
"""
import pageTable as pt

class CircularQueue():

    def __init__(self, queue_size):
        """
        Must be a Queue of Frames
        :param queue_size:
        :return:
        """
        self.qsize = queue_size
        self.pointer = 0
        self.list = []
        for i in range (0, queue_size):
            self.list.append(pt.Frame())
            self.list[i].PPN = i

    def add_or_update_successful(self, vpn, read_or_write):
        """
        :param frame: A frame to add to the Queue
        :return: False if a frame was NOT added, because the queue is full (will be page fault), True otherwise
        """
        # set sentinel value
        added = False

        # iterate through the list and try to add
        for elem in self.list:
            # if we have an element NOT in use, then we can add there
            # also need to check if we're just doing an update
            if elem.in_use == False or elem.VPN == vpn:
                added = True
                elem.in_use = True
                elem.VPN = vpn
                # if we're doing a write, need to set dirty bit
                if read_or_write == 'W':
                    elem.dirty = True
                # if we're not writing, then we're reading, and so we need to set the reference bit
                else:
                    elem.reference = True

                return added

        return added

    def remove(self, ppn):
        removal_page = self.list[ppn]
        removal_page.in_use = False
        removal_page.referenced = False
        removal_page.dirty = False
        removal_page.vpn = None


    def find_victim(self):
        for index in range(0,self.qsize):
            elem = self.list[self.pointer]
            # if we find a page which is unreferenced (recently) and clean, that's our victim
            if elem.reference == False and elem.dirty == False:
                # return it's PPN, so we can index into it and remove it
                return elem.PPN
            elif elem.reference == False and elem.dirty == True:
                #skip, do nothing
                continue
            elif elem.reference == True and elem.dirty == False:
                elem.reference = False
                elem.dirty = False
            elif elem.reference == True and elem.dirty == True:
                elem.reference = False

            # use modulus of queue size to achieve a circular queue
            self.pointer = (self.pointer + 1) % self.qsize
            assert self.pointer <= self.qsize

        # if we get this far, no victim page was found,
        # need to flush __dirty unreferenced pages__ to disk
        # and then repeat

        return None

    def flush_dirty_and_unreferenced_pages(self):
        # NOTE: need to account for a DISK WRITE in clock algorithm

        # remove the dirty and unreferenced pages, count how many we removed
        number_of_disk_writes = 0
        for elem in self.list:
            if elem.dirty == True and elem.reference == False:
                elem.dirty = False
                number_of_disk_writes += 1

        return number_of_disk_writes