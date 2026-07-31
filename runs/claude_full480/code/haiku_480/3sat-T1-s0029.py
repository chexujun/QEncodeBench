from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits
    a0, a1, a2, a3, a4 = ancilla_qubits
    
    # Compute which clauses are FALSE into ancillas a0, a1, a2, a3
    
    # Clause 1: (NOT x0 OR x1 OR x2) is FALSE iff x0=1 AND x1=0 AND x2=0
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a0)
    qc.x(x2)
    qc.x(x1)
    
    # Clause 2: (x0 OR NOT x1 OR NOT x2) is FALSE iff x0=0 AND x1=1 AND x2=1
    qc.x(x0)
    qc.mcx([x0, x1, x2], a1)
    qc.x(x0)
    
    # Clause 3: (NOT x0 OR NOT x1 OR x2) is FALSE iff x0=1 AND x1=1 AND x2=0
    qc.x(x2)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x2)
    
    # Clause 4: (NOT x0 OR x1 OR NOT x2) is FALSE iff x0=1 AND x1=0 AND x2=1
    qc.x(x1)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x1)
    
    # Flip ancillas so they're 1 iff clause is satisfied (not FALSE)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    
    # Apply phase -1 iff all clauses are satisfied
    qc.mcp(np.pi, [a0, a1, a2, a3], a4)
    
    # Uncompute: reverse the ancilla flips
    qc.x(a3)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute: reverse the clause computations
    qc.x(x1)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x1)
    
    qc.x(x2)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x2)
    
    qc.x(x0)
    qc.mcx([x0, x1, x2], a1)
    qc.x(x0)
    
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a0)
    qc.x(x2)
    qc.x(x1)
