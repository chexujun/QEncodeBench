from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # pattern = "?11?": require s_1 == 1 and s_2 == 1; positions 0 and 3 are wildcards.
    q1 = problem_qubits[1]
    q2 = problem_qubits[2]
    qc.cz(q1, q2)
