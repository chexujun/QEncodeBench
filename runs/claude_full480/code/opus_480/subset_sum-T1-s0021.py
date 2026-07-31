from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [6, 6, 4]
    T = 4
    n = len(a)
    nsum = 4  # sum register width: max sum = 16 fits in 4 bits (0..15)
    s = ancilla_qubits[0:nsum]      # sum accumulator qubits (little-endian)
    flag = ancilla_qubits[nsum]     # phase flag ancilla

    def add_constant(ctrl, c, sqs):
        # Controlled add of constant c into sum register sqs (little-endian),
        # ripple via controlled increments per bit using ccx cascades.
        # Implement controlled addition by adding each bit of c with carries.
        w = len(sqs)
        cbits = [(c >> k) & 1 for k in range(w)]
        # Add c to register controlled on ctrl.
        # Use a schoolbook ripple: for each set bit position k of c, add 1 at position k.
        for k in range(w):
            if cbits[k]:
                # add 1 starting at bit k, controlled on ctrl
                # increment sqs[k:] by 1: standard controlled increment
                for j in range(w - 1, k, -1):
                    controls = [ctrl] + sqs[k:j]
                    qc.mcx(controls, sqs[j])
                qc.cx(ctrl, sqs[k])

    def unadd_constant(ctrl, c, sqs):
        w = len(sqs)
        cbits = [(c >> k) & 1 for k in range(w)]
        for k in reversed(range(w)):
            if cbits[k]:
                qc.cx(ctrl, sqs[k])
                for j in range(k + 1, w):
                    controls = [ctrl] + sqs[k:j]
                    qc.mcx(controls, sqs[j])

    # Compute sum = sum of selected a[i] into s
    for i in range(n):
        add_constant(problem_qubits[i], a[i], s)

    # Flag = 1 iff s == T. T=4 -> bits (little-endian over 4): 0,0,1,0
    Tbits = [(T >> k) & 1 for k in range(nsum)]
    for k in range(nsum):
        if Tbits[k] == 0:
            qc.x(s[k])
    qc.h(flag)
    qc.mcx(s, flag)
    qc.h(flag)
    for k in range(nsum):
        if Tbits[k] == 0:
            qc.x(s[k])

    # Uncompute sum
    for i in reversed(range(n)):
        unadd_constant(problem_qubits[i], a[i], s)
