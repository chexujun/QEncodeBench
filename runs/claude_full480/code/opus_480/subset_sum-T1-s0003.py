from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [5, 1, 3]
    T = 8
    n = len(a)
    nbits = 4  # sum ranges 0..9, needs 4 bits

    s = ancilla_qubits[:nbits]  # sum register bits (LSB first)

    def add_constant(const, ctrl):
        # controlled add of `const` into ripple register s, controlled on ctrl
        # implemented via controlled increments using a simple carry-ripple
        # We add const conditioned on ctrl by adding bit-shifted controlled adds.
        # Use a straightforward controlled-add of a classical constant:
        for shift in range(nbits):
            if (const >> shift) & 1:
                # add 1 at position `shift`, controlled on ctrl
                _cadd_one_at(shift, ctrl)

    def _cadd_one_at(pos, ctrl):
        # ripple: increment s starting at bit `pos`, controlled by ctrl
        # carries propagate upward using multi-controlled X
        for j in range(nbits - 1, pos, -1):
            controls = [ctrl] + s[pos:j]
            qc.mcx(controls, s[j])
        qc.ccx(ctrl, s[pos], s[pos]) if False else None
        qc.cx(ctrl, s[pos])

    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # phase -1 iff s == T
    Tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(s[k])
    qc.h(s[nbits - 1])
    qc.mcx(s[:nbits - 1], s[nbits - 1])
    qc.h(s[nbits - 1])
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(s[k])

    # uncompute the sum register (reverse of compute)
    for i in reversed(range(n)):
        _uncadd_constant(qc, a[i], problem_qubits[i], s, nbits)


def _uncadd_constant(qc, const, ctrl, s, nbits):
    for shift in reversed(range(nbits)):
        if (const >> shift) & 1:
            _uncadd_one_at(qc, shift, ctrl, s, nbits)


def _uncadd_one_at(qc, pos, ctrl, s, nbits):
    qc.cx(ctrl, s[pos])
    for j in range(pos + 1, nbits):
        controls = [ctrl] + s[pos:j]
        qc.mcx(controls, s[j])
