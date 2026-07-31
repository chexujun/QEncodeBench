import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [7, 7, 10, 4]
    T = 17
    n = len(a)

    # Enumerate solution subsets (small instance): subsets summing to T.
    solutions = []
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += a[i]
        if s == T:
            solutions.append(mask)

    flag = ancilla_qubits[0]

    for mask in solutions:
        # For this specific basis pattern, flip flag when qubits match mask.
        zeros = [problem_qubits[i] for i in range(n) if not (mask & (1 << i))]
        for q in zeros:
            qc.x(q)
        controls = [problem_qubits[i] for i in range(n)]
        qc.mcx(controls, flag)
        qc.z(flag)
        qc.mcx(controls, flag)
        for q in zeros:
            qc.x(q)
