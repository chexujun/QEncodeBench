from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    anc = ancilla_qubits

    # Unique valid completion:
    #   cell0 (0,1) = value 0  -> code 00 or 11 -> b0 == b1
    #   cell1 (1,1) = value 2  -> code 10       -> b0 == 0, b1 == 1
    #   cell2 (1,2) = value 1  -> code 01       -> b0 == 1, b1 == 0
    # bits: cell0 b0=p[0] b1=p[1]; cell1 b0=p[2] b1=p[3]; cell2 b0=p[4] b1=p[5]

    a0, a1, a2 = anc[0], anc[1], anc[2]

    # compute a0 = 1 iff b0 == b1  (NOT(b0 XOR b1))
    qc.cx(p[0], a0)
    qc.cx(p[1], a0)
    qc.x(a0)

    # compute a1 = 1 iff (b0 == 0 and b1 == 1)
    qc.x(p[2])
    qc.ccx(p[2], p[3], a1)
    qc.x(p[2])

    # compute a2 = 1 iff (b0 == 1 and b1 == 0)
    qc.x(p[5])
    qc.ccx(p[4], p[5], a2)
    qc.x(p[5])

    # phase: -1 iff a0 AND a1 AND a2  (multi-controlled Z via H-MCX-H on a2)
    qc.h(a2)
    qc.ccx(a0, a1, a2)
    qc.h(a2)

    # uncompute a2
    qc.x(p[5])
    qc.ccx(p[4], p[5], a2)
    qc.x(p[5])

    # uncompute a1
    qc.x(p[2])
    qc.ccx(p[2], p[3], a1)
    qc.x(p[2])

    # uncompute a0
    qc.x(a0)
    qc.cx(p[1], a0)
    qc.cx(p[0], a0)
