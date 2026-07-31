import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c = ancilla_qubits  # clause ancillas 0..4, final ancilla 5

    def compute():
        # Clause 0: (NOT x0 OR NOT x2 OR NOT x3) -> false only when x0=x2=x3=1
        qc.x(x0); qc.x(x2); qc.x(x3)
        qc.mcx([x0, x2, x3], c[0])
        qc.x(x0); qc.x(x2); qc.x(x3)
        qc.x(c[0])  # c0 = clause0 truth

        # Clause 1: (x0 OR x2 OR x3) -> false only when x0=x2=x3=0
        qc.x(x0); qc.x(x2); qc.x(x3)
        qc.mcx([x0, x2, x3], c[1])
        qc.x(x0); qc.x(x2); qc.x(x3)
        qc.x(c[1])

        # Clause 2: (x0 OR x2 OR NOT x3) -> false only when x0=0,x2=0,x3=1
        qc.x(x0); qc.x(x2)
        qc.mcx([x0, x2, x3], c[2])
        qc.x(x0); qc.x(x2)
        qc.x(c[2])

        # Clause 3: (x1 OR x2 OR NOT x3) -> false only when x1=0,x2=0,x3=1
        qc.x(x1); qc.x(x2)
        qc.mcx([x1, x2, x3], c[3])
        qc.x(x1); qc.x(x2)
        qc.x(c[3])

        # Clause 4: (x0 OR x1 OR NOT x2) -> false only when x0=0,x1=0,x2=1
        qc.x(x0); qc.x(x1)
        qc.mcx([x0, x1, x2], c[4])
        qc.x(x0); qc.x(x1)
        qc.x(c[4])

    compute()
    # phase -1 iff all clauses satisfied (c0..c4 all 1)
    qc.h(c[5])
    qc.mcx([c[0], c[1], c[2], c[3], c[4]], c[5])
    qc.h(c[5])
    # uncompute (mirror)
    qc.x(c[4])
    qc.x(x0); qc.x(x1)
    qc.mcx([x0, x1, x2], c[4])
    qc.x(x0); qc.x(x1)

    qc.x(c[3])
    qc.x(x1); qc.x(x2)
    qc.mcx([x1, x2, x3], c[3])
    qc.x(x1); qc.x(x2)

    qc.x(c[2])
    qc.x(x0); qc.x(x2)
    qc.mcx([x0, x2, x3], c[2])
    qc.x(x0); qc.x(x2)

    qc.x(c[1])
    qc.x(x0); qc.x(x2); qc.x(x3)
    qc.mcx([x0, x2, x3], c[1])
    qc.x(x0); qc.x(x2); qc.x(x3)

    qc.x(c[0])
    qc.x(x0); qc.x(x2); qc.x(x3)
    qc.mcx([x0, x2, x3], c[0])
    qc.x(x0); qc.x(x2); qc.x(x3)
