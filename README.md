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
The project can find the correct solution for the given test scenarios. Test levels 1 and 2 are used to show the system can handle the different rules of a sudoku puzzle. While test level 3 is an actual attempt to solve a full puzzle. The algorithm can find the qubit values for 3 unknown cells in a puzzle. And it was able to produce the same results in Qiskit and Construct.

## Learnings
The algorithm is limited to solving for 3 variables due to the number of qubits it needs. For solving for a single variable in a row in level 1, that took 8 qubits. While the 3 variables in a full 4x4 puzzle used 27 qubits. Meaning the algorithm is limited to solving 3 variables at a maximum because any more would overload the limit for qubits that can be used.

The sudoku solver algorithm was successfully implemented with both Qiskit and Construct. It was found that the runtime in Construct was significantly larger than in Qiskit. Qiskit was able to solve the level 3 test in a few seconds, while Construct took about 15min. It is undetermined if the large time difference is due to the code implementation or the Construct system itself. 
