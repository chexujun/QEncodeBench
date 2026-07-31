from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c = ancilla_qubits[0:5]
    out = ancilla_qubits[5]

    # Clause 1: (x1 OR NOT x2 OR NOT x3) -> false iff x1=0, x2=1, x3=1
    #   c0 = 1 when clause satisfied. Compute NOT(unsat).
    #   unsat: x1=0 & x2=1 & x3=1. c0 = 1 - unsat.
    qc.x(x1)
    qc.mcx([x1, x2, x3], c[0])
    qc.x(x1)
    qc.x(c[0])  # c0 = satisfied

    # Clause 2: (NOT x0 OR NOT x2 OR x3) -> unsat iff x0=1, x2=1, x3=0
    qc.x(x3)
    qc.mcx([x0, x2, x3], c[1])
    qc.x(x3)
    qc.x(c[1])

    # Clause 3: (NOT x1 OR x2 OR x3) -> unsat iff x1=1, x2=0, x3=0
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], c[2])
    qc.x(x3)
    qc.x(x2)
    qc.x(c[2])

    # Clause 4: (x0 OR x2 OR x3) -> unsat iff x0=0, x2=0, x3=0
    qc.x(x0)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x0, x2, x3], c[3])
    qc.x(x3)
    qc.x(x2)
    qc.x(x0)
    qc.x(c[3])

    # Clause 5: (x0 OR NOT x2 OR NOT x3) -> unsat iff x0=0, x2=1, x3=1
    qc.x(x0)
    qc.mcx([x0, x2, x3], c[4])
    qc.x(x0)
    qc.x(c[4])

    # AND of all five clauses -> phase
    qc.h(out)
    qc.mcx([c[0], c[1], c[2], c[3], c[4]], out)
    qc.h(out)

    # Uncompute clauses (mirror)
    qc.x(c[4])
    qc.x(x0)
    qc.mcx([x0, x2, x3], c[4])
    qc.x(x0)

    qc.x(c[3])
    qc.x(x0)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x0, x2, x3], c[3])
    qc.x(x3)
    qc.x(x2)
    qc.x(x0)

    qc.x(c[2])
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], c[2])
    qc.x(x3)
    qc.x(x2)

    qc.x(c[1])
    qc.x(x3)
    qc.mcx([x0, x2, x3], c[1])
    qc.x(x3)

    qc.x(c[0])
    qc.x(x1)
    qc.mcx([x1, x2, x3], c[0])
    qc.x(x1)
