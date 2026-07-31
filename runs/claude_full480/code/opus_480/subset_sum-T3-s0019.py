from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [8, 13, 14, 7, 11]
    T = 11
    n = len(a)

    W = max(T, sum(a))
    nbits = W.bit_length()  # number of bits to hold running sum up to sum(a)

    # ancilla layout:
    #   sum register: nbits qubits (running subset sum, little-endian)
    #   we also need a carry scratch qubit for the adder
    sum_reg = ancilla_qubits[:nbits]
    carry = ancilla_qubits[nbits]

    # ---- helper: add classical constant `val` (with control ctrl) into sum_reg ----
    # Controlled add of a constant into a little-endian register using a ripple
    # of controlled increments. We use a simple approach: for a constant add
    # controlled by one qubit, add bit by bit with carry propagation via a
    # sequence of multi-controlled Toffolis. To keep it self-inverse-friendly for
    # uncompute, we implement add and its exact mirror sub.

    def _add_const(ctrl, val, sign):
        # sign = +1 for add, -1 for subtract (subtract = add of (2^nbits - val))
        v = val % (1 << nbits)
        if sign < 0:
            v = (1 << nbits - 0) - v
            v = v % (1 << nbits)
        # ripple-carry constant addition controlled by ctrl
        # process from MSB down so that using carry chain via Toffolis works;
        # standard approach: for each bit position, add bit and propagate carry.
        # We implement the "controlled increment by constant" via the
        # Cuccaro-style trick using controlled adds of each set bit with carries.
        # Simplemost correct method: add each power-of-two term of v using a
        # controlled-increment-by-2^k gadget.
        for k in range(nbits):
            if (v >> k) & 1:
                _cinc(ctrl, k)

    def _cinc(ctrl, start):
        # controlled increment of sum_reg by 2^start, controlled by `ctrl`.
        # increment: for bit j from top down to start, flip bit j if all lower
        # bits (start..j-1) are 1 and ctrl is 1 (carry chain).
        for j in range(nbits - 1, start, -1):
            controls = [ctrl] + sum_reg[start:j]
            qc.mcx(controls, sum_reg[j])
        qc.cx(ctrl, sum_reg[start])

    def _cinc_inv(ctrl, start):
        qc.cx(ctrl, sum_reg[start])
        for j in range(start + 1, nbits):
            controls = [ctrl] + sum_reg[start:j]
            qc.mcx(controls, sum_reg[j])

    def _add_const_inv(ctrl, val, sign):
        v = val % (1 << nbits)
        if sign < 0:
            v = (1 << nbits) - v
            v = v % (1 << nbits)
        for k in reversed(range(nbits)):
            if (v >> k) & 1:
                _cinc_inv(ctrl, k)

    # ---- compute running subset sum into sum_reg ----
    for i in range(n):
        _add_const(problem_qubits[i], a[i], +1)

    # ---- phase: flip sign iff sum_reg == T ----
    Tbits = T % (1 << nbits)
    zero_ctrl = [q for q in range(nbits) if not ((Tbits >> q) & 1)]
    # map sum_reg == T  -> all sum_reg qubits become 1 after X on zero-bits
    for q in zero_ctrl:
        qc.x(sum_reg[q])
    if nbits == 1:
        qc.z(sum_reg[0])
    else:
        qc.h(sum_reg[-1])
        qc.mcx(sum_reg[:-1], sum_reg[-1])
        qc.h(sum_reg[-1])
    for q in zero_ctrl:
        qc.x(sum_reg[q])

    # ---- uncompute running subset sum ----
    for i in reversed(range(n)):
        _add_const_inv(problem_qubits[i], a[i], +1)
