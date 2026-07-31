import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits

    # Each clause is a list of (variable_index, is_negated)
    clauses = [
        [(0, False), (1, False), (3, False)],
        [(2, True),  (3, True),  (4, False)],
        [(1, True),  (2, False), (4, False)],
        [(1, False), (2, False), (5, True)],
        [(2, False), (3, False), (4, False)],
        [(0, True),  (1, False), (3, True)],
        [(1, True),  (2, True),  (5, True)],
        [(0, False), (4, True),  (5, False)],
        [(0, True),  (2, False), (4, True)],
    ]

    # One ancilla per clause holds clause_value; last ancilla holds the AND.
    clause_anc = ancilla_qubits[:len(clauses)]   # 9 ancillas
    result_anc = ancilla_qubits[len(clauses)]    # 1 ancilla

    def compute_clauses():
        for c, lits in zip(clause_anc, clauses):
            # clause is OR of literals. Use De Morgan:
            # clause = NOT( AND of negated literals ).
            # A literal (v, neg): literal true when qubit == (0 if neg else 1).
            # negated-literal true when qubit == (1 if neg else 0).
            # Flip controls so that control-on means negated-literal true.
            ctrls = []
            for v, neg in lits:
                if not neg:
                    qc.x(x[v])   # so control fires when literal is false (var==0)
                ctrls.append(x[v])
            # if all negated literals true -> all clause literals false -> clause false
            # set ancilla to AND of controls, then we want clause = NOT(that)
            qc.mcx(ctrls, c)
            # undo the flips
            for v, neg in lits:
                if not neg:
                    qc.x(x[v])
            # ancilla c currently = 1 iff clause is FALSE; invert to get clause value
            qc.x(c)

    compute_clauses()
    # result = AND of all clause values
    qc.mcx(clause_anc, result_anc)
    # phase
    qc.z(result_anc)
    # uncompute result
    qc.mcx(clause_anc, result_anc)

    # uncompute clauses (mirror)
    for c, lits in zip(clause_anc, clauses):
        qc.x(c)
        ctrls = []
        for v, neg in lits:
            if not neg:
                qc.x(x[v])
            ctrls.append(x[v])
        qc.mcx(ctrls, c)
        for v, neg in lits:
            if not neg:
                qc.x(x[v])
