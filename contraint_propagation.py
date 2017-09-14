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
