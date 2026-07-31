from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:6]
    out = ancilla_qubits[6]

    # Clause definitions: list of (qubit_index, negated) literals.
    # A clause is satisfied if any literal is true.
    # literal true = (x[i]==1 and not negated) or (x[i]==0 and negated)
    clauses = [
        [(1, True), (3, True), (4, False)],   # (NOT x1 OR NOT x3 OR x4)
        [(0, False), (2, False), (3, False)],  # (x0 OR x2 OR x3)
        [(1, False), (3, False), (4, True)],   # (x1 OR x3 OR NOT x4)
        [(0, True), (2, True), (3, False)],    # (NOT x0 OR NOT x2 OR x3)
        [(0, False), (1, False), (2, True)],   # (x0 OR x1 OR NOT x2)
        [(1, False), (2, True), (3, True)],    # (x1 OR NOT x2 OR NOT x3)
    ]

    def compute_clause(clause, target):
        # Clause is OR of literals. NOT(clause) = AND of negated literals.
        # We compute clause value into target (=1 if satisfied).
        # Use De Morgan: set target=1, then flip inputs so that a literal being
        # FALSE corresponds to control=1; if all literals false, all controls=1.
        # For each literal, control qubit is x[i]; literal false when:
        #   not negated -> x[i]==0 ; negated -> x[i]==1
        # We want an mcx that fires (target ^=1) exactly when ALL literals false.
        # Arrange so control==1 means literal false: apply X on x[i] when
        # literal is true-at-1 (not negated), leave when negated.
        ctrls = []
        for (i, negated) in clause:
            if not negated:
                qc.x(x[i])   # now x[i]==1 means literal false (orig 0)
            ctrls.append(x[i])
        # target starts |0>; set target = OR = NOT(all controls 1)
        qc.x(target)
        qc.mcx(ctrls, target)
        # undo the X flips on inputs
        for (i, negated) in clause:
            if not negated:
                qc.x(x[i])

    def uncompute_clause(clause, target):
        for (i, negated) in clause:
            if not negated:
                qc.x(x[i])
        qc.mcx([x[i] for (i, _) in clause], target)
        qc.x(target)
        for (i, negated) in clause:
            if not negated:
                qc.x(x[i])

    # Compute each clause value into its clause ancilla.
    for k, clause in enumerate(clauses):
        compute_clause(clause, cl[k])

    # Formula satisfied iff all clause ancillas == 1. Phase flip via mcp.
    qc.mcp(pi, cl[:-1], cl[-1])

    # Uncompute clause ancillas.
    for k in reversed(range(len(clauses))):
        uncompute_clause(clauses[k], cl[k])
