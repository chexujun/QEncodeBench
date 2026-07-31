from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:6]
    out = ancilla_qubits[6]

    # Clause literal specs: (var_index, negated?)
    clauses = [
        [(0, False), (1, False), (2, True)],   # x0 OR x1 OR NOT x2
        [(0, False), (2, False), (3, True)],   # x0 OR x2 OR NOT x3
        [(1, True),  (2, False), (3, False)],  # NOT x1 OR x2 OR x3
        [(0, True),  (2, True),  (3, True)],   # NOT x0 OR NOT x2 OR NOT x3
        [(0, True),  (2, False), (3, False)],  # NOT x0 OR x2 OR x3
        [(1, False), (2, False), (3, False)],  # x1 OR x2 OR x3
    ]

    def compute_clauses():
        # For each clause, set cl[i] = 1 iff clause satisfied.
        # A clause (l_a OR l_b OR l_c) is FALSE iff all literals false.
        # Compute NOT(clause) via CCX on the "false" conditions, then X to flip.
        for i, lits in enumerate(clauses):
            controls = []
            flips = []
            for (vi, neg) in lits:
                q = x[vi]
                # literal is false when: (positive lit) var==0 ; (negated lit) var==1
                # We want control-on-condition-that-literal-is-false.
                if not neg:
                    # positive literal false when var==0 -> flip var so control on 1
                    qc.x(q)
                    flips.append(q)
                    controls.append(q)
                else:
                    # negated literal false when var==1 -> control on 1 directly
                    controls.append(q)
            # cl[i] = AND(all literals false) = NOT(clause)
            qc.mcx(controls, cl[i])
            # undo temporary flips
            for q in flips:
                qc.x(q)
            # cl[i] currently = NOT(clause); flip to get clause value
            qc.x(cl[i])

    def uncompute_clauses():
        for i in reversed(range(len(clauses))):
            lits = clauses[i]
            qc.x(cl[i])
            controls = []
            flips = []
            for (vi, neg) in lits:
                q = x[vi]
                if not neg:
                    qc.x(q)
                    flips.append(q)
                    controls.append(q)
                else:
                    controls.append(q)
            qc.mcx(controls, cl[i])
            for q in flips:
                qc.x(q)

    # Compute all clause bits
    compute_clauses()
    # out = AND of all clause bits = formula satisfied
    qc.mcx(cl, out)
    # Phase flip when out == 1
    qc.z(out)
    # Uncompute out
    qc.mcx(cl, out)
    # Uncompute clause bits
    uncompute_clauses()
