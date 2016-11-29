"""
@author Anthony (Tony) Poerio - adp59@pitt.edu
CS1550 - Operating Systems
Project #3:   VM Simulator for Page Replacement Algorithms
Summer 2016

Test and report on algorithms for page replacement in an Operating System

Usage:  python vmsim.py -n <numframes> -a <opt|clock|aging|lru> [-r <refresh>] <tracefile>

"""
import sys
import parseInput as parse
import pageTable as pt
import opt as opt
import clock as clock
import lru as lru
import aging as aging
import time

####################################
### PARSE INPUT FROM TRACE FILES ###
####################################



####################
### CONTROL FLOW ###
####################
def main():
    # get user input from command line args, store it in a list
    cmdLineArgs = getUserInput()

    # get the user input from our list, so we can use it in main
    try:
        num_frames = int(cmdLineArgs[0])
    except:
        print "Number of frames not specified properly."
        print "Usage:  python vmsim.py -n <numframes> -a <opt|clock|aging|lru> [-r <refresh>] <tracefile>"

    algorithm = cmdLineArgs[1]
    if cmdLineArgs[2] is not None:
        refresh = float(cmdLineArgs[2])
    traceFile = cmdLineArgs[3]


    # parse the input and store it
    memory_addresses = parse.parse_trace_file(traceFile)

    # build the model for our page table, 32bit address space
    # initialize our table
    pageTable = pt.PageTable(num_frames)




    # write opt algorithm
    if algorithm == "opt":
        t0 = time.time()
        OptAlgorithm = opt.Opt(pageTable, memory_addresses)
        OptAlgorithm.run_algorithm()
        t1 = time.time()
        total = t1-t0
        print "TOTAL RUNNING TIME IN MINUTES: " + str(total*0.0166667)


    # write clock algorithm
    elif algorithm == "clock":
        t0 = time.time()
        clock_algorithm = clock.Clock(pageTable, memory_addresses)
        clock_algorithm.run_algorithm()
        t1 = time.time()
        total = t1-t0
        print "TOTAL RUNNING TIME IN MINUTES: " + str(total*0.0166667)


    # write aging algorithm
    elif algorithm == "aging":
        t0 = time.time()
        aging_algorithm = aging.Aging(pageTable, memory_addresses, refresh)
        aging_algorithm.run_algorithm()
        t1 = time.time()
        total = t1-t0
        print "TOTAL RUNNING TIME IN MINUTES: " + str(total*0.0166667)


    # write lru algorithm
    elif algorithm == "lru":
        t0 = time.time()
        LRU_algorithm = lru.LRU(pageTable, memory_addresses)
        LRU_algorithm.run_algorithm()
        t1 = time.time()
        total = t1-t0
        print "TOTAL RUNNING TIME IN MINUTES: " + str(total*0.0166667)


    else:
        print "Invalid algorithm name. Acceptable choices are:" \
              "\n\t- 'opt' \n\t- 'clock' \n\t- 'aging' \n\t- 'lru' " \
              "\n\n\tNote: algorithm names are case sensitive\n"

        print "Usage:  python vmsim.py -n <numframes> -a <opt|clock|aging|lru> [-r <refresh>] <tracefile>\n"
    return


# NOTE:  Need to change this later... because once we start using -n, etc., the arg values will change
def getUserInput():
    """ Gets user input and saves as class level variables
        :return A list of arguments passed in by the user
    """
    # create a list of argumenst to return, and index variables, so we can find args
    arglist = []
    counter = 0
    num_frames_index = 0
    algorithm_index = 0
    refresh_index = 0
    args = sys.argv

    # parse command line arguments and get our argument indices
    for elem in sys.argv:
        element = elem
        if elem == "-n":
            num_frames_index = counter + 1
        if elem == "-a":
            algorithm_index = counter + 1
        if elem == "-r":
            refresh_index = counter + 1
        counter += 1

    # check that input is okay
    if algorithm_index == 0:
        print "Usage:  python vmsim.py -n <numframes> -a <opt|clock|aging|lru> [-r <refresh>] <tracefile>"



    # get the num frames and algorithm selection
    num_frames = sys.argv[2]
    algorithm = sys.argv[algorithm_index]
    # and append them to the list
    arglist.append(num_frames)
    arglist.append(algorithm)

    # if algorithm is aging
    if algorithm == "aging":
        if len(sys.argv) < 8:
            print "Usage:  python vmsim.py -n <numframes> -a <opt|clock|aging|lru> [-r <refresh>] <tracefile>"
            exit("Too few arguments. Please ensure there is a refresh rate.")
        # then we need a refresh rate
        refresh = sys.argv[refresh_index]
        # append refresh rate and tracefile to our list
        arglist.append(refresh)


    # otherwise, we just need the tracefile
    else:
        # and apend that to the list, with a None in place of our refresh rate
        arglist.append(None)

    # append the tracefile last, since it is always our final argument
    tracefile = sys.argv[-1]
    arglist.append(tracefile)

    # return the list we've built
    return arglist



###################
### ENTRY POINT ###
###################

if __name__ == "__main__":
    main()

