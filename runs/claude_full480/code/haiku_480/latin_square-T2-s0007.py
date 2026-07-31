from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for completing a 3x3 Latin square.
    
    Free cells at (0,1), (1,1), (1,2) must decode to values 0, 2, 1 respectively.
    Each cell uses 2 qubits with surjective encoding: 00->0, 01->1, 10->2, 11->0.
    
    Ancilla usage:
    - a[0]: q[0] XNOR q[1]  (cell 0 has value 0)
    - a[1]: NOT q[2] AND q[3]  (cell 1 has value 2)
    - a[2]: q[4] AND NOT q[5]  (cell 2 has value 1)
    - a[3]: a[0] AND a[1]
    - a[4]: a[3] AND a[2]  (final flag)
    - a[5], a[6]: temporary helpers for negated controls
    """
    
    q = problem_qubits
    a = ancilla_qubits
    
    # COMPUTE PHASE
    
    # a[0] = NOT(q[0] XOR q[1]) = q[0] XNOR q[1]
    # Cell 0 decodes to 0 iff (q0,q1) in {00, 11}
    qc.x(a[0])
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])
    
    # a[1] = NOT q[2] AND q[3]
    # Cell 1 decodes to 2 iff (q2,q3) = (0,1)
    qc.cx(q[2], a[5])
    qc.x(a[5])
    qc.ccx(a[5], q[3], a[1])
    qc.x(a[5])
    qc.cx(q[2], a[5])
    
    # a[2] = q[4] AND NOT q[5]
    # Cell 2 decodes to 1 iff (q4,q5) = (1,0)
    qc.cx(q[5], a[6])
    qc.x(a[6])
    qc.ccx(q[4], a[6], a[2])
    qc.x(a[6])
    qc.cx(q[5], a[6])
    
    # a[3] = a[0] AND a[1]
    qc.ccx(a[0], a[1], a[3])
    
    # a[4] = a[3] AND a[2]  (all three conditions met)
    qc.ccx(a[3], a[2], a[4])
    
    # APPLY PHASE: -1 iff a[4] = 1
    qc.z(a[4])
    
    # UNCOMPUTE (reverse order)
    qc.ccx(a[3], a[2], a[4])
    qc.ccx(a[0], a[1], a[3])
    
    qc.cx(q[5], a[6])
    qc.x(a[6])
    qc.ccx(q[4], a[6], a[2])
    qc.x(a[6])
    qc.cx(q[5], a[6])
    
    qc.cx(q[2], a[5])
    qc.x(a[5])
    qc.ccx(a[5], q[3], a[1])
    qc.x(a[5])
    qc.cx(q[2], a[5])
    
    qc.cx(q[1], a[0])
    qc.cx(q[0], a[0])
    qc.x(a[0])
