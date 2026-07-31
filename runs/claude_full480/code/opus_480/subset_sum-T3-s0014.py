from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [6, 15, 11, 10, 10]
    T = 6
    n = len(a)

    # Sum-register width: enough bits to hold the max possible sum (52 -> 6 bits)
    total_max = sum(a)
    m = total_max.bit_length()           # number of sum-register bits
    sum_qubits = ancilla_qubits[:m]      # ancillas used as a binary adder register
    flag = ancilla_qubits[m]             # extra ancilla for the phase kick

    def add_constant(const, sign):
        # Add (sign=+1) or subtract (sign=-1) a constant `const`, controlled by
        # selection qubit, into the sum register using controlled ripple adds.
        pass

    # We implement compute as: for each element, controlled-add a[i] into the
    # sum register (an integer accumulator). Then compare register == T, flip
    # flag, phase, then uncompute the comparison and the additions.

    def ctrl_add(ctrl, value):
        # Controlled addition of integer `value` into sum register (LSB first),
        # ripple-carry via reversible increments. We realize controlled +value
        # by processing each set bit of value with controlled ripple carries.
        # Standard controlled ripple-carry increment-by-value.
        for shift in range(m):
            if (value >> shift) & 1:
                # add 1 at position `shift`: ripple carry from `shift` upward
                for j in range(m - 1, shift, -1):
                    controls = [ctrl] + [sum_qubits[k] for k in range(shift, j)]
                    qc.mcx(controls, sum_qubits[j])
                qc.cx(ctrl, sum_qubits[shift])

    def ctrl_add_inv(ctrl, value):
        for shift in range(m):
            if (value >> shift) & 1:
                qc.cx(ctrl, sum_qubits[shift])
                for j in range(shift + 1, m):
                    controls = [ctrl] + [sum_qubits[k] for k in range(shift, j)]
                    qc.mcx(controls, sum_qubits[j])

    # compute: accumulate sum
    for i in range(n):
        ctrl_add(problem_qubits[i], a[i])

    # compare register == T : set flag if all bits match T
    # X-mask bits that should be 0 in T, then multi-controlled X onto flag,
    # then unmask.
    mask = [q for q in range(m) if not ((T >> q) & 1)]
    for q in mask:
        qc.x(sum_qubits[q])
    qc.mcx(sum_qubits[:m], flag)
    for q in mask:
        qc.x(sum_qubits[q])

    # phase
    qc.z(flag)

    # uncompute comparison
    for q in mask:
        qc.x(sum_qubits[q])
    qc.mcx(sum_qubits[:m], flag)
    for q in mask:
        qc.x(sum_qubits[q])

    # uncompute sum
    for i in range(n - 1, -1, -1):
        ctrl_add_inv(problem_qubits[i], a[i])
