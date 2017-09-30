'''

https://github.com/taufanardi/sudoku-sat-solver/blob/master/Sudoku.py

'''

import numpy as np
import subprocess
import json
import csv
import yappi

MEASURE_LABELS = ['seconds', 'level', 'variables', 'used', 'original', 'conflicts', 'learned', 'limit', 'agility', 'MB']

def main():

    with open('data-table.csv', 'wb') as csvfile:
        FIELD_NAMES = ['id', 'givens', 'agility', 'used', 'seconds', 'variables', 'n_phases', 'conflicts', 'level', 'MB', 'limit', 'learned', 'original']
        csv_writer = csv.DictWriter(csvfile, FIELD_NAMES, delimiter=";")

        csv_writer.writeheader()

        data = []

        for n_clues in range(17, 40):
            input_file_path = "../starting_grids/" + str(n_clues) + "_clues_per_line.txt"
            with open(input_file_path, 'r') as input:

                print("Were're at " + input_file_path)

                # Iterate over all lines in the input file
                sudokus = input.readlines()
                for i, sudoku in enumerate(sudokus):

                    # Build matrix as input for solver
                    matrix = parse_sudoku(sudoku)

                    # Extract results from picosat
                    result = solve(matrix)

                    # Add some markers
                    result['givens'] = n_clues
                    result['id'] = str(n_clues) + "-" + str(i)

                    data.append(result)

        # Write to file
        csv_writer.writerows(data)


def parse_sudoku(row):
    # Remove excess whitespace
    row = row.strip()

    # Transform row into array of characters
    row = np.array(list(row))

    # Reshape array to fit solve_problem's expected input
    matrix = row.reshape((9,9)).astype(int)
    return matrix.tolist()


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

def make_dict(output):

    result = {}

    # Initialize number of phases (is incremented on restart and finish)
    result['n_phases'] = 0

    lines = output.split('\nc')

    # Delete table header and footer
    lines = lines[4:-4]
    lines = [line for line in lines if len(line) > 1]

    # Each line represents a phase of the SAT-solver, except for the line that
    # indicates the 'initial reduction limit'. That case is handled in the if/elif
    # Example: s   0.0   0.0   267  63.9    61     8     0     0   0.0   0.3
    for line in lines:

        # separate values
        split_line = line.split()
        phase = split_line[0]

        #Only look at the final result
        if phase == '1':
            for i, value in enumerate(split_line[1:]):
                result[MEASURE_LABELS[i]] = value

        # Count phases
        if phase in 's+R1':
            result['n_phases'] += 1

    return result



def solve(grid):

    #solve a Sudoku problem and return statisitics as nested dict

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

    # Run solve as subprocess and send printed output to string
    lines_to_run = "import pycosat; pycosat.solve(" + json.dumps(clauses) + ", verbose=1)"
    process = subprocess.Popen(["python", "-c", lines_to_run], stdout=subprocess.PIPE)

    out, outerr = process.communicate()

    return make_dict(out)

main()
