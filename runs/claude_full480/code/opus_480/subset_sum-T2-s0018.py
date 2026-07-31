import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    a = [7, 7, 5, 8]
    T = 8
    n = len(a)

    # subsets summing to T = 8: {8} (index 3), and {7,... } none since 7+? =8 impossible with 7,7,5,8.
    # Actually check: single 8 -> 8. 7+? no. 5+? no. So only x = 1000 (bit3 set, others clear).
    # But be general: find all subsets whose sum == T.
    solutions = []
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if (mask >> i) & 1:
                s += a[i]
        if s == T:
            solutions.append(mask)

    # For each solution mask, flip a phase on exactly that basis state using an mcp/mcz
    # implemented via X-conditioning: apply X to qubits that must be 0, multi-controlled Z, undo X.
    # This marks each solution basis state with -1. Disjoint solutions => phases just multiply.
    for mask in solutions:
        zero_bits = [problem_qubits[i] for i in range(n) if not ((mask >> i) & 1)]
        for q in zero_bits:
            qc.x(q)
        ctrls = list(problem_qubits[:-1])
        tgt = problem_qubits[-1]
        # multi-controlled Z on all problem qubits
        qc.h(tgt)
        if len(ctrls) == 0:
            qc.x(tgt)
        else:
            qc.mcx(ctrls, tgt, ancilla_qubits[0] if len(ancilla_qubits) else None,
                   mode='recursion' if False else 'noancilla')
        qc.h(tgt)
        for q in zero_bits:
            qc.x(q)
