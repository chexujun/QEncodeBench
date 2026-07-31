from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute whether each clause is NOT satisfied into ancillas a[0], a[1], a[2], a[3]
    # C1: (x[2] OR NOT x[3] OR x[4]) - NOT satisfied when (NOT x[2]) AND x[3] AND (NOT x[4])
    qc.x(x[2])
    qc.x(x[4])
    qc.ccx(x[2], x[3], a[4])
    qc.ccx(a[4], x[4], a[0])
    qc.ccx(x[2], x[3], a[4])
    qc.x(x[4])
    qc.x(x[2])
    
    # C2: (NOT x[2] OR NOT x[3] OR x[4]) - NOT satisfied when x[2] AND x[3] AND (NOT x[4])
    qc.x(x[4])
    qc.ccx(x[2], x[3], a[4])
    qc.ccx(a[4], x[4], a[1])
    qc.ccx(x[2], x[3], a[4])
    qc.x(x[4])
    
    # C3: (x[2] OR x[3] OR NOT x[4]) - NOT satisfied when (NOT x[2]) AND (NOT x[3]) AND x[4]
    qc.x(x[2])
    qc.x(x[3])
    qc.ccx(x[2], x[3], a[4])
    qc.ccx(a[4], x[4], a[2])
    qc.ccx(x[2], x[3], a[4])
    qc.x(x[3])
    qc.x(x[2])
    
    # C4: (x[1] OR NOT x[2] OR NOT x[4]) - NOT satisfied when (NOT x[1]) AND x[2] AND x[4]
    qc.x(x[1])
    qc.ccx(x[1], x[2], a[4])
    qc.ccx(a[4], x[4], a[3])
    qc.ccx(x[1], x[2], a[4])
    qc.x(x[1])
    
    # Apply phase -1 when all clauses are satisfied (all a[0..3] are 0)
    # Flip ancillas to apply mcp when all were originally 0
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.mcp(np.pi, [a[0], a[1], a[2], a[3]], a[4])
    qc.x(a[3])
    qc.x(a[2])
    qc.x(a[1])
    qc.x(a[0])
    
    # Uncompute all ancillas in reverse order
    qc.x(x[1])
    qc.ccx(x[1], x[2], a[4])
    qc.ccx(a[4], x[4], a[3])
    qc.ccx(x[1], x[2], a[4])
    qc.x(x[1])
    
    qc.x(x[2])
    qc.x(x[3])
    qc.ccx(x[2], x[3], a[4])
    qc.ccx(a[4], x[4], a[2])
    qc.ccx(x[2], x[3], a[4])
    qc.x(x[3])
    qc.x(x[2])
    
    qc.x(x[4])
    qc.ccx(x[2], x[3], a[4])
    qc.ccx(a[4], x[4], a[1])
    qc.ccx(x[2], x[3], a[4])
    qc.x(x[4])
    
    qc.x(x[2])
    qc.x(x[4])
    qc.ccx(x[2], x[3], a[4])
    qc.ccx(a[4], x[4], a[0])
    qc.ccx(x[2], x[3], a[4])
    qc.x(x[4])
    qc.x(x[2])
