from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [13, 4, 4, 2, 6]
    T = 27
    n = len(a)
    W = T + 1  # sums range 0..T of interest

    p = problem_qubits
    anc = ancilla_qubits
    nb = 5  # bits to hold sum up to 29 (need 5 bits for value 27)

    # We use a ripple accumulation of the running sum into an ancilla register,
    # then phase-flip iff the register equals T, then uncompute.
    # But we only have 5 ancillas total. Use a comparison-by-controlled-adds
    # approach that stays reversible without a wide register: encode the target
    # test as a nested MCX predicate is not possible without enumeration.
    #
    # Instead: accumulate the selected sum into a 5-qubit ancilla register using
    # controlled ripple-carry additions of the constants a[i], flip phase when
    # the register holds T, then run every step in reverse to clear the register.

    reg = anc[:nb]

    def add_const_controlled(ctrl, const, sign):
        # Add (sign * const) to the little-endian register `reg`, conditioned
        # on control qubit `ctrl`, using controlled ripple increments.
        # Implemented as repeated controlled +/-1 is too deep; instead do a
        # bitwise controlled ripple add of the constant.
        c = const % (1 << nb)
        # controlled add of constant c into reg (mod 2^nb), controlled on ctrl.
        # Ripple: for each set bit, add 2^k with carry propagation.
        # Reversible in-place adder of a classical constant, MSB-first carry.
        def cadd(bit_start):
            # add 1<<bit_start into reg with carries, controlled on ctrl
            for j in range(nb - 1, bit_start, -1):
                ctrls = [ctrl] + reg[bit_start:j]
                qc.mcx(ctrls, reg[j])
            qc.ccx(ctrl, reg[bit_start], reg[bit_start]) if False else None
            qc.cx(ctrl, reg[bit_start])
        def csub(bit_start):
            qc.cx(ctrl, reg[bit_start])
            for j in range(bit_start + 1, nb):
                ctrls = [ctrl] + reg[bit_start:j]
                qc.mcx(ctrls, reg[j])
        bits = [k for k in range(nb) if (c >> k) & 1]
        if sign > 0:
            for k in reversed(bits):
                cadd(k)
        else:
            for k in bits:
                csub(k)

    for i in range(n):
        add_const_controlled(p[i], a[i], +1)

    # Phase flip iff reg == T (little-endian). Set zero-bits, MCZ, unset.
    tbits = [(T >> k) & 1 for k in range(nb)]
    for k in range(nb):
        if tbits[k] == 0:
            qc.x(reg[k])
    qc.h(reg[nb - 1])
    qc.mcx(reg[:nb - 1], reg[nb - 1])
    qc.h(reg[nb - 1])
    for k in range(nb):
        if tbits[k] == 0:
            qc.x(reg[k])

    for i in reversed(range(n)):
        add_const_controlled(p[i], a[i], -1)
