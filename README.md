The program should be run in the command line using Python:
    python minimax.py [-v] [-ab] -range n min/max graph-file

-v indicates verbose mode (more later)
-ab indicates to use alpha-beta pruning (by default do not do A-B but always do max-value)
-range and a number n indicating the max value (and by inference - n is the minimum)
provide whether the root player is min or max
a graph file to read (next section)

Run the following:
    python minimax.py -range 1000 max ./examples/example1.txt
    python minimax.py -range 1000 min ./examples/example1.txt
    python minimax.py -v -range 1000 max ./examples/example1.txt
    python minimax.py -v -range 1000 min ./examples/example1.txt
    python minimax.py -v -ab -range 1000 max ./examples/example1.txt
    python minimax.py -v -ab -range 1000 min ./examples/example1.txt

Change the number in example1.txt to run on another file.
Change 1000 to 10 for example7.txt.