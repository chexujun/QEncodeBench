from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = [0, 0, 1, 0, 1, 0]
    
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    temp = ancilla_qubits[2]
    
    # Compute matches for both offsets
    _check_substring_match(qc, problem_qubits[0:6], pattern, a0)
    _check_substring_match(qc, problem_qubits[1:7], pattern, a1)
    
    # Apply phase if either offset matches (a0 OR a1)
    qc.x(a0)
    qc.x(a1)
    qc.ccx(a0, a1, temp)
    qc.x(temp)
    qc.z(temp)
    qc.x(temp)
    qc.ccx(a0, a1, temp)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute
    _check_substring_match(qc, problem_qubits[1:7], pattern, a1)
    _check_substring_match(qc, problem_qubits[0:6], pattern, a0)


def _check_substring_match(qc: QuantumCircuit, text_qubits: list[int],
                           pattern: list[int], ancilla: int) -> None:
    """Check if text matches pattern, toggle ancilla accordingly."""
    qc.x(ancilla)
    
    for text_q, pattern_bit in zip(text_qubits, pattern):
        if pattern_bit == 0:
            qc.cx(text_q, ancilla)
        else:
            qc.x(text_q)
            qc.cx(text_q, ancilla)
            qc.x(text_q)
