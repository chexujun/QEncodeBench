from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    c = ancilla_qubits  # one ancilla per clause: c[0..3]
    out = ancilla_qubits[4] if len(ancilla_qubits) > 4 else None

    # Clause literals: (var_index, positive?)
    clauses = [
        [(2, True), (3, False), (4, True)],    # x2 OR NOT x3 OR x4
        [(2, False), (3, False), (4, True)],   # NOT x2 OR NOT x3 OR x4
        [(2, True), (3, True), (4, False)],    # x2 OR x3 OR NOT x4
        [(1, True), (2, False), (4, False)],   # x1 OR NOT x2 OR NOT x4
    ]

    def compute_clause(clause, target):
        # target becomes 1 iff clause is satisfied.
        # Clause is OR of literals; NOT-satisfied iff all literals false.
        # Compute AND of negated-literals into target, then flip.
        neg = []
        for (v, pos) in clause:
            if pos:
                qc.x(x[v])  # so that control-on-1 means literal false
            neg.append(x[v])
        qc.mcx(neg, target)  # target = AND(all literals false)
        for (v, pos) in clause:
            if pos:
                qc.x(x[v])
        qc.x(target)  # target = clause satisfied

    # Compute each clause into its ancilla
    for i in range(4):
        compute_clause(clauses[i], c[i])

    # Phase -1 iff all four clause ancillas are 1
    qc.h(c[3])
    qc.mcx([c[0], c[1], c[2]], c[3])
    qc.h(c[3])

    # Uncompute clauses (mirror)
    for i in reversed(range(4)):
        compute_clause(clauses[i], c[i])
