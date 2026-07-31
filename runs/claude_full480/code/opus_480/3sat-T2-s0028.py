from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:6]
    out = ancilla_qubits[6]

    # Each clause: (lit_a OR lit_b OR lit_c). Clause is satisfied unless all literals false.
    # We compute clause-ancilla = 1 when clause is SATISFIED.
    # A literal "x_i" is false when qubit=0; "NOT x_i" is false when qubit=1.
    # Strategy: clause is FALSE iff every literal is false. Set clause ancilla via:
    #   temporarily set each involved qubit so that "all literals false" -> all controls 1,
    #   then mcx flips clause ancilla to 1 for the all-false case, then X to invert (satisfied=1).
    # For a positive literal x_i (false when 0): apply X so control=1 means literal false.
    # For a negative literal NOT x_i (false when 1): control=1 already means literal false.

    clauses = [
        [(0, True),  (1, True),  (2, True)],   # NOT x0 OR NOT x1 OR NOT x2
        [(0, False), (1, True),  (3, True)],   # x0 OR NOT x1 OR NOT x3
        [(0, True),  (2, False), (3, True)],   # NOT x0 OR x2 OR NOT x3
        [(0, True),  (1, False), (3, True)],   # NOT x0 OR x1 OR NOT x3
        [(1, True),  (2, False), (3, True)],   # NOT x1 OR x2 OR NOT x3
        [(0, True),  (2, True),  (3, False)],  # NOT x0 OR NOT x2 OR x3
    ]

    def compute_clauses():
        for ci, clause in enumerate(clauses):
            ctrls = []
            for (var, negated) in clause:
                if not negated:
                    # positive literal x_var: false when qubit==0 -> flip so control=1 on false
                    qc.x(x[var])
                ctrls.append(x[var])
            # all controls==1 means all literals false -> clause false
            qc.mcx(ctrls, cl[ci])
            qc.x(cl[ci])  # invert: now cl[ci]==1 iff clause satisfied
            # restore flipped positive-literal qubits
            for (var, negated) in clause:
                if not negated:
                    qc.x(x[var])

    def uncompute_clauses():
        for ci in reversed(range(len(clauses))):
            clause = clauses[ci]
            for (var, negated) in clause:
                if not negated:
                    qc.x(x[var])
            qc.x(cl[ci])
            qc.mcx([x[var] for (var, negated) in clause], cl[ci])
            for (var, negated) in clause:
                if not negated:
                    qc.x(x[var])

    compute_clauses()
    # phase -1 iff all clause ancillas are 1 (formula satisfied)
    qc.h(out)
    qc.mcx(cl, out)
    qc.h(out)
    uncompute_clauses()
