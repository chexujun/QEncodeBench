from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    a0, a1, a2, a3, a4, a5, temp = ancilla_qubits
    
    # ============ COMPUTE UNSATISFIED VALUES ============
    
    # Clause 1: (NOT x1 OR NOT x2 OR x3) = NOT(x1 AND x2 AND NOT x3)
    qc.x(x3)
    qc.ccx(x1, x2, temp)
    qc.ccx(temp, x3, a0)
    qc.ccx(x1, x2, temp)
    qc.x(x3)
    
    # Clause 2: (NOT x0 OR NOT x1 OR NOT x3) = NOT(x0 AND x1 AND x3)
    qc.ccx(x0, x1, temp)
    qc.ccx(temp, x3, a1)
    qc.ccx(x0, x1, temp)
    
    # Clause 3: (NOT x1 OR x2 OR x3) = NOT(x1 AND NOT x2 AND NOT x3)
    qc.x(x2)
    qc.x(x3)
    qc.ccx(x1, x2, temp)
    qc.ccx(temp, x3, a2)
    qc.ccx(x1, x2, temp)
    qc.x(x3)
    qc.x(x2)
    
    # Clause 4: (NOT x0 OR x1 OR NOT x2) = NOT(x0 AND NOT x1 AND x2)
    qc.x(x1)
    qc.ccx(x0, x1, temp)
    qc.ccx(temp, x2, a3)
    qc.ccx(x0, x1, temp)
    qc.x(x1)
    
    # Clause 5: (x1 OR x2 OR NOT x3) = NOT(NOT x1 AND NOT x2 AND x3)
    qc.x(x1)
    qc.x(x2)
    qc.ccx(x1, x2, temp)
    qc.ccx(temp, x3, a4)
    qc.ccx(x1, x2, temp)
    qc.x(x2)
    qc.x(x1)
    
    # Clause 6: (x0 OR x1 OR x3) = NOT(NOT x0 AND NOT x1 AND NOT x3)
    qc.x(x0)
    qc.x(x1)
    qc.x(x3)
    qc.ccx(x0, x1, temp)
    qc.ccx(temp, x3, a5)
    qc.ccx(x0, x1, temp)
    qc.x(x3)
    qc.x(x1)
    qc.x(x0)
    
    # ============ APPLY PHASE ============
    # All clauses satisfied when all unsatisfied values are 0
    # Flip ancillas to detect when all are 0
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    qc.x(a5)
    
    # Multi-controlled phase gate
    qc.mcp(pi, [a0, a1, a2, a3, a4, a5], temp)
    
    # Flip back
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    qc.x(a5)
    
    # ============ UNCOMPUTE ============
    # Reverse order, repeating computation (gates are self-inverse)
    
    qc.x(x0)
    qc.x(x1)
    qc.x(x3)
    qc.ccx(x0, x1, temp)
    qc.ccx(temp, x3, a5)
    qc.ccx(x0, x1, temp)
    qc.x(x3)
    qc.x(x1)
    qc.x(x0)
    
    qc.x(x1)
    qc.x(x2)
    qc.ccx(x1, x2, temp)
    qc.ccx(temp, x3, a4)
    qc.ccx(x1, x2, temp)
    qc.x(x2)
    qc.x(x1)
    
    qc.x(x1)
    qc.ccx(x0, x1, temp)
    qc.ccx(temp, x2, a3)
    qc.ccx(x0, x1, temp)
    qc.x(x1)
    
    qc.x(x2)
    qc.x(x3)
    qc.ccx(x1, x2, temp)
    qc.ccx(temp, x3, a2)
    qc.ccx(x1, x2, temp)
    qc.x(x3)
    qc.x(x2)
    
    qc.ccx(x0, x1, temp)
    qc.ccx(temp, x3, a1)
    qc.ccx(x0, x1, temp)
    
    qc.x(x3)
    qc.ccx(x1, x2, temp)
    qc.ccx(temp, x3, a0)
    qc.ccx(x1, x2, temp)
    qc.x(x3)
