# QuantumSudokuSolver
This project implements a quantum Sudoku solver using Grover's Algorithm for a 4x4 puzzle. The goal is to show how constraint satisfaction problems can be mapped into a quantum search problem

## Problem
Sudoku requires assigning values to a grid while satisfying row, column, and box constraints.

## Approach
The project encodes Sudoku constrains into a quantum oracle. Each unknown cell is represented by two qubits which allows values from {0, 1, 2, 3}. Grover's algorithm is then used to amplify the states that satisfy all Sudoku rules

To reduce circuit size, only unknown cells are encoded as quantum variables and fixed cells are treated like classical constants.

The oracle evaluates Sudoku constraints uses logic circuits that check whether pairs of cells contain different values. If all constraints are satisfied, the oracle flips the phase of the corresponding quantum state.

## Test Scenarios
Level 1: Single variable with row/column constraints
Level 2: Solving a 2x2 Sudoku box
Level 3: Full Sudoku with 3 unknown cells

## Results

## Learnings