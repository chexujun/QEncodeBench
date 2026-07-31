from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [1, 4, 4, 7]
    T = 8
    n = len(problem_qubits)

    # We compute the weighted sum of selected elements into a small binary
    # register held on ancillas, then phase-mark the states whose sum == T,
    # then uncompute.  Max possible sum = 1+4+4+7 = 16, needs 5 bits (0..31),
    # but we only have 5 ancillas total and need them all for the accumulator.
    #
    # Instead of a full adder network (which would exceed the ancilla budget),
    # we use a phase-accumulation trick: implement the diagonal predicate
    # f(x)=[sum == T] via the QFT-based comparator would also need ancillas.
    #
    # We adopt the standard "sum into a register, compare, uncompute" scheme
    # using a binary accumulator on 5 ancilla qubits (values 0..31 fit).

    acc = ancilla_qubits[:5]          # 5-bit accumulator, acc[0] = LSB
    nbits = len(acc)

    def add_constant_controlled(ctrl, c):
        # Add constant c (0<=c<32) into the acc register, all controlled on ctrl.
        # Ripple-carry increment by a constant using controlled multi-controlled X.
        # We add c by adding each set bit position with carries, implemented as
        # a sequence of controlled increments. Simplest correct approach:
        # add c by performing c-th... no; instead add bit-plane with carry.
        #
        # Standard constant addition (Draper-style via increments): to add c,
        # for each bit j of c that is 1, add 2^j. Adding 2^j into the register
        # is an increment at position j: flip acc[j]; if it carried (was 1),
        # propagate carry upward. Implement increment-at-position with a chain
        # of multi-controlled X gates (highest bit first).
        for j in range(nbits):
            if (c >> j) & 1:
                # add 2^j into acc, controlled on ctrl: increment starting at bit j
                for k in range(nbits - 1, j, -1):
                    controls = [ctrl] + [acc[m] for m in range(j, k)]
                    qc.mcx(controls, acc[k])
                qc.cx(ctrl, acc[j])

    def add_constant_controlled_inv(ctrl, c):
        # Inverse of add_constant_controlled (subtract), used for uncompute.
        for j in range(nbits - 1, -1, -1):
            if (c >> j) & 1:
                qc.cx(ctrl, acc[j])
                for k in range(j + 1, nbits):
                    controls = [ctrl] + [acc[m] for m in range(j, k)]
                    qc.mcx(controls, acc[k])

    # compute: accumulate the selected sum
    for i in range(n):
        add_constant_controlled(problem_qubits[i], a[i])

    # phase: -1 iff acc == T (bit pattern of T over nbits)
    zero_flips = [acc[j] for j in range(nbits) if not ((T >> j) & 1)]
    for q in zero_flips:
        qc.x(q)
    qc.h(acc[nbits - 1])
    qc.mcx(acc[:nbits - 1], acc[nbits - 1])
    qc.h(acc[nbits - 1])
    for q in zero_flips:
        qc.x(q)

    # uncompute: reverse the accumulation
    for i in range(n - 1, -1, -1):
        add_constant_controlled_inv(problem_qubits[i], a[i])
