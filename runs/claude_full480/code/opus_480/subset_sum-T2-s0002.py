import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits):
    a = [6, 10, 8, 3]
    T = 14
    n = len(problem_qubits)

    # Number of bits needed to hold the running sum (max sum = 27 -> 5 bits)
    total = sum(a)
    nbits = total.bit_length()  # 5

    sum_qubits = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant(const, ctrl):
        # Controlled add of `const` into the sum register (ripple, controlled on ctrl).
        # Add const to sum_qubits (little-endian) using controlled ripple-carry via Toffoli chain.
        cbits = [(const >> k) & 1 for k in range(nbits)]
        # Perform addition from most significant handled by successive controlled increments.
        # Simple approach: for each set bit position p of const, add 2^p (controlled) with carry propagation.
        for p in range(nbits):
            if cbits[p] == 0:
                continue
            # add 1 at position p, controlled by ctrl, propagate carry upward
            # carry chain: flip sum[p]; carry into higher bits
            for j in range(nbits - 1, p, -1):
                # controlled increment carry: if ctrl and all sum[p..j-1] were 1 before flip
                controls = [ctrl] + sum_qubits[p:j]
                qc.mcx(controls, sum_qubits[j])
            qc.cx(ctrl, sum_qubits[p])

    def add_all(sign_forward=True):
        order = range(n) if sign_forward else reversed(range(n))
        for i in order:
            add_constant(a[i], problem_qubits[i])

    def uncompute_constant(const, ctrl):
        cbits = [(const >> k) & 1 for k in range(nbits)]
        for p in range(nbits):
            if cbits[p] == 0:
                continue
            qc.cx(ctrl, sum_qubits[p])
            for j in range(p + 1, nbits):
                controls = [ctrl] + sum_qubits[p:j]
                qc.mcx(controls, sum_qubits[j])

    # Compute the sum
    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # Flag = 1 iff sum register == T
    tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(sum_qubits[k])
    qc.h(flag)
    qc.mcx(sum_qubits, flag)
    qc.h(flag)
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(sum_qubits[k])

    # Uncompute the sum (reverse order, reverse operations)
    for i in reversed(range(n)):
        uncompute_constant(a[i], problem_qubits[i])
