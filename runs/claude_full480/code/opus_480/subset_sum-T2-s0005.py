import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [10, 2, 8, 9]
    T = 2
    n = len(problem_qubits)

    # The only subset of [10,2,8,9] summing to 2 is {2} (index 1).
    # So f(x) = 1 iff x1 = 1 and x0 = x2 = x3 = 0.
    # Mark that single basis state with a multi-controlled phase.

    # Flip the qubits that must be 0 so they act as "1"-controls.
    zero_bits = [0, 2, 3]
    one_bits = [1]

    for i in zero_bits:
        qc.x(problem_qubits[i])

    controls = [problem_qubits[i] for i in one_bits + zero_bits]
    # Multi-controlled Z (phase -1) on the all-ones control pattern.
    target = controls[-1]
    ctrls = controls[:-1]
    qc.h(target)
    qc.mcx(ctrls, target, ancilla_qubits[0], mode='recursion')
    qc.h(target)

    for i in zero_bits:
        qc.x(problem_qubits[i])
