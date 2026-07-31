from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits
    a0, a1, a2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    
    # Target state: q0=1, q1=0, q2=0, q3=1
    # (Free cell 0 needs value 1 -> code 01; Free cell 1 needs value 2 -> code 10)
    # Compute (q0 AND NOT(q1) AND NOT(q2) AND q3) into ancilla
    
    # Flip q1 and q2 so we can use positive controls
    qc.x(q1)
    qc.x(q2)
    # Now target is q0=1, q1=1, q2=1, q3=1
    
    # Compute AND of all four problem qubits
    qc.ccx(q0, q1, a0)      # a0 = q0 AND q1
    qc.ccx(a0, q2, a1)      # a1 = a0 AND q2
    qc.ccx(a1, q3, a2)      # a2 = a1 AND q3
    
    # Apply Z to a2 (phase -1 when predicate is true)
    qc.z(a2)
    
    # Uncompute
    qc.ccx(a1, q3, a2)
    qc.ccx(a0, q2, a1)
    qc.ccx(q0, q1, a0)
    
    # Restore q1 and q2
    qc.x(q2)
    qc.x(q1)
