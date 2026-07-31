from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    c1, c2, c3, c4, c5, all_sat = ancilla_qubits
    
    # Compute clause satisfaction bits (1 means unsatisfied)
    # Clause 1: (NOT x0 OR x1 OR NOT x3) - unsatisfied when x0=1, x1=0, x3=1
    qc.x(x1)
    qc.mcx([x0, x1, x3], c1)
    qc.x(x1)
    
    # Clause 2: (NOT x0 OR x2 OR x3) - unsatisfied when x0=1, x2=0, x3=0
    qc.x(x0)
    qc.x(x3)
    qc.mcx([x0, x2, x3], c2)
    qc.x(x0)
    qc.x(x3)
    
    # Clause 3: (x0 OR NOT x1 OR NOT x3) - unsatisfied when x0=0, x1=1, x3=1
    qc.x(x0)
    qc.mcx([x0, x1, x3], c3)
    qc.x(x0)
    
    # Clause 4: (x0 OR x1 OR x2) - unsatisfied when x0=0, x1=0, x2=0
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c4)
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    
    # Clause 5: (x1 OR NOT x2 OR NOT x3) - unsatisfied when x1=0, x2=1, x3=1
    qc.x(x1)
    qc.mcx([x1, x2, x3], c5)
    qc.x(x1)
    
    # Flip to get clause satisfaction bits (1 means satisfied)
    qc.x(c1)
    qc.x(c2)
    qc.x(c3)
    qc.x(c4)
    qc.x(c5)
    
    # AND all satisfactions into all_sat
    qc.mcx([c1, c2, c3, c4, c5], all_sat)
    
    # Apply phase
    qc.z(all_sat)
    
    # Uncompute AND
    qc.mcx([c1, c2, c3, c4, c5], all_sat)
    
    # Flip back
    qc.x(c1)
    qc.x(c2)
    qc.x(c3)
    qc.x(c4)
    qc.x(c5)
    
    # Uncompute clause satisfactions in reverse
    qc.x(x1)
    qc.mcx([x1, x2, x3], c5)
    qc.x(x1)
    
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c4)
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    
    qc.x(x0)
    qc.mcx([x0, x1, x3], c3)
    qc.x(x0)
    
    qc.x(x0)
    qc.x(x3)
    qc.mcx([x0, x2, x3], c2)
    qc.x(x0)
    qc.x(x3)
    
    qc.x(x1)
    qc.mcx([x0, x1, x3], c1)
    qc.x(x1)
