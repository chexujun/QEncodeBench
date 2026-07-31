from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1 = ancilla_qubits[0], ancilla_qubits[1]
    
    # Pattern "1??10?" requires: s_0=1, s_3=1, s_4=0
    # Compute the predicate s_0 AND s_3 AND (NOT s_4), then apply phase
    
    # Compute s_0 into a0
    qc.cx(problem_qubits[0], a0)
    
    # Compute s_0 AND s_3 into a1 (using a0 as control)
    qc.ccx(a0, problem_qubits[3], a1)
    
    # Uncompute a0 so it's fresh for reuse
    qc.cx(problem_qubits[0], a0)
    
    # Flip s_4 to enable control on NOT s_4
    qc.x(problem_qubits[4])
    
    # Compute (s_0 AND s_3) AND (NOT s_4) into a0
    qc.ccx(a1, problem_qubits[4], a0)
    
    # Apply phase flip on a0 (which holds the full predicate)
    qc.z(a0)
    
    # Uncompute in reverse order
    qc.ccx(a1, problem_qubits[4], a0)
    qc.x(problem_qubits[4])
    qc.cx(problem_qubits[0], a0)
    qc.ccx(a0, problem_qubits[3], a1)
    qc.cx(problem_qubits[0], a0)
