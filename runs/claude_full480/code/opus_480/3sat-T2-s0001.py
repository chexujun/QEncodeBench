from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    c0, c1, c2, c3 = ancilla_qubits[0:4]
    out = ancilla_qubits[4]

    # Clause 0: (NOT x1 OR NOT x2 OR x3)
    # Falsified iff x1=1, x2=1, x3=0. c0=1 when clause satisfied.
    qc.x(x3)
    qc.ccx(x1, x2, c0)      # c0 = x1 & x2 & (NOT x3) = clause falsified
    qc.x(x3)
    qc.x(c0)               # c0 = clause satisfied

    # Clause 1: (NOT x0 OR NOT x3 OR NOT x4)
    # Falsified iff x0=1, x3=1, x4=1.
    qc.mcx([x0, x3, x4], c1)
    qc.x(c1)

    # Clause 2: (x0 OR x1 OR x2)
    # Falsified iff x0=0, x1=0, x2=0.
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.x(c2)

    # Clause 3: (NOT x1 OR x2 OR x4)
    # Falsified iff x1=1, x2=0, x4=0.
    qc.x(x2); qc.x(x4)
    qc.mcx([x1, x2, x4], c3)
    qc.x(x2); qc.x(x4)
    qc.x(c3)

    # out = AND of all clause-satisfied bits
    qc.mcx([c0, c1, c2, c3], out)
    qc.z(out)
    qc.mcx([c0, c1, c2, c3], out)

    # Uncompute clause bits (mirror)
    qc.x(c3)
    qc.x(x2); qc.x(x4)
    qc.mcx([x1, x2, x4], c3)
    qc.x(x2); qc.x(x4)

    qc.x(c2)
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x0); qc.x(x1); qc.x(x2)

    qc.x(c1)
    qc.mcx([x0, x3, x4], c1)

    qc.x(c0)
    qc.x(x3)
    qc.ccx(x1, x2, c0)
    qc.x(x3)
