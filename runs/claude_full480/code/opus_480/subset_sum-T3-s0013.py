from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [13, 4, 9, 15, 4]
    T = 32
    n = len(a)
    W = max(T, sum(a))
    nbits = W.bit_length()  # number of qubits for the running sum register

    sum_q = ancilla_qubits[:nbits]      # sum register (holds subset sum)
    flag = ancilla_qubits[nbits]        # equality flag ancilla

    def add_constant(const, ctrl):
        # Controlled add of `const` into sum register (mod 2^nbits, no overflow
        # since register is sized to hold max possible sum), ripple via MCX.
        for _ in range(const):
            # increment sum register by 1, controlled on ctrl
            for i in range(nbits - 1, -1, -1):
                controls = [ctrl] + sum_q[:i]
                if len(controls) == 1:
                    qc.cx(controls[0], sum_q[i])
                else:
                    qc.mcx(controls, sum_q[i])

    def add_constant_inv(const, ctrl):
        for _ in range(const):
            for i in range(0, nbits):
                controls = [ctrl] + sum_q[:i]
                if len(controls) == 1:
                    qc.cx(controls[0], sum_q[i])
                else:
                    qc.mcx(controls, sum_q[i])

    # compute: build subset sum in sum register
    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # phase: -1 iff sum register == T
    Tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sum_q[k])
    qc.h(flag)
    qc.mcx(sum_q, flag)
    qc.h(flag)
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sum_q[k])

    # uncompute: reverse the subset sum
    for i in range(n - 1, -1, -1):
        add_constant_inv(a[i], problem_qubits[i])
