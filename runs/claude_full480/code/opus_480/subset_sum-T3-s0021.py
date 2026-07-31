import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [4, 13, 3, 9, 15]
    T = 19
    n = len(a)
    # Sum register: 5 bits suffice (max sum 44 < 64, but use 5 bits since
    # we only need to detect exactly T=19; use 5 sum-bits, indices in ancilla)
    # Use ancilla_qubits[0..4] as a binary counter accumulating the sum,
    # ancilla_qubits[5] as the phase-flag ancilla.
    S = ancilla_qubits[0:5]   # sum bits, S[0] = LSB
    flag = ancilla_qubits[5]
    nbits = len(S)

    def add_constant(ctrl, c):
        # Controlled add of classical constant c into the S register,
        # controlled on qubit `ctrl`. Ripple add MSB-first to reuse carries.
        for j in range(nbits - 1, -1, -1):
            if (c >> j) & 1:
                # add 1 at bit position j: propagate carry to higher bits
                for k in range(nbits - 1, j, -1):
                    controls = [ctrl] + S[j:k]
                    qc.mcx(controls, S[k])
                qc.cx(ctrl, S[j])

    def add_constant_inv(ctrl, c):
        for j in range(nbits - 1, -1, -1):
            if (c >> j) & 1:
                qc.cx(ctrl, S[j])
                for k in range(j + 1, nbits):
                    controls = [ctrl] + S[j:k]
                    qc.mcx(controls, S[k])

    # compute: accumulate selected values
    for i in range(n):
        add_constant(problem_qubits[i], a[i])

    # phase: flip when S == T (mask non-matching bits)
    tbits = [(T >> j) & 1 for j in range(nbits)]
    for j in range(nbits):
        if tbits[j] == 0:
            qc.x(S[j])
    qc.h(flag)
    qc.mcx(S, flag)
    qc.h(flag)
    for j in range(nbits):
        if tbits[j] == 0:
            qc.x(S[j])

    # uncompute
    for i in range(n - 1, -1, -1):
        add_constant_inv(problem_qubits[i], a[i])
