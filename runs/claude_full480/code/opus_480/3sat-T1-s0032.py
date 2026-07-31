import numpy as np
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c0, c1, c2, c3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    out = ancilla_qubits[4]

    # Clause literals: clause satisfied -> ancilla = 1
    # Clause j ancilla is 1 iff clause is satisfied. Compute via NOT(all literals false).
    # We compute clause-unsatisfied indicator then flip.

    # Clause 0: (x0 OR x1 OR NOT x2). Unsatisfied iff x0=0,x1=0,x2=1.
    qc.x(x0); qc.x(x1)
    qc.mcx([x0, x1, x2], c0)
    qc.x(x0); qc.x(x1)
    qc.x(c0)  # c0 = clause0 satisfied

    # Clause 1: (x0 OR NOT x1 OR NOT x2). Unsatisfied iff x0=0,x1=1,x2=1.
    qc.x(x0)
    qc.mcx([x0, x1, x2], c1)
    qc.x(x0)
    qc.x(c1)

    # Clause 2: (x0 OR NOT x1 OR x2). Unsatisfied iff x0=0,x1=1,x2=0.
    qc.x(x0); qc.x(x2)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x0); qc.x(x2)
    qc.x(c2)

    # Clause 3: (x0 OR x1 OR x2). Unsatisfied iff x0=0,x1=0,x2=0.
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.mcx([x0, x1, x2], c3)
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.x(c3)

    # Phase -1 iff all clauses satisfied (c0=c1=c2=c3=1)
    qc.h(out)
    qc.mcx([c0, c1, c2, c3], out)
    qc.h(out)

    # Uncompute clause ancillas (mirror)
    qc.x(c3)
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.mcx([x0, x1, x2], c3)
    qc.x(x0); qc.x(x1); qc.x(x2)

    qc.x(c2)
    qc.x(x0); qc.x(x2)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x0); qc.x(x2)

    qc.x(c1)
    qc.x(x0)
    qc.mcx([x0, x1, x2], c1)
    qc.x(x0)

    qc.x(c0)
    qc.x(x0); qc.x(x1)
    qc.mcx([x0, x1, x2], c0)
    qc.x(x0); qc.x(x1)
