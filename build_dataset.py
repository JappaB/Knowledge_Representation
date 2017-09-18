import time, random
import os
import copy

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
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print ''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols)
        if r in 'CF': print line
    print

def assign(values, s, d):
    #"""Eliminate all the other values (except d) from values[s] and propagate.
    #Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False

def parse_grid(grid):
    # """Convert grid to a dict of possible values, {square: digits}, or
    # return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s,d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.)
    return values

def parse_values(grid_values):
    # Same as parse_grid but instead af a grid, the grid_values are passed
    # as an argument
    values = dict((s, digits) for s in squares)
    for s,d in grid_values.items():
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.)
    return values

# Eliminate d from values[s]; propagate when values or places <= 2.
# Return values, except return False if a contradiction is detected.
def eliminate(values, s, d):
    if d not in values[s]:
        return values ## Already eliminated
    values[s] = values[s].replace(d,'')
    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
	return False ## Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
	dplaces = [s for s in u if d in values[s]]
	if len(dplaces) == 0:
	    return False ## Contradiction: no place for this value
	elif len(dplaces) == 1:
	    # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values

def solved(values):
    # "A puzzle is solved if each unit is a permutation of the digits 1 to 9."
    def unitsolved(unit):
        return set(values[s] for s in unit) == set(digits)

    return values is not False and all(unitsolved(unit) for unit in unitlist)

def solve(grid): return search(parse_grid(grid))

def search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!
    ## Chose the unfilled square s with the fewest possibilities
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d))
		for d in values[s])

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
        if e: return e
    return False


def solve_all(grids, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""
    def time_solve(grid):
        start = time.clock()
        values = solve(grid)
        t = time.clock()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print '(%.2f seconds)\n' % t
        return (t, solved(values))
    times, results = zip(*[time_solve(grid) for grid in grids])
    N = len(grids)
    if N > 1:
        print "Solved %d of %d %s puzzles (avg %.2f secs (%d Hz), max %.2f secs)." % (
            sum(results), N, name, sum(times)/N, N/sum(times), max(times))

def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return file(filename).read().strip().split(sep)

def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s])==1 else '.' for s in squares)
    return random_puzzle(N) ## Give up and make a new puzzle

def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq

def test():
    "A set of unit tests."
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                               'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                               'A1', 'A3', 'B1', 'B3'])
    print 'All tests pass.'

def display_string(values):
    "return these values as a 2-D grid."
    grid = ""
    for r in rows:
        line = ' '.join(values[r+c] for c in cols)
        grid += line.strip().replace('0', '-')
        if r != rows[-1]:
            grid += '\n'

    return grid

def difference(clues, solution):
    clue_set = set(clues.items())
    solution_items = solution.items()
    diff = [square for square in solution_items if square not in clue_set]
    return {k:v for k, v in diff}

# Return a dictionary of n additional clues from a collection of options.
# Mutates original options dict.
def pick_additional_clues(options, n):
    extra_clues = {}

    for i in range(n):
        key, value = random.choice(options.items())
        extra_clues[key] = value
        del(options[key])

    return extra_clues

def flatten_grid(grid):
    return ''.join([grid[key] for key in squares])

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

# 23 categories
# 49,151 / 23 =
# 2,137 sudokus per number of clues
if __name__ == '__main__':
    test()

    sudoku_lines = open('raw_17_clue_sudokus.txt', 'r').readlines()

    file_collection = []
    for file_number in range(0, 23):
        n_givens = file_number + 17
        file_collection.append(open('starting_grids/{}_clues_per_line.txt'.format(n_givens, n_givens), 'w+'))

    for i, grid in enumerate(sudoku_lines):
        if i % 2137 == 0: print i

        extra_givens = i % 23
        n_givens = extra_givens + 17

        # Save both the dictionary representation of the starting grid and the
        # solved grid
        clue_values = grid_values(grid)
        solved_values = solve(grid)

        # Calculate difference between starting grid and solution
        possible_tranfers = difference(clue_values, solved_values)

        # Take i clues from the dict of options
        new_clues = pick_additional_clues(possible_tranfers, extra_givens)

        # Add new clues to the starting configuation
        new_sudoku = copy.copy(clue_values)
        for key in new_clues.keys():
            new_sudoku[key] = new_clues[key]

        # Write string representation of new grid to appropriate file
        file_collection[extra_givens].write(flatten_grid(new_sudoku) + '\n')

    for output_file in file_collection:
        output_file.close()
