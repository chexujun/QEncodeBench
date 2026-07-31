from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2, x3 = (problem_qubits[0], problem_qubits[1],
                      problem_qubits[2], problem_qubits[3])

    # Clauses as (qubit, negated?) literals. Clause satisfied unless ALL
    # literals are false. We compute per-clause "clause is FALSE" flags,
    # then the formula is satisfied iff none of the clause-false flags is set.
    clauses = [
        [(x0, True),  (x2, True),  (x3, False)],  # (¬x0 ∨ ¬x2 ∨ x3)
        [(x0, False), (x2, False), (x3, False)],  # ( x0 ∨  x2 ∨ x3)
        [(x0, False), (x2, True),  (x3, False)],  # ( x0 ∨ ¬x2 ∨ x3)
        [(x0, False), (x1, True),  (x2, True)],   # ( x0 ∨ ¬x1 ∨ ¬x2)
        [(x0, True),  (x2, True),  (x3, True)],   # (¬x0 ∨ ¬x2 ∨ ¬x3)
    ]

    clause_anc = ancilla_qubits[0:5]   # one flag per clause
    phase_anc = ancilla_qubits[5]      # AND of all satisfied clauses

    def compute():
        for c_idx, clause in enumerate(clauses):
            a = clause_anc[c_idx]
            ctrls = [q for (q, _) in clause]
            # A literal (q, neg) is TRUE when q == (0 if neg else 1).
            # Clause is FALSE when every literal is false, i.e.
            #   q == (1 if neg else 0) for all literals.
            # Flip controls so that "all literals false" -> all controls |1>.
            for (q, neg) in clause:
                if not neg:
                    qc.x(q)          # non-negated: literal false when q==0
            # else negated: literal false when q==1 -> already |1>, no flip
            qc.mcx(ctrls, a)         # a = 1 iff clause is FALSE
            qc.x(a)                  # a = 1 iff clause is TRUE (satisfied)
            for (q, neg) in clause:
                if not neg:
                    qc.x(q)          # restore

    compute()
    # phase_anc = AND of all clause-satisfied flags
    qc.mcx(clause_anc, phase_anc)
    qc.z(phase_anc)
    qc.mcx(clause_anc, phase_anc)
    # uncompute clause flags (compute is its own inverse)
    compute()
