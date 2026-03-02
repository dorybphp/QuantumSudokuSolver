from typing import List, Tuple, Dict
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Gate

def diffuser(n_qubits: int) -> Gate:
    """
    Diffuser (inversion about the mean) operator.
    
    This operator amplifies the probability amplitude of the states marked by 
    the oracle by reflecting all amplitudes about the average.

    Args:
        n_qubits (int): The number of variable qubits the diffuser acts upon.
        
    Returns:
        Gate: A Qiskit Gate object representing the diffusion operator.
    """
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits)) 
    qc.x(range(n_qubits)) 
    
    # multi-controlled Z using H-MCX-H sandwich
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc.to_gate(label="diffuser")

def check_logic(qc: QuantumCircuit, var_a_qs: List, var_b_qs: List, aux: QuantumRegister):
    """
    Oracle component: Marks an auxiliary qubit if two quantum variables are NOT equal.
    
    Uses bitwise XOR logic. If the variables are different, at least one bit in 
    the XOR result will be 1.

    Args:
        qc (QuantumCircuit): The circuit to append gates to.
        var_a_qs (List): Two qubits representing Sudoku Cell A.
        var_b_qs (List): Two qubits representing Sudoku Cell B.
        aux (QuantumRegister): The auxiliary qubit to flip if A != B.
    """
    # bitwise XOR
    qc.cx(var_a_qs[0], var_b_qs[0])
    qc.cx(var_a_qs[1], var_b_qs[1])
    
    # check if XOR result is NOT '00'
    qc.x(var_b_qs)
    qc.ccx(var_b_qs[0], var_b_qs[1], aux)
    qc.x(aux) 
    
    # uncompute
    qc.x(var_b_qs)
    qc.cx(var_a_qs[1], var_b_qs[1])
    qc.cx(var_a_qs[0], var_b_qs[0])

def check_logic_const(qc: QuantumCircuit, var_qs: List, val: int, aux: QuantumRegister):
    """
    Oracle component: Marks an auxiliary qubit if a quantum variable != a fixed integer.
    
    Optimizes the circuit by comparing a quantum state directly to a classical 
    constant, saving 2 qubits per comparison.

    Args:
        qc (QuantumCircuit): The circuit to append gates to.
        var_qs (List): Two qubits representing the Sudoku Cell.
        val (int): The fixed integer (0, 1, 2, or 3) to compare against.
        aux (QuantumRegister): The auxiliary qubit to flip if Var != val.
    """
    # flip bits based on the constant so that the 'Equal' state is |11>
    if not (val & 1): qc.x(var_qs[1])
    if not (val & 2): qc.x(var_qs[0])
    
    qc.ccx(var_qs[0], var_qs[1], aux)
    qc.x(aux) # Flip to 1 if NOT equal
    
    # uncompute
    if not (val & 2): qc.x(var_qs[0])
    if not (val & 1): qc.x(var_qs[1])

def grover_sudoku(variables: List[int], fixed: Dict[int, int], all_constraints: List[Tuple[int, int]], iterations: int) -> QuantumCircuit:
    """
    Builds the complete Grover's algorithm circuit for a 4x4 Sudoku puzzle.
    
    This function handles variable initialization, the Oracle (including constraints 
    against fixed cells), and the Diffusion operator.

    Args:
        variables (List[int]): Indices of the empty Sudoku cells (0-15).
        fixed (Dict[int, int]): Dictionary of pre-filled cells {index: value}.
        all_constraints (List[Tuple[int, int]]): List of pairs that must be different.
        iterations (int): Number of Grover iterations to perform.

    Returns:
        QuantumCircuit: The executable Qiskit circuit.
    """
    # only use constraints that involve the variables we are solving for
    rel_constraints = [c for c in all_constraints if c[0] in variables or c[1] in variables]
    
    v = QuantumRegister(len(variables) * 2, 'v')
    c = QuantumRegister(len(rel_constraints), 'c')
    out = QuantumRegister(1, 'out')
    cr = ClassicalRegister(len(variables) * 2)
    qc = QuantumCircuit(v, c, out, cr)
    
    # init variables to superposition
    qc.h(v)
    # phase kickback setup
    qc.x(out); qc.h(out)

    for _ in range(iterations):
        # oracle
        for i, (idx1, idx2) in enumerate(rel_constraints):
            if idx1 in variables and idx2 in variables:
                p1, p2 = variables.index(idx1), variables.index(idx2)
                check_logic(qc, [v[p1*2], v[p1*2+1]], [v[p2*2], v[p2*2+1]], c[i])
            else:
                var_idx = idx1 if idx1 in variables else idx2
                const_val = fixed[idx2] if idx1 in variables else fixed[idx1]
                p = variables.index(var_idx)
                check_logic_const(qc, [v[p*2], v[p*2+1]], const_val, c[i])
        
        qc.mcx(c, out) # mark state if ALL rules are passed
        
        # uncompute
        for i, (idx1, idx2) in reversed(list(enumerate(rel_constraints))):
            if idx1 in variables and idx2 in variables:
                p1, p2 = variables.index(idx1), variables.index(idx2)
                check_logic(qc, [v[p1*2], v[p1*2+1]], [v[p2*2], v[p2*2+1]], c[i])
            else:
                var_idx = idx1 if idx1 in variables else idx2
                const_val = fixed[idx2] if idx1 in variables else fixed[idx1]
                p = variables.index(var_idx)
                check_logic_const(qc, [v[p*2], v[p*2+1]], const_val, c[i])

        # diffuser
        qc.append(diffuser(len(variables) * 2), v)

    qc.measure(v, cr)
    return qc