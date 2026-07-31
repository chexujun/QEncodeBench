from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [4, 4, 5]
    T = 4
    n = len(a)

    # Solutions: subsets summing to 4 -> select a[0] alone (100) or a[1] alone (010).
    # Enumerate via arithmetic-free per-solution multi-controlled phase using
    # control-state matching. We compute a fresh AND of literals into an ancilla
    # for each satisfying assignment, phase it, and uncompute.
    solutions = []
    for x in range(2 ** n):
        s = 0
        for i in range(n):
            if (x >> i) & 1:
                s += a[i]
        if s == T:
            solutions.append(x)

    flag = ancilla_qubits[0]

    for x in solutions:
        # Set X on qubits that should be 0 so an all-ones MCX fires on this pattern.
        zero_bits = [problem_qubits[i] for i in range(n) if not ((x >> i) & 1)]
        for q in zero_bits:
            qc.x(q)
        controls = [problem_qubits[i] for i in range(n)]
        qc.mcx(controls, flag)
        qc.z(flag)
        qc.mcx(controls, flag)
        for q in zero_bits:
            qc.x(q)
