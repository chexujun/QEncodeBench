from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [6, 6, 2]
    T = 8
    n = len(a)
    maxsum = sum(a)
    nbits = max(1, int(np.floor(np.log2(maxsum))) + 1) if maxsum > 0 else 1

    sum_reg = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant(const, control):
        # controlled add of `const` into sum_reg (little-endian) via QFT-based phase adder
        m = len(sum_reg)
        for q in sum_reg:
            qc.h(q)
        for j in range(m):
            angle = 0.0
            for k in range(j + 1):
                if (const >> k) & 1:
                    angle += np.pi / (2 ** (j - k))
            if angle != 0.0:
                qc.cp(angle, control, sum_reg[j])
        for q in reversed(sum_reg):
            qc.h(q)
        # inverse QFT internal swaps/H are folded; use standard QFT
        # (note: the H-only framing above is not a full QFT)

    # Full QFT adder implementation
    def qft(reg):
        m = len(reg)
        for j in range(m - 1, -1, -1):
            qc.h(reg[j])
            for k in range(j - 1, -1, -1):
                qc.cp(np.pi / (2 ** (j - k)), reg[k], reg[j])
        for i in range(m // 2):
            qc.swap(reg[i], reg[m - 1 - i])

    def iqft(reg):
        m = len(reg)
        for i in range(m // 2):
            qc.swap(reg[i], reg[m - 1 - i])
        for j in range(0, m):
            for k in range(0, j):
                qc.cp(-np.pi / (2 ** (j - k)), reg[k], reg[j])
            qc.h(reg[j])

    def cadd_const(const, control, reg):
        m = len(reg)
        for j in range(m):
            angle = 0.0
            for k in range(m):
                if (const >> k) & 1:
                    if j - k >= 0:
                        angle += np.pi / (2 ** (j - k))
            if angle != 0.0:
                qc.cp(angle, control, reg[j])

    def compute_sum():
        qft(sum_reg)
        for i in range(n):
            cadd_const(a[i], problem_qubits[i], sum_reg)
        iqft(sum_reg)

    def uncompute_sum():
        qft(sum_reg)
        for i in range(n):
            cadd_const((-a[i]) % (2 ** len(sum_reg)), problem_qubits[i], sum_reg)
        iqft(sum_reg)

    # compute sum into sum_reg
    compute_sum()

    # flip bits of sum_reg where T has 0, so sum_reg == all-ones iff sum == T
    for j in range(len(sum_reg)):
        if not ((T >> j) & 1):
            qc.x(sum_reg[j])

    # phase -1 iff all sum_reg bits are 1 (i.e. sum == T)
    qc.h(sum_reg[-1])
    qc.mcx(sum_reg[:-1], sum_reg[-1])
    qc.h(sum_reg[-1])

    # undo mask
    for j in range(len(sum_reg)):
        if not ((T >> j) & 1):
            qc.x(sum_reg[j])

    # uncompute sum
    uncompute_sum()
