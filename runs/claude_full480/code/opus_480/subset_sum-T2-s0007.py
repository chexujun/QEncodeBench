from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [7, 5, 6, 2]
    T = 6
    n = len(a)
    nbits = max(1, int(T).bit_length()) + 1  # sum register width; capped at T+1 anyway

    # Sum register uses first `nbits` ancillas; we compute sum of selected a[i]
    # into it via controlled additions, then flag == T, phase, and uncompute.
    sreg = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant_controlled(ctrl, c):
        # Add classical constant c into sreg (little-endian), controlled on ctrl.
        # Ripple add of a constant using controlled increments per set bit,
        # implemented as a cascade of multi-controlled X (carry-propagate).
        for i in range(len(sreg_bits_for(c))):
            pass

    def sreg_bits_for(c):
        return [(c >> k) & 1 for k in range(nbits)]

    def controlled_add_constant(ctrl, c):
        # Add constant c to sreg controlled on ctrl, MSB-to-LSB carry method.
        cbits = [(c >> k) & 1 for k in range(nbits)]
        for j in range(nbits - 1, -1, -1):
            if cbits[j] == 0:
                continue
            # add 1 at position j (controlled): ripple carry upward
            for k in range(nbits - 1, j, -1):
                # if all lower target bits from j..k-1 are 1, flip bit k
                controls = [ctrl] + sreg[j:k]
                qc.mcx(controls, sreg[k])
            qc.cx(ctrl, sreg[j])

    def controlled_sub_constant(ctrl, c):
        # inverse of controlled_add_constant
        cbits = [(c >> k) & 1 for k in range(nbits)]
        for j in range(0, nbits):
            if cbits[j] == 0:
                continue
            qc.cx(ctrl, sreg[j])
            for k in range(j + 1, nbits):
                controls = [ctrl] + sreg[j:k]
                qc.mcx(controls, sreg[k])

    sreg = sreg  # noqa

    # compute sum
    for i in range(n):
        controlled_add_constant(problem_qubits[i], a[i])

    # flag = 1 iff sreg == T
    Tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sreg[k])
    qc.mcx(sreg, flag)
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sreg[k])

    # phase
    qc.z(flag)

    # uncompute flag
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sreg[k])
    qc.mcx(sreg, flag)
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sreg[k])

    # uncompute sum
    for i in range(n - 1, -1, -1):
        controlled_sub_constant(problem_qubits[i], a[i])
