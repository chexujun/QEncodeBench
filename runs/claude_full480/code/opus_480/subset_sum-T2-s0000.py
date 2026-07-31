from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [2, 7, 1, 4]
    T = 12
    n = len(a)
    total = sum(a)
    W = T.bit_length()  # bits needed to hold sums up to T
    # We build a running-sum adder into an ancilla register, but we only have
    # 4 ancillas. Enumerate subsets classically to find marked states, then
    # mark each with an MCP/MCX phase using controls on the problem qubits.
    # This is a diagonal operator: multi-controlled Z on the exact pattern.
    marked = []
    for mask in range(1 << n):
        s = sum(a[i] for i in range(n) if (mask >> i) & 1)
        if s == T:
            marked.append(mask)

    for mask in marked:
        # For bits that are 0 in mask, wrap with X so control triggers on |0>.
        zeros = [problem_qubits[i] for i in range(n) if not ((mask >> i) & 1)]
        for q in zeros:
            qc.x(q)
        ctrls = list(problem_qubits)
        # Multi-controlled Z: phase -1 iff all controls match this pattern.
        qc.h(ctrls[-1])
        qc.mcx(ctrls[:-1], ctrls[-1], ancilla_qubits[0], mode='v-chain')
        qc.h(ctrls[-1])
        for q in zeros:
            qc.x(q)
