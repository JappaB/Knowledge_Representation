import sudoku2cnf

def grid_values(grid):
    # "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))

def cross(A, B):
    # "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

# Displays data in dictionary in a pretty grid
def display(values):
    "Display these values as a 2-D grid."
    width = 1+max(len(values[s]) for s in squares)
    grid = ""
    for r in rows:
        line = ''.join(values[r+c].center(width) for c in cols)
        grid += line.strip().replace('0', '-')
        if r != rows[-1]:
            grid += '\n'

    return grid

digits   = '123456789'
rows     = 'ABCDEFGHI'
cols     = digits
squares  = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)

file = open('raw_17_clue_sudokus.txt', 'r')
sudoku_lines = file.readlines()

for (i, line) in enumerate(sudoku_lines):
    output = open('sudoku_grids/' + str(i) + '_grid.txt', 'w')
    grid = display(grid_values(line))
    output.write(grid)
