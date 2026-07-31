from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    # pattern = "01?1": position 0 -> 0, position 1 -> 1, position 2 -> ?, position 3 -> 1
    a = ancilla_qubits[0]
    # Flip qubits that must be 0 so that a match becomes all-ones on the checked positions.
    qc.x(problem_qubits[0])  # position 0 must be 0
    # positions 1 and 3 must be 1 (no flip); position 2 is wildcard (excluded)
    checked = [problem_qubits[0], problem_qubits[1], problem_qubits[3]]
    qc.h(a)
    qc.mcx(checked, a)       # phase kickback: -1 iff all checked positions are 1
    qc.h(a)
    qc.x(problem_qubits[0])  # uncompute the flip
