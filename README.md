#VMsim
@author Tony Poerio  
@email tony@tonypoer.io  
  
Simulation and Data Analysis for 4 different Page Replacement Algorithms  

## Algorithms Simulated
    * OPT --> the optimal page replacement algorithm, used as a baseline in our data analysis, because it requires perfect future knowledge and is therefore not possible to implement in a real system.
    * Clock --> Second-chance 'clock' algorithm
    * Aging --> Aging algorithm that approximates LRU
    * LRU --> Exact LRU (Least Recently Used) page replacement algorithm

## Usage notes
This is a python program. Please run it from the command line like so:  

* Opt – Simulate what the optimal page replacement algorithm would choose if it had perfect knowledge  
    - EXAMPLE RUN:  `python vmsim.py –n 8 –a opt gcc.trace`  
* Clock – Use the better implementation of the second-chance algorithm  
    - EXAMPLE RUN:  `python vmsim.py –n 16 –a clock swim.trace`  
* Aging – Implement the aging algorithm that approximates LRU with an 8-bit counter  
    - EXAMPLE RUN:  `python vmsim.py –n 32 –a aging –r 1 gcc.trace`  
* LRU – Do exact LRU.  
    - EXAMPLE RUN:  `python vmsim.py –n 64 –a lru swim.trace`  

## Data Analysis
Analysis can be found in:  
`adp59-Project_3_Analysis.pdf`  

Source code for the graphs can be found in:  
`SimulationOutputs.xlsx`

