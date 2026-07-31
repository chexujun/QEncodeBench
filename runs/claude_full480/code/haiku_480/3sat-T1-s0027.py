from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # Compute Clause 1: (x0 OR x1 OR NOT x2) into a0
    # NOT satisfied iff x0=0, x1=0, x2=1
    qc.x(a0)
    qc.x(x0)
    qc.x(x1)
    qc.ccx(x0, x1, a1)
    qc.ccx(a1, x2, a0)
    qc.ccx(x0, x1, a1)
    qc.x(x1)
    qc.x(x0)
    
    # Compute Clause 2: (NOT x0 OR x1 OR NOT x2) into a2
    # NOT satisfied iff x0=1, x1=0, x2=1
    qc.x(a2)
    qc.x(x1)
    qc.ccx(x0, x1, a1)
    qc.ccx(a1, x2, a2)
    qc.ccx(x0, x1, a1)
    qc.x(x1)
    
    # Compute Clause 3: (NOT x0 OR NOT x2 OR NOT x3) into a3
    # NOT satisfied iff x0=1, x2=1, x3=1
    qc.x(a3)
    qc.ccx(x0, x2, a1)
    qc.ccx(a1, x3, a3)
    qc.ccx(x0, x2, a1)
    
    # Compute Clause 4: (x0 OR NOT x1 OR NOT x2) into a4
    # NOT satisfied iff x0=0, x1=1, x2=1
    qc.x(a4)
    qc.x(x0)
    qc.ccx(x0, x1, a1)
    qc.ccx(a1, x2, a4)
    qc.ccx(x0, x1, a1)
    qc.x(x0)
    
    # Compute Clause 5: (NOT x0 OR x1 OR x2) into a5
    # NOT satisfied iff x0=1, x1=0, x2=0
    qc.x(a5)
    qc.x(x1)
    qc.x(x2)
    qc.ccx(x0, x1, a1)
    qc.ccx(a1, x2, a5)
    qc.ccx(x0, x1, a1)
    qc.x(x2)
    qc.x(x1)
    
    # Apply phase -1 if all clauses satisfied
    qc.mcp(math.pi, [a0, a2, a3, a4], a5)
    
    # Uncompute Clause 5
    qc.x(x1)
    qc.x(x2)
    qc.ccx(x0, x1, a1)
    qc.ccx(a1, x2, a5)
    qc.ccx(x0, x1, a1)
    qc.x(x2)
    qc.x(x1)
    qc.x(a5)
    
    # Uncompute Clause 4
    qc.x(x0)
    qc.ccx(x0, x1, a1)
    qc.ccx(a1, x2, a4)
    qc.ccx(x0, x1, a1)
    qc.x(x0)
    qc.x(a4)
    
    # Uncompute Clause 3
    qc.ccx(x0, x2, a1)
    qc.ccx(a1, x3, a3)
    qc.ccx(x0, x2, a1)
    qc.x(a3)
    
    # Uncompute Clause 2
    qc.x(x1)
    qc.ccx(x0, x1, a1)
    qc.ccx(a1, x2, a2)
    qc.ccx(x0, x1, a1)
    qc.x(x1)
    qc.x(a2)
    
    # Uncompute Clause 1
    qc.x(x0)
    qc.x(x1)
    qc.ccx(x0, x1, a1)
    qc.ccx(a1, x2, a0)
    qc.ccx(x0, x1, a1)
    qc.x(x1)
    qc.x(x0)
    qc.x(a0)
