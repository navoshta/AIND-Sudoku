# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

### Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?  
A: We find naked twins within every unit (by identifying duplicate values), and then eliminate digits mentioned in naked twins from all other boxes within this unit.

### Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?  
A: Since all contraints are listed in the `unitlist`, we simply add two additional diagonal constraints to this list:
```python
unitlist = unitlist + [[s + t for (s, t) in zip(rows, cols)]] 		# Top-left to bottom-right
		    + [[s + t for (s, t) in zip(rows, reversed(cols))]] # Top-right to bottom-left
```
