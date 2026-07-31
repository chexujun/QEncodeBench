from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = ancilla_qubits[0]
    
    # Pattern "01101": s_0=0, s_1=1, s_2=1, s_3=0, s_4=1
    # Flip qubits that must be 0 for a match (indices 0, 3)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[3])
    
    # After flipping, all problem qubits are 1 iff text matches pattern
    # Compute AND into ancilla via multi-controlled X
    qc.mcx(problem_qubits, a)
    
    # Apply phase -1 to marked states
    qc.z(a)
    
    # Uncompute: restore ancilla to |0>
    qc.mcx(problem_qubits, a)
    
    # Restore problem qubits
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[3])
