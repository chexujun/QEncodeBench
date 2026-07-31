from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # Clauses as (var, negated) literals. Clause satisfied unless all literals false.
    clauses = [
        [(0, True), (2, True), (3, False)],   # NOT x0 OR NOT x2 OR x3
        [(0, True), (2, False), (3, False)],  # NOT x0 OR x2 OR x3
        [(0, True), (1, False), (2, False)],  # NOT x0 OR x1 OR x2
        [(0, False), (1, True), (2, False)],  # x0 OR NOT x1 OR x2
        [(1, False), (2, True), (3, False)],  # x1 OR NOT x2 OR x3
    ]

    def compute():
        for k, clause in enumerate(clauses):
            # A literal is FALSE when: positive literal and var=0, or negative literal and var=1.
            # Set clause ancilla = 1 iff all three literals false (clause unsatisfied).
            # Flip qubits so that the "all false" condition maps to all-ones, then ccx.
            controls = []
            for (v, neg) in clause:
                if not neg:
                    # positive literal false when var=0 -> flip so 0->1
                    qc.x(x[v])
                controls.append(x[v])
            qc.mcx(controls, cl[k])
            # restore
            for (v, neg) in clause:
                if not neg:
                    qc.x(x[v])
            # Now cl[k] = 1 iff clause unsatisfied; invert so cl[k]=1 iff satisfied
            qc.x(cl[k])

    compute()
    # formula satisfied iff all clause ancillas are 1
    qc.mcx(cl, out)
    qc.z(out)
    qc.mcx(cl, out)

    # uncompute (mirror)
    for k in reversed(range(len(clauses))):
        clause = clauses[k]
        qc.x(cl[k])
        controls = []
        for (v, neg) in clause:
            if not neg:
                qc.x(x[v])
            controls.append(x[v])
        qc.mcx(controls, cl[k])
        for (v, neg) in clause:
            if not neg:
                qc.x(x[v])
