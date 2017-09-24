'''

https://github.com/taufanardi/sudoku-sat-solver/blob/master/Sudoku.py

'''



import pycosat

import sys, getopt 

import time

import numpy as np


def main(argv): 

    argument = '' 

    try:

        opts, args = getopt.getopt(argv,"f:h",["file","help"])

    except getopt.GetoptError:

        print('Argument error, check -h | --help')

        sys.exit(2)


    for opt, arg in opts:

        print(opt, arg)

        if opt in ("--help"):
            help()

        elif opt in ("-f", "--file"):
            file_name = arg
            n_givens = file_name[:2]

            input_file = open(file_name,'r').readlines()

            for row in input_file:
                # Remove excess whitespace
                row = row.strip()

                # Transform row into array of characters
                row = np.array(list(row))

                # Reshape array to fit solve_problem's expected input
                matrix = row.reshape((9,9)).astype(int)
                matrix = matrix.tolist()

                # Solve row
                solve_problem(matrix, n_givens)

        else:
            help()
            sys.exit()

            

def help():

    print('Usage:')
    print('Sudoku.py -f <file_name> [or] --file <file_name>')

    sys.exit()



def solve_problem(problemset, n_givens):
    print
    print("------------------")
    print("Number of givens: " + n_givens)
    solve(problemset)
    print("------------------")
    print

    

def v(i, j, d): 

    return 81 * (i - 1) + 9 * (j - 1) + d



#Reduces Sudoku problem to a SAT clauses 

def sudoku_clauses(): 

    res = []

    # for all cells, ensure that the each cell:

    for i in range(1, 10):

        for j in range(1, 10):

            # denotes (at least) one of the 9 digits (1 clause)

            res.append([v(i, j, d) for d in range(1, 10)])

            # does not denote two different digits at once (36 clauses)

            for d in range(1, 10):

                for dp in range(d + 1, 10):

                    res.append([-v(i, j, d), -v(i, j, dp)])



    def valid(cells): 

        for i, xi in enumerate(cells):

            for j, xj in enumerate(cells):

                if i < j:

                    for d in range(1, 10):

                        res.append([-v(xi[0], xi[1], d), -v(xj[0], xj[1], d)])



    # ensure rows and columns have distinct values

    for i in range(1, 10):

        valid([(i, j) for j in range(1, 10)])

        valid([(j, i) for j in range(1, 10)])

        

    # ensure 3x3 sub-grids "regions" have distinct values

    for i in 1, 4, 7:

        for j in 1, 4 ,7:

            valid([(i + k % 3, j + k // 3) for k in range(9)])

      

    assert len(res) == 81 * (1 + 36) + 27 * 324

    return res



def solve(grid):

    #solve a Sudoku problem

    clauses = sudoku_clauses()
    thefile = open('test.txt', 'w')

    for clause in clauses:
        thefile.write("%s\n" % clause)

    for i in range(1, 10):

        for j in range(1, 10):

            d = grid[i - 1][j - 1]

            # For each digit already known, a clause (with one literal). 

            if d:

                clauses.append([v(i, j, d)])

    # solve the SAT problem
    start = time.time()
    sol = pycosat.solve(clauses, verbose = 1)
    end = time.time()

    print("Time: "+str(end - start))


    def read_cell(i, j):
        # return the digit of cell i, j according to the solution

        for d in range(1, 10):
            if v(i, j, d) in sol:
                return d



    for i in range(1, 10):

        for j in range(1, 10):

            grid[i - 1][j - 1] = read_cell(i, j)





if __name__ == '__main__':

    from pprint import pprint

    if(len(sys.argv[1:]) == 0):

        print('Argument error, check --help')

    else:
        print(sys.argv)
        main(sys.argv[1:])