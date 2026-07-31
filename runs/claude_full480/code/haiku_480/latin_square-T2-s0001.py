from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # The unique valid Latin square completion is:
    # Free cell 0 (row 0, col 1) = 0
    # Free cell 1 (row 2, col 0) = 0
    # Free cell 2 (row 2, col 2) = 1
    #
    # With 2-qubit encoding per cell (b0=low, b1=high): 00→0, 01→1, 10→2, 11→0
    # Condition: (q[0] XNOR q[1]) AND (q[2] XNOR q[3]) AND (q[4] AND NOT q[5])
    
    # Compute (q[0] XNOR q[1]) into a[0]
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])
    qc.x(a[0])
    
    # Compute (q[2] XNOR q[3]) into a[1]
    qc.cx(q[2], a[1])
    qc.cx(q[3], a[1])
    qc.x(a[1])
    
    # Compute (q[4] AND NOT q[5]) into a[2]
    qc.x(q[5])
    qc.ccx(q[4], q[5], a[2])
    qc.x(q[5])
    
    # AND the three sub-conditions together
    qc.ccx(a[0], a[1], a[3])
    qc.ccx(a[3], a[2], a[4])
    
    # Apply phase -1 when all conditions are met
    qc.z(a[4])
    
    # Uncompute in reverse order
    qc.ccx(a[3], a[2], a[4])
    qc.ccx(a[0], a[1], a[3])
    
    qc.x(q[5])
    qc.ccx(q[4], q[5], a[2])
    qc.x(q[5])
    
    qc.x(a[1])
    qc.cx(q[3], a[1])
    qc.cx(q[2], a[1])
    
    qc.x(a[0])
    qc.cx(q[1], a[0])
    qc.cx(q[0], a[0])
