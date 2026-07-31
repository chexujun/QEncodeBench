from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2, x3 = (problem_qubits[0], problem_qubits[1],
                      problem_qubits[2], problem_qubits[3])
    c = ancilla_qubits[:6]   # one ancilla per clause
    out = ancilla_qubits[6]  # AND-accumulator target for the phase

    # Each clause ci is computed to |1> iff the clause is SATISFIED.
    # Trick: clause (a OR b OR c) is FALSE iff a=b=c=0. Compute the
    # "all-false" pattern with an mcx onto the fresh ancilla (init |0>),
    # then X to flip: ancilla = NOT(all-false) = clause satisfied.
    # A literal NOT x is handled by pre-flipping that variable with X
    # (and undoing it), so the mcx controls fire on the "false" pattern.

    # Clause 0: (NOT x0 OR NOT x2 OR x3)  false iff x0=1,x2=1,x3=0
    qc.x(x3)
    qc.mcx([x0, x2, x3], c[0]); qc.x(c[0])
    qc.x(x3)

    # Clause 1: (x0 OR x1 OR x2)  false iff x0=0,x1=0,x2=0
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.mcx([x0, x1, x2], c[1]); qc.x(c[1])
    qc.x(x0); qc.x(x1); qc.x(x2)

    # Clause 2: (x0 OR NOT x1 OR NOT x2)  false iff x0=0,x1=1,x2=1
    qc.x(x0)
    qc.mcx([x0, x1, x2], c[2]); qc.x(c[2])
    qc.x(x0)

    # Clause 3: (NOT x0 OR x1 OR x2)  false iff x0=1,x1=0,x2=0
    qc.x(x1); qc.x(x2)
    qc.mcx([x0, x1, x2], c[3]); qc.x(c[3])
    qc.x(x1); qc.x(x2)

    # Clause 4: (NOT x0 OR x1 OR NOT x2)  false iff x0=1,x1=0,x2=1
    qc.x(x1)
    qc.mcx([x0, x1, x2], c[4]); qc.x(c[4])
    qc.x(x1)

    # Clause 5: (x1 OR x2 OR x3)  false iff x1=0,x2=0,x3=0
    qc.x(x1); qc.x(x2); qc.x(x3)
    qc.mcx([x1, x2, x3], c[5]); qc.x(c[5])
    qc.x(x1); qc.x(x2); qc.x(x3)

    # Phase: -1 iff all six clause ancillas are 1 (formula satisfied)
    qc.h(out)
    qc.mcx(c, out)
    qc.h(out)

    # Uncompute clause ancillas (exact mirror of compute)
    qc.x(x1); qc.x(x2); qc.x(x3)
    qc.x(c[5]); qc.mcx([x1, x2, x3], c[5])
    qc.x(x1); qc.x(x2); qc.x(x3)

    qc.x(x1)
    qc.x(c[4]); qc.mcx([x0, x1, x2], c[4])
    qc.x(x1)

    qc.x(x1); qc.x(x2)
    qc.x(c[3]); qc.mcx([x0, x1, x2], c[3])
    qc.x(x1); qc.x(x2)

    qc.x(x0)
    qc.x(c[2]); qc.mcx([x0, x1, x2], c[2])
    qc.x(x0)

    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.x(c[1]); qc.mcx([x0, x1, x2], c[1])
    qc.x(x0); qc.x(x1); qc.x(x2)

    qc.x(x3)
    qc.x(c[0]); qc.mcx([x0, x2, x3], c[0])
    qc.x(x3)
