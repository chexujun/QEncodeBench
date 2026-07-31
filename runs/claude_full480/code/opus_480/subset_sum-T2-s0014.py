import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [2, 8, 5, 6]
    T = 2
    n = len(a)

    # Sum bit-width: enough to hold the maximum possible sum (2+8+5+6 = 21 -> 5 bits)
    total = sum(a)
    W = max(1, total.bit_length())

    sum_q = ancilla_qubits[:W]           # register holding the running sum
    flag = ancilla_qubits[W]             # phase flag ancilla

    def add_constant(c, control):
        # Controlled add of constant c into sum register (ripple, LSB->MSB),
        # implemented via controlled increments per set bit using carry chains.
        # We add c to sum_q conditioned on `control`, in place, no extra carry ancilla
        # by doing controlled ripple addition of a classical constant.
        # Use the standard "add classical constant" via controlled increments.
        for shift in range(W):
            if (c >> shift) & 1:
                # add 1 at position `shift`: ripple increment from MSB down to shift
                for j in range(W - 1, shift, -1):
                    ctrls = [control] + sum_q[shift:j]
                    qc.mcx(ctrls, sum_q[j])
                qc.cx(control, sum_q[shift])

    def add_constant_inv(c, control):
        for shift in range(W):
            if (c >> shift) & 1:
                qc.cx(control, sum_q[shift])
                for j in range(shift + 1, W):
                    ctrls = [control] + sum_q[shift:j]
                    qc.mcx(ctrls, sum_q[j])

    # Compute: accumulate selected values into sum register
    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # Phase: mark states where sum == T
    tbits = [(T >> k) & 1 for k in range(W)]
    for k in range(W):
        if tbits[k] == 0:
            qc.x(sum_q[k])
    if W == 1:
        qc.z(sum_q[0])
    else:
        qc.h(sum_q[W - 1])
        qc.mcx(sum_q[:W - 1], sum_q[W - 1])
        qc.h(sum_q[W - 1])
    for k in range(W):
        if tbits[k] == 0:
            qc.x(sum_q[k])

    # Uncompute
    for i in range(n - 1, -1, -1):
        add_constant_inv(a[i], problem_qubits[i])
