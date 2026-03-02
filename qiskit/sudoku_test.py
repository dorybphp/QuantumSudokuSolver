import matplotlib.pyplot as plt
from qiskit_aer import AerSimulator
from qiskit import transpile
from sudokuSolver import *

def get_full_sudoku_rules():
    """
    Generates all 56 standard Row, Column, and Box constraints for a 4x4 grid.

    Returns:
        List[Tuple[int, int]]: A list of unique cell index pairs that must be different.
    """
    rules = set()
    for i in range(4):
        row = [i*4 + j for j in range(4)]
        col = [j*4 + i for j in range(4)]
        for p in [(row[a], row[b]) for a in range(4) for b in range(a+1, 4)]: rules.add(tuple(sorted(p)))
        for p in [(col[a], col[b]) for a in range(4) for b in range(a+1, 4)]: rules.add(tuple(sorted(p)))
    for r, c in [(0,0), (0,2), (2,0), (2,2)]:
        box = [r*4+c, r*4+c+1, (r+1)*4+c, (r+1)*4+c+1]
        for p in [(box[a], box[b]) for a in range(4) for b in range(a+1, 4)]: rules.add(tuple(sorted(p)))
    return list(rules)

def decode(bitstring: str, variables: List[int]) -> str:
    """
    Translates a measurement bitstring into human-readable Sudoku values.

    Args:
        bitstring (str): The raw binary string from the quantum simulator.
        variables (List[int]): The list of cell indices being solved.

    Returns:
        str: A formatted string showing cell values (e.g., "Cell 0: 3, Cell 1: 1").
    """
    bits = bitstring[::-1]
    return ", ".join([f"Cell {v}: {int(bits[i*2+1])*2 + int(bits[i*2])}" for i, v in enumerate(variables)])

def run_test(vars, fixed, rules, iters, title):
    """
    Standardizes the transpilation and execution of the Sudoku circuits.
    """
    print(f"\nRunning {title}...")
    qc = grover_sudoku(vars, fixed, rules, iters)
    sim = AerSimulator()
    t_qc = transpile(qc, sim)
    
    # Check if we are within the user's 28-qubit limit
    num_qubits = len(qc.qubits)
    print(f"Total Qubits Used: {num_qubits}")
    if num_qubits > 28:
        print("WARNING: This circuit exceeds the 28-qubit limit.")
        
    counts = sim.run(t_qc, shots=4096).result().get_counts()
    winner = max(counts, key=counts.get)
    print(f"Top Result: {winner} -> ({decode(winner, vars)})")

def test_level_1_row():
    run_test([0], {1: 1, 4: 2}, [(0,1), (0,4)], 1, "LEVEL 1: Row/Col")

def test_level_2_box():
    vars = [0, 1, 4, 5]
    fixed = {2: 2, 3: 3, 6: 0, 7: 1}
    rules = [(0,1), (4,5), (0,4), (1,5), (0,5), (1,4), (0,2), (1,3), (4,6), (5,7)]
    run_test(vars, fixed, rules, 12, "LEVEL 2: 2x2 Box")

def test_level_3_full_25q():
    """ Integration test scaled to 25 qubits for 28-qubit hardware compatibility. """
    vars = [0, 1, 2] # 3 Variables = 6 qubits
    fixed = {3:0, 4:2, 5:3, 6:0, 7:1, 8:1, 9:0, 10:3, 11:2, 12:3, 13:1, 14:2, 15:0}
    all_rules = get_full_sudoku_rules()
    run_test(vars, fixed, all_rules, 6, "LEVEL 3: Full Integration (25 Qubits)")

if __name__ == "__main__":
    test_level_1_row()
    test_level_2_box()
    test_level_3_full_25q()