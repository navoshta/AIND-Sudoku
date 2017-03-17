assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    """
    Cross product of elements in A and elements in B.

    Parameters
    ----------
    a   : First string.
    b   : Second string.

    Returns
    -------
    List of element-wose products.
    """
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[s + t for (s, t) in zip(rows, cols)]] + [[s + t for (s, t) in zip(rows, reversed(cols))]]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """
    Eliminates values using the naked twins strategy.

    Parameters
    ----------
    values  : A dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    The values dictionary with the naked twins eliminated from peers.
    """

    for unit in unitlist:
        unit_values = [values[box] for box in unit]
        # Find all instances of naked twins in the unit
        twins = set([values[box] for box in unit if len(values[box]) > 1 and unit_values.count(values[box]) == len(values[box])])
        # Eliminate the naked twins as possibilities for their peers
        for twin in twins:
            for box in unit:
                if values[box] != twin and len(values[box]) > 1:
                    assign_value(values, box, remove_digits(values[box], twin))
    return values

def remove_digits(value, digits):
    """
    Removes digits from the value.

    Parameters
    ----------
    value   : A string to remove digits from.
    digits  : A string containing digits to remove.

    Returns
    -------
    Value without provided digits.
    """

    for digit in digits:
        value = value.replace(digit, '')
    return value

def grid_values(grid):
    """
    Converts a grid string into {<box>: <value>} dict with '123456789' value for empties.

    Parameters
    ----------
    grid    : Sudoku grid in string form, 81 characters long

    Returns
    -------
    Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """

    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))

def display(values):
    """
    Displays the values as a 2-D grid.

    Parameters
    ----------
    values  : The sudoku in dictionary form.
    """

    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Eliminates values from peers of each box with a single value.

    Goes through all the boxes, and whenever there is a box with a single value,
    eliminates this value from the set of values of all its peers.

    Parameters
    ----------
    values  : The sudoku in dictionary form.

    Returns
    -------
    Resulting Sudoku in dictionary form after eliminating values.
    """

    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    """
    Finalizes all values that are the only choice for a unit.

    Goes through all the units, and whenever there is a unit with a value that only fits in one box,
    assigns the value to this box.

    Parameters
    ----------
    values  : The sudoku in dictionary form.

    Returns
    -------
    Resulting Sudoku in dictionary form after filling in only choices.
    """

    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    """
    Iterates `eliminate()` and `only_choice()`. If at some point, there is a box with no available values,
    returns `False`. If the sudoku is solved, returns the sudoku. If after an iteration of both functions, the sudoku
    remains the same, function returns the sudoku.

    Parameters
    ----------
    values  : The sudoku in dictionary form.

    Returns
    -------
    The resulting sudoku in dictionary form.
    """

    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, tries all possible values.

    Parameters
    ----------
    values  : The sudoku in dictionary form.

    Returns
    -------
    The dictionary representation of the final sudoku grid. `False` if no solution exists.
    """

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Finds the solution to a Sudoku grid.
    Parameters
    ----------
    grid    : A string representing a sudoku grid.

    Returns
    -------
    The dictionary representation of the final sudoku grid. `False` if no solution exists.
    """

    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
