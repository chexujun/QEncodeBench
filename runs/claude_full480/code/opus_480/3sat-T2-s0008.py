from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    cl = ancilla_qubits[:6]
    out = ancilla_qubits[6]

    # clause literal specs: (var_index, negated?)
    clauses = [
        [(0, True),  (1, True),  (3, False)],
        [(2, True),  (3, False), (4, True)],
        [(0, False), (1, True),  (2, False)],
        [(0, False), (2, False), (3, False)],
        [(0, True),  (2, True),  (5, False)],
        [(1, True),  (2, True),  (5, False)],
    ]

    def compute_clauses(sign=+1):
        # For each clause, set clause-ancilla = OR of its 3 literals.
        # OR via De Morgan: NOT(AND(NOT l1, NOT l2, NOT l3)).
        for ci, lits in enumerate(clauses):
            ctrls = []
            flipped = []
            for (v, neg) in lits:
                q = p[v]
                # literal is True when: (neg False and q=1) or (neg True and q=0)
                # We want control-on for NOT(literal): control fires when literal is False.
                # literal False when: neg False -> q=0 ; neg True -> q=1
                if not neg:
                    # need control on q==0 -> flip q
                    qc.x(q); flipped.append(q)
                # else literal negated: literal False when q==1 -> control on q==1 directly
                ctrls.append(q)
            # mcx: all NOT-literals true -> AND of negations -> clause is False
            qc.mcx(ctrls, cl[ci])
            # clause ancilla currently = 1 iff clause False. Invert to get clause True.
            qc.x(cl[ci])
            for q in flipped:
                qc.x(q)

    # compute all clause ancillas
    compute_clauses()

    # out = AND of all clause ancillas
    qc.mcx(cl, out)
    qc.z(out)
    qc.mcx(cl, out)

    # uncompute clause ancillas (mirror)
    for ci in reversed(range(len(clauses))):
        lits = clauses[ci]
        flipped = []
        ctrls = []
        for (v, neg) in lits:
            q = p[v]
            if not neg:
                qc.x(q); flipped.append(q)
            ctrls.append(q)
        qc.x(cl[ci])
        qc.mcx(ctrls, cl[ci])
        for q in flipped:
            qc.x(q)
