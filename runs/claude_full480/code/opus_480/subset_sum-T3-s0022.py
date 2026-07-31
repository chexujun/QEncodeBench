import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    a = [15, 10, 9, 4, 13]
    T = 4
    n = len(a)

    # Number of sum-register qubits needed to hold the running sum.
    # Max possible sum = sum(a) = 51 -> needs 6 bits.
    total = sum(a)
    m = total.bit_length()  # 6 bits for 51

    if len(ancilla_qubits) < m:
        raise ValueError("not enough ancillas")

    sreg = ancilla_qubits[:m]  # sum register (little-endian), starts at |0...0>

    def add_constant(const, ctrl):
        # Controlled addition of integer `const` into sreg, controlled on qubit ctrl.
        # Ripple-carry via controlled increments realized with a cascade of
        # multi-controlled X gates over the sum register (little-endian).
        # Add const to the register value: for each set bit position and carries,
        # implement using the standard "controlled add classical constant" via
        # a sequence of MCX gates from high bit downward for each 1-bit added.
        for _ in range(const):
            # controlled increment by 1
            # increment sreg (little-endian) controlled on ctrl:
            # flip bit0 if ctrl; carry ripples upward.
            for j in range(m - 1, 0, -1):
                controls = [ctrl] + sreg_slice(0, j)
                qc.mcx(controls, sreg[j])
            qc.cx(ctrl, sreg[0])

    def sreg_slice(lo, hi):
        return [sreg[k] for k in range(lo, hi)]

    # Compute: add a[i] into sum register controlled on problem qubit i.
    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # Phase: flip phase iff sum register == T (binary of T over m bits).
    tbits = [(T >> k) & 1 for k in range(m)]
    for k in range(m):
        if tbits[k] == 0:
            qc.x(sreg[k])
    if m == 1:
        qc.z(sreg[0])
    else:
        qc.h(sreg[m - 1])
        qc.mcx(sreg[:m - 1], sreg[m - 1])
        qc.h(sreg[m - 1])
    for k in range(m):
        if tbits[k] == 0:
            qc.x(sreg[k])

    # Uncompute: subtract a[i] (mirror the additions in reverse).
    def sub_constant(const, ctrl):
        for _ in range(const):
            qc.cx(ctrl, sreg[0])
            for j in range(1, m):
                controls = [ctrl] + sreg_slice(0, j)
                qc.mcx(controls, sreg[j])

    for i in reversed(range(n)):
        sub_constant(a[i], problem_qubits[i])
