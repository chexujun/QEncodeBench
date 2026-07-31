import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]

    # One ancilla per clause; ancilla=1 means the clause is SATISFIED.
    clauses = [
        [(x0, True), (x1, False), (x2, False)],   # (NOT x0 OR x1 OR x2)
        [(x0, False), (x1, True), (x2, True)],    # (x0 OR NOT x1 OR NOT x2)
        [(x0, True), (x1, True), (x2, True)],     # (NOT x0 OR NOT x1 OR NOT x2)
        [(x0, False), (x1, False), (x2, True)],   # (x0 OR x1 OR NOT x2)
        [(x0, True), (x1, True), (x2, False)],    # (NOT x0 OR NOT x1 OR x2)
    ]
    clause_anc = ancilla_qubits[0:5]
    final_anc = ancilla_qubits[5]

    def compute_clause(clause, anc):
        # clause literals: (qubit, negated?) where negated=True means NOT var.
        # A clause is FALSE only when every literal is False, i.e. each var
        # equals the value that makes its literal false.
        # Flip inputs so that the "clause false" configuration maps to all-1,
        # then AND with an mcx; result stored, then invert so anc=1 => satisfied.
        for q, neg in clause:
            # literal is false when: (neg=True and var=1) or (neg=False and var=0)
            # We want the "all literals false" state to be all-ones on controls.
            if not neg:
                qc.x(q)  # var=0 makes literal false -> map to control-1
        qc.mcx([q for q, _ in clause], anc)
        for q, neg in clause:
            if not neg:
                qc.x(q)
        qc.x(anc)  # anc=1 iff clause satisfied

    # Compute all clause ancillas.
    for clause, anc in zip(clauses, clause_anc):
        compute_clause(clause, anc)

    # AND all clause ancillas into the final ancilla, apply phase.
    qc.mcx(clause_anc, final_anc)
    qc.z(final_anc)
    qc.mcx(clause_anc, final_anc)

    # Uncompute clause ancillas (mirror).
    for clause, anc in zip(reversed(clauses), reversed(clause_anc)):
        compute_clause(clause, anc)
