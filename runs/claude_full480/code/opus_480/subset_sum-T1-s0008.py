from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = a_vals = [2, 5, 5]
    T = 5
    p = problem_qubits
    anc = ancilla_qubits
    # Sum register: need to represent sums up to 2+5+5=12 -> 4 bits.
    s = anc[0:4]  # sum bits, little-endian, initially 0

    def add_constant(control, c):
        # controlled addition of constant c into sum register s (ripple, in place)
        # add c to the 4-bit register s when 'control' qubit is 1.
        cbits = [(c >> k) & 1 for k in range(4)]
        # ripple add constant: process bit by bit using carry via mcx into higher bits.
        # We add c by, for each set bit position k, doing a controlled increment of s starting at bit k.
        for k in range(4):
            if cbits[k]:
                # controlled increment of s[k:] by 1, conditioned on 'control'
                for j in range(3, k, -1):
                    # flip s[j] if control and s[k..j-1] all 1
                    ctrls = [control] + s[k:j]
                    qc.mcx(ctrls, s[j])
                qc.ccx(control, s[k], s[k]) if False else qc.cx(control, s[k])

    for i in range(3):
        add_constant(p[i], a_vals[i])

    # phase if sum == T (=5 -> bits 1,0,1,0 -> s0=1,s1=0,s2=1,s3=0)
    tbits = [(T >> k) & 1 for k in range(4)]
    for k in range(4):
        if not tbits[k]:
            qc.x(s[k])
    qc.h(s[3])
    qc.mcx(s[0:3], s[3])
    qc.h(s[3])
    for k in range(4):
        if not tbits[k]:
            qc.x(s[k])

    # uncompute additions in reverse
    def add_constant_inv(control, c):
        cbits = [(c >> k) & 1 for k in range(4)]
        for k in reversed(range(4)):
            if cbits[k]:
                qc.cx(control, s[k])
                for j in range(k + 1, 4):
                    ctrls = [control] + s[k:j]
                    qc.mcx(ctrls, s[j])

    for i in reversed(range(3)):
        add_constant_inv(p[i], a_vals[i])
