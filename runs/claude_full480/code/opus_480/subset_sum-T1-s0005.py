from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [4, 4, 5]
    T = 5
    q = problem_qubits
    n = len(a)

    # Ancillas: 3 sum-register qubits (T=5 needs values 0..13, but we only
    # need to detect exactly 5; use 4-bit register to be safe -> we have 4).
    # sum bits s0,s1,s2,s3 on ancilla_qubits[0..3]
    s = ancilla_qubits[:4]

    def add_constant(ctrl, val):
        # controlled add of integer `val` into register s (ripple, MSB-first
        # to avoid needing extra carry ancilla). We implement controlled
        # increment-by-constant on a 4-bit register modulo 16; since max
        # possible true sum = 4+4+5 = 13 < 16, no overflow wraps a marked state.
        bits = [(val >> i) & 1 for i in range(4)]
        # add from most significant handled bit downward using controlled ripple
        for i in range(3, -1, -1):
            if bits[i]:
                # add 1 at position i: this ripples a carry upward through s[i..3]
                # controlled (on ctrl) increment of subregister s[i:]
                for j in range(3, i, -1):
                    # carry into bit j happens if all lower bits s[i..j-1] are 1
                    controls = [ctrl] + s[i:j]
                    qc.mcx(controls, s[j])
                qc.cx(ctrl, s[i])

    # compute sum
    for i in range(n):
        add_constant(q[i], a[i])

    # phase -1 iff s == T (binary of 5 = 0101 -> s0=1,s1=0,s2=1,s3=0)
    Tbits = [(T >> i) & 1 for i in range(4)]
    for i in range(4):
        if Tbits[i] == 0:
            qc.x(s[i])
    qc.h(s[3])
    qc.mcx(s[:3], s[3])
    qc.h(s[3])
    for i in range(4):
        if Tbits[i] == 0:
            qc.x(s[i])

    # uncompute sum (reverse order, reverse each add_constant)
    for i in range(n - 1, -1, -1):
        ctrl = q[i]
        val = a[i]
        bits = [(val >> b) & 1 for b in range(4)]
        for pos in range(0, 4):
            if bits[pos]:
                qc.cx(ctrl, s[pos])
                for j in range(pos + 1, 4):
                    controls = [ctrl] + s[pos:j]
                    qc.mcx(controls, s[j])
