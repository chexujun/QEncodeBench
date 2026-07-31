from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits
    c0, c1, c2, c3, c4, result = ancilla_qubits
    
    # Initialize result to |1> to serve as phase target
    qc.x(result)
    
    # Clause 1: (NOT x0 OR x1 OR x2)
    # False iff x0=1 AND x1=0 AND x2=0
    # Compute: c0 = 1 iff clause satisfied
    qc.x(c0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c0)
    qc.x(x2)
    qc.x(x1)
    
    # Clause 2: (x0 OR NOT x1 OR NOT x2)
    # False iff x0=0 AND x1=1 AND x2=1
    qc.x(c1)
    qc.x(x0)
    qc.mcx([x0, x1, x2], c1)
    qc.x(x0)
    
    # Clause 3: (x0 OR x1 OR x2)
    # False iff x0=0 AND x1=0 AND x2=0
    qc.x(c2)
    qc.mcx([x0, x1, x2], c2)
    
    # Clause 4: (x0 OR NOT x1 OR x2)
    # False iff x0=0 AND x1=1 AND x2=0
    qc.x(c3)
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c3)
    qc.x(x2)
    qc.x(x0)
    
    # Clause 5: (NOT x0 OR NOT x1 OR NOT x2)
    # False iff x0=1 AND x1=1 AND x2=1
    qc.x(c4)
    qc.mcx([x0, x1, x2], c4)
    
    # Apply phase -1 iff all clauses satisfied (all c_i = 1)
    qc.mcp(np.pi, [c0, c1, c2, c3, c4], result)
    
    # Uncompute clauses (reverse order)
    qc.mcx([x0, x1, x2], c4)
    qc.x(c4)
    
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c3)
    qc.x(c3)
    qc.x(x2)
    qc.x(x0)
    
    qc.mcx([x0, x1, x2], c2)
    qc.x(c2)
    
    qc.x(x0)
    qc.mcx([x0, x1, x2], c1)
    qc.x(c1)
    qc.x(x0)
    
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c0)
    qc.x(c0)
    qc.x(x2)
    qc.x(x1)
    
    # Uncompute result
    qc.x(result)
