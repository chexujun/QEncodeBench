import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [4, 2, 5]
    T = 7
    n = len(a)
    # sum bits needed to hold up to sum(a)=11 -> 4 bits
    total = sum(a)
    m = total.bit_length()  # number of sum-register bits
    s = ancilla_qubits[:m]  # sum register, initialized |0>

    def add_constant(const, ctrl):
        # controlled add of `const` into sum register s (little-endian),
        # controlled on qubit `ctrl`, using QFT-free ripple via controlled increments.
        # Use phase-free approach: add const by iterating bits with CCX carries is complex;
        # instead use controlled-controlled increments through repeated add-1? Too deep.
        pass

    # Compute sum register using QFT adder (draper) controlled on selection bits.
    # Apply QFT on s
    def qft(regs, inverse=False):
        rr = regs[::-1]
        if not inverse:
            for j in range(len(rr)):
                qc.h(rr[j])
                for k in range(j + 1, len(rr)):
                    qc.cp(math.pi / (2 ** (k - j)), rr[k], rr[j])
        else:
            for j in reversed(range(len(rr))):
                for k in reversed(range(j + 1, len(rr))):
                    qc.cp(-math.pi / (2 ** (k - j)), rr[k], rr[j])
                qc.h(rr[j])

    def add_const_controlled(const, ctrl, sign=1):
        # in Fourier basis, add const to register s controlled on ctrl
        for j in range(m):
            angle = sign * const * math.pi / (2 ** (m - 1 - j))
            qc.cp(angle, ctrl, s[j])

    # compute: Fourier-basis controlled additions
    qft(s, inverse=False)
    for i in range(n):
        add_const_controlled(a[i], problem_qubits[i], sign=+1)
    qft(s, inverse=True)

    # phase: mark states where s == T
    # flip bits where T has 0, so that all-ones triggers mcp
    Tbits = [(T >> j) & 1 for j in range(m)]
    for j in range(m):
        if Tbits[j] == 0:
            qc.x(s[j])
    if m == 1:
        qc.z(s[0])
    else:
        qc.h(s[m - 1])
        qc.mcx(s[:m - 1], s[m - 1])
        qc.h(s[m - 1])
    for j in range(m):
        if Tbits[j] == 0:
            qc.x(s[j])

    # uncompute: reverse the addition
    qft(s, inverse=False)
    for i in range(n):
        add_const_controlled(a[i], problem_qubits[i], sign=-1)
    qft(s, inverse=True)
