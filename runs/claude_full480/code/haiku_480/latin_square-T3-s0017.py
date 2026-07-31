import numpy as np
from qiskit.circuit.library import MCPhaseGate

def build_oracle(qc, problem_qubits, ancilla_qubits):
    b0_0, b1_0, b0_1, b1_1, b0_2, b1_2, b0_3, b1_3 = problem_qubits
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # Constraint 1: free_cell_0 = 1 (code 01) → b0_0=1 AND b1_0=0
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b1_0)
    
    # Constraint 2: free_cell_1 = 0 (code 00 or 11) → NOT(b0_1 XOR b1_1)
    qc.cx(b0_1, a1)
    qc.cx(b1_1, a1)
    qc.x(a1)
    
    # Constraint 3: free_cell_2 = 2 (code 10) → b0_2=0 AND b1_2=1
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, a2)
    qc.x(b0_2)
    
    # Constraint 4: free_cell_3 = 0 (code 00 or 11) → NOT(b0_3 XOR b1_3)
    qc.cx(b0_3, a3)
    qc.cx(b1_3, a3)
    qc.x(a3)
    
    # Apply phase -1 when all constraints satisfied
    qc.append(MCPhaseGate(np.pi, 4), [a0, a1, a2, a3])
    
    # Uncompute in reverse
    qc.x(a3)
    qc.cx(b1_3, a3)
    qc.cx(b0_3, a3)
    
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, a2)
    qc.x(b0_2)
    
    qc.x(a1)
    qc.cx(b1_1, a1)
    qc.cx(b0_1, a1)
    
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b1_0)
