from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute clause satisfactions into a[0..6]
    # Each clause is represented as NOT(conjunction of literals)
    
    # Clause 1: (NOT x0 OR NOT x1 OR NOT x6) = NOT(x0 AND x1 AND x6)
    qc.x(a[0])
    qc.mcx([x[0], x[1], x[6]], a[0])
    
    # Clause 2: (NOT x3 OR NOT x5 OR x6) = NOT(x3 AND x5 AND NOT x6)
    qc.x(a[1])
    qc.x(x[6])
    qc.mcx([x[3], x[5], x[6]], a[1])
    qc.x(x[6])
    
    # Clause 3: (x2 OR NOT x4 OR x6) = NOT(NOT x2 AND x4 AND NOT x6)
    qc.x(a[2])
    qc.x(x[2])
    qc.x(x[6])
    qc.mcx([x[2], x[4], x[6]], a[2])
    qc.x(x[6])
    qc.x(x[2])
    
    # Clause 4: (NOT x3 OR NOT x5 OR NOT x6) = NOT(x3 AND x5 AND x6)
    qc.x(a[3])
    qc.mcx([x[3], x[5], x[6]], a[3])
    
    # Clause 5: (x1 OR NOT x5 OR NOT x6) = NOT(NOT x1 AND x5 AND x6)
    qc.x(a[4])
    qc.x(x[1])
    qc.mcx([x[1], x[5], x[6]], a[4])
    qc.x(x[1])
    
    # Clause 6: (x3 OR x4 OR x5) = NOT(NOT x3 AND NOT x4 AND NOT x5)
    qc.x(a[5])
    qc.x(x[3])
    qc.x(x[4])
    qc.x(x[5])
    qc.mcx([x[3], x[4], x[5]], a[5])
    qc.x(x[5])
    qc.x(x[4])
    qc.x(x[3])
    
    # Clause 7: (NOT x0 OR NOT x1 OR x2) = NOT(x0 AND x1 AND NOT x2)
    qc.x(a[6])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[6])
    qc.x(x[2])
    
    # Apply multi-controlled phase: P(pi) to a[7] iff all clauses are satisfied
    qc.mcp(np.pi, [a[0], a[1], a[2], a[3], a[4], a[5], a[6]], a[7])
    
    # Uncompute (mirror of compute phase)
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[6])
    qc.x(x[2])
    qc.x(a[6])
    
    qc.x(x[3])
    qc.x(x[4])
    qc.x(x[5])
    qc.mcx([x[3], x[4], x[5]], a[5])
    qc.x(x[5])
    qc.x(x[4])
    qc.x(x[3])
    qc.x(a[5])
    
    qc.x(x[1])
    qc.mcx([x[1], x[5], x[6]], a[4])
    qc.x(x[1])
    qc.x(a[4])
    
    qc.mcx([x[3], x[5], x[6]], a[3])
    qc.x(a[3])
    
    qc.x(x[2])
    qc.x(x[6])
    qc.mcx([x[2], x[4], x[6]], a[2])
    qc.x(x[6])
    qc.x(x[2])
    qc.x(a[2])
    
    qc.x(x[6])
    qc.mcx([x[3], x[5], x[6]], a[1])
    qc.x(x[6])
    qc.x(a[1])
    
    qc.mcx([x[0], x[1], x[6]], a[0])
    qc.x(a[0])
