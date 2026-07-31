from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = ancilla_qubits[0:4]
    out = ancilla_qubits[4]

    # Clause 0: (x0 OR x1 OR NOT x2). Unsatisfied iff x0=0,x1=0,x2=1.
    qc.x(x0); qc.x(x1)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[0]) if False else None
    qc.mcx([x0, x1, x2], c[0])
    qc.x(x0); qc.x(x1)

    # Clause 1: (x0 OR x1 OR x2). Unsatisfied iff x0=0,x1=0,x2=0.
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.mcx([x0, x1, x2], c[1])
    qc.x(x0); qc.x(x1); qc.x(x2)

    # Clause 2: (NOT x0 OR NOT x1 OR x2). Unsatisfied iff x0=1,x1=1,x2=0.
    qc.x(x2)
    qc.mcx([x0, x1, x2], c[2])
    qc.x(x2)

    # Clause 3: (x0 OR NOT x1 OR NOT x2). Unsatisfied iff x0=0,x1=1,x2=1.
    qc.x(x0)
    qc.mcx([x0, x1, x2], c[3])
    qc.x(x0)

    # c[k] == 1 means clause k is UNSATISFIED. Formula satisfied iff all c[k]==0.
    qc.x(c[0]); qc.x(c[1]); qc.x(c[2]); qc.x(c[3])
    qc.mcx([c[0], c[1], c[2], c[3]], out)
    qc.x(c[0]); qc.x(c[1]); qc.x(c[2]); qc.x(c[3])

    # Phase flip
    qc.z(out)

    # Uncompute out
    qc.x(c[0]); qc.x(c[1]); qc.x(c[2]); qc.x(c[3])
    qc.mcx([c[0], c[1], c[2], c[3]], out)
    qc.x(c[0]); qc.x(c[1]); qc.x(c[2]); qc.x(c[3])

    # Uncompute clause ancillas (mirror)
    qc.x(x0)
    qc.mcx([x0, x1, x2], c[3])
    qc.x(x0)

    qc.x(x2)
    qc.mcx([x0, x1, x2], c[2])
    qc.x(x2)

    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.mcx([x0, x1, x2], c[1])
    qc.x(x0); qc.x(x1); qc.x(x2)

    qc.x(x0); qc.x(x1)
    qc.mcx([x0, x1, x2], c[0])
    qc.x(x0); qc.x(x1)
