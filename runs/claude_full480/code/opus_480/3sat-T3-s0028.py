from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    clause_anc = ancilla_qubits[:8]
    out = ancilla_qubits[8]

    # Each clause: (lit_a OR lit_b OR lit_c).
    # clause literals: (qubit_index, negated?)  negated=True means literal is NOT x_i
    clauses = [
        [(0, False), (1, False), (7, False)],
        [(3, True),  (4, False), (6, False)],
        [(0, False), (2, True),  (4, True)],
        [(0, False), (1, True),  (3, True)],
        [(0, True),  (6, False), (7, False)],
        [(5, False), (6, True),  (7, True)],
        [(0, False), (4, True),  (6, False)],
        [(0, False), (6, True),  (7, True)],
    ]

    def compute_clauses():
        for k, clause in enumerate(clauses):
            a = clause_anc[k]
            # OR = NOT(AND of negated literals).
            # Set clause ancilla to 1 iff clause satisfied.
            # Compute AND of (NOT literal) into a, then flip.
            ctrls = [p[i] for (i, neg) in clause]
            # For literal true when x_i == (not neg). NOT-literal true when x_i == neg.
            # We want AND of NOT-literals -> flip qubits so that control-on-1 matches x_i==neg.
            for (i, neg) in clause:
                if not neg:
                    qc.x(p[i])   # so control fires when original x_i==0 (i.e., NOT literal of a positive lit)
                # for neg literal, NOT-literal true when x_i==1 -> control on 1 directly
            qc.mcx(ctrls, a)
            for (i, neg) in clause:
                if not neg:
                    qc.x(p[i])
            qc.x(a)  # a = 1 iff clause satisfied

    # compute
    compute_clauses()
    # AND all clause ancillas into out
    qc.mcx(clause_anc, out)
    # phase
    qc.z(out)
    # uncompute out
    qc.mcx(clause_anc, out)
    # uncompute clauses (mirror)
    for k in reversed(range(len(clauses))):
        clause = clauses[k]
        a = clause_anc[k]
        ctrls = [p[i] for (i, neg) in clause]
        qc.x(a)
        for (i, neg) in clause:
            if not neg:
                qc.x(p[i])
        qc.mcx(ctrls, a)
        for (i, neg) in clause:
            if not neg:
                qc.x(p[i])
