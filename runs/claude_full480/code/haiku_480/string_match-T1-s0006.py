from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern: "?0?1?"
    # f(x) = 1 iff text[1] == 0 AND text[3] == 1
    
    # Compute NOT text[1] into ancilla[0]
    qc.x(ancilla_qubits[0])
    qc.cx(problem_qubits[1], ancilla_qubits[0])
    
    # Compute text[3] AND (NOT text[1]) into ancilla[1]
    qc.ccx(problem_qubits[3], ancilla_qubits[0], ancilla_qubits[1])
    
    # Apply phase -1 when both conditions are met
    qc.z(ancilla_qubits[1])
    
    # Uncompute to restore ancillas to |0>
    qc.ccx(problem_qubits[3], ancilla_qubits[0], ancilla_qubits[1])
    qc.cx(problem_qubits[1], ancilla_qubits[0])
    qc.x(ancilla_qubits[0])
