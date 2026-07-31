from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [7, 6, 3, 3]
    T = 12
    n = len(problem_qubits)
    W = max(a).bit_length() + 1  # bits needed for running sum

    sum_anc = ancilla_qubits[:W]          # register holding the running subset sum
    flag = ancilla_qubits[W]              # phase flag ancilla

    def add_constant(control, const):
        # controlled increment of the sum register by `const` (ripple-carry via QFT-free method)
        # Implement controlled addition of a classical constant using a simple
        # carry-ripple with Toffoli-based increments on the sum register.
        bits = [(const >> k) & 1 for k in range(W)]
        # Add const to sum_anc controlled on `control`.
        # Do it bit by bit from LSB using controlled ripple carry.
        for k in range(W):
            if bits[k]:
                # add 1 at position k, controlled on `control`, ripple carry upward
                # carry chain: for positions j from top down to k+1, flip if all lower are 1
                for j in range(W - 1, k, -1):
                    ctrls = [control] + sum_anc[k:j]
                    qc.mcx(ctrls, sum_anc[j])
                qc.cx(control, sum_anc[k])

    def add_constant_inv(control, const):
        bits = [(const >> k) & 1 for k in range(W)]
        for k in range(W):
            if bits[k]:
                qc.cx(control, sum_anc[k])
                for j in range(k + 1, W):
                    ctrls = [control] + sum_anc[k:j]
                    qc.mcx(ctrls, sum_anc[j])

    # compute: accumulate selected elements into sum_anc
    for i in range(n):
        add_constant(problem_qubits[i], a[i])

    # phase: mark when sum_anc == T
    Tbits = [(T >> k) & 1 for k in range(W)]
    for k in range(W):
        if Tbits[k] == 0:
            qc.x(sum_anc[k])
    qc.h(flag)
    qc.mcx(sum_anc, flag)
    qc.h(flag)
    for k in range(W):
        if Tbits[k] == 0:
            qc.x(sum_anc[k])

    # uncompute: reverse the accumulation
    for i in reversed(range(n)):
        add_constant_inv(problem_qubits[i], a[i])
