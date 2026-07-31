from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "001?0"
    zero_positions = [i for i, c in enumerate(pattern) if c == '0']
    fixed_controls = [i for i, c in enumerate(pattern) if c in ('0', '1')]

    # Map fixed positions to |1> when they match the pattern:
    # flip the qubits that must be 0 so a match makes all fixed controls |1>.
    for i in zero_positions:
        qc.x(problem_qubits[i])

    control_qubits = [problem_qubits[i] for i in fixed_controls]

    # Phase flip iff all fixed controls are 1 (i.e. text matches pattern).
    qc.h(ancilla_qubits[0])
    qc.mcx(control_qubits, ancilla_qubits[0])
    qc.h(ancilla_qubits[0])

    # Uncompute the flips.
    for i in zero_positions:
        qc.x(problem_qubits[i])
