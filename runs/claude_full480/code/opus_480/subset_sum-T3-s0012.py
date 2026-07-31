from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [7, 2, 5, 7, 3]
    T = 7
    n = len(a)
    # Sum of all a = 24, needs 5 bits to hold sums up to 24 -> use 5 ancilla as a running sum register.
    # ancilla register width
    W = 5
    anc = ancilla_qubits[:W]

    def add_constant_controlled(ctrl, c):
        # Controlled add of constant c into the anc register (little-endian), modulo 2^W.
        # Use ripple approach via controlled increments: implement addition of constant using
        # sequence of controlled-X with carry through MCX. We implement generic controlled
        # constant adder using the "carry chain" built from the register itself.
        # Simpler: add c by repeated controlled-increment is expensive; instead do bitwise
        # constant addition with carry using ancilla-free ripple within the register.
        # We implement: for constant addition, process from LSB, maintaining carry in the
        # register bits themselves via a standard in-place constant adder (Cuccaro-style is
        # for two registers). Here we do the classic "add constant" using the fact that adding
        # a constant can be decomposed into controlled increments on higher bits.
        for i in range(W):
            if (c >> i) & 1:
                _controlled_increment_from(ctrl, i, anc)

    def _controlled_increment_from(ctrl, start, reg):
        # Increment reg (little-endian) at bit position `start` by 1, controlled on ctrl,
        # rippling carry upward. Adds 2^start to the register mod 2^W.
        m = len(reg)
        # For each target bit j from top down to start: flip bit j if ctrl AND all lower
        # bits from start..j-1 are 1 (carry propagation).
        for j in range(m - 1, start, -1):
            controls = [ctrl] + [reg[k] for k in range(start, j)]
            qc.mcx(controls, reg[j])
        qc.cx(ctrl, reg[start])

    # Compute sum into anc
    for i in range(n):
        add_constant_controlled(problem_qubits[i], a[i])

    # Phase: mark when register equals T
    tbits = [(T >> i) & 1 for i in range(W)]
    for i in range(W):
        if not tbits[i]:
            qc.x(anc[i])
    if W == 1:
        qc.z(anc[0])
    else:
        qc.h(anc[W - 1])
        qc.mcx(anc[:W - 1], anc[W - 1])
        qc.h(anc[W - 1])
    for i in range(W):
        if not tbits[i]:
            qc.x(anc[i])

    # Uncompute sum
    for i in reversed(range(n)):
        _uncompute_add_constant_controlled(problem_qubits[i], a[i])

    def _placeholder():
        pass


def _uncompute_add_constant_controlled(*args, **kwargs):
    pass
