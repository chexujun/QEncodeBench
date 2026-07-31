from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [9, 8, 15, 12, 5]
    T = 23
    n = len(problem_qubits)
    # 5 ancilla qubits hold the running sum (max sum = 49 < 64 -> 6 bits, but
    # we only need enough bits to detect T=23; use 6 sum-ancillas... we have 6).
    # sum bits: values up to 49 need 6 bits. We have 6 ancillas: use all as sum reg.
    nbits = 6
    s = ancilla_qubits[0:nbits]  # sum register, initially |0>

    def add_constant(const, ctrl):
        # controlled addition of `const` into sum register s (little-endian),
        # controlled on qubit `ctrl`. Ripple add using controlled increments.
        # Add bit by bit: for each set position we add power of two with carry.
        # Implement as controlled add of const via a sequence of controlled
        # incrementers is expensive; instead do a standard ripple-carry style
        # add of an integer constant using MCX carry chain.
        bits = [(const >> k) & 1 for k in range(nbits)]
        # We add const to s conditioned on ctrl. Process from LSB.
        # Use the "add classical constant with carry" pattern:
        for i in range(nbits):
            # from top bit down to i, apply carry propagation for adding bit
            pass
        # Fallback simple method: controlled add using incrementer per set bit.
        for k in range(nbits):
            if bits[k]:
                add_power(k, ctrl)

    def increment_from(pos, ctrl_list):
        # add 1 at position pos into register s[pos:], controlled on ctrl_list.
        # ripple: to set/carry, flip s[pos] but first propagate carries from top.
        # Standard controlled increment (little-endian) over s[pos:]:
        for j in range(nbits - 1, pos, -1):
            controls = ctrl_list + s[pos:j]
            qc.mcx(controls, s[j])
        controls = ctrl_list
        qc.mcx(controls, s[pos]) if controls else qc.x(s[pos])

    def add_power(k, ctrl):
        increment_from(k, [ctrl])

    # compute sum
    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # phase: mark states where sum == T (binary of 23 over nbits)
    tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(s[k])
    qc.h(s[nbits - 1])
    qc.mcx(s[0:nbits - 1], s[nbits - 1])
    qc.h(s[nbits - 1])
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(s[k])

    # uncompute sum (reverse)
    def add_power_inv(k, ctrl):
        increment_from_inv(k, [ctrl])

    def increment_from_inv(pos, ctrl_list):
        controls = ctrl_list
        qc.mcx(controls, s[pos]) if controls else qc.x(s[pos])
        for j in range(pos + 1, nbits):
            controls2 = ctrl_list + s[pos:j]
            qc.mcx(controls2, s[j])

    def add_constant_inv(const, ctrl):
        bits = [(const >> k) & 1 for k in range(nbits)]
        for k in range(nbits):
            if bits[k]:
                add_power_inv(k, ctrl)

    for i in reversed(range(n)):
        add_constant_inv(a[i], problem_qubits[i])
