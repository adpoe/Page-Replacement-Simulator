#VMsim
Simulation and Data Analysis for 4 different Page Replacement Algorithms  

## Usage notes
This is a python program. Please run it from the command line like so:  

•	Opt – Simulate what the optimal page replacement algorithm would choose if it had perfect knowledge
        o	EXAMPLE RUN:  python vmsim.py –n 8 –a opt gcc.trace
•	Clock – Use the better implementation of the second-chance algorithm
        o	EXAMPLE RUN:  python vmsim.py –n 16 –a clock swim.trace
•	Aging – Implement the aging algorithm that approximates LRU with an 8-bit counter
        o	EXAMPLE RUN:  python vmsim.py –n 32 –a aging –r 1 gcc.trace
•	LRU – Do exact LRU.
        o	EXAMPLE RUN:  python vmsim.py –n 64 –a lru swim.trace
