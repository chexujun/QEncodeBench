from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits
    c = ancilla_qubits
    
    # Negation patterns for computing unsatisfied conditions.
    # Each clause is (OR of literals). We compute when it's unsatisfied (all literals false).
    # Clause 1: (x0 OR NOT x1 OR x2) → unsatisfied when (NOT x0 AND x1 AND NOT x2)
    # Clause 2: (NOT x0 OR NOT x1 OR x2) → unsatisfied when (x0 AND x1 AND NOT x2)
    # Clause 3: (NOT x0 OR NOT x1 OR NOT x2) → unsatisfied when (x0 AND x1 AND x2)
    # Clause 4: (x0 OR NOT x1 OR NOT x2) → unsatisfied when (NOT x0 AND x1 AND x2)
    # Clause 5: (x0 OR x1 OR NOT x2) → unsatisfied when (NOT x0 AND NOT x1 AND x2)
    negations_list = [
        [True, False, True],   # c[0]
        [False, False, True],  # c[1]
        [False, False, False], # c[2]
        [True, False, False],  # c[3]
        [True, True, False],   # c[4]
    ]
    
    # COMPUTE: Compute each unsatisfied condition into c[0..4]
    for i, negations in enumerate(negations_list):
        # Apply X gates for negations
        for j, negate in enumerate(negations):
            if negate:
                qc.x(problem_qubits[j])
        
        # Compute AND(x0, x1, x2) into c[i] using c[5] as temporary
        qc.ccx(x0, x1, c[5])
        qc.ccx(c[5], x2, c[i])
        qc.ccx(x0, x1, c[5])  # Uncompute c[5]
        
        # Undo X gates
        for j, negate in enumerate(negations):
            if negate:
                qc.x(problem_qubits[j])
    
    # Flip c[0..4] to convert unsatisfied flags to satisfied flags
    for i in range(5):
        qc.x(c[i])
    
    # PHASE: Compute AND of all satisfied flags into c[5]
    qc.mcx([c[0], c[1], c[2], c[3], c[4]], c[5])
    
    # Apply Z gate for the phase (applies -1 to |1> state of c[5])
    qc.z(c[5])
    
    # UNCOMPUTE: Reverse the AND computation
    qc.mcx([c[0], c[1], c[2], c[3], c[4]], c[5])
    
    # Unflip satisfied flags back to unsatisfied
    for i in range(5):
        qc.x(c[i])
    
    # UNCOMPUTE: Undo each unsatisfied condition in reverse order
    for i in reversed(range(len(negations_list))):
        negations = negations_list[i]
        
        # Undo X gates
        for j, negate in enumerate(negations):
            if negate:
                qc.x(problem_qubits[j])
        
        # Uncompute AND(x0, x1, x2) from c[i]
        qc.ccx(x0, x1, c[5])
        qc.ccx(c[5], x2, c[i])
        qc.ccx(x0, x1, c[5])
        
        # Undo X gates
        for j, negate in enumerate(negations):
            if negate:
                qc.x(problem_qubits[j])
