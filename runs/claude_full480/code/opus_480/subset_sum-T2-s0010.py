import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [8, 4, 9, 3]
    T = 20
    n = len(problem_qubits)

    # Sum register width: max sum = 8+4+9+3 = 24 -> needs 5 bits
    nbits = 5
    s = ancilla_qubits[:nbits]  # sum register, initialized to |0>

    def add_constant_controlled(ctrl, const):
        # Add `const` into the sum register s (little-endian), controlled on ctrl.
        # Ripple: for each set of bits, use controlled increments via carry-chain
        # Implement addition of a constant using controlled-controlled logic:
        # We add const by processing bit positions; use a standard controlled
        # constant-adder via successive controlled increments is expensive, so
        # instead add const bit-by-bit with a carry ripple using ctrl as guard.
        # Simplest correct approach: controlled increment repeated is too deep.
        # Use ripple-carry add of constant into register, all controlled by ctrl.
        cbits = [(const >> i) & 1 for i in range(nbits)]
        # We add using the identity: for a controlled add of constant c into s,
        # process from most significant to least significant using MCX carry.
        # Perform in-place add: s += ctrl*const.
        # Use the "increment gate" pattern generalized: add cbits with carry.
        # Carry approach: go from LSB up; maintain carry implicitly via gates.
        for i in range(nbits - 1, -1, -1):
            if cbits[i]:
                # add 1 at position i (controlled by ctrl): this is a controlled
                # increment of the sub-register s[i:]. Implement as cascade of MCX.
                for j in range(nbits - 1, i, -1):
                    controls = [ctrl] + s[i:j]
                    qc.mcx(controls, s[j])
                qc.cx(ctrl, s[i])

    # Compute the sum of selected elements into register s.
    for i in range(n):
        add_constant_controlled(problem_qubits[i], a[i])

    # Phase: mark states where s == T (little-endian bits of T).
    tbits = [(T >> i) & 1 for i in range(nbits)]
    for i in range(nbits):
        if tbits[i] == 0:
            qc.x(s[i])
    qc.h(s[nbits - 1])
    qc.mcx(s[:nbits - 1], s[nbits - 1])
    qc.h(s[nbits - 1])
    for i in range(nbits):
        if tbits[i] == 0:
            qc.x(s[i])

    # Uncompute the sum register (mirror the addition).
    for i in range(n - 1, -1, -1):
        ctrl = problem_qubits[i]
        const = a[i]
        cbits = [(const >> j) & 1 for j in range(nbits)]
        for pos in range(nbits):
            if cbits[pos]:
                qc.cx(ctrl, s[pos])
                for j in range(pos + 1, nbits):
                    controls = [ctrl] + s[pos:j]
                    qc.mcx(controls, s[j])
