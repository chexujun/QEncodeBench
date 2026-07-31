from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits
    a0, a1 = ancilla_qubits[0], ancilla_qubits[1]
    
    # Identify marked state: sum of selected elements = 27
    # Only subset {a[0], a[1], a[2]} = {9, 9, 9} sums to 27
    # This is the state (b0=1, b1=1, b2=1, b3=0)
    
    # Compute b0 AND b1 AND b2 using ancillas
    qc.ccx(q0, q1, a0)      # a0 = b0 AND b1
    qc.ccx(a0, q2, a1)      # a1 = (b0 AND b1) AND b2
    
    # Apply phase -1 when a1=1 AND b3=0
    qc.x(q3)                # Flip b3 to check for b3=0
    qc.cz(a1, q3)           # Z gate when both a1=1 and flipped q3=1
    qc.x(q3)                # Flip b3 back
    
    # Uncompute to restore ancillas to |0>
    qc.ccx(a0, q2, a1)      # Uncompute a1
    qc.ccx(q0, q1, a0)      # Uncompute a0
