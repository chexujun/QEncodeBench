from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [3, 1, 1, 7]
    T = 1
    n = len(a)
    maxsum = sum(a)
    nb = max(1, int(np.floor(np.log2(maxsum))) + 1) if maxsum > 0 else 1

    reg = ancilla_qubits[:nb]
    flag = ancilla_qubits[nb]

    def add_constant(const, ctrl):
        # controlled add of `const` into register `reg` (mod 2^nb), controlled on ctrl
        bits = [(const >> j) & 1 for j in range(nb)]
        for j in range(nb - 1, -1, -1):
            if bits[j]:
                for k in range(nb - 1, j, -1):
                    controls = [ctrl] + [reg[m] for m in range(j, k)]
                    qc.mcx(controls, reg[k])
                qc.cx(ctrl, reg[j])

    def add_constant_inv(const, ctrl):
        bits = [(const >> j) & 1 for j in range(nb)]
        for j in range(0, nb, 1):
            if bits[j]:
                qc.cx(ctrl, reg[j])
                for k in range(j + 1, nb):
                    controls = [ctrl] + [reg[m] for m in range(j, k)]
                    qc.mcx(controls, reg[k])

    def compute():
        for i in range(n):
            add_constant(a[i], problem_qubits[i])

    def uncompute():
        for i in range(n - 1, -1, -1):
            add_constant_inv(a[i], problem_qubits[i])

    compute()

    tbits = [(T >> j) & 1 for j in range(nb)]
    for j in range(nb):
        if tbits[j] == 0:
            qc.x(reg[j])
    qc.h(flag)
    qc.mcx(reg, flag)
    qc.h(flag)
    for j in range(nb):
        if tbits[j] == 0:
            qc.x(reg[j])

    uncompute()
